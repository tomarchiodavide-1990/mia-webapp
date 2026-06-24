import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configurazione Pagina
st.set_page_config(page_title="Retail Pipeline Master Platform 2026", layout="wide", page_icon="🏢")

# Palette Colori Istituzionale Nexi
NEXI_COLORS = ['#E30613', '#1D1D1B', '#555555', '#8A8A8A', '#CCCCCC']

# --- LOGO E HEADER ---
logo_col, title_col = st.columns([1, 4])
with logo_col:
    st.markdown("""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 75" width="180" height="54">
        <path d="M 0 0 L 45 0 L 45 45 L 0 45 Z" fill="#E30613"/>
        <path d="M 9 36 L 9 9 L 18 9 L 27 24 L 27 9 L 36 9 L 36 36 L 27 36 L 18 21 L 18 36 Z" fill="#FFFFFF"/>
        <path d="M 58 9 L 82 9 L 82 15 L 66 15 L 66 21 L 80 21 L 80 27 L 66 27 L 66 33 L 83 33 L 83 39 L 58 39 Z" fill="#1D1D1B"/>
        <path d="M 91 9 L 102 9 L 111 22 L 120 9 L 131 9 L 118 24 L 132 39 L 121 39 L 111 26 L 101 39 L 90 39 L 104 24 Z" fill="#1D1D1B"/>
        <path d="M 140 9 L 149 9 L 149 39 L 140 39 Z" fill="#1D1D1B"/>
    </svg>
    """, unsafe_allow_html=True)

with title_col:
    st.markdown("### Retail & Luxury | Pipeline Master Platform 2026")
st.markdown("---")

# --- FUNZIONI DI SERVIZIO ---
def clean_numeric(series):
    return pd.to_numeric(series.astype(str).str.replace(r'[€\s]', '', regex=True).str.replace(',', '.'), errors='coerce').fillna(0.0)

@st.cache_data
def load_data():
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if not files: return None, None, None
    df_p = pd.read_excel(files[0], sheet_name="PIPELINE")
    df_t = pd.read_excel(files[0], sheet_name="CB + DBS IR")
    df_s = pd.read_excel(files[0], sheet_name="SOW 2025")
    return df_p, df_t, df_s

df_p, df_t, df_s = load_data()

if df_p is not None:
    # Preparazione Pipeline
    df_p.columns = [str(c).strip() for c in df_p.columns]
    col_acc = next((c for c in df_p.columns if 'ACCOUNT' in c.upper() or 'SALES' in c.upper()), df_p.columns[0])
    col_ric = next((c for c in df_p.columns if 'RICAVI' in c.upper() or 'VALORE' in c.upper()), df_p.columns[2])
    df_p[col_ric] = clean_numeric(df_p[col_ric])

    # Sidebar
    with st.sidebar:
        st.header("🎛️ Filtri")
        acc_list = sorted([str(x) for x in df_p[col_acc].dropna().unique()])
        acc_sel = st.multiselect("Account Team:", acc_list, default=acc_list)
        df_f = df_p[df_p[col_acc].isin(acc_sel)]

    # Tabs
    tabs = st.tabs(["🎯 Pipeline", "📈 Dashboard", "👥 Budget", "🦅 SOW"])

    with tabs[0]:
        st.dataframe(df_f, use_container_width=True)

    with tabs[1]:
        st.plotly_chart(px.bar(df_f, x=col_acc, y=col_ric, color_discrete_sequence=NEXI_COLORS), use_container_width=True)

    with tabs[2]:
        df_t.columns = [str(c).strip() for c in df_t.columns]
        df_t = df_t.loc[:, ~df_t.columns.astype(str).str.contains('^Unnamed')]
        st.dataframe(df_t, use_container_width=True)

    with tabs[3]:
        st.dataframe(df_s, use_container_width=True)
else:
    st.error("File Excel non trovato o non leggibile.")
