import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Retail Pipeline Master Platform 2026", layout="wide", page_icon="🏢")

st.title("🏢 Retail Pipeline Master Platform 2026")
st.markdown("### Piattaforma Strategica di Monitoraggio Acquiring & E-commerce per il Team Retail")

# -----------------------------------------------------------------------------
# LETTURA TOTALMENTE APERTA E SICURA DELL'EXCEL
# -----------------------------------------------------------------------------
@st.cache_data
def load_real_data_ultra_safe():
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if not files:
        return None, None, None, "Nessun file .xlsx trovato nella cartella principale di GitHub."
    
    file_path = files[0]
    try:
        xls = pd.ExcelFile(file_path, engine='openpyxl')
        sheets = xls.sheet_names
        
        # Carichiamo i fogli così come sono, senza filtri o manipolazioni preventive
        df_p = pd.read_excel(file_path, sheet_name="PIPELINE", engine='openpyxl') if "PIPELINE" in sheets else pd.read_excel(file_path, sheet_name=0, engine='openpyxl')
        df_t = pd.read_excel(file_path, sheet_name="CB + DBS IR", engine='openpyxl') if "CB + DBS IR" in sheets else pd.DataFrame()
        df_s = pd.read_excel(file_path, sheet_name="SOW 2025", engine='openpyxl') if "SOW 2025" in sheets else pd.DataFrame()
        
        return df_p, df_t, df_s, file_path
    except Exception as e:
        return None, None, None, f"Errore critico di lettura: {str(e)}"

df_pipeline, df_team_raw, df_sow, detected_file = load_real_data_ultra_safe()

# Se c'è un errore bloccante, lo mostriamo chiaramente a schermo per fare debug
if df_pipeline is None:
    st.error(f"⚠️ {detected_file}")
    st.stop()

# Banner informativo sul file agganciato
st.info(f"📁 File Excel letto con successo: **{detected_file}**")

# Pulizia base dei nomi delle colonne per evitare spazi vuoti laterali
df_pipeline.columns = [str(c).strip() for c in df_pipeline.columns]

# Individuiamo la colonna del commerciale e dello stato in modo flessibile
col_account = next((c for c in df_pipeline.columns if c.upper() in ['ACCOUNT', 'COMMERCIALE', 'SALES']), None)
col_status = next((c for c in df_pipeline.columns if c.upper() in ['STATUS', 'STATO']), None)
col_ricavi = next((c for c in df_pipeline.columns if c.upper() in ['RICAVI', 'VALORE', 'REVENUE']), None)

# -----------------------------------------------------------------------------
# FILTRI POSIZIONATI COME BANDA ORIZZONTALE IN ALTO
# -----------------------------------------------------------------------------
st.markdown("### 🎛️ Filtri di Monitoraggio")
f_col1, f_col2 = st.columns(2)

df_filtered = df_pipeline.copy()

with f_col1:
    if col_account:
        commerciali_disponibili = list(df_pipeline[col_account].dropna().unique())
        acc_sel = st.multiselect("Filtra per Account Team:", options=commerciali_disponibili, default=commerciali_disponibili)
        if acc_sel:
            df_filtered = df_filtered[df_filtered[col_account].isin(acc_sel)]
    else:
        st.caption("Filtro Account non disponibile (colonna non intercettata)")

with f_col2:
    if col_status:
        stati_disponibili = list(df_pipeline[col_status].dropna().unique())
        st_sel = st.multiselect("Filtra per Stato del Deal:", options=stati_disponibili, default=stati_disponibili)
        if st_sel:
            df_filtered = df_filtered[df_filtered[col_status].isin(st_sel)]
    else:
        st.caption("Filtro Stato non disponibile (colonna non intercettata)")

st.markdown("---")

# -----------------------------------------------------------------------------
# PAGINE (TABS)
# -----------------------------------------------------------------------------
tabs = st.tabs([
    "🎯 Database Pipeline",
    "📈 Dashboard Grafica", 
    "👤 Focus Personale", 
    "👥 Performance Budget Team", 
    "🦅 Share of Wallet (SOW)"
])

# =============================================================================
# TAB 1: DATABASE PIPELINE (Messa come prima tab così vedi subito i dati!)
# =============================================================================
with tabs[0]:
    st.header("Database Completo della Pipeline (Foglio PIPELINE)")
