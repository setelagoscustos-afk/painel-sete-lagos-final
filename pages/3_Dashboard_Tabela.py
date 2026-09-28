import streamlit as st
import pandas as pd
import glob

st.set_page_config(layout="wide", page_title="Painel Sete Lagos")
st.title("Painel Sete Lagos - Tabela de Fretes")
st.caption("Filtro: Pagador > UF Destino > Receptora (mostra só receptoras da UF)")

arquivos = glob.glob("ssw0137*.csv")
if not arquivos:
    st.error("Não achei os CSVs na raiz")
    st.stop()

lista=[]
for arq in arquivos:
    try:
        t = pd.read_csv(arq, sep=";", encoding="latin1", dtype=str, low_memory=False)
        if "CLIENTE PAGADOR" in t.columns:
            lista.append(t)
    except:
        pass

dados = pd.concat(lista, ignore_index=True)

for c in ["FRETE","R$ LÍQUIDO","CUSTO GERAL","PESO"]:
    if c in dados.columns:
        dados[c] = dados[c].str.replace(".","", regex=False).str.replace(",",".", regex=False).str.replace("R$","", regex=False)
        dados[c] = pd.to_numeric(dados[c], errors='coerce')

dados["UF_DESTINO"] = dados.get("UF.1","").astype(str)
dados["MES"] = pd.to_datetime(dados.get("DATA EMISSÃO",""), errors='coerce').dt.strftime("%m/%y")

# FILTROS EM PORTUGUÊS
cliente = st.selectbox("1️⃣ Cliente Pagador (Principal)", sorted(dados["CLIENTE PAGADOR"].dropna().unique()))
df_f = dados[dados["CLIENTE PAGADOR"]==cliente].copy()

col1, col2 = st.columns(2)
with col1:
    ufs = sorted(df_f["UF_DESTINO"].dropna().unique())
    uf_sel = st.multiselect("2️⃣ UF de Destino", ufs)
with col2:
    recs = sorted(df_f["RECEPTORA"].dropna().unique()) if "RECEPTORA" in df_f.columns else []
    rec_sel = st.multiselect("3️⃣ Transportadora Receptora", recs)

if uf_sel: df_f = df_f[df_f["UF_DESTINO"].isin(uf_sel)]
if rec_sel: df_f = df_f[df_f["RECEPTORA"].isin(rec_sel)]

# CARDS IGUAL SUA FOTO
st.divider()
frete = df_f["FRETE"].sum()
liquido = df_f["R$ LÍQUIDO"].sum() if "R$ LÍQUIDO" in df_f else 0
perc = liquido/frete*100 if frete>0 else 0

c1,c2,c3,c4 = st.columns(4)
c1.metric("FRETE", f"R$ {frete:,.2f}")
c2.metric("LÍQUIDO", f"R$ {liquido:,.2f}")
c3.metric("%", f"{perc:.2f}%")
c4.metric("QTD CTe", len(df_f))

if "RECEPTORA" in df_f.columns:
    ranking = df_f.groupby("RECEPTORA").agg(Frete=("FRETE","sum"), Liquido=("R$ LÍQUIDO","sum"), Qtd=("FRETE","count")).reset_index()
    ranking["%"] = ranking["Liquido"]/ranking["Frete"]*100
    ranking = ranking.sort_values("%")
    st.subheader("Ranking por Receptora (só da UF filtrada)")
    st.dataframe(ranking, use_container_width=True)
    st.bar_chart(ranking.set_index("RECEPTORA")["%"])

st.subheader("Detalhamento")
st.dataframe(df_f, use_container_width=True, height=500)
