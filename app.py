import streamlit as st
import pandas as pd
import pdfplumber

st.set_page_config(layout="wide", page_title="Sete Lagos Final")
st.title("Painel Sete Lagos - 5 Painéis")

@st.cache_data
def carrega_cidades():
    try:
        return pd.read_csv("Cidades Atendidas.csv", sep=None, engine='python', encoding='latin1', dtype=str)
    except:
        return pd.DataFrame()

def ler_excel_csv(up):
    try:
        if up.name.lower().endswith((".xlsx",".xls")):
            return pd.read_excel(up, dtype=str)
        else:
            return pd.read_csv(up, sep=None, engine='python', encoding='latin1', dtype=str)
    except Exception as e:
        st.error(f"Erro ao ler {up.name}: {e}")
        return pd.DataFrame()

abas = st.tabs(["📍 1-CIDADES", "🤝 2-PARCEIROS", "📦 3-DISTRIB", "🚛 4-TRANSF", "💰 5-RESULTADO"])

with abas[0]:
    df = carrega_cidades()
    if not df.empty:
        st.success(f"{len(df)} cidades carregadas")
        st.dataframe(df, use_container_width=True, height=600)
    else:
        st.warning("Sem Cidades Atendidas.csv")

with abas[1]:
    st.subheader("2 - Tabelas de Parceiros - Aceita Excel, CSV, PDF e Imagem")
    up2 = st.file_uploader("Anexar parceiros (xlsx, csv, pdf, png, jpg)", type=["xlsx","csv","pdf","png","jpg","jpeg"], key="c2")

    if "parc" not in st.session_state:
        st.session_state.parc = pd.DataFrame(columns=["UF","CIDADE","PARCEIRO","CUSTO"])

    if up2:
        if up2.name.lower().endswith(".pdf"):
            st.info(f"PDF carregado: {up2.name} - {up2.size/1000:.1f} KB")
            try:
                with pdfplumber.open(up2) as pdf:
                    texto = pdf.pages[0].extract_text() if pdf.pages else ""
                    st.text_area("Texto do PDF (copie se precisar)", texto, height=200)
                    # tenta tabela mas sem quebrar
                    for page in pdf.pages[:2]:
                        tabela = page.extract_table()
                        if tabela:
                            st.write("Tabela encontrada no PDF:")
                            st.dataframe(pd.DataFrame(tabela))
            except Exception as e:
                st.error(f"Não consegui extrair tabela: {e}. Use a tabela editável abaixo.")
        elif up2.name.lower().endswith((".png",".jpg",".jpeg")):
            st.image(up2, caption=up2.name, use_container_width=True)
        else:
            st.session_state.parc = ler_excel_csv(up2)

    # ESSE ERA O ERRO - agora com try
    try:
        st.session_state.parc = st.data_editor(st.session_state.parc, num_rows="dynamic", use_container_width=True, height=500, key="ed2")
    except Exception as e:
        st.warning("Tabela vazia, resetando...")
        st.session_state.parc = pd.DataFrame(columns=["UF","CIDADE","PARCEIRO","CUSTO"])
        st.data_editor(st.session_state.parc, num_rows="dynamic", use_container_width=True, height=500, key="ed2b")

with abas[2]:
    st.subheader("3 - Custo de Distribuição")
    up3 = st.file_uploader("Anexar", type=["xlsx","csv","pdf","png","jpg","jpeg"], key="c3")
    if "dist" not in st.session_state: st.session_state.dist = pd.DataFrame(columns=["UNIDADE","CUSTO"])
    if up3 and up3.name.lower().endswith((".xlsx",".xls",".csv")):
        st.session_state.dist = ler_excel_csv(up3)
    if up3 and up3.name.lower().endswith(".pdf"): st.info("PDF anexado - digite manual abaixo")
    if up3 and up3.name.lower().endswith((".png",".jpg",".jpeg")): st.image(up3, use_container_width=True)
    st.data_editor(st.session_state.dist, num_rows="dynamic", use_container_width=True, key="ed3")

with abas[3]:
    st.subheader("4 - Custo de Transferência")
    up4 = st.file_uploader("Anexar", type=["xlsx","csv","pdf","png","jpg","jpeg"], key="c4")
    if "transf" not in st.session_state: st.session_state.transf = pd.DataFrame(columns=["ORIGEM","DESTINO","CUSTO"])
    if up4 and up4.name.lower().endswith((".xlsx",".xls",".csv")):
        st.session_state.transf = ler_excel_csv(up4)
    if up4 and up4.name.lower().endswith((".png",".jpg",".jpeg")): st.image(up4, use_container_width=True)
    st.data_editor(st.session_state.transf, num_rows="dynamic", use_container_width=True, key="ed4")

with abas[4]:
    st.subheader("5 - Resultado por Cliente")
    try:
        df1 = pd.read_excel("82 - BRASCOLA.xlsx", dtype=str)
        df2 = pd.read_excel("83 - Colson.xlsx", dtype=str)
        df = pd.concat([df1, df2], ignore_index=True)
        st.metric("CTes", len(df))
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.warning(f"Aguardando 82 e 83: {e}")
