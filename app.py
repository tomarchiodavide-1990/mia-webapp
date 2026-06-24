import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configurazione della pagina ad impatto Enterprise
st.set_page_config(page_title="Retail Pipeline Master Platform 2026", layout="wide", page_icon="🏢")

# Palette Colori Istituzionale Nexi per i Grafici
NEXI_COLORS = ['#E30613', '#1D1D1B', '#555555', '#8A8A8A', '#CCCCCC']

# -----------------------------------------------------------------------------
# LOGO UFFICIALE NEXI HD (VETTORIALE PRECISO) + TITOLO RETAIL & LUXURY
# -----------------------------------------------------------------------------
logo_col, title_col = st.columns([1, 4])

with logo_col:
    nexi_svg_hd = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 75" width="180" height="54">
        <g transform="translate(10,10)">
            <path d="M 0 0 L 45 0 L 45 45 L 0 45 Z" fill="#E30613"/>
            <path d="M 9 36 L 9 9 L 18 9 L 27 24 L 27 9 L 36 9 L 36 36 L 27 36 L 18 21 L 18 36 Z" fill="#FFFFFF"/>
            <path d="M 58 9 L 82 9 L 82 15 L 66 15 L 66 21 L 80 21 L 80 27 L 66 27 L 66 33 L 83 33 L 83 39 L 58 39 Z" fill="#1D1D1B"/>
            <path d="M 91 9 L 102 9 L 111 22 L 120 9 L 131 9 L 118 24 L 132 39 L 121 39 L 111 26 L 101 39 L 90 39 L 104 24 Z" fill="#1D1D1B"/>
            <path d="M 140 9 L 149 9 L 149 39 L 140 39 Z" fill="#1D1D1B"/>
        </g>
    </svg>
    """
    st.markdown(nexi_svg_hd, unsafe_allow_html=True)

with title_col:
    st.markdown(
        """
        <div style="padding-top: 2px;">
            <span style="font-size: 34px; font-weight: bold; color: #1e1e1e; font-family: 'Helvetica Neue', sans-serif;">
                Retail & Luxury
            </span>
            <br>
            <span style="font-size: 14px; color: #555555; font-family: sans-serif; letter-spacing: 0.5px;">
                RETAIL PIPELINE MASTER PLATFORM 2026 | Centro Direzionale Monitoraggio Acquiring & E-commerce
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# FUNZIONE DI PULIZIA NUMERICA RESTRITTIVA
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
# CARICAMENTO DATI EXCEL
# -----------------------------------------------------------------------------
@st.cache_data
def load_real_data_optimized():
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if not files:
        return None, None, None, "Nessun file .xlsx trovato nella directory."
    
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
    st.error(f"⚠️ Errore critico nel caricamento dell'Excel: {detected_file}")
    st.stop()

# Mapping dinamico colonne pipeline
df_pipeline = df_pipeline_raw.copy()
df_pipeline.columns = [str(c).strip() for c in df_pipeline.columns]

col_account = next((c for c in df_pipeline.columns if c.upper() in ['ACCOUNT', 'COMMERCIALE', 'SALES']), 'Account')
col_status = next((c for c in df_pipeline.columns if c.upper() in ['STATUS', 'STATO']), 'STATUS')
col_ricavi = next((c for c in df_pipeline.columns if c.upper() in ['RICAVI', 'VALORE', 'REVENUE']), 'RICAVI')
col_merchant = next((c for c in df_pipeline.columns if c.upper() in ['MERCHANT', 'CLIENTE', 'RAGIONE SOCIALE']), 'Merchant')
col_categoria = next((c for c in df_pipeline.columns if c.upper() in ['CATEGORIA', 'CATEGORIA DEAL', 'PRODOTTO', 'SOLUZIONE']), 'CATEGORIA DEAL')

if col_ricavi in df_pipeline.columns:
    df_pipeline[col_ricavi] = clean_numeric_col_final(df_pipeline[col_ricavi])
else:
    df_pipeline[col_ricavi] = 0.0

# =============================================================================
# 🎛️ BARRA LATERALE AZIENDALE (SIDEBAR) PER I FILTRI
# =============================================================================
with st.sidebar:
    st.markdown("### 🏢 Filtri Globali Platform")
    st.markdown("Usa i selettori sotto per aggiornare istantaneamente tutte le metriche e le tabelle del team.")
    st.markdown("---")
    
    df_filtered = df_pipeline.copy()
    
    if col_account in df_pipeline.columns:
        commerciali = sorted([str(x).strip() for x in df_pipeline[col_account].dropna().unique() if str(x).strip() not in ['nan', '']])
        acc_sel = st.multiselect("👤 Seleziona Account Team:", options=commerciali, default=commerciali)
        if acc_sel:
            df_filtered = df_filtered[df_filtered[col_account].isin(acc_sel)]
            
    st.markdown(" ")
    if col_status in df_pipeline.columns:
        stati = sorted([str(x).strip() for x in df_pipeline[col_status].dropna().unique() if str(x).strip() not in ['nan', '']])
        st_sel = st.multiselect("🎯 Seleziona Stato Deal:", options=stati, default=stati)
        if st_sel:
            df_filtered = df_filtered[df_filtered[col_status].isin(st_sel)]
            
    st.markdown("---")
    st.caption(f"File Dati Attivo:\n`{detected_file}`")

# -----------------------------------------------------------------------------
# STRUTTURA A TAB INTERNE
# -----------------------------------------------------------------------------
tabs = st.tabs([
    "🎯 Database Pipeline",
    "📈 Dashboard Grafica", 
    "👤 Focus Personale", 
    "👥 Performance Budget Team", 
    "🦅 Share of Wallet (SOW)"
])

# =============================================================================
# TAB 1: DATABASE PIPELINE (CON FUNZIONE DOWNLOAD ESTERNA)
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
    
    # Pulsante Export in CSV/Excel per l'utente Business
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Esporta questa selezione di dati (CSV)",
        data=csv_data,
        file_name="pipeline_filtrata_retail_nexi.csv",
        mime="text/csv"
    )

# =============================================================================
# TAB 2: DASHBOARD GRAFICA (COLORI NEXI ISTITUZIONALI)
# =============================================================================
with tabs[1]:
    st.header("Analisi Macro ed Economica Retail 2026")
    g1, g2 = st.columns(2)
    
    with g1:
        st.subheader("Valore Pipeline per Singolo Account")
        fig_acc = px.bar(df_filtered, x=col_account, y=col_ricavi, color=col_status, 
                         barmode="stack", text_auto='.2s',
                         color_discrete_sequence=NEXI_COLORS)
        fig_acc.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_acc, use_container_width=True)
        
    with g2:
        st.subheader("Concentrazione Ricavi per Stato Trattativa")
        fig_pie = px.pie(df_filtered, values=col_ricavi, names=col_status, hole=0.4,
                         color_discrete_sequence=NEXI_COLORS)
        st.plotly_chart(fig_pie, use_container_width=True)

# =============================================================================
# TAB 3: FOCUS PERSONALE
# =============================================================================
with tabs[2]:
    st.header("Area Personale Commerciale")
    if col_account in df_pipeline.columns:
        commerciali_list = sorted([str(x).strip() for x in df_pipeline[col_account].dropna().unique() if str(x).strip() not in ['nan', '']])
        default_idx =Box = commerciali_list.index("Tomarchio") if "Tomarchio" in commerciali_list else 0
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
        st.dataframe(df_singolo, use_container_width=True)

# =============================================================================
# TAB 4: PERFORMANCE BUDGET TEAM
# =============================================================================
with tabs[3]:
    st.header("Quadro Sintetico Budget & Target (CB + DBS IR)")
    
    if df_team_raw is not None and not df_team_raw.empty:
        df_t_clean = df_team_raw.copy()
        
        if df_t_clean.iloc[0].astype(str).str.contains('Target|Commerciale|Budget|Dalla', case=False, na=False).any():
            df_t_clean.columns = df_t_clean.iloc[0].astype(str)
            df_t_clean = df_t_clean[1:].reset_index(drop=True)
        elif df_t_clean.iloc[1].astype(str).str.contains('Target|Commerciale|Budget|Dalla', case=False, na=False).any():
            df_t_clean.columns = df_t_clean.iloc[1].astype(str)
            df_t_clean = df_t_clean[2:].reset_index(drop=True)
            
        df_t_clean.columns = [str(c).strip() for c in df_t_clean.columns]
        
        nomi_commerciali = ['Dalla Torre', 'Mariani', 'Tomarchio', 'Luzzio']
        df_team_filtered = df_t_clean[df_t_clean.astype(str).apply(lambda x: x.str.contains('|'.join(nomi_commerciali), case=False)).any(axis=1)].copy()
        
        st.markdown("#### 📊 Tabella Target Ricostruita con Intestazioni Corrette")
        if not df_team_filtered.empty:
            st.dataframe(df_team_filtered, use_container_width=True)
        else:
            st.dataframe(df_t_clean.head(15), use_container_width=True)
            
        with st.expander("Visualizza Foglio Budget Integrale Grezzo"):
            st.dataframe(df_team_raw, use_container_width=True)

# =============================================================================
# TAB 5: SHARE OF WALLET (SOW) - PROFILATO SUL TEAM RETAIL (COLORI NEXI)
# =============================================================================
with tabs[4]:
    st.header("Analisi Posizionamento Competitivo (SOW 2025) - Focus Retail Team")
    
    if df_sow_raw is not None and not df_sow_raw.empty:
        df_sow = df_sow_raw.copy()
        df_sow.columns = [str(c).strip() for c in df_sow.columns]
        
        col_merchant_sow = next((c for c in df_sow.columns if c.upper() in ['LAKA', 'MERCHANT', 'CLIENTE', 'RAGIONE SOCIALE']), df_sow.columns[0])
        col_nexi_sow = next((c for c in df_sow.columns if 'NEXI' in c.upper()), None)
        
        if col_nexi_sow:
            df_sow['SOW NEXI (%)'] = clean_numeric_col_final(df_sow[col_nexi_sow])
            
            # Filtro esclusivo clienti attivi o assegnati al team
            if col_merchant in df_pipeline.columns:
                clienti_retail_pipeline = set(df_pipeline[col_merchant].dropna().astype(str).str.strip().str.upper().unique())
                df_sow['Is_Retail_Team'] = df_sow[col_merchant_sow].astype(str).str.strip().str.upper().apply(lambda x: any(c in x for c in clienti_retail_pipeline))
                df_sow_retail = df_sow[df_sow['Is_Retail_Team'] == True].copy()
            else:
                df_sow_retail = df_sow.head(20).copy()
            
            sow_c1, sow_c2 = st.columns([2, 1])
            
            with sow_c1:
                st.markdown(f"#### 🎯 Quota di Mercato Nexi (%) sui Clienti Assegnati al Nostro Team (N. {len(df_sow_retail)})")
                if not df_sow_retail.empty:
                    fig_sow_bar = px.bar(df_sow_retail.head(15), x=col_merchant_sow, y='SOW NEXI (%)', 
                                         color='SOW NEXI (%)', color_continuous_scale="Reds", text_auto=True)
                    st.plotly_chart(fig_sow_bar, use_container_width=True)
                else:
                    st.info("Nessuna corrispondenza esatta automatica. Visualizzazione dei record principali:")
                    fig_sow_bar = px.bar(df_sow.head(15), x=col_merchant_sow, y='SOW NEXI (%)', text_auto=True)
                    st.plotly_chart(fig_sow_bar, use_container_width=True)
                    
            with sow_c2:
                st.markdown("#### 🦅 Presidio Nexi del Team vs Competitor")
                quota_media_team = df_sow_retail['SOW NEXI (%)'].mean() if not df_sow_retail.empty else df_sow['SOW NEXI (%)'].mean()
                if quota_media_team > 100: 
                    quota_media_team = quota_media_team / 100 if quota_media_team <= 10000 else 50.0
                
                quota_competitor = max(0.0, 100.0 - quota_media_team)
                fig_sow_pie = px.pie(names=['Quota Nexi Team', 'Quota Competitor'], values=[quota_media_team, quota_competitor], 
                                     color_discrete_sequence=['#E30613', '#777777'], hole=0.5)
                st.plotly_chart(fig_sow_pie, use_container_width=True)
                
            st.markdown("#### 📄 Tabella Estratta Condivisa (Solo Clienti Assegnati a Noi)")
            colonne_da_mostrare = [col_merchant_sow, col_nexi_sow, 'SOW NEXI (%)']
            colonne_presenti = [c for c in colonne_da_mostrare if c in df_sow_retail.columns]
            st.dataframe(df_sow_retail[colonne_presenti] if not df_sow_retail.empty else df_sow[colonne_presenti].head(30), use_container_width=True)
    else:
        st.warning("Il foglio 'SOW 2025' risulta vuoto o non è stato configurato nel file Excel.")
