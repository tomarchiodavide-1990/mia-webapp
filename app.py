import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configurazione Pagina
st.set_page_config(page_title="Retail Pipeline Master Platform 2026", layout="wide", page_icon="🏢")

# Palette Colori Istituzionale Nexi
NEXI_COLORS = ['#E30613', '#1D1D1B', '#555555', '#8A8A8A', '#CCCCCC']

# -----------------------------------------------------------------------------
# LOGO E HEADER
# -----------------------------------------------------------------------------
logo_col, title_col = st.columns([1, 4])
with logo_col:
    st.markdown("""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 75" width="180" height="54">
        <g transform="translate(10,10)">
            <path d="M 0 0 L 45 0 L 45 45 L 0 45 Z" fill="#E30613"/>
            <path d="M 9 36 L 9 9 L 18 9 L 27 24 L 27 9 L 36 9 L 36 36 L 27 36 L 18 21 L 18 36 Z" fill="#FFFFFF"/>
            <path d="M 58 9 L 82 9 L 82 15 L 66 15 L 66 21 L 80 21 L 80 27 L 66 27 L 66 33 L 83 33 L 83 39 L 58 39 Z" fill="#1D1D1B"/>
            <path d="M 91 9 L 102 9 L 111 22 L 120 9 L 131 9 L 118 24 L 132 39 L 121 39 L 111 26 L 101 39 L 90 39 L 104 24 Z" fill="#1D1D1B"/>
            <path d="M 140 9 L 149 9 L 149 39 L 140 39 Z" fill="#1D1D1B"/>
        </g>
    </svg>
    """, unsafe_allow_html=True)

with title_col:
    st.markdown("""
        <div style="padding-top: 2px;">
            <span style="font-size: 34px; font-weight: bold; color: #1e1e1e; font-family: sans-serif;">Retail & Luxury</span>
            <br><span style="font-size: 14px; color: #555555; font-family: sans-serif;">RETAIL PIPELINE MASTER PLATFORM 2026 | Centro Direzionale Monitoraggio</span>
        </div>
    """, unsafe_allow_html=True)
st.markdown("---")

# -----------------------------------------------------------------------------
# FUNZIONI DI SERVIZIO
# -----------------------------------------------------------------------------
def clean_numeric(series):
    s = series.astype(str).str.replace('€', '', regex=False).str.replace(r'\s+', '', regex=True)
    return s.apply(lambda val: float(val.replace(',', '.')) if ',' in val else float(val) if str(val).replace('.','',1).isdigit() else 0.0).fillna(0.0)

@st.cache_data
def load_data():
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if not files: return None, None, None, "Nessun file trovato"
    try:
        df_p = pd.read_excel(files[0], sheet_name="PIPELINE")
        df_t = pd.read_excel(files[0], sheet_name="CB + DBS IR")
        df_s = pd.read_excel(files[0], sheet_name="SOW 2025")
        return df_p, df_t, df_s, files[0]
    except Exception as e: return None, None, None, str(e)

df_p_raw, df_t_raw, df_s_raw, file_name = load_data()
if df_p_raw is None: st.stop()

# -----------------------------------------------------------------------------
# LOGICA FILTRI SIDEBAR
# -----------------------------------------------------------------------------
df_p = df_p_raw.copy()
df_p.columns = [str(c).strip() for c in df_p.columns]
col_account = next((c for c in df_p.columns if c.upper() in ['ACCOUNT', 'COMMERCIALE', 'SALES']), df_p.columns[0])
col_status = next((c for c in df_p.columns if c.upper() in ['STATUS', 'STATO']), df_p.columns[1])
col_ricavi = next((c for c in df_p.columns if c.upper() in ['RICAVI', 'VALORE', 'REVENUE']), df_p.columns[2])
df_p[col_ricavi] = clean_numeric(df_p[col_ricavi])

with st.sidebar:
    st.header("🎛️ Filtri Globali")
    acc_list = sorted([str(x) for x in df_p[col_account].dropna().unique() if str(x) not in ['nan','']])
    acc_sel = st.multiselect("Account Team:", acc_list, default=acc_list)
    df_filtered =
