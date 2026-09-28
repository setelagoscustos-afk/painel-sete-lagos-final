import streamlit as st
import pandas as pd
import pdfplumber

st.set_page_config(layout="wide", page_title="Sete Lagos Final")
st.title("Painel Sete Lagos - 5 Painéis")

@st.cache_data
def carrega_cidades():
    return pd.read_csv("Cidades Atendidas.csv", sep=None, engine='python', encoding='latin1', dtype=str)

def ler_arquivo_generico(up):
    """Lê xlsx, csv, pdf e imagem"""
    nome = up.name.lower()
    if nome.endswith(".xlsx") or nome.endswith(".xls"):
        return pd.read_excel(up, dtype=str)
    elif nome.endswith(".csv"):
        try:
            return pd.read_csv(up, sep=None, engine='python', encoding='latin1', dtype=str)
        except:
            return pd.read_csv(up, sep=";", encoding='latin1', dtype=str)
    elif nome.endswith(".pdf"):
        # tenta extrair tabelas do PDF
        try:
            with pdfplumber.open(up) as pdf:
                tabelas = []
                for page in pdf.pages:
                    t = page.extract_table()
                    if t:
                        tabelas.extend(t)
                if tabelas:
                    return pd.DataFrame(tabelas[1:], columns=tabelas[0])
                else:
                    st.warning("PDF sem tabela detectável. Mostrando texto.")
                    texto = "\n".join([p.extract_text() or "" for p in pdf.pages])
                    return pd.DataFrame({"TEXTO_PDF":[texto]})
        except Exception as e:
            st.error(f"Erro ao ler PDF: {e}")
            return pd.DataFrame()
    elif nome.endswith((".png",".jpg",".jpeg")):
        st.image(up, caption=f"Imagem: {up.name}", use_container_width=True)
        # cria DF vazio para digitar manual a partir da imagem
        st.info("Imagem carregada. Digite os dados abaixo baseado na imagem.")
        return pd.DataFrame(columns=["DADOS_DA_IMAGEM"])

abas = st.tabs(["📍 1-CIDADES", "🤝 2-PARCEIROS", "📦 3-DISTRIB", "🚛 4-TRANSF", "💰 5-RESULTADO"])

with abas[0]:
    df = carrega_cidades()
    st.success(f"{len(df)} cidades carregadas")
    st.data_editor(df, num_rows="dynamic", use_container_width=True, height=600, key="ed1")

with abas[1]:
    st.subheader("2 - Tabelas de Parceiros - Aceita Excel, CSV, PDF e Imagem")
    up2 = st.file_uploader("Anexar parceiros (xlsx, csv, pdf, png, jpg)", type=["xlsx","csv","pdf","png","jpg","jpeg"], key="c2")
    if "parc" not in st.session_state:
        st.session_state.parc = pd.DataFrame(columns=["UF","CIDADE","PARCEIRO","CUSTO"])
    if up2:
        df_up = ler_arquivo_generico(up2)
        if not df_up.empty and "DADOS_DA_IMAGEM" not in df_up.columns and "TEXTO_PDF" not in df_up.columns:
            st.session_state.parc = df_up
        elif "TEXTO_PDF" in df_up.columns:
            st.dataframe(df_up)
    st.write("Editável:")
    st.data_editor(st.session_state.parc, num_rows="dynamic", use_container_width=True, height=500, key="ed2")

with abas[2]:
    st.subheader("3 - Custo de Distribuição - Aceita Excel, CSV, PDF e Imagem")
    up3 = st.file_uploader("Anexar distribuição", type=["xlsx","csv","pdf","png","jpg","jpeg"], key="c3")
    if "dist" not in st.session_state:
        st.session_state.dist = pd.DataFrame(columns=["UNIDADE","CUSTO"])
    if up3:
        df_up = ler_arquivo_generico(up3)
        if not df_up.empty and "DADOS_DA_IMAGEM" not in df_up.columns:
            st.session_state.dist = df_up
    st.data_editor(st.session_state.dist, num_rows="dynamic", use_container_width=True, height=500, key="ed3")

with abas[3]:
    st.subheader("4 - Custo de Transferência - Aceita Excel, CSV, PDF e Imagem")
    up4 = st.file_uploader("Anexar transferência", type=["xlsx","csv","pdf","png","jpg","jpeg"], key="c4")
    if "transf" not in st.session_state:
        st.session_state.transf = pd.DataFrame(columns=["ORIGEM","DESTINO","CUSTO"])
    if up4:
        df_up = ler_arquivo_generico(up4)
        if not df_up.empty and "DADOS_DA_IMAGEM" not in df_up.columns:
            st.session_state.transf = df_up
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
        st.warning(f"Aguardando 82 e 83: {e}")
