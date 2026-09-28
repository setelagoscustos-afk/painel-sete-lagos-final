import streamlit as st
import pandas as pd
st.set_page_config(layout="wide")

arquivos = st.file_uploader("Suba as planilhas", type=["xlsx"], accept_multiple_files=True)

if arquivos:
    lista=[]
    for arq in arquivos:
        df_t = pd.read_excel(arq, sheet_name="CUSTO NOVA")
        df_t = df_t[pd.to_numeric(df_t["FRETE"], errors='coerce').notna()].copy()
        for c in ["FRETE","R$ LÍQUIDO","CUSTO GERAL","PESO","R$ MERCADORIA","TOTAL R$ TRIBUTOS"]:
            if c in df_t.columns:
                df_t[c] = pd.to_numeric(df_t[c], errors='coerce')
        df_t["RESULTADO_%"] = pd.to_numeric(df_t["RESULTADO"], errors='coerce')*100
        lista.append(df_t)
    df = pd.concat(lista, ignore_index=True)
    df["MÊS"] = pd.to_datetime(df["DATA EMISSÃO"], errors='coerce').dt.strftime("%m/%Y")
    df["UF_DEST"] = df["UF.1"].astype(str)
    df["UF_REM"] = df["UF"].astype(str)

    # ========== 1. FILTRO PRINCIPAL - CLIENTE PAGADOR ==========
    st.markdown("### 1️⃣ FILTRO PRINCIPAL")
    pagadores = sorted(df["CLIENTE PAGADOR"].dropna().unique())
    f_pagador = st.selectbox("CLIENTE PAGADOR (Principal)", pagadores, index=0)

    df_pagador = df[df["CLIENTE PAGADOR"] == f_pagador].copy()

    # Cards do pagador selecionado - igual foto
    FRETE = df_pagador["FRETE"].sum()
    LIQUIDO = df_pagador["R$ LÍQUIDO"].sum()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric(f"FRETE - {f_pagador[:15]}", f"R$ {FRETE:,.2f}")
    c2.metric("LÍQUIDO", f"R$ {LIQUIDO:,.2f}", f"{LIQUIDO/FRETE*100:.2f}%")
    c3.metric("QTD CTe", f"{len(df_pagador)}")
    c4.metric("Tonelada", f"{df_pagador['PESO'].sum():,.0f} kg")

    st.divider()

    # ========== 2. DRILL-DOWN POR REGIÃO - UF -> RECEPTORA ==========
    st.markdown("### 2️⃣ DRILL-DOWN POR REGIÃO")
    st.info(f"Cliente: **{f_pagador}** - Agora selecione a UF para ver o resultado por Unidade Receptora")

    col_uf, col_rec = st.columns([1,2])

    with col_uf:
        # Lista de UFs com resultado
        cubo_uf = df_pagador.groupby("UF_DEST").agg(
            Frete=("FRETE","sum"),
            Liquido=("R$ LÍQUIDO","sum"),
            Qtd=("FRETE","count")
        ).reset_index()
        cubo_uf["Resultado_%"] = cubo_uf["Liquido"]/cubo_uf["Frete"]*100
        cubo_uf = cubo_uf.sort_values("Resultado_%", ascending=False)

        st.markdown("**Resultado por UF Destino**")
        st.dataframe(
            cubo_uf.style.background_gradient(subset=["Resultado_%"], cmap="RdYlGn")
           .format({"Frete":"R$ {:,.2f}", "Liquido":"R$ {:,.2f}", "Resultado_%":"{:.2f}%"}),
            use_container_width=True
        )

        ufs_selecionadas = st.multiselect(
            "Selecione a UF para detalhar por Receptora:",
            sorted(cubo_uf["UF_DEST"].unique()),
            default=sorted(cubo_uf["UF_DEST"].unique())[:1]
        )

    with col_rec:
        if ufs_selecionadas:
            df_uf = df_pagador[df_pagador["UF_DEST"].isin(ufs_selecionadas)]

            cubo_rec = df_uf.groupby("RECEPTORA").agg(
                Frete=("FRETE","sum"),
                Liquido=("R$ LÍQUIDO","sum"),
                Qtd=("FRETE","count"),
                Peso=("PESO","sum")
            ).reset_index()
            cubo_rec["Resultado_%"] = cubo_rec["Liquido"]/cubo_rec["Frete"]*100
            cubo_rec["Custo_kg"] = (cubo_rec["Frete"]-cubo_rec["Liquido"])/cubo_rec["Peso"]
            cubo_rec = cubo_rec.sort_values("Resultado_%")

            st.markdown(f"**Resultado por Unidade Receptora na UF: {', '.join(ufs_selecionadas)}**")
            st.dataframe(
                cubo_rec.style.background_gradient(subset=["Resultado_%"], cmap="RdYlGn")
               .format({"Frete":"R$ {:,.2f}", "Liquido":"R$ {:,.2f}", "Resultado_%":"{:.2f}%", "Custo_kg":"R$ {:.4f}"}),
                use_container_width=True,
                height=400
            )

            # Gráfico
            st.bar_chart(cubo_rec.set_index("RECEPTORA")["Resultado_%"])
        else:
            st.warning("Selecione uma UF ao lado")

    st.divider()

    # ========== 3. TABELA QUE MOSTRA RESULTADO POR RECEPTORA QUANDO SELECIONA UF ==========
    st.markdown("### 3️⃣ TABELA DINÂMICA - UF -> RECEPTORA")

    # Tabela pivô
    pivot_uf_rec = df_pagador.pivot_table(
        index="RECEPTORA",
        columns="UF_DEST",
        values="RESULTADO_%",
        aggfunc="mean"
    ).round(2)

    st.markdown(f"**Matriz: Quando seleciono a UF, mostra o resultado por Unidade Receptora - Cliente: {f_pagador}**")
    st.dataframe(
        pivot_uf_rec.style.background_gradient(cmap="RdYlGn").format("{:.2f}%"),
        use_container_width=True
    )

    # ========== PAINEL IGUAL SUA FOTO MAS FILTRADO ==========
    st.divider()
    st.markdown(f"### Painel Dashboard Tabela - {f_pagador} | UF: {', '.join(ufs_selecionadas) if ufs_selecionadas else 'Todas'}")

    if ufs_selecionadas:
        df_final = df_pagador[df_pagador["UF_DEST"].isin(ufs_selecionadas)]
    else:
        df_final = df_pagador

    FRETE_F = df_final["FRETE"].sum()
    TRIB_F = df_final["TOTAL R$ TRIBUTOS"].sum()
    LIQUIDO_F = df_final["R$ LÍQUIDO"].sum()
    CUSTO_F = df_final["CUSTO GERAL"].sum()

    # Aqui entra o HTML da tabela igual foto que te mandei antes, mas com valores filtrados
    col_e, col_d = st.columns(2)
    with col_e:
        st.markdown(f"""
        **COMPETENCIA TOTAL GERAL - FRETE**\n
        VALOR: R$ {FRETE_F:,.2f} | Receita/kg: {FRETE_F/df_final['PESO'].sum():.4f} | ICMS 12%: R$ {FRETE_F*0.12:,.2f}
        """)
        st.metric("VALOR RECEITA LIQUIDA", f"R$ {FRETE_F-TRIB_F:,.2f}")
        st.metric("INFORMAÇÕES EXTRAS - Tonelada", f"{df_final['PESO'].sum():,.0f} kg")

    with col_d:
        st.metric("TOTAL CUSTOS", f"R$ {CUSTO_F:,.2f}")
        st.metric("VALOR LIQUIDO", f"R$ {LIQUIDO_F:,.2f}", f"{LIQUIDO_F/FRETE_F*100:.2f}%")
        st.metric("QTD CTRC", f"{len(df_final)}", f"Bases: {len(df_final[df_final['R$ REDESPACHO']==0])} | Redesp: {len(df_final[df_final['R$ REDESPACHO']>0])}")

    st.dataframe(df_final[["DATA EMISSÃO","EMISSORA","UF_REM","RECEPTORA","UF_DEST","PESO","FRETE","CUSTO GERAL","R$ LÍQUIDO","RESULTADO_%"]].sort_values("RESULTADO_%"), use_container_width=True, height=500)
