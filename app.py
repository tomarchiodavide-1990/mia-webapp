import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Retail Pipeline Master Platform 2026", layout="wide", page_icon="🏢")

# -----------------------------------------------------------------------------
# INTESTAZIONE CON LOGO NEXI VETTORIALE (SVG INCORPORATO) E SCRITTA RETAIL & LUXURY
# -----------------------------------------------------------------------------
logo_col, title_col = st.columns([1, 4])

with logo_col:
    nexi_svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 80" width="160" height="53">
        <rect width="240" height="80" fill="transparent"/>
        <path d="M25 25h16.5l22 30V25h14v30h-16l-22.5-30.5V55H25V25z" fill="#E30613"/>
        <path d="M88 25h32v9H99v4h19v8H99v4h22v9H88V25z" fill="#1D1D1B"/>
        <path d="M126 25h15l10.5 14.5L162 25h15l-17.5 23.5L178 55h-15.5l-11-15.5L140.5 55H126l17.5-23.5L126 25z" fill="#1D1D1B"/>
        <path d="M184 25h14v30h-14V25z" fill="#1D1D1B"/>
    </svg>
    """
    st.markdown(nexi_svg, unsafe_allow_html=True)

with title_col:
    st.markdown(
        """
        <div style="padding-top: 5px;">
            <span style="font-size: 32px; font-weight: bold; color: #1e1e1e; font-family: sans-serif;">
                Retail & Luxury
            </span>
            <br>
            <span style="font-size: 15px; color: #666666; font-family: sans-serif;">
                Retail Pipeline Master Platform 2026 | Piattaforma Strategica di Monitoraggio Acquiring & E-commerce
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# FUNZIONE DI PULIZIA NUMERICA ULTRA RESTRITTIVA
# -----------------------------------------------------------------------------
def clean_numeric_col_final(series):
    s = series.astype(str).str.replace('€', '', regex=False)
    s = s.str.replace(r'\s+', '', regex=True)
    
    def convert_single_value(val):
        try:
            if ',' in val and '.' in val:
                val = val.replace('.', '').replace(',', '.')
            elif ',' in val:
                val = val.replace(',', '.')
            return float(val)
        except:
            return 0.0

    return s.apply(convert_single_value).fillna(0.0)

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
# ALLINEAMENTO DATI PIPELINE (RISOLTO NAMEERROR RIGA 96)
# -----------------------------------------------------------------------------
df_pipeline = df_pipeline_raw.copy()
df_pipeline.columns = [str(c).strip() for c in df_pipeline.columns]

col_account = next((c for c in df_pipeline.columns if c.upper() in ['ACCOUNT', 'COMMERCIALE', 'SALES']), 'Account')
col_status = next((c for c in df_pipeline.columns if c.upper() in ['STATUS', 'STATO']), 'STATUS')
col_ricavi = next((c for c in df_pipeline.columns if c.upper() in ['RICAVI', 'VALORE', 'REVENUE']), 'RICAVI')
col_merchant = next((c for c in df_pipeline.columns if c.upper() in ['MERCHANT', 'CLIENTE', 'RAGIONE SOCIALE']), 'Merchant')
col_categoria = next((c for c in df_pipeline.columns if c.upper() in ['CATEGORIA', 'CATEGORIA DEAL', 'PRODOTTO', 'SOLUZIONE', 'TIPO']), 'CATEGORIA DEAL')

if col_ricavi in df_pipeline.columns:
    df_pipeline[col_ricavi] = clean_numeric_col_final(df_pipeline[col_ricavi])
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
        commerciali = sorted([str(x).strip() for x in df_pipeline[col_account].dropna().unique() if str(x).strip() not in ['nan', '']])
        acc_sel = st.multiselect("Filtra per Account Team:", options=commerciali, default=commerciali)
        if acc_sel:
            df_filtered = df_filtered[df_filtered[col_account].isin(acc_sel)]

with f_col2:
    if col_status in df_pipeline.columns:
        stati = sorted([str(x).strip() for x in df_pipeline[col_status].dropna().unique() if str(x).strip() not in ['nan', '']])
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
# TAB 1: DATABASE PIPELINE
# =============================================================================
with tabs[0]:
    st.header("Database & Avanzamento Pipeline")
    
    s1, s2, s3 = st.columns(3)
    with s1:
        st.metric("Valore Pipeline Selezionata", f"€ {df_filtered[col_ricavi].sum():,.2f}")
    with s2:
        st.metric("Deal in Pancia", len(df_filtered))
    with s3:
        win_deals = len(df_filtered[df_filtered[col_status].astype(str).str.upper() == 'WIN'])
        win_rate = (win_deals / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
        st.metric("Percentuale Deal Chiusi (WIN)", f"{win_rate:.1f}%")
        
    st.markdown("#### Lista Dati Estratti")
    st.dataframe(df_filtered, use_container_width=True)

# =============================================================================
# TAB 2: DASHBOARD GRAFICA
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

    if col_categoria in df_filtered.columns and not df_filtered[col_categoria].dropna().empty:
        st.markdown("---")
        st.subheader("Sintesi per Tipologia/Categoria di Prodotto")
        fig_cat = px.bar(df_filtered, x=col_categoria, y=col_ricavi, color=col_status, barmode="group")
        st.plotly_chart(fig_cat, use_container_width=True)

# =============================================================================
# TAB 3: FOCUS PERSONALE
# =============================================================================
with tabs[2]:
    st.header("Area Personale Commerciale")
    
    if col_account in df_pipeline.columns:
        commerciali_list = sorted([str(x).strip() for x in df_pipeline[col_account].dropna().unique() if str(x).strip() not in ['nan', '']])
        default_idx = commerciali_list.index("Tomarchio") if "Tomarchio" in commerciali_list else 0
        
        utente = st.selectbox("Seleziona il profilo commerciale da analizzare:", options=commerciali_list, index=default_idx)
        
        df_singolo = df_pipeline[df_pipeline[col_account] == utente].copy()
        
        p1, p2, p3 = st.columns(3)
        val_win = df_singolo[df_singolo[col_status].astype(str).str.upper() == 'WIN'][col_ricavi].sum()
        val_wip = df_singolo[df_singolo[col_status].astype(str).str.upper() == 'WIP'][col_ricavi].sum()
        
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
# TAB 4: PERFORMANCE BUDGET TEAM
# =============================================================================
with tabs[3]:
    st.header("Quadro Sintetico Budget & Target (CB + DBS IR)")
    
    if df_team_raw is not None and not df_team_raw.empty:
        st.markdown("#### 📊 Dati di Sintesi Budget Commerciali")
        df_t_clean = df_team_raw.copy()
        df_t_clean.columns = [str(c).strip() for c in df_t_clean.columns]
        
        nomi_commerciali = ['Dalla Torre', 'Mariani', 'Tomarchio', 'Luzzio']
        df_team_filtered = df_t_clean[df_t_clean.astype(str).apply(lambda x: x.str.contains('|'.join(nomi_commerciali))).any(axis=1)].copy()
        
        if not df_team_filtered.empty:
            st.dataframe(df_team_filtered, use_container_width=True)
        else:
            st.info("Layout di budget complesso. Naviga l'intero foglio espandendo la sezione sotto:")
            
        with st.expander("Visualizza Foglio Budget Excel Integrale"):
            st.dataframe(df_team_raw, use_container_width=True)
    else:
        st.warning("Il foglio 'CB + DBS IR' non contiene dati o è vuoto.")

# =============================================================================
# TAB 5: SHARE OF WALLET (SOW)
# =============================================================================
with tabs[4]:
    st.header("Analisi Posizionamento Competitivo (SOW 2025)")
    
    if df_sow_raw is not None and not df_sow_raw.empty:
        df_sow = df_sow_raw.copy()
        df_sow.columns = [str(c).strip() for c in df_sow.columns]
        
        col_merchant_sow = next((c for c in df_sow.columns if c.upper() in ['LAKA', 'MERCHANT', 'CLIENTE']), df_sow.columns[0])
        col_nexi_sow = next((c for c in df_sow.columns if 'NEXI' in c.upper()), None)
        
        if col_nexi_sow:
            df_sow['SOW NEXI NUMERICA (%)'] = clean_numeric_col_final(df_sow[col_nexi_sow])
            
            st.markdown("#### 📈 Grafico di Sintesi: Presidio Quota Nexi sui Clienti")
            df_sow_chart = df_sow.dropna(subset=[col_merchant_sow]).head(15)
            fig_sow = px.bar(df_sow_chart, x=col_merchant_sow, y='SOW NEXI NUMERICA (%)', title="Quota di Mercato Nexi (%) sui Top 15 Clienti", text_auto=True)
            st.plotly_chart(fig_sow, use_container_width=True)
            
        st.markdown("#### 📄 Tabella Analitica Completa Share of Wallet")
        st.dataframe(df_sow, use_container_width=True)
    else:
        st.warning("Il foglio 'SOW 2025' risulta vuoto o non trovato.")
