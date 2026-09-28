import streamlit as st
import pandas as pd
import glob

st.set_page_config(layout="wide", page_title="Sete Lagos Final")
st.title("Painel Sete Lagos - 5 Painéis")

abas = st.tabs(["📍 1-CIDADES ATENDIDAS", "🤝 2-PARCEIROS", "📦 3-CUSTO DISTRIB", "🚛 4-CUSTO TRANSF", "💰 5-RESULTADO CLIENTE"])

# 1 - CIDADES ATENDIDAS - ARQUIVO ÚNICO
with abas[0]:
    st.subheader("1 - Cidades Atendidas - Arquivo Único")
    up = st.file_uploader("Anexar se quiser trocar (csv, xlsx)", type=["xlsx","csv","sswweb"], key="c1")

    def ler(f):
        try:
            if str(f).endswith(".csv") or "csv" in str(f).lower() or str(f).endswith(".sswweb"):
                return pd.read_csv(f, sep=None, engine='python', encoding='latin1', dtype=str)
            else:
                return pd.read_excel(f, dtype=str)
        except Exception as e:
            st.error(f"Erro: {e}")
            return pd.DataFrame()

    if up:
        st.session_state["cidades"] = ler(up)
    elif "cidades" not in st.session_state:
        # lê do GitHub
        if glob.glob("*Cidades*.csv"):
            st.session_state["cidades"] = pd.read_csv(glob.glob("*Cidades*.csv")[0], sep=None, engine='python', encoding='latin1', dtype=str)
        else:
            st.session_state["cidades"] = pd.DataFrame()

    if not st.session_state["cidades"].empty:
        df = st.session_state["cidades"]
        st.metric("Total", len(df))
        if "UF" in df.columns or "Uf" in df.columns:
            col_uf = "UF" if "UF" in df.columns else "Uf"
            uf = st.selectbox("UF", ["TODOS"] + sorted(df[col_uf].dropna().astype(str).str.strip().unique()), key="uf1")
            if uf!="TODOS":
                df = df[df[col_uf]==uf]
        st.write("Editável dentro do app:")
        st.data_editor(df, num_rows="dynamic", use_container_width=True, height=600, key="ed1")
    else:
        st.warning("Aguardando Cidades Atendidas.csv")

# 2 - PARCEIROS
with abas[1]:
    st.subheader("2 - Tabelas de Parceiros - Editável + Anexar")
    up2 = st.file_uploader("Anexar arquivo de parceiros", type=["xlsx","csv"], key="c2")
    if up2:
        st.session_state["parc"] = ler(up2)
    if "parc" not in st.session_state:
        st.session_state["parc"] = pd.DataFrame(columns=["UF","CIDADE","PARCEIRO","CUSTO"])
    st.data_editor(st.session_state["parc"], num_rows="dynamic", use_container_width=True, height=500, key="ed2")

# 3 - DISTRIB
with abas[2]:
    st.subheader("3 - Custo de Distribuição por Unidade")
    up3 = st.file_uploader("Anexar", type=["xlsx","csv"], key="c3")
    if up3: st.session_state["dist"] = ler(up3)
    if "dist" not in st.session_state: st.session_state["dist"] = pd.DataFrame(columns=["UNIDADE","CUSTO"])
    st.data_editor(st.session_state["dist"], num_rows="dynamic", use_container_width=True, height=500, key="ed3")

# 4 - TRANSF
with abas[3]:
    st.subheader("4 - Custo de Transferência")
    up4 = st.file_uploader("Anexar", type=["xlsx","csv"], key="c4")
    if up4: st.session_state["transf"] = ler(up4)
    if "transf" not in st.session_state: st.session_state["transf"] = pd.DataFrame(columns=["ORIGEM","DESTINO","CUSTO"])
    st.data_editor(st.session_state["transf"], num_rows="dynamic", use_container_width=True, height=500, key="ed4")

# 5 - RESULTADO CLIENTE
with abas[4]:
    st.subheader("5 - Resultado por Cliente")
    arqs = glob.glob("82*.xlsx") + glob.glob("83*.xlsx")
    if arqs:
        dfs = [pd.read_excel(a, dtype=str) for a in arqs]
        df = pd.concat(dfs, ignore_index=True)
        st.metric("CTes carregados", len(df))
        st.dataframe(df, use_container_width=True, height=500)
    else:
        st.info("Suba 82 e 83")
