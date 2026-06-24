import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. CONFIGURAZIONE TEMA NEXI
st.set_page_config(page_title="Retail Pipeline Master Platform 2026", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background-color: #001e46; color: #ffffff; }
    h1, h2, h3, h4, p, div, label { color: #ffffff !important; }
    [data-testid="stMetricValue"] { color: #E30613 !important; }
    .stDataFrame { border: 1px solid #004a99; }
    </style>
""", unsafe_allow_html=True)

NEXI_COLORS = ['#E30613', '#1D1D1B', '#555555', '#8A8A8A', '#CCCCCC']

# 2. HEADER
c1, c2 = st.columns([1, 4])
with c1: st.image("https://assets.norbr.io/image/partners/Nexi_colorbg@2x.png", width=180)
with c2: st.markdown("# Retail & Luxury | Pipeline Master Platform 2026")
st.markdown("---")

# 3. LOGICA DATI
def clean_numeric(s):
    return pd.to_numeric(s.astype(str).str.replace(r'[€\s]', '', regex=True).str.replace(',', '.'), errors='coerce').fillna(0.0)

@st.cache_data
def load_data():
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if not files: return None, None, None
    f = files[0]
    return pd.read_excel(f, sheet_name="PIPELINE"), pd.read_excel(f, sheet_name="CB + DBS IR"), pd.read_excel(f, sheet_name="SOW 2025")

df_p, df_t, df_s = load_data()

if df_p is not None:
    # Preparazione Pipeline
    df_p.columns = [str(c).strip() for c in df_p.columns]
    col_acc = next((c for c in df_p.columns if 'ACCOUNT' in c.upper() or 'SALES' in c.upper()), df_p.columns[0])
    col_ric = next((c for c in df_p.columns if 'RICAVI' in c.upper() or 'VALORE' in c.upper()), df_p.columns[2])
    col_status = next((c for c in df_p.columns if 'STATUS' in c.upper() or 'STATO' in c.upper()), df_p.columns[1])
    df_p[col_ric] = clean_numeric(df_p[col_ric])

    # Filtri in alto
    acc_list = sorted([str(x) for x in df_p[col_acc].dropna().unique()])
    acc_sel = st.multiselect("Filtra per Account Team:", acc_list, default=acc_list)
    df_f = df_p[df_p[col_acc].isin(acc_sel)]

    # 4. TABS
    tabs = st.tabs(["🎯 Pipeline", "📈 Retail vs Resto", "👥 Budget", "🦅 SOW"])

    with tabs[0]: # PIPELINE
        m1, m2, m3 = st.columns(3)
        m1.metric("Valore Totale", f"€ {df_f[col_ric].sum():,.0f}")
        m2.metric("Deal Attivi", len(df_f))
        m3.metric("Ticket Medio", f"€ {df_f[col_ric].mean():,.0f}")
        st.dataframe(df_f, use_container_width=True)

    with tabs[1]: # RETAIL VS RESTO
        df_f['Categoria'] = df_f[col_acc].apply(lambda x: 'Retail Team' if x in acc_sel else 'Resto del Mondo')
        fig = px.pie(df_f, values=col_ric, names='Categoria', color='Categoria', 
                     color_discrete_sequence=['#E30613', '#004a99'], template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]: # BUDGET
        for i in range(10):
            if df_t.iloc[i].astype(str).str.contains('Target|Budget|Commerciale', case=False).any():
                df_t.columns = df_t.iloc[i]
                df_t = df_t[i+1:].reset_index(drop=True)
                break
        df_t = df_t.loc[:, ~df_t.columns.astype(str).str.contains('^Unnamed')]
        st.dataframe(df_t, use_container_width=True)

    with tabs[3]: # SOW
        col_n = next((c for c in df_s.columns if 'NEXI' in c.upper()), df_s.columns[-1])
        st.metric("SOW Medio Nexi", f"{clean_numeric(df_s[col_n]).mean():.2f}%")
        st.dataframe(df_s, use_container_width=True)
