import streamlit as st
import pandas as pd
import glob, os

st.set_page_config(layout="wide")
st.title("Painel Sete Lagos - Tabela de Fretes")
st.caption("Filtro: Pagador > UF Destino > Receptora (mostra só receptoras da UF)")

# DEBUG: mostra onde estão os arquivos
st.write("Procurando arquivos...")
todos_arqs = glob.glob("**/*.*", recursive=True)
csvs = [f for f in todos_arqs if f.lower().endswith(".csv")]
st.write(f"Achei {len(csvs)} CSVs:", csvs[:20])

arquivos = glob.glob("ssw0137*.csv") + glob.glob("**/ssw0137*.csv", recursive=True)
# tenta também sem filtro se não achar
if not arquivos:
    arquivos = csvs

if not arquivos:
    st.error("Não encontrou nenhum CSV. Verifica se os arquivos estão na pasta principal do GitHub.")
    st.stop()

lista=[]
for arq in arquivos:
    try:
        # tenta dois separadores
        try:
            t = pd.read_csv(arq, sep=";", encoding="latin1", dtype=str, low_memory=False)
        except:
            t = pd.read_csv(arq, sep=",", encoding="latin1", dtype=str, low_memory=False)
        if "CLIENTE PAGADOR" in t.columns or "PAGADOR" in str(t.columns).upper():
            lista.append(t)
    except Exception as e:
        st.warning(f"Erro ao ler {arq}: {e}")

if not lista:
    st.error("Li os CSVs mas nenhum tem a coluna CLIENTE PAGADOR. Mostrando colunas do primeiro:")
    try:
        t0 = pd.read_csv(arquivos[0], sep=";", encoding="latin1", nrows=2)
        st.write(list(t0.columns))
    except:
        pass
    st.stop()

dados = pd.concat(lista, ignore_index=True)

for c in ["FRETE","R$ LÍQUIDO","CUSTO GERAL","PESO"]:
    if c in dados.columns:
        dados[c] = dados[c].astype(str).str.replace(".","", regex=False).str.replace(",",".", regex=False).str.replace("R$","", regex=False)
        dados[c] = pd.to_numeric(dados[c], errors='coerce')

dados["UF_DESTINO"] = dados.get("UF.1", dados.get("UF_DEST",""))

cliente = st.selectbox("1️⃣ Cliente Pagador (Principal)", sorted(dados["CLIENTE PAGADOR"].dropna().astype(str).unique()))
df_f = dados[dados["CLIENTE PAGADOR"]==cliente].copy()

uf_sel = st.multiselect("2️⃣ UF de Destino", sorted(df_f["UF_DESTINO"].dropna().astype(str).unique()))
if uf_sel: df_f = df_f[df_f["UF_DESTINO"].isin(uf_sel)]

if "RECEPTORA" in df_f.columns:
    rec_sel = st.multiselect("3️⃣ Transportadora Receptora (só da UF selecionada)", sorted(df_f["RECEPTORA"].dropna().astype(str).unique()))
    if rec_sel: df_f = df_f[df_f["RECEPTORA"].isin(rec_sel)]

c1,c2,c3,c4 = st.columns(4)
frete = df_f["FRETE"].sum() if "FRETE" in df_f else 0
liq = df_f["R$ LÍQUIDO"].sum() if "R$ LÍQUIDO" in df_f else 0
c1.metric("FRETE", f"R$ {frete:,.2f}")
c2.metric("LÍQUIDO", f"R$ {liq:,.2f}")
c3.metric("%", f"{liq/frete*100:.1f}%" if frete else "0%")
c4.metric("QTD", len(df_f))

if "RECEPTORA" in df_f.columns and not df_f.empty:
    ranking = df_f.groupby("RECEPTORA").agg(Frete=("FRETE","sum"), Liquido=("R$ LÍQUIDO","sum"), Qtd=("FRETE","count")).reset_index()
    ranking["%"] = ranking["Liquido"]/ranking["Frete"]*100
    st.dataframe(ranking.sort_values("%"), use_container_width=True)
    st.bar_chart(ranking.set_index("RECEPTORA")["%"])

st.dataframe(df_f, use_container_width=True)
