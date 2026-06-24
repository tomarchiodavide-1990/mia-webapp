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
# CARICAMENTO DEI DATI REALI DAL FILE EXCEL
# -----------------------------------------------------------------------------
excel_filename = "Pipeline Retail Master 2026_24062026.xlsx"

@st.cache_data
def load_excel_data(file_path):
    # Verifichiamo se il file esiste nella cartella dell'app
    if not os.path.exists(file_path):
        return None, None, None
    
    # Caricamento dinamico dei fogli principali
    try:
        df_p = pd.read_excel(file_path, sheet_name="PIPELINE")
        df_t = pd.read_excel(file_path, sheet_name="CB + DBS IR")
        df_s = pd.read_excel(file_path, sheet_name="SOW 2025")
        return df_p, df_t, df_s
    except Exception as e:
        # Se i fogli hanno nomi leggermente diversi, usiamo i primi 3 fogli disponibili
        xls = pd.ExcelFile(file_path)
        df_p = pd.read_excel(file_path, sheet_name=xls.sheet_names[0])
        df_t = pd.read_excel(file_path, sheet_name=xls.sheet_names[1]) if len(xls.sheet_names) > 1 else pd.DataFrame()
        df_s = pd.read_excel(file_path, sheet_name=xls.sheet_names[2]) if len(xls.sheet_names) > 2 else pd.DataFrame()
        return df_p, df_t, df_s

df_pipeline, df_team, df_sow = load_excel_data(excel_filename)

# Controllo di sicurezza nel caso il file non sia ancora stato caricato su GitHub
if df_pipeline is None:
    st.error(f"⚠️ Non ho trovato il file `{excel_filename}` nella tua repository di GitHub.")
    st.info("💡 **Come risolvere:** Carica il file Excel sul tuo GitHub dentro la cartella `mia-webapp` (esattamente dove si trova `app.py`) mantenendo lo stesso identico nome, e l'applicazione leggerà tutto istantaneamente!")
    st.stop()

# -----------------------------------------------------------------------------
# PULIZIA DATI E VALORI DI DEFAULT (Adattamento colonne Excel standard)
# -----------------------------------------------------------------------------
# Rendiamo i nomi delle colonne minuscoli o standard per evitare errori di battitura nel file
df_pipeline.columns = [c.strip() for c in df_pipeline.columns]
account_col = 'Account' if 'Account' in df_pipeline.columns else (df_pipeline.columns[2] if len(df_pipeline.columns) > 2 else df_pipeline.columns[0])
status_col = 'STATUS' if 'STATUS' in df_pipeline.columns else ('Stato' if 'Stato' in df_pipeline.columns else df_pipeline.columns[0])
ricavi_col = 'RICAVI' if 'RICAVI' in df_pipeline.columns else ('Ricavi' if 'Ricavi' in df_pipeline.columns else df_pipeline.columns[0])

# -----------------------------------------------------------------------------
# BARRA LATERALE - FILTRI DINAMICI AVANZATI (Per tutto il Team)
# -----------------------------------------------------------------------------
st.sidebar.header("🎛️ Pannello di Controllo & Filtri")

# Filtro Commerciali del Team
commerciali_disponibili = list(df_pipeline[account_col].dropna().unique())
account_selezionati = st.sidebar.multiselect("Visualizza Account Team:", options=commerciali_disponibili, default=commerciali_disponibili)

# Filtro Stato Trattativa
stati_disponibili = list(df_pipeline[status_col].dropna().unique())
stati_selezionati = st.sidebar.multiselect("Stato del Deal:", options=stati_disponibili, default=stati_disponibili)

# Applicazione filtri
df_filtered = df_pipeline[
    (df_pipeline[account_col].isin(account_selezionati)) &
    (df_pipeline[status_col].isin(stati_selezionati))
]

# -----------------------------------------------------------------------------
# LE 6 PAGINE DELLA WEB APP (Tabs)
# -----------------------------------------------------------------------------
tabs = st.tabs([
    "📈 Dashboard Esecutiva", 
    "👤 Focus Personale", 
    "👥 Performance Team", 
    "🎯 Analisi Pipeline", 
    "🦅 Share of Wallet (SOW)", 
    "🏬 Settori & Merchant Focus"
])

# =============================================================================
# TAB 1: DASHBOARD ESECUTIVA
# =============================================================================
with tabs[0]:
    st.header("Analytics di Sintesi Retail 2026")
    
    # Calcolo metriche reali basate sul file excel filtrato
    try:
        tot_ricavi = float(df_filtered[ricavi_col].sum())
    except:
        tot_ricavi = 0.0
        
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Valore Totale Pipeline Filtrata", f"€ {tot_ricavi:,.2f}")
    with col2:
        st.metric("Numero di Deal in Pancia", len(df_filtered))
    with col3:
        st.metric("Account Attivi Monitorati", len(account_selezionati))

    st.markdown("---")
    
    st.subheader("Volume di Business per Singolo Account")
    if account_col in df_filtered.columns and ricavi_col in df_filtered.columns:
        fig_barra = px.bar(df_filtered, x=account_col, y=ricavi_col, color=status_col, title="Distribuzione Economica dei Deal nel Team")
        st.plotly_chart(fig_barra, use_container_width=True)

# =============================================================================
# TAB 2: FOCUS PERSONALE (TOMARCHIO & CO.)
# =============================================================================
with tabs[1]:
    st.header("Area Personale Commerciale")
    utente_selezionato = st.selectbox("Seleziona il tuo profilo commerciale:", options=commerciali_disponibili)
    
    df_singolo = df_pipeline[df_pipeline[account_col] == utente_selezionato]
    
    st.markdown(f"### I tuoi Deal in gestione ({utente_selezionato})")
    st.dataframe(df_singolo, use_container_width=True)
    
    if ricavi_col in df_singolo.columns:
        st.subheader("Avanzamento Economico Personale")
        fig_pie_singolo = px.pie(df_singolo, values=ricavi_col, names=status_col, title="Quota Deal Chiusi vs In Trattativa")
        st.plotly_chart(fig_pie_singolo, use_container_width=True)

# =============================================================================
# TAB 3: PERFORMANCE TEAM
# =============================================================================
with tabs[2]:
    st.header("Quadro Comparativo delle Performance del Team Retail")
    if not df_team.empty:
        st.dataframe(df_team, use_container_width=True)
    else:
        st.warning("Dati di sintesi del budget non trovati nel secondo foglio del file Excel.")

# =============================================================================
# TAB 4: ANALISI PIPELINE DETTAGLIATA
# =============================================================================
with tabs[3]:
    st.header("Analisi Dettagliata dei Deal")
    st.dataframe(df_filtered, use_container_width=True)

# =============================================================================
# TAB 5: SHARE OF WALLET (SOW - COMPETITOR)
# =============================================================================
with tabs[4]:
    st.header("Quota di Mercato e Analisi SOW (Share of Wallet)")
    if not df_sow.empty:
        st.dataframe(df_sow, use_container_width=True)
    else:
        st.warning("Dati Share of Wallet non trovati nel terzo foglio del file Excel.")

# =============================================================================
# TAB 6: SETTORI & MERCHANT FOCUS
# =============================================================================
with tabs[5]:
    st.header("Analisi dei Settori Merceologici e Merchant Strategici")
    merchant_col = 'Merchant' if 'Merchant' in df_filtered.columns else df_filtered.columns[1]
    
    if merchant_col in df_filtered.columns and ricavi_col in df_filtered.columns:
        fig_merchant = px.treemap(df_filtered, path=[merchant_col], values=ricavi_col, title="Mappatura Dimensionale dei Clienti per Ricavi")
        st.plotly_chart(fig_merchant, use_container_width=True)
