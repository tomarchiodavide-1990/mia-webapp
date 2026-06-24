import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Retail Pipeline Master Platform 2026", layout="wide", page_icon="🏢")

st.title("🏢 Retail Pipeline Master Platform 2026")
st.markdown("### Piattaforma Strategica di Monitoraggio Acquiring & E-commerce per il Team Retail")

# -----------------------------------------------------------------------------
# LETTURA TOTALMENTE APERTA E ULTRA PURIFFICATA
# -----------------------------------------------------------------------------
@st.cache_data
def load_real_data_ultra_safe():
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if not files:
        return None, None, None, "Nessun file .xlsx trovato."
    
    file_path = files[0]
    try:
        # Carichiamo i fogli forzando la conversione in stringhe di tutto l'Excel per evitare blocchi grafici
        df_p = pd.read_excel(file_path, sheet_name="PIPELINE", engine='openpyxl').astype(str)
        df_t = pd.read_excel(file_path, sheet_name="CB + DBS IR", engine='openpyxl').astype(str) if "CB + DBS IR" in os.listdir('.') or True else pd.DataFrame()
        
        # Tentiamo di recuperare SOW 2025
        try:
            df_s = pd.read_excel(file_path, sheet_name="SOW 2025", engine='openpyxl').astype(str)
        except:
            df_s = pd.DataFrame()
            
        return df_p, df_t, df_s, file_path
    except Exception as e:
        return None, None, None, f"Errore critico di lettura: {str(e)}"

df_pipeline, df_team_raw, df_sow, detected_file = load_real_data_ultra_safe()

if df_pipeline is None:
    st.error(f"⚠️ {detected_file}")
    st.stop()

st.info(f"📁 File Excel letto con successo: **{detected_file}**")

# Pulizia colonne
df_pipeline.columns = [str(c).strip() for c in df_pipeline.columns]

col_account = next((c for c in df_pipeline.columns if c.upper() in ['ACCOUNT', 'COMMERCIALE', 'SALES']), None)
col_status = next((c for c in df_pipeline.columns if c.upper() in ['STATUS', 'STATO']), None)
col_ricavi = next((c for c in df_pipeline.columns if c.upper() in ['RICAVI', 'VALORE', 'REVENUE']), None)

# -----------------------------------------------------------------------------
# FILTRI IN BANDA ORIZZONTALE
# -----------------------------------------------------------------------------
st.markdown("### 🎛️ Filtri di Monitoraggio")
f_col1, f_col2 = st.columns(2)

df_filtered = df_pipeline.copy()

with f_col1:
    if col_account:
        commerciali_disponibili = sorted(list(df_pipeline[col_account].dropna().unique()))
        acc_sel = st.multiselect("Filtra per Account Team:", options=commerciali_disponibili, default=commerciali_disponibili)
        if acc_sel:
            df_filtered = df_filtered[df_filtered[col_account].isin(acc_sel)]

with f_col2:
    if col_status:
        stati_disponibili = sorted(list(df_pipeline[col_status].dropna().unique()))
        st_sel = st.multiselect("Filtra per Stato del Deal:", options=stati_disponibili, default=stati_disponibili)
        if st_sel:
            df_filtered = df_filtered[df_filtered[col_status].isin(st_sel)]

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
# TAB 1: DATABASE PIPELINE (Rendering indistruttibile in HTML statico)
# =============================================================================
with tabs[0]:
    st.header("Database Completo della Pipeline (Foglio PIPELINE)")
    if not df_filtered.empty:
        # Sostituiamo i valori 'nan' grafici con celle vuote pulite
        df_html = df_filtered.replace('nan', '')
        # Usiamo st.markdown con l'HTML per forzare il browser a stampare la tabella, saltando i blocchi di Streamlit
        st.write(df_html)
    else:
        st.warning("Nessun dato corrispondente ai filtri selezionati.")

# =============================================================================
# TAB 2: DASHBOARD GRAFICA
# =============================================================================
with tabs[1]:
    st.header("Analytics di Sintesi Retail 2026")
    
    if col_ricavi and col_ricavi in df_filtered.columns:
        # Convertiamo al volo i ricavi in numeri solo per fare il grafico
        df_chart = df_filtered.copy()
        df_chart[col_ricavi] = pd.to_numeric(df_chart[col_ricavi].str.replace('€', '').str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0)
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Valore Totale Pipeline Filtrata", f"€ {df_chart[col_ricavi].sum():,.2f}")
        with c2:
            st.metric("Numero di Deal Attivi", len(df_filtered))
            
        st.markdown("---")
        if col_account:
            st.subheader("Fatturato Pipeline per Account (€)")
            fig = px.bar(df_chart, x=col_account, y=col_ricavi, color=col_status if col_status else None, barmode="stack")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Caricamento grafici... Seleziona i filtri per aggiornare.")

# =============================================================================
# TAB 3: FOCUS PERSONALE
# =============================================================================
with tabs[2]:
    st.header("Area Personale Commerciale")
    if col_account:
        commerciali_list = sorted(list(df_pipeline[col_account].dropna().unique()))
        utente = st.selectbox("Seleziona il profilo commerciale da analizzare:", options=commerciali_list)
        
        df_singolo = df_pipeline[df_pipeline[col_account] == utente].replace('nan', '')
        st.write(df_singolo)

# =============================================================================
# TAB 4: PERFORMANCE BUDGET TEAM
# =============================================================================
with tabs[3]:
    st.header("Visualizzazione Dati di Budget (Foglio CB + DBS IR)")
    if df_team_raw is not None and not df_team_raw.empty:
        st.write(df_team_raw.replace('nan', ''))
    else:
        st.warning("Foglio budget non accessibile.")

# =============================================================================
# TAB 5: SHARE OF WALLET (SOW)
# =============================================================================
with tabs[4]:
    st.header("Quota di Mercato e Analisi SOW (Foglio SOW 2025)")
    if df_sow is not None and not df_sow.empty:
        st.write(df_sow.replace('nan', ''))
    else:
        st.warning("Foglio SOW 2025 non trovato o vuoto.")
