import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Retail Pipeline Master Platform 2026", layout="wide", page_icon="🏢")

st.title("🏢 Retail Pipeline Master Platform 2026")
st.markdown("### Piattaforma Strategica di Monitoraggio Acquiring & E-commerce per il Team Retail")

# -----------------------------------------------------------------------------
# FUNZIONE DI PULIZIA DEI NUMERI EXCEL
# -----------------------------------------------------------------------------
def clean_numeric_col(series):
    # Rimuove simboli, spazi e sistema la formattazione italiana (punti come migliaia, virgole come decimali)
    s = series.astype(str).str.replace('€', '', regex=False)
    s = s.str.replace(r'\s+', '', regex=True)
    # Se contiene sia punto che virgola (es. 1.200,00) o solo virgola (1200,00)
    s = s.str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    return pd.to_numeric(s, errors='coerce').fillna(0)

# -----------------------------------------------------------------------------
# CARICAMENTO DATI
# -----------------------------------------------------------------------------
@st.cache_data
def load_real_data_optimized():
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if not files:
        return None, None, None, "Nessun file .xlsx trovato."
    
    file_path = files[0]
    try:
        # Carichiamo i fogli mantenendo i tipi nativi per l'elaborazione numerica
        df_p = pd.read_excel(file_path, sheet_name="PIPELINE", engine='openpyxl')
        df_t = pd.read_excel(file_path, sheet_name="CB + DBS IR", engine='openpyxl')
        df_s = pd.read_excel(file_path, sheet_name="SOW 2025", engine='openpyxl')
        return df_p, df_t, df_s, file_path
    except Exception as e:
        return None, None, None, str(e)

df_pipeline_raw, df_team_raw, df_sow_raw, detected_file = load_real_data_optimized()

if df_pipeline_raw is None:
    st.error(f"⚠️ Errore di caricamento: {detected_file}")
    st.stop()

# -----------------------------------------------------------------------------
# PRE-ELABORAZIONE E ALLINEAMENTO DATI (INDISTRUTTIBILE)
# -----------------------------------------------------------------------------
df_pipeline = df_pipeline_raw.copy()
df_pipeline.columns = [str(c).strip() for c in df_pipeline.columns]

# Mappatura colonne core
col_account = next((c for c in df_pipeline.columns if c.upper() in ['ACCOUNT', 'COMMERCIALE']), 'Account')
col_status = next((c for c in df_pipeline.columns if c.upper() in ['STATUS', 'STATO']), 'STATUS')
col_ricavi = next((c for c in df_pipeline.columns if c.upper() in ['RICAVI', 'VALORE']), 'RICAVI')
col_merchant = next((c for c in df_pipeline.columns if c.upper() in ['MERCHANT', 'CLIENTE']), 'Merchant')
col_categoria = next((c for c in df_pipeline.columns if c.upper() in ['CATEGORIA', 'CATEGORIA DEAL', 'PRODOTTO']), 'CATEGORIA DEAL')

# Forza la pulizia numerica della colonna ricavi per evitare i numeri infiniti sporchi
if col_ricavi in df_pipeline.columns:
    df_pipeline[col_ricavi] = clean_numeric_col(df_pipeline[col_ricavi])
else:
    df_pipeline[col_ricavi] = 0.0

# -----------------------------------------------------------------------------
# BANDA DEI FILTRI ORIZZONTALI IN ALTO
# -----------------------------------------------------------------------------
st.markdown("### 🎛️ Filtri di Monitoraggio")
f_col1, f_col2 = st.columns(2)
df_filtered = df_pipeline.copy()

with f_col1:
    if col_account in df_pipeline.columns:
        commerciali = sorted([str(x) for x in df_pipeline[col_account].dropna().unique() if str(x).strip() != 'nan'])
        acc_sel = st.multiselect("Filtra per Account Team:", options=commerciali, default=commerciali)
        if acc_sel:
            df_filtered = df_filtered[df_filtered[col_account].isin(acc_sel)]

with f_col2:
    if col_status in df_pipeline.columns:
        stati = sorted([str(x) for x in df_pipeline[col_status].dropna().unique() if str(x).strip() != 'nan'])
        st_sel = st.multiselect("Filtra per Stato del Deal:", options=stati, default=stati)
        if st_sel:
            df_filtered = df_filtered[df_filtered[col_status].isin(st_sel)]

st.markdown("---")

# -----------------------------------------------------------------------------
# NAVIGAZIONE INTERNA (TABS)
# -----------------------------------------------------------------------------
tabs = st.tabs([
    "🎯 Database Pipeline",
    "📈 Dashboard Grafica", 
    "👤 Focus Personale", 
    "👥 Performance Budget Team", 
    "🦅 Share of Wallet (SOW)"
])

# =============================================================================
# TAB 1: DATABASE PIPELINE (+ SINTESI AGGREGATA)
# =============================================================================
with tabs[0]:
    st.header("Database & Avanzamento Pipeline")
    
    # Dati di sintesi aggregata richiesti
    s1, s2, s3 = st.columns(3)
    with s1:
        st.metric("Valore Pipeline Selezionata", f"€ {df_filtered[col_ricavi].sum():,.2f}")
    with s2:
        st.metric("Deal in Pancia", len(df_filtered))
    with s3:
        win_rate = (len(df_filtered[df_filtered[col_status].str.upper() == 'WIN']) / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
        st.metric("Percentuale Deal Chiusi (WIN)", f"{win_rate:.1f}%")
        
    st.markdown("#### Lista Dati Estratti")
    st.dataframe(df_filtered, use_container_width=True)

# =============================================================================
# TAB 2: DASHBOARD GRAFICA (CORRETTA)
# =============================================================================
with tabs[1]:
    st.header("Analisi Macro ed Economica Retail 2026")
    
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.metric("Valore Corretto Pipeline Filtrata", f"€ {df_filtered[col_ricavi].sum():,.2f}")
    with d_col2:
        st.metric("Numero totale Deal", len(df_filtered))
        
    st.markdown("---")
    g1, g2 = st.columns(2)
    
    with g1:
        st.subheader("Valore Pipeline per Singolo Account")
        fig_acc = px.bar(df_filtered, x=col_account, y=col_ricavi, color=col_status, barmode="stack", text_auto='.2s')
        st.plotly_chart(fig_acc, use_container_width=True)
        
    with g2:
        st.subheader("Concentrazione Ricavi per Stato Trattativa")
        fig_pie = px.pie(df_filtered, values=col_ricavi, names=col_status, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    if col_categoria in df_filtered.columns:
        st.markdown("---")
        st.subheader("Sintesi per Tipologia/Categoria di Prodotto")
        fig_cat = px.bar(df_filtered, x=col_categoria, y=col_ricavi, color=col_status, barmode="group")
        st.plotly_chart(fig_cat, use_container_width=True)

# =============================================================================
# TAB 3: FOCUS PERSONALE
# =============================================================================
with tabs[2]:
    st.header("Area Personale Commerciale")
    
    commerciali_list = sorted([str(x) for x in df_pipeline[col_account].dropna().unique() if str(x).strip() != 'nan'])
    default_idx = commercials_list.index("Tomarchio") if "Tomarchio" in commercials_list else 0
    utente = st.selectbox("Seleziona il profilo commerciale da analizzare:", options=commerciali_list, index=default_idx)
    
    df_singolo = df_pipeline[df_pipeline[col_account] == utente].copy()
    
    # Sintesi numerica personale
    p1, p2, p3 = st.columns(3)
    val_win = df_singolo[df_singolo[col_status].str.upper() == 'WIN'][col_ricavi].sum()
    val_wip = df_singolo[df_singolo[col_status].str.upper() == 'WIP'][col_ricavi].sum()
    
    with p1:
        st.metric("I tuoi Deal Chiusi (WIN)", f"€ {val_win:,.2f}")
    with p2:
        st.metric("Il tuo Portafoglio in Lavorazione (WIP)", f"€ {val_wip:,.2f}")
    with p3:
        st.metric("Numero Deal Totali in Gestione", len(df_singolo))
        
    st.markdown("---")
    
    f_g1, f_g2 = st.columns([2, 1])
    with f_g1:
        st.markdown(f"#### Elenco dei Deal Attivi - {utente}")
        st.dataframe(df_singolo, use_container_width=True)
    with f_g2:
        st.markdown("#### Ripartizione Stato")
        fig_pers_pie = px.pie(df_singolo, values=col_ricavi, names=col_status)
        st.plotly_chart(fig_pers_pie, use_container_width=True)

# =============================================================================
# TAB 4: PERFORMANCE BUDGET TEAM (CB + DBS IR - CON SINTESI GRAFICA)
# =============================================================================
with tabs[3]:
    st.header("Quadro Sintetico Budget & Target (CB + DBS IR)")
    
    if df_team_raw is not None and not df_team_raw.empty:
        # Mostriamo prima il foglio completo per controllo
        with st.expander("Visualizza Foglio Budget Excel Integrale"):
            st.dataframe(df_team_raw, use_container_width=True)
            
        st.markdown("#### 📊 Sintesi Grafica Budget Estratta")
        # Proviamo a ripulire i dati del budget in modo dinamico per fare un grafico
        df_t_clean = df_team_raw.copy()
        df_t_clean.columns = [str(c).strip() for c in df_t_clean.columns]
        
        # Cerchiamo se ci sono righe associate ai commerciali del team retail
        nomi_commerciali = ['Dalla Torre', 'Mariani', 'Tomarchio', 'Luzzio']
        
        # Rendiamo tutto stringa per la ricerca
        df_t_clean = df_t_clean.astype(str)
        # Filtriamo le righe che contengono i cognomi del team
        df_team_filtered = df_t_clean[df_t_clean.astype(str).apply(lambda x: x.str.contains('|'.join(nomi_commerciali))).any(axis=1)].copy()
        
        if not df_team_filtered.empty:
            st.dataframe(df_team_filtered, use_container_width=True)
        else:
            st.info("Per visualizzare i grafici di budget personalizzati, assicurati che i cognomi (Tomarchio, Mariani, ecc.) siano scritti chiaramente nelle celle del foglio Excel.")
    else:
        st.warning("Il foglio 'CB + DBS IR' non contiene dati analizzabili.")

# =============================================================================
# TAB 5: SHARE OF WALLET (SOW - VISUALIZZAZIONE OTTIMIZZATA)
# =============================================================================
with tabs[4]:
    st.header("Analisi Posizionamento Competitivo (SOW 2025)")
    
    if df_sow_raw is not None and not df_sow_raw.empty:
        df_sow = df_sow_raw.copy()
        df_sow.columns = [str(c).strip() for c in df_sow.columns]
        
        col_merchant_sow = next((c for c in df_sow.columns if c.upper() in ['LAKA', 'MERCHANT', 'CLIENTE']), None)
        col_nexi_sow = next((c for c in df_sow.columns if 'NEXI' in c.upper()), None)
        
        # Pulizia numerica delle colonne quote
        if col_nexi_sow:
            df_sow['SOW NEXI CLEAN'] = clean_numeric_col(df_sow[col_nexi_sow])
            
        st.markdown("#### 📈 Grafico di Sintesi: Presidio Quota Nexi sui Clienti")
        if col_merchant_sow and col_nexi_sow:
            # Prendiamo i primi 15 merchant per importanza per non appesantire il grafico
            df_sow_chart = df_sow.head(15)
            fig_sow = px.bar(df_sow_chart, x=col_merchant_sow, y='SOW NEXI CLEAN', title="Quota di Mercato Nexi (%) sui Top 15 Account", text_auto=True)
            st.plotly_chart(fig_sow, use_container_width=True)
            
        st.markdown("#### 📄 Tabella Analitica Completa Share of Wallet")
        st.dataframe(df_sow, use_container_width=True)
    else:
        st.warning("Il foglio 'SOW 2025' risulta vuoto o non configurato.")
