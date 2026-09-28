import streamlit as st
import pandas as pd
import glob

st.set_page_config(layout="wide")
st.title("Painel Sete Lagos - Tabela de Fretes")
st.caption("Filtro: Pagador > UF Destino > Receptora")

# Lê todos xlsx que NÃO são modeloSLG
arquivos = [f for f in glob.glob("*.xlsx") + glob.glob("*.xls") + glob.glob("**/*.xlsx", recursive=True) if "modeloSLG" not in f and "GRF" not in f and "TRU" not in f]
st.write(f"Arquivos de frete encontrados: {arquivos}")

if not arquivos:
    st.error("Não achei 82 e 83")
    st.stop()

lista=[]
for arq in arquivos:
    try:
        t = pd.read_excel(arq, dtype=str)
        # mostra colunas pra debug
        st.write(f"{arq} -> colunas: {list(t.columns)[:10]}")
        lista.append(t)
    except Exception as e:
        st.error(f"Erro {arq}: {e}")

dados = pd.concat(lista, ignore_index=True)
dados.columns = [c.strip().upper() for c in dados.columns]

# acha coluna pagador
col_pag = None
for c in dados.columns:
    if "PAGADOR" in c or "CLIENTE" in c:
        col_pag = c
        break

if not col_pag:
    st.error(f"Não achei PAGADOR. Colunas: {list(dados.columns)}")
    st.stop()

dados.rename(columns={col_pag:"CLIENTE PAGADOR"}, inplace=True)

# converte valores
for c in ["FRETE","R$ LÍQUIDO","R$ LIQUIDO","CUSTO GERAL","PESO","VALOR"]:
    if c in dados.columns:
        dados[c] = dados[c].astype(str).str.replace("R$","", regex=False).str.replace(".","", regex=False).str.replace(",",".", regex=False).str.replace("-","0")
        dados[c] = pd.to_numeric(dados[c], errors='coerce').fillna(0)

dados["UF_DESTINO"] = dados.get("UF.1", dados.get("UF_DEST", dados.get("UF",""))).astype(str)
if "RECEPTORA" not in dados.columns and "TRANSPORTADORA" in dados.columns:
    dados["RECEPTORA"] = dados["TRANSPORTADORA"]

# FILTROS EM PORTUGUÊS
cliente = st.selectbox("1️⃣ Cliente Pagador (Principal)", sorted(dados["CLIENTE PAGADOR"].dropna().astype(str).unique()))
df_f = dados[dados["CLIENTE PAGADOR"]==cliente].copy()

col1, col2 = st.columns(2)
with col1:
    ufs = sorted([u for u in df_f["UF_DESTINO"].dropna().unique() if str(u)!='nan' and str(u)!=''])
    uf_sel = st.multiselect("2️⃣ UF de Destino", ufs)
with col2:
    if "RECEPTORA" in df_f.columns:
        recs = sorted(df_f["RECEPTORA"].dropna().unique())
        rec_sel = st.multiselect("3️⃣ Transportadora Receptora (filtra só da UF)", recs)

if uf_sel: df_f = df_f[df_f["UF_DESTINO"].isin(uf_sel)]
if 'rec_sel' in locals() and rec_sel: df_f = df_f[df_f["RECEPTORA"].isin(rec_sel)]

st.divider()
c1,c2,c3,c4 = st.columns(4)
frete = df_f["FRETE"].sum() if "FRETE" in df_f else 0
liq_col = "R$ LÍQUIDO" if "R$ LÍQUIDO" in df_f.columns else "R$ LIQUIDO" if "R$ LIQUIDO" in df_f.columns else None
liq = df_f[liq_col].sum() if liq_col else 0

c1.metric("FRETE TOTAL", f"R$ {frete:,.2f}")
c2.metric("LÍQUIDO", f"R$ {liq:,.2f}")
c3.metric("%", f"{liq/frete*100:.2f}%" if frete else "0%")
c4.metric("QTD CTe", len(df_f))

if "RECEPTORA" in df_f.columns and not df_f.empty and liq_col:
    ranking = df_f.groupby("RECEPTORA").agg(Frete=("FRETE","sum"), Liquido=(liq_col,"sum"), Qtd=("FRETE","count")).reset_index()
    ranking["%"] = ranking["Liquido"]/ranking["Frete"]*100
    ranking = ranking.sort_values("%")
    st.subheader(f"Ranking por Receptora - {cliente} (só UF selecionada)")
    st.dataframe(ranking, width='stretch')
    st.bar_chart(ranking.set_index("RECEPTORA")["%"])

st.subheader("Detalhamento")
st.dataframe(df_f, width='stretch', height=500)
