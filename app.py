import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Sete Lagos Final")
st.title("Painel Sete Lagos - 5 Painéis")

@st.cache_data
def carrega_cidades():
    try:
        return pd.read_csv("Cidades Atendidas.csv", sep=None, engine='python', encoding='latin1', dtype=str)
    except Exception as e:
        return pd.DataFrame()

abas = st.tabs(["📍 1-CIDADES", "🤝 2-PARCEIROS", "📦 3-DISTRIB", "🚛 4-TRANSF", "💰 5-RESULTADO"])

with abas[0]:
    st.subheader("1 - Cidades Atendidas - Arquivo Único")
    df = carrega_cidades()
    if df.empty:
        st.warning("Não consegui ler Cidades Atendidas.csv - verifique o arquivo")
        up = st.file_uploader("Anexe aqui", type=["csv","xlsx"], key="c1")
        if up:
            df = pd.read_csv(up, sep=None, engine='python', encoding='latin1', dtype=str)
    else:
        st.success(f"{len(df)} cidades carregadas")
        col_uf = [c for c in df.columns if "UF" in c.upper()][0] if len(df)>0 else "UF"
        if col_uf in df.columns:
            ufs = ["TODOS"] + sorted(df[col_uf].dropna().astype(str).str.strip().unique().tolist())
            sel = st.selectbox("Filtrar UF", ufs)
            if sel!= "TODOS":
                df = df[df[col_uf]==sel]
        st.data_editor(df, num_rows="dynamic", use_container_width=True, height=600, key="ed1")
        st.download_button("Baixar", df.to_csv(index=False, sep=";", encoding="latin1"), "cidades.csv")

with abas[1]:
    st.subheader("2 - Tabelas de Parceiros - Editável + Anexar arquivo do computador")
    up2 = st.file_uploader("Anexar parceiros", type=["xlsx","csv"], key="c2")
    if "parc" not in st.session_state:
        st.session_state.parc = pd.DataFrame(columns=["UF","CIDADE","PARCEIRO","CUSTO"])
    if up2:
        st.session_state.parc = pd.read_excel(up2, dtype=str) if up2.name.endswith(".xlsx") else pd.read_csv(up2, sep=None, engine='python', dtype=str)
    st.data_editor(st.session_state.parc, num_rows="dynamic", use_container_width=True, height=500, key="ed2")

with abas[2]:
    st.subheader("3 - Custo de Distribuição por Unidade - Editável")
    up3 = st.file_uploader("Anexar distribuição", type=["xlsx","csv"], key="c3")
    if "dist" not in st.session_state:
        st.session_state.dist = pd.DataFrame(columns=["UNIDADE","CUSTO"])
    if up3:
        st.session_state.dist = pd.read_excel(up3, dtype=str) if up3.name.endswith(".xlsx") else pd.read_csv(up3, sep=None, engine='python', dtype=str)
    st.data_editor(st.session_state.dist, num_rows="dynamic", use_container_width=True, height=500, key="ed3")

with abas[3]:
    st.subheader("4 - Custo de Transferência - Editável")
    up4 = st.file_uploader("Anexar transferência", type=["xlsx","csv"], key="c4")
    if "transf" not in st.session_state:
        st.session_state.transf = pd.DataFrame(columns=["ORIGEM","DESTINO","CUSTO"])
    if up4:
        st.session_state.transf = pd.read_excel(up4, dtype=str) if up4.name.endswith(".xlsx") else pd.read_csv(up4, sep=None, engine='python', dtype=str)
    st.data_editor(st.session_state.transf, num_rows="dynamic", use_container_width=True, height=500, key="ed4")

with abas[4]:
    st.subheader("5 - Resultado por Cliente - 82 e 83")
    try:
        df1 = pd.read_excel("82 - BRASCOLA.xlsx", dtype=str)
        df2 = pd.read_excel("83 - Colson.xlsx", dtype=str)
        df = pd.concat([df1, df2], ignore_index=True)
        st.metric("CTes", len(df))
        st.dataframe(df, use_container_width=True, height=500)
    except Exception as e:
        st.warning(f"Aguardando arquivos 82 e 83: {e}")
