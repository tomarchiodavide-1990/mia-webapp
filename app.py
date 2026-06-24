import streamlit as st
import pandas as pd
import plotly.express as px

# Configurazione della pagina
st.set_page_config(page_title="Tomarchio Performance Dashboard", layout="wide", page_icon="🚀")

st.title("🚀 Tomarchio Strategic Commercial Dashboard")
st.markdown("Focus sulle performance reali, potenziale di Pipeline e quote di mercato (SOW).")

# -----------------------------------------------------------------------------
# ESTRAZIONE DATI REALI (Dai fogli PIPELINE e SOW)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    # I tuoi veri deal estratti dal file
    pipeline_data = [
        {"Merchant": "PRENATAL (Artsana)", "Nome Deal": "Repricing ISP", "STATUS": "WIP", "RICAVI": 215000, "Categoria": "REPRICING", "Canale": "FISICO", "Note": "In rinegoziazione da 2.5bps a 7bps"},
        {"Merchant": "PRENATAL (Artsana)", "Nome Deal": "DCC", "STATUS": "WIP", "RICAVI": 34400, "Categoria": "REPRICING", "Canale": "FISICO", "Note": "Margine extra su carte estere"},
        {"Merchant": "GRUPPO INDITEX (ZARA)", "Nome Deal": "Gateway Ecom", "STATUS": "WIN", "RICAVI": 120000, "Categoria": "CAMPAGNA ECOMMERCE", "Canale": "ECOMMERCE", "Note": "Chiuso con successo"},
        {"Merchant": "D.M.O. S.P.A (Beauty Star)", "Nome Deal": "CNP Beauty Star", "STATUS": "WIP", "RICAVI": 600, "Categoria": "CAMPAGNA ECOMMERCE", "Canale": "ECOMMERCE", "Note": "Offerta inviata (Volumi 1M)"},
        {"Merchant": "ACQUA & SAPONE", "Nome Deal": "Svecchiamento POS '26", "STATUS": "WIP", "RICAVI": 1500, "Categoria": "RINNOVO POS", "Canale": "FISICO", "Note": "Tender Card Present via BPER"},
    ]
    
    # Dati Share of Wallet (SOW) - Nomi colonne semplificati per evitare bug
    sow_data = [
        {"Merchant": "ZARA", "Canale": "ECOMMERCE", "Quota_Nexi": 0.64, "Quota_Competitor": 0.36, "Market_Volume": "1.0 Bln€"},
        {"Merchant": "D.M.O. S.P.A", "Canale": "MISTO", "Quota_Nexi": 0.65, "Quota_Competitor": 0.35, "Market_Volume": "230 M€"},
        {"Merchant": "PRENATAL", "Canale": "FISICO", "Quota_Nexi": 0.80, "Quota_Competitor": 0.20, "Market_Volume": "430 M€"}
    ]
    
    return pd.DataFrame(pipeline_data), pd.DataFrame(sow_data)

df_pipeline, df_sow = load_data()

# -----------------------------------------------------------------------------
# TABS
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🎯 Il Mio Vero Valore (Pipeline)", "🦅 Attacco ai Competitor (SOW)", "📊 Confronto Team Ricalibrato"])

# =============================================================================
# TAB 1: IL MIO VERO VALORE
# =============================================================================
with tab1:
    st.header("Focus Valore Totale Generato + Potenziale")
    st.info("💡 **Nota Strategica:** Il target YTD misura solo i contratti già firmati. Se consideriamo i deal ad alto stadio di avanzamento (WIP), la performance reale è nettamente superiore al budget assegnato.")
    
    chiuso_ytd = df_pipeline[df_pipeline["STATUS"] == "WIN"]["RICAVI"].sum()
    wip_potenziale = df_pipeline[df_pipeline["STATUS"] == "WIP"]["RICAVI"].sum()
    valore_totale = chiuso_ytd + wip_potenziale
    target_aziendale = 150000
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Budget Assegnato 2026", value=f"€{target_aziendale/1000:.1f} K")
    with col2:
        st.metric(label="Valore Totale (WIN + WIP Attivo)", value=f"€{valore_totale/1000:.1f} K", delta=f"+€{(valore_totale-target_aziendale)/1000:.1f} K Oltre Target")
    with col3:
        st.metric(label="Percentuale Copertura Target", value=f"{int((valore_totale/target_aziendale)*100)}%", delta="Target Ampiamente Superato")

    st.subheader("Avanzamento e Copertura del Budget")
    df_chart = pd.DataFrame({
        "Stato": ["Target Richiesto", "Gia Chiuso (WIN)", "In Chiusura (WIP)"],
        "Valore": [target_aziendale, chiuso_ytd, wip_potenziale]
    })
    fig_potenziale = px.bar(df_chart, x="Stato", y="Valore", color="Stato",
                           title="Visione Prospettica: Come la tua Pipeline supera gli obiettivi dell'anno",
                           color_discrete_map={"Target Richiesto": "#7f7f7f", "Gia Chiuso (WIN)": "#2ca02c", "In Chiusura (WIP)": "#1f77b4"})
    st.plotly_chart(fig_potenziale, use_container_width=True)

    st.subheader("Dettaglio dei Grandi Account in Gestione")
    st.dataframe(df_pipeline, use_container_width=True)

# =============================================================================
# TAB 2: ATTACCO AI COMPETITOR (SOW)
# =============================================================================
with tab2:
    st.header("Analisi Share of Wallet (SOW) sui Top Client")
    st.markdown("Questa schermata mostra la tua efficacia nel difendere e sottrarre fette di mercato ai competitor sui merchant che gestisci.")
    
    col1_sow, col2_sow = st.columns([1, 2])
    
    with col1_sow:
        st.subheader("I tuoi Merchant")
        for index, row in df_sow.iterrows():
            st.write(f"🍏 **{row['Merchant']}** ({row['Canale']})")
            st.progress(int(row['Quota_Nexi'] * 100))
            st.caption(f"Tua Quota: {int(row['Quota_Nexi']*100)}% | Competitor: {int(row['Quota_Competitor']*100)}% (Mercato: {row['Market_Volume']})")
            st.markdown("---")
            
    with col2_sow:
        st.subheader("Presidio del Mercato Gestito da Tomarchio")
        # Riorganizziamo i dati per il grafico evitando stringhe con caratteri speciali
        df_sow_melt = df_sow.melt(id_vars=["Merchant"], value_vars=["Quota_Nexi", "Quota_Competitor"], var_name="Posizionamento", value_name="Quota")
        df_sow_melt["Posizionamento"] = df_sow_melt["Posizionamento"].replace({"Quota_Nexi": "Quota Nexi/ISP", "Quota_Competitor": "Quota Competitor"})
        
        fig_sow = px.bar(df_sow_melt, x="Merchant", y="Quota", color="Posizionamento", barmode="stack",
                         title="Dominanza Nexi/ISP sui tuoi Clienti Rispetto ai Concorrenti",
                         color_discrete_sequence=["#2ca02c", "#d62728"])
        st.plotly_chart(fig_sow, use_container_width=True)

# =============================================================================
# TAB 3: CONFRONTO TEAM RICALIBRATO
# =============================================================================
with tab3:
    st.header("Posizionamento nel Team per Qualità dei Clienti")
    st.markdown("Mentre altri gestiscono molti contratti piccoli, la tua strategia si concentra su **Grandi Account Core** (Retail & Apparel) che muovono volumi miliardari.")
    
    team_metrics = [
        {"Account": "Dalla Torre", "Numero Merchant": 12, "Volume Medio Clienti (M€)": 15, "Focus Primario": "Mass Market"},
        {"Account": "Mariani", "Numero Merchant": 8, "Volume Medio Clienti (M€)": 10, "Focus Primario": "SME / E-com local"},
        {"Account": "Tomarchio", "Numero Merchant": 5, "Volume Medio Clienti (M€)": 215, "Focus Primario": "Enterprise Tier 1 (Zara/Prenatal)"},
        {"Account": "Luzzio", "Numero Merchant": 4, "Volume Medio Clienti (M€)": 180, "Focus Primario": "Corporate / Partners"}
    ]
    df_team_metrics = pd.DataFrame(team_metrics)
    
    fig_team_qual = px.scatter(df_team_metrics, x="Numero Merchant", y="Volume Medio Clienti (M€)", size="Volume Medio Clienti (M€)",
                               color="Account", text="Account", title="Mappatura del Team: Chi gestisce i Clienti con più Volumi di Mercato?",
                               size_max=40)
    st.plotly_chart(fig_team_qual, use_container_width=True)
    st.caption("Nota: Tomarchio si posiziona nel quadrante ad altissimo valore (pochi clienti ma con volumi transati enormi), richiedendo una gestione strategica complessa rispetto al mass-market.")
