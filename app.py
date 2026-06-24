import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Retail Pipeline Master Platform 2026", layout="wide", page_icon="🏢")

st.title("🏢 Retail Pipeline Master Platform 2026")
st.markdown("### Piattaforma Strategica di Monitoraggio Acquiring & E-commerce per il Team Retail")

# -----------------------------------------------------------------------------
# LETTURA SICURA DELL'EXCEL
# -----------------------------------------------------------------------------
@st.cache_data
def load_real_data_safe():
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if not files:
        return None, None, None, "Nessun file .xlsx trovato nella cartella"
    
    file_path = files[0]
    try:
        xls = pd.ExcelFile(file_path, engine='openpyxl')
        sheets = xls.sheet_names
        
        df_p = pd.read_excel(file_path, sheet_name="PIPELINE", engine='openpyxl') if "PIPELINE" in sheets else pd.read_excel(file_path, sheet_name=0, engine='openpyxl')
        df_t = pd.read_excel(file_path, sheet_name="CB + DBS IR", engine='openpyxl') if "CB + DBS IR" in sheets else pd.DataFrame()
        df_s = pd.read_excel(file_path, sheet_name="SOW 2025", engine='openpyxl') if "SOW 2025" in sheets else pd.DataFrame()
        
        return df_p, df_t, df_s, file_path
    except Exception as e:
        return None, None, None, str(e)

df_pipeline, df_team_raw, df_sow, status_msg = load_real_data_safe()

if df_pipeline is None:
    st.error(f"⚠️ Errore nel caricamento: {status_msg}")
    st.stop()

st.sidebar.success(f"📁 Collegato a: {status_msg}")

# -----------------------------------------------------------------------------
# TRATTAMENTO INTELLIGENTE DEL FOGLIO BUDGET (CB + DBS IR)
# -----------------------------------------------------------------------------
df_team = pd.DataFrame()
if not df_team_raw.empty:
    # Cerchiamo in quale riga si trovano i nomi dei commerciali per ricostruire la tabella
    nomi_team = ['Dalla Torre', 'Mariani', 'Tomarchio', 'Luzzio']
    riga_inizio = None
    colonna_nomi = None
    
    # Scansioniamo il foglio per trovare dove sono posizionati i commerciali
    for r in range(min(len(df_team_raw), 15)):
        for c in range(len(df_team_raw.columns)):
            valore = str(df_team_raw.iloc[r, c]).strip()
            if any(nome in valore for nome in nomi_team):
                riga_inizio = r
                colonna_nomi = c
                break
        if riga_inizio is not None:
            break
            
    if riga_inizio is not None:
        # Trovata l'intestazione, ricreiamo il dataframe pulito
        intestazioni = df_team_raw.iloc[riga_inizio - 1].tolist()
        # Se l'intestazione sopra è vuota, usiamo quella della riga stessa
        if all(pd.isna(x) for x in intestazioni):
            intestazioni = df_team_raw.iloc[riga_inizio].tolist()
            
        df_pulito = df_team_raw.iloc[riga_inizio:].copy()
        df_pulito.columns = [str(h).strip() for h in intestazioni]
        
        # Identifichiamo qual è la colonna che contiene i nomi (es. OBIETTIVO o Commerciale)
        col_target_name = df_pulito.columns[colonna_nomi]
        
        # Filtriamo tenendo solo le righe dei commerciali ed eliminando i totali finali
        df_team = df_pulito[df_pulito[col_target_name].astype(str).str.contains('|'.join(nomi_team), na=False)].copy()
        df_team.rename(columns={col_target_name: "Commerciale"}, inplace=True)
        
        # Rendiamo numeriche le colonne dei dati (YTD, Budget, GAP)
        for col in df_team.columns:
            if col != "Commerciale":
                df_team[col] = pd.to_numeric(df_team[col], errors='coerce')
    else:
        # Se la ricerca fallisce, mostriamo i dati così come sono senza crash
        df_team = df_team_raw.copy()

# -----------------------------------------------------------------------------
# PULIZIA COLONNE PIPELINE
# -----------------------------------------------------------------------------
df_pipeline.columns = [str(c).strip() for c in df_pipeline.columns]
col_account = next((c for c in df_pipeline.columns if c.upper() == 'ACCOUNT'), None)
col_status = next((c for c in df_pipeline.columns if c.upper() == 'STATUS'), None)
col_ricavi = next((c for c in df_pipeline.columns if c.upper() == 'RICAVI'), None)

# Filtri barra laterale
st.sidebar.header("🎛️ Pannello di Controllo & Filtri")
df_filtered = df_pipeline.copy()

if col_account:
    commerciali = list(df_pipeline[col_account].dropna().unique())
    acc_sel = st.sidebar.multiselect("Visualizza Account Team:", options=commerciali, default=commerciali)
    if acc_sel:
        df_filtered = df_filtered[df_filtered[col_account].isin(acc_sel)]

if col_status:
    stati = list(df_pipeline[col_status].dropna().unique())
    st_sel = st.sidebar.multiselect("Stato del Deal:", options=stati, default=stati)
    if st_sel:
        df_filtered = df_filtered[df_filtered[col_status].isin(st_sel)]

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
    col1, col2 = st.columns(2)
    with col1:
        if col_ricavi and col_ricavi in df_filtered.columns:
            st.metric("Valore Totale Pipeline Filtrata", f"€ {df_filtered[col_ricavi].sum():,.2f}")
    with col2:
        st.metric("Numero di Deal Attivi", len(df_filtered))

    st.markdown("---")
    if col_account and col_ricavi:
        st.subheader("Fatturato Pipeline per Account (€)")
        fig = px.bar(df_filtered, x=col_account, y=col_ricavi, color=col_status if col_status else None, barmode="stack")
        st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# TAB 2: FOCUS PERSONALE
# =============================================================================
with tabs[1]:
    st.header("Area Personale Commerciale")
    if col_account and col_account in df_pipeline.columns:
        commerciali_list = list(df_pipeline[col_account].dropna().unique())
        default_idx = commerciali_list.index("Tomarchio") if "Tomarchio" in commerciali_list else 0
        utente = st.selectbox("Seleziona il profilo commerciale:", options=commerciali_list, index=default_idx)
        
        df_singolo = df_pipeline[df_pipeline[col_account] == utente]
        st.dataframe(df_singolo, use_container_width=True)

# =============================================================================
# TAB 3: PERFORMANCE BUDGET TEAM
# =============================================================================
with tabs[2]:
    st.header("Analisi Obiettivi e Budget Estrapolati (CB + DBS IR)")
    if not df_team.empty:
        st.dataframe(df_team, use_container_width=True)
        
        # Cerchiamo colonne numeriche per fare un grafico di performance commerciale
        col_ytd = next((c for c in df_team.columns if 'YTD' in c.upper() or 'CHIUSO' in c.upper()), None)
        col_gap = next((c for c in df_team.columns if 'GAP' in c.upper() or 'RESTANTE' in c.upper()), None)
        
        if col_ytd and "Commerciale" in df_team.columns:
            st.subheader("Avanzamento Target per Commerciale")
            metriche_grafico = [col_ytd]
            if col_gap: metriche_grafico.append(col_gap)
            fig_perf = px.bar(df_team, x="Commerciale", y=metriche_grafico, title="Performance Reale vs Gap", barmode="group")
            st.plotly_chart(fig_perf, use_container_width=True)
    else:
        st.warning("Impossibile mappare la struttura del foglio budget. Viene mostrato il foglio grezzo sotto:")
        st.dataframe(df_team_raw, use_container_width=True)

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
        st.dataframe(df_sow, use_container_width=True)
    else:
        st.warning("Foglio 'SOW 2025' non trovato o vuoto.")
