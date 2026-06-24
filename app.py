import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Configurazione della pagina ad alta densità informativa
st.set_page_config(page_title="Retail Pipeline Master Platform 2026", layout="wide", page_icon="🏢")

st.title("🏢 Retail Pipeline Master Platform 2026")
st.markdown("### Piattaforma Strategica di Monitoraggio Acquiring & E-commerce per il Team Retail")

# -----------------------------------------------------------------------------
# RICERCA AUTOMATICA E INTELLIGENTE DEL FILE EXCEL
# -----------------------------------------------------------------------------
@st.cache_data
def load_any_excel():
    # Cerchiamo qualsiasi file .xlsx presente nella cartella dell'app
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if not files:
        return None, None, None, None
    
    # Scegliamo il primo file excel trovato (che sarà la tua pipeline)
    file_path = files[0]
    
    try:
        xls = pd.ExcelFile(file_path)
        sheets = xls.sheet_names
        
        # Caricamento dinamico basato sui fogli reali che abbiamo trovato nel tuo file
        df_p = pd.read_excel(file_path, sheet_name="PIPELINE") if "PIPELINE" in sheets else pd.read_excel(file_path, sheet_name=0)
        df_t = pd.read_excel(file_path, sheet_name="DB IR") if "DB IR" in sheets else (pd.read_excel(file_path, sheet_name="CB + DBS IR") if "CB + DBS IR" in sheets else pd.DataFrame())
        df_s = pd.read_excel(file_path, sheet_name="SOW 2025") if "SOW 2025" in sheets else pd.DataFrame()
        
        return df_p, df_t, df_s, file_path
    except Exception as e:
        st.error(f"Errore nel caricamento del file: {e}")
        return None, None, None, None

df_pipeline, df_team, df_sow, detected_filename = load_any_excel()

# Controllo di sicurezza se non trova proprio nessun file .xlsx
if df_pipeline is None:
    st.error("⚠️ Non ho trovato nessun file Excel con estensione `.xlsx` su GitHub.")
    st.info("💡 **Verifica questo:** Quando hai caricato il file su GitHub, sei sicuro di aver cliccato sul pulsante verde **'Commit changes'** in fondo alla pagina per salvarlo? Se non lo fai, il file non viene memorizzato.")
    st.stop()

# Mostra il file rilevato per conferma
st.sidebar.success(f"📁 File rilevato: {detected_filename}")

# -----------------------------------------------------------------------------
# BARRA LATERALE - FILTRI DINAMICI REALI
# -----------------------------------------------------------------------------
st.sidebar.header("🎛️ Pannello di Controllo & Filtri")

# Pulizia nomi colonne foglio PIPELINE
df_pipeline.columns = [c.strip() for c in df_pipeline.columns]

# Creazione filtri basati sulle colonne REALI del tuo foglio Excel
commerciali = list(df_pipeline["Account"].dropna().unique()) if "Account" in df_pipeline.columns else []
stati = list(df_pipeline["STATUS"].dropna().unique()) if "STATUS" in df_pipeline.columns else []

account_selezionati = st.sidebar.multiselect("Visualizza Account Team:", options=commerciali, default=commerciali)
stati_selezionati = st.sidebar.multiselect("Stato del Deal:", options=stati, default=stati)

# Applicazione filtri sul database
df_filtered = df_pipeline.copy()
if "Account" in df_filtered.columns and account_selezionati:
    df_filtered = df_filtered[df_filtered["Account"].isin(account_selezionati)]
if "STATUS" in df_filtered.columns and stati_selezionati:
    df_filtered = df_filtered[df_filtered["STATUS"].isin(stati_selezionati)]

# -----------------------------------------------------------------------------
# LE SCHEDE DELLA WEB APP
# -----------------------------------------------------------------------------
tabs = st.tabs([
    "📈 Dashboard Esecutiva", 
    "👤 Focus Personale", 
    "👥 Performance Team (DB IR)", 
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
        if "RICAVI" in df_filtered.columns:
            st.metric("Valore Totale Pipeline Filtrata", f"€ {df_filtered['RICAVI'].sum():,.2f}")
    with col2:
        st.metric("Numero di Deal in Gestione", len(df_filtered))
    with col3:
        st.metric("Commerciali Attivi", len(account_selezionati))

    st.markdown("---")
    
    if "Account" in df_filtered.columns and "RICAVI" in df_filtered.columns:
        st.subheader("Distribuzione Economica dei Deal nel Team")
        fig_barra = px.bar(df_filtered, x="Account", y="RICAVI", color="STATUS" if "STATUS" in df_filtered.columns else None, 
                           title="Volume di Business per Singolo Account (€)")
        st.plotly_chart(fig_barra, use_container_width=True)

# =============================================================================
# TAB 2: FOCUS PERSONALE (TOMARCHIO DEFAUL)
# =============================================================================
with tabs[1]:
    st.header("Area Personale Commerciale")
    if commerciali:
        # Se ci sei tu, ti seleziona in automatico, altrimenti prende il primo
        default_index = commerciali.index("Tomarchio") if "Tomarchio" in commerciali else 0
        utente_selezionato = st.selectbox("Seleziona il tuo profilo commerciale:", options=commerciali, index=default_index)
        
        df_singolo = df_pipeline[df_pipeline["Account"] == utente_selezionato]
        
        st.markdown(f"### I tuoi Deal in gestione ({utente_selezionato})")
        st.dataframe(df_singolo, use_container_width=True)
        
        if "RICAVI" in df_singolo.columns and "STATUS" in df_singolo.columns:
            st.subheader("Avanzamento Economico Personale")
            fig_pie_singolo = px.pie(df_singolo, values="RICAVI", names="STATUS", title="Quota Deal Chiusi (WIN) vs In Trattativa (WIP)")
            st.plotly_chart(fig_pie_singolo, use_container_width=True)
    else:
        st.warning("Colonna 'Account' non rilevata per il filtro personale.")

# =============================================================================
# TAB 3: PERFORMANCE TEAM (DB IR)
# =============================================================================
with tabs[2]:
    st.header("Quadro Budget e Performance (Dati da Review)")
    if not df_team.empty:
        st.dataframe(df_team, use_container_width=True)
    else:
        st.warning("Nessun dato aggiuntivo trovato nel foglio delle performance budget.")

# =============================================================================
# TAB 4: DATABASE PIPELINE
# =============================================================================
with tabs[3]:
    st.header("Database Completo della Pipeline Filtrata")
    st.dataframe(df_filtered, use_container_width=True)

# =============================================================================
# TAB 5: SHARE OF WALLET (SOW)
# =============================================================================
with tabs[4]:
    st.header("Quota di Mercato e Analisi SOW (Share of Wallet)")
    if not df_sow.empty:
        st.dataframe(df_sow, use_container_width=True)
        
        # Se ci sono le colonne giuste facciamo un grafico al volo
        if "LAKA" in df_sow.columns and "SOW NEXI" in df_sow.columns:
            st.subheader("Visualizzazione Grafica SOW Nexi per Merchant")
            fig_sow = px.bar(df_sow, x="LAKA", y="SOW NEXI", title="Presidio Nexi sui Clienti")
            st.plotly_chart(fig_sow, use_container_width=True)
    else:
        st.warning("Dati Share of Wallet non trovati nel relativo foglio.")
