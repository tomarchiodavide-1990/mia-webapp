import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Retail Pipeline Master Platform 2026", layout="wide", page_icon="🏢")

st.title("🏢 Retail Pipeline Master Platform 2026")
st.markdown("### Piattaforma Strategica di Monitoraggio Acquiring & E-commerce per il Team Retail")

# -----------------------------------------------------------------------------
# RICERCA AUTOMATICA E LETTURA INTELLIGENTE DELL'EXCEL
# -----------------------------------------------------------------------------
@st.cache_data
def load_real_data():
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if not files:
        return None, None, None, "Nessun file trovato"
    
    file_path = files[0]
    try:
        # Caricamento dei fogli con openpyxl
        df_p = pd.read_excel(file_path, sheet_name="PIPELINE")
        
        # Lettura mirata del foglio budget saltando le righe vuote iniziali
        df_t = pd.read_excel(file_path, sheet_name="CB + DBS IR", skiprows=3)
        # Filtriamo solo le righe dei commerciali reali per evitare i totali sporchi
        if not df_t.empty and 'OBIETTIVO' in df_t.columns:
            df_t = df_t[df_t['OBIETTIVO'].isin(['Dalla Torre', 'Mariani', 'Tomarchio', 'Luzzio'])]
            
        df_s = pd.read_excel(file_path, sheet_name="SOW 2025")
        return df_p, df_t, df_s, file_path
    except Exception as e:
        return None, None, None, str(e)

df_pipeline, df_team, df_sow, status_msg = load_real_data()

if df_pipeline is None:
    st.error(f"⚠️ Errore di lettura o file mancante: {status_msg}")
    st.info("Assicurati di aver aggiornato il file `requirements.txt` inserendo anche `openpyxl` su una nuova riga.")
    st.stop()

st.sidebar.success(f"📁 Collegato all'Excel: {status_msg}")

# -----------------------------------------------------------------------------
# FILTRI BARRA LATERALE
# -----------------------------------------------------------------------------
st.sidebar.header("🎛️ Pannello di Controllo & Filtri")

commerciali = list(df_pipeline["Account"].dropna().unique()) if "Account" in df_pipeline.columns else []
stati = list(df_pipeline["STATUS"].dropna().unique()) if "STATUS" in df_pipeline.columns else []
categorie = list(df_pipeline["CATEGORIA DEAL"].dropna().unique()) if "CATEGORIA DEAL" in df_pipeline.columns else []

account_selezionati = st.sidebar.multiselect("Visualizza Account Team:", options=commerciali, default=commerciali)
stati_selezionati = st.sidebar.multiselect("Stato del Deal:", options=stati, default=stati)
cat_selezionate = st.sidebar.multiselect("Categoria Deal:", options=categorie, default=categorie)

# Applicazione filtri incrociati
df_filtered = df_pipeline.copy()
if account_selezionati:
    df_filtered = df_filtered[df_filtered["Account"].isin(account_selezionati)]
if stati_selezionati:
    df_filtered = df_filtered[df_filtered["STATUS"].isin(stati_selezionati)]
if cat_selezionate:
    df_filtered = df_filtered[df_filtered["CATEGORIA DEAL"].isin(cat_selezionate)]

# -----------------------------------------------------------------------------
# PAGINE (TABS)
# -----------------------------------------------------------------------------
tabs = st.tabs([
    "📈 Dashboard Esecutiva", 
    "👤 Focus Personale", 
    "👥 Performance Budget Team", 
    "🎯 Database Pipeline", 
    "🦅 Share of Wallet (SOW)"
])

# =============================================================================
# TAB 1: DASHBOARD ESECUTIVA
# =============================================================================
with tabs[0]:
    st.header("Analytics di Sintesi Retail 2026")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        ricavi_tot = df_filtered['RICAVI'].sum() if 'RICAVI' in df_filtered.columns else 0
        st.metric("Valore Totale Pipeline Filtrata", f"€ {ricavi_tot:,.2f}")
    with col2:
        st.metric("Numero di Deal Attivi", len(df_filtered))
    with col3:
        st.metric("Commerciali Inclusi", len(account_selezionati))

    st.markdown("---")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Fatturato Pipeline per Account (€)")
        fig = px.bar(df_filtered, x="Account", y="RICAVI", color="STATUS", barmode="stack",
                     color_discrete_map={"WIN": "#2ca02c", "WIP": "#1f77b4"})
        st.plotly_chart(fig, use_container_width=True)
        
    with col_g2:
        st.subheader("Impatto delle Banche Partner sui Deal")
        fig_banca = px.bar(df_filtered, x="BANCA PARTNER", y="RICAVI", color="STATUS", barmode="group")
        st.plotly_chart(fig_banca, use_container_width=True)

# =============================================================================
# TAB 2: FOCUS PERSONALE
# =============================================================================
with tabs[1]:
    st.header("Area Personale Commerciale")
    if commerciali:
        default_idx = commerciali.index("Tomarchio") if "Tomarchio" in commerciali else 0
        utente = st.selectbox("Seleziona il profilo commerciale:", options=commerciali, index=default_idx)
        
        df_singolo = df_pipeline[df_pipeline["Account"] == utente]
        
        st.markdown(f"### I tuoi Deal in gestione ({utente})")
        st.dataframe(df_singolo[["PRIORITA'", "Merchant", "Nome Deal", "STATUS", "RICAVI", "BANCA PARTNER", "next"]], use_container_width=True)
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            fig_pie = px.pie(df_singolo, values="RICAVI", names="STATUS", title="Stato dei tuoi Ricavi (WIN vs WIP)")
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_s2:
            fig_cat = px.bar(df_singolo, x="CATEGORIA DEAL", y="RICAVI", title="I tuoi Deal per Categoria Prodotto", color="STATUS")
            st.sidebar.markdown("---")
            st.plotly_chart(fig_cat, use_container_width=True)

# =============================================================================
# TAB 3: PERFORMANCE BUDGET TEAM (CB + DBS IR)
# =============================================================================
with tabs[2]:
    st.header("Quadro Comparativo degli Obiettivi e Target Reali")
    if not df_team.empty and 'OBIETTIVO' in df_team.columns:
        st.dataframe(df_team[['OBIETTIVO', 'OBIETTIVO', 'YTD', 'GAP']].rename(columns={'OBIETTIVO':'Commerciale'}), use_container_width=True)
        
        fig_perf = px.bar(df_team, x="OBIETTIVO", y=["YTD", "GAP"], title="Avanzamento Target YTD rispetto al GAP rimanente", barmode="group")
        st.plotly_chart(fig_perf, use_container_width=True)
    else:
        st.info("Dati budget non strutturati o foglio 'CB + DBS IR' non configurato per la visualizzazione.")

# =============================================================================
# TAB 4: DATABASE PIPELINE
# =============================================================================
with tabs[3]:
    st.header("Database Completo della Pipeline (Filtrato)")
    st.dataframe(df_filtered, use_container_width=True)

# =============================================================================
# TAB 5: SHARE OF WALLET (SOW)
# =============================================================================
with tabs[4]:
    st.header("Quota di Mercato e Analisi SOW (Share of Wallet)")
    if not df_sow.empty:
        st.dataframe(df_sow[['LAKA', 'CANALE', 'STIMA VOLUME MERCATO (ISSUING)', 'SOW NEXI', 'SOW POSTE', 'SOW ADYEN']].head(20), use_container_width=True)
        
        fig_sow = px.bar(df_sow.head(15), x="LAKA", y=["SOW NEXI", "SOW ADYEN", "SOW POSTE"], 
                         title="Presidio Nexi vs Competitor sui Top Client (Primi 15)", barmode="stack")
        st.plotly_chart(fig_sow, use_container_width=True)
