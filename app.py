import streamlit as st
import pandas as pd
import plotly.express as px

# Configurazione della pagina
st.set_page_config(page_title="Retail Pipeline Dashboard", layout="wide", page_icon="📊")

st.title("📊 Commercial Performance & Pipeline WebApp")
st.markdown("Analisi dell'andamento dei KPI di Acquiring (Fisico ed E-commerce) per il Team Retail.")

# -----------------------------------------------------------------------------
# SIMULAZIONE STRUTTURATA DEI DATI (Basata sui tuoi file)
# In produzione: df_pipeline = pd.read_csv("Pipeline Retail Master 2026_24062026.xlsx - PIPELINE.csv")
# -----------------------------------------------------------------------------

@st.cache_data
def load_data():
    # Dati estratti fedelmente dalla tua pipeline commerciale
    pipeline_data = [
        {"PRIORITA'": 1, "Merchant": "PRENATAL", "Account": "Tomarchio", "Nome Deal": "Repricing ISP", "STATUS": "WIP", "RICAVI": 215000, "KPI": "VOLUMI", "valore KPI": 43000000, "Categoria": "REPRICING", "Attivita": "Puericultura"},
        {"PRIORITA'": 1, "Merchant": "PRENATAL", "Account": "Tomarchio", "Nome Deal": "DCC", "STATUS": "WIP", "RICAVI": 34400, "KPI": "VOLUMI", "valore KPI": 43000000, "Categoria": "REPRICING", "Attivita": "Puericultura"},
        {"PRIORITA'": 2, "Merchant": "D.M.O. S.P.A", "Account": "Tomarchio", "Nome Deal": "CNP Beauty Star", "STATUS": "WIP", "RICAVI": 600, "KPI": "VOLUMI", "valore KPI": 1000000, "Categoria": "CAMPAGNA ECOMMERCE", "Attivita": "Pet shop"},
        {"PRIORITA'": 1, "Merchant": "ACQUA & SAPONE", "Account": "Tomarchio", "Nome Deal": "Svecchiamento POS '26 MPS", "STATUS": "WIP", "RICAVI": 0, "KPI": "RICAVI", "valore KPI": 0, "Categoria": "RINNOVO POS", "Attivita": "Health & Beauty"},
        {"PRIORITA'": 3, "Merchant": "1000FARMACIE", "Account": "Mariani", "Nome Deal": "CNP + wallet", "STATUS": "WIP", "RICAVI": 15000, "KPI": "VOLUMI", "valore KPI": 5000000, "Categoria": "VOLUMI NO CAMPAGNA", "Attivita": "Pharmacy"},
        {"PRIORITA'": 1, "Merchant": "CISALFA", "Account": "Mariani", "Nome Deal": "Ecom Integration", "STATUS": "WIN", "RICAVI": 45000, "KPI": "VOLUMI", "valore KPI": 12000000, "Categoria": "CAMPAGNA ECOMMERCE", "Attivita": "Sport"},
        {"PRIORITA'": 1, "Merchant": "DECATHLON ITALIA", "Account": "Dalla Torre", "Nome Deal": "SoftPOS rollout", "STATUS": "WIN", "RICAVI": 80000, "KPI": "RICAVI", "valore KPI": 80000, "Categoria": "SOFTPOS", "Attivita": "Sport"},
        {"PRIORITA'": 2, "Merchant": "GRUPPO INDITEX - ZARA", "Account": "Tomarchio", "Nome Deal": "Gateway Ecom", "STATUS": "WIN", "RICAVI": 120000, "KPI": "VOLUMI", "valore KPI": 35000000, "Categoria": "CAMPAGNA ECOMMERCE", "Attivita": "Apparel"},
        {"PRIORITA'": 1, "Merchant": "EATALY", "Account": "Dalla Torre", "Nome Deal": "Softpos 8k", "STATUS": "WIN", "RICAVI": 8000, "KPI": "RICAVI", "valore KPI": 8000, "Categoria": "SOFTPOS", "Attivita": "Food"},
    ]
    
    # Dati di performance di sintesi (DB IR / CB + DBS IR)
    team_summary = [
        {"Account": "Dalla Torre", "Budget_2026_K": 390.0, "YTD_K": 464.0, "Gap_K": 74.0},
        {"Account": "Mariani", "Budget_2026_K": 160.0, "YTD_K": 63.2, "Gap_K": -96.8},
        {"Account": "Tomarchio", "Budget_2026_K": 150.0, "YTD_K": 19.3, "Gap_K": -130.6},
        {"Account": "Luzzio", "Budget_2026_K": 750.0, "YTD_K": 750.0, "Gap_K": 0.0}
    ]
    
    return pd.DataFrame(pipeline_data), pd.DataFrame(team_summary)

df_pipeline, df_team = load_data()

# -----------------------------------------------------------------------------
# NAVIGAZIONE INTERFACCIA (Tabs)
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["👤 La Mia Dashboard (Tomarchio)", "👥 Team & Confronto", "🏬 Industry Retail Focus"])

# =============================================================================
# TAB 1: FOCUS TOMARCHIO
# =============================================================================
with tab1:
    st.header("Andamento Personale: Account Tomarchio")
    
    # Filtriamo i dati solo per te
    df_tomarchio = df_pipeline[df_pipeline["Account"] == "Tomarchio"]
    df_team_t = df_team[df_team["Account"] == "Tomarchio"].iloc[0]
    
    # KPIs in evidenza
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Budget 2026 Obiettivo", value=f"€{df_team_t['Budget_2026_K']:.1f} K")
    with col2:
        st.metric(label="Chiuso YTD (WIN)", value=f"€{df_team_t['YTD_K']:.1f} K")
    with col3:
        # Calcolo pipeline pesata o valore totale WIP
        wip_totale = df_tomarchio[df_tomarchio["STATUS"] == "WIP"]["RICAVI"].sum()
        st.metric(label="Valore Pipeline Attiva (WIP)", value=f"€{wip_totale/1000:.1f} K")
    with col4:
        gap_colore = "normal" if df_team_t['Gap_K'] >= 0 else "inverse"
        st.metric(label="Distanza Target (Gap)", value=f"€{df_team_t['Gap_K']:.1f} K")

    st.subheader("I Tuoi Deal in Gestione (Filtro Rapido per Stato)")
    stato_filtro = st.radio("Mostra Deal:", ["Tutti", "WIP", "WIN"], horizontal=True)
    
    df_display = df_tomarchio if stato_filtro == "Tutti" else df_tomarchio[df_tomarchio["STATUS"] == stato_filtro]
    
    st.dataframe(df_display[["PRIORITA'", "Merchant", "Nome Deal", "STATUS", "RICAVI", "Categoria", "Attivita"]], use_container_width=True)

    # Grafico personale Categorie di Deal
    st.subheader("Distribuzione dei tuoi Ricavi Potenziali per Categoria")
    fig_tom = px.bar(df_tomarchio, x="Categoria", y="RICAVI", color="STATUS", 
                     title="Ricavi per Tipo di Soluzione (Fisico vs E-commerce)",
                     labels={"RICAVI": "Ricavi (€)"}, barmode="group", color_discrete_sequence=["#1f77b4", "#ff7f0e"])
    st.plotly_chart(fig_tom, use_container_width=True)

# =============================================================================
# TAB 2: CONFRONTO TEAM
# =============================================================================
with tab2:
    st.header("Confronto Performance Commerciale del Team")
    st.markdown("Analisi comparativa del target rispetto ai risultati YTD dei vari Account Manager.")
    
    # Grafico a barre confronto Budget vs YTD
    df_melted = df_team.melt(id_vars=["Account"], value_vars=["Budget_2026_K", "YTD_K"], 
                             var_name="Metrica", value_name="Valore_K€")
    
    fig_team = px.bar(df_melted, x="Account", y="Valore_K€", color="Metrica", barmode="group",
                      title="Performance YTD rispetto al Budget Assegnato (K€)",
                      color_discrete_map={"Budget_2026_K": "#7f7f7f", "YTD_K": "#2ca02c"})
    st.plotly_chart(fig_team, use_container_width=True)
    
    # Tabella riassuntiva del team
    st.subheader("Classifica e Avanzamento Performance")
    st.dataframe(df_team.style.background_gradient(subset=["Gap_K"], cmap="RdYlGn"), use_container_width=True)

# =============================================================================
# TAB 3: FOCUS INDUSTRY RETAIL
# =============================================================================
with tab3:
    st.header("Analisi Generale Sull'Industry Retail")
    
    # Filtri dinamici sull'intera pipeline dell'Industry
    st.sidebar.header("Filtri Globali App")
    merchant_filter = st.sidebar.multiselect("Filtra per Categoria Merceologica:", options=df_pipeline["Attivita"].unique(), default=df_pipeline["Attivita"].unique())
    
    df_filtered_industry = df_pipeline[df_pipeline["Attivita"].isin(merchant_filter)]
    
    col1_ind, col2_ind = st.columns(2)
    
    with col1_ind:
        st.subheader("Opportunità per Volume Mercato (KPI Volumi)")
        fig_pie = px.pie(df_filtered_industry, values="valore KPI", names="Merchant", 
                         title="Quota dei Volumi di Transato Stimati per Merchant")
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col2_ind:
        st.subheader("Andamento Deal del Mese nell'Industry")
        fig_scatter = px.scatter(df_filtered_industry, x="valore KPI", y="RICAVI", color="Account", size="PRIORITA'",
                                 hover_name="Merchant", title="Rapporto tra Volumi Transati e Ricavi Generati")
        st.plotly_chart(fig_scatter, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Consiglio Acquiring Fisico & E-com:** I dati indicano che soluzioni come il **SoftPOS** e campagne mirate **E-commerce (CNP / Wallet)** generano conversioni rapide con un buon delta di ricavi.")