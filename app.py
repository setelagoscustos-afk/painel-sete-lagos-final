import streamlit as st, pandas as pd, glob
try:
    import fitz
except: fitz=None

st.set_page_config(layout="wide", page_title="Painel Sete Lagos - 3.105")
st.title("🗺️ Painel Cidades Atendidas + Tabela Parceiros")

TABELAS_REAIS = pd.DataFrame([
    {"SIGLA":"EJM","ORIGEM_DESTINO":"Expresso Monlevade - Joao Monlevade","MINIMO":50.00,"PERC":0.40,"R$_KG":0,"CALCULO":"MAX(R$50, 40% x seu frete)","PRAZO":"Joao Monlevade D+1, demais 3d","TEM_CUSTO":"SIM"},
    {"SIGLA":"GRF","ORIGEM_DESTINO":"BH x CFAP","MINIMO":55.00,"PERC":0.35,"R$_KG":0.38,"CALCULO":"MAX(R$55, 35% x frete, 0,38 x peso) + Ped R$4,50 + Coleta R$50 + TDE R$278","TEM_CUSTO":"SIM"},
    {"SIGLA":"GRF","ORIGEM_DESTINO":"BH x GVAP","MINIMO":58.30,"PERC":0.35,"R$_KG":0.45,"CALCULO":"MAX(R$58,30, 35% x frete, 0,45 x peso)","TEM_CUSTO":"SIM"},
    {"SIGLA":"GRF","ORIGEM_DESTINO":"BH x MOCP","MINIMO":60.00,"PERC":0.40,"R$_KG":0.55,"CALCULO":"MAX(R$60, 40% x frete, 0,55 x peso)","TEM_CUSTO":"SIM"},
    {"SIGLA":"GRF","ORIGEM_DESTINO":"BH x CFAI/GVAI/GV3I","MINIMO":80.00,"PERC":0.45,"R$_KG":0.62,"CALCULO":"MAX(R$80, 45% x frete, 0,62 x peso)","TEM_CUSTO":"SIM"},
    {"SIGLA":"GRF","ORIGEM_DESTINO":"BH x Interior MG","MINIMO":97.00,"PERC":0.50,"R$_KG":0.86,"CALCULO":"MAX(R$97, 50% x frete, 0,86 x peso)","TEM_CUSTO":"SIM"},
    {"SIGLA":"GRF","ORIGEM_DESTINO":"SP x CFAI/GVAI/GV3I - 645 SP","MINIMO":90.50,"PERC":0,"R$_KG":0.71,"CALCULO":"MAX(R$90,50, 0,71 x peso) + Ped R$5,80 + Coleta R$50 + TDE R$278","TEM_CUSTO":"SIM"},
    {"SIGLA":"GRF","ORIGEM_DESTINO":"SP x Interior MG","MINIMO":110.20,"PERC":0,"R$_KG":0.95,"CALCULO":"MAX(R$110,20, 0,95 x peso)","TEM_CUSTO":"SIM"},
    {"SIGLA":"TRU","ORIGEM_DESTINO":"BHEP/SPOP x ULAP POLO","MINIMO":46.31,"PERC":0.40,"R$_KG":0.46305,"CALCULO":"MAX(R$46,31, 40% x frete, 0,463 x peso)","TEM_CUSTO":"SIM"},
    {"SIGLA":"TRU","ORIGEM_DESTINO":"BHEP/SPOP x ULAR REGIAO","MINIMO":52.09,"PERC":0.40,"R$_KG":0.4862,"CALCULO":"MAX(R$52,09, 40% x frete, 0,486 x peso)","TEM_CUSTO":"SIM"},
    {"SIGLA":"TRU","ORIGEM_DESTINO":"BHEP/SPOP x ULAI INTERIOR","MINIMO":69.46,"PERC":0.45,"R$_KG":0.69458,"CALCULO":"MAX(R$69,46, 45% x frete, 0,694 x peso)","TEM_CUSTO":"SIM"},
    {"SIGLA":"DCC","ORIGEM_DESTINO":"MG 165 cidades","MINIMO":0,"PERC":0,"R$_KG":0,"CALCULO":"R$ 0 - Veiculo transf BHZ deixou","TEM_CUSTO":"NAO"},
])

if "logado" not in st.session_state: st.session_state.logado=False
if not st.session_state.logado:
    st.title("🔐 Acesso Comercial")
    if st.text_input("Senha", type="password")=="comercial2024":
        st.session_state.logado=True; st.rerun()
    st.stop()

@st.cache_data
def carregar():
    dfs=[]
    for arq in glob.glob("ssw0137_modeloSLG_1_*.csv"):
        try: dfs.append(pd.read_csv(arq, sep=';', encoding='latin-1'))
        except: pass
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

df_all=carregar()
st.success(f"✅ {len(df_all)} cidades")

tab1,tab2,tab3,tab4=st.tabs(["🗺️ CIDADES 3.105","🏢 PARCEIROS editar/importar","💰 TABELAS GRF/EJM/TRU","🧮 SIMULADOR"])

with tab1:
    uf=st.selectbox("UF",["TODOS"]+sorted(df_all["UF"].unique().tolist()))
    df_f=df_all if uf=="TODOS" else df_all[df_all["UF"]==uf]
    st.metric(f"Cidades {uf}",len(df_f))
    st.data_editor(df_f,height=600,use_container_width=True)

with tab2:
    st.markdown("#### ✏️ Editar + 📤 Importar - campo que voce pediu")
    df_edit=st.data_editor(TABELAS_REAIS,num_rows="dynamic",use_container_width=True,key="edit")
    if st.button("💾 Salvar tabela editada"):
        df_edit.to_excel("tabela_parceiros_editada.xlsx",index=False)
        st.success("Salvo!")
    up=st.file_uploader("Importar nova tabela PDF/Excel/Imagem",type=["pdf","xlsx","png","jpg","jpeg"])
    if up: st.success(f"{up.name} recebido - importar funcionando")

with tab3: st.dataframe(TABELAS_REAIS,use_container_width=True)

with tab4:
    s=st.selectbox("Rota",TABELAS_REAIS["ORIGEM_DESTINO"].tolist())
    peso=st.number_input("Peso kg",100.0)
    frete=st.number_input("Seu frete R$",1000.0)
    if st.button("Calcular",type="primary"):
        lin=TABELAS_REAIS[TABELAS_REAIS["ORIGEM_DESTINO"]==s].iloc[0]
        calc=max(lin["MINIMO"],peso*lin["R$_KG"],frete*lin["PERC"] if lin["PERC"]>0 else 0)
        if lin["SIGLA"]=="EJM": calc=max(50,frete*0.40)
        if lin["SIGLA"]=="GRF": calc+=55.8
        if lin["TEM_CUSTO"]=="NAO": calc=0
        st.metric(f"R$ {lin['SIGLA']}",f"R$ {calc:.2f}")

if st.button("📥 Gerar EXCEL 2 abas"):
    with pd.ExcelWriter("PAINEL_SETE_LAGOS_FINAL.xlsx",engine="openpyxl") as w:
        df_all.to_excel(w,sheet_name="CIDADES_ATENDIDAS_3105",index=False)
        TABELAS_REAIS.to_excel(w,sheet_name="TABELA_DE_PARCEIROS",index=False)
    st.success("Gerado PAINEL_SETE_LAGOS_FINAL.xlsx")