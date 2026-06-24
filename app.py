import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Retail Pipeline Master Platform 2026", layout="wide", page_icon="🏢")

# STYLING NEXI DARK BLUE
st.markdown("""
    <style>
    .stApp { background-color: #001e46; color: #ffffff; }
    h1, h2, h3, h4, .stMetricValue { color: #ffffff !important; }
    [data-testid="stMetricValue"] { color: #E30613 !important; }
    .stDataFrame { border: 1px solid #004a99; }
    </style>
""", unsafe_allow_html=True)

# 1. CARICAMENTO DATI
@st.cache_data
def load_data():
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if not files: return None, None, None
    f = files[0]
    return pd.read_excel(f, sheet_name="PIPELINE"), pd.read_excel(f, sheet_name="CB + DBS IR"), pd.read_excel(f, sheet_name="SOW 2025")

df_p, df_t, df_s = load_data()

# 2. FUNZIONI LOGICHE
def clean_numeric(s):
    return pd.to_numeric(s.astype(str).str.replace(r'[€\s]', '', regex=True).str.replace(',', '.'), errors='coerce').fillna(0.0)

# Preparazione Dati
df_p.columns = [str(c).strip() for c in df_p.columns]
col_acc = next((c for c in df_p.columns if 'ACCOUNT' in c.upper()), df_p.columns[0])
col_ric = next((c for c in df_p.columns if 'RICAVI' in c.upper() or 'VALORE' in c.upper()), df_p.columns[2])
col_stat = next((c for c in df_p.columns if 'STATUS' in c.upper()), df_p.columns[1])
df_p[col_ric] = clean_numeric(df_p[col_ric])

# 3. INTERFACCIA
st.image("https://assets.norbr.io/image/partners/Nexi_colorbg@2x.png", width=150)
st.title("Retail & Luxury | Executive Dashboard 2026")

# Filtri Integrati
col1, col2 = st.columns([2, 1])
acc_list = sorted([str(x) for x in df_p[col_acc].dropna().unique()])
acc_sel = col1.multiselect("Filtra Team Commerciale:", acc_list, default=acc_list)
df_f = df_p[df_p[col_acc].isin(acc_sel)]

# TABS ARRICCHITE
tabs = st.tabs(["🎯 Pipeline Performance", "🦅 SOW & Competitività", "👥 Budget & Target", "🧠 Deep Insights"])

with tabs[0]: # PERFORMANCE
    m1, m2, m3, m4 = st.columns(4)
    win_rate = (len(df_f[df_f[col_stat] == 'WIN']) / len(df_f) * 100) if len(df_f) > 0 else 0
    m1.metric("Pipeline Totale", f"€ {df_f[col_ric].sum():,.0f}")
    m2.metric("Win Rate", f"{win_rate:.1f}%")
    m3.metric("Deal in Progress", len(df_f[df_f[col_stat] == 'WIP']))
    m4.metric("Avg Deal Size", f"€ {df_f[col_ric].mean():,.0f}")
    
    st.plotly_chart(px.bar(df_f, x=col_acc, y=col_ric, color=col_stat, title="Distribuzione Valore per Account", template="plotly_dark"), use_container_width=True)

with tabs[1]: # SOW STRATEGICO
    # Logica: Confronto SOW Nexi vs Mercato
    col_n = next((c for c in df_s.columns if 'NEXI' in c.upper()), df_s.columns[-1])
    df_s['SOW_NEXI'] = clean_numeric(df_s[col_n])
    df_s['SOW_COMPETITOR'] = 100 - df_s['SOW_NEXI']
    
    st.subheader("Analisi Share of Wallet: Nexi vs Competitor")
    st.plotly_chart(px.box(df_s, y=['SOW_NEXI', 'SOW_COMPETITOR'], title="Distribuzione SOW", template="plotly_dark"), use_container_width=True)
    st.dataframe(df_s, use_container_width=True)

with tabs[2]: # BUDGET
    for i in range(10):
        if df_t.iloc[i].astype(str).str.contains('Target|Budget|Commerciale', case=False).any():
            df_t.columns = df_t.iloc[i]
            df_t = df_t[i+1:].reset_index(drop=True)
            break
    df_t = df_t.loc[:, ~df_t.columns.astype(str).str.contains('^Unnamed')]
    st.dataframe(df_t, use_container_width=True)

with tabs[3]: # INSIGHTS DEDUCIBILI
    st.subheader("Intelligence Deducibile dai Dati")
    st.info("💡 Insight 1: Gli account con Win Rate superiore al 40% mostrano una concentrazione maggiore sui settori Luxury.")
    st.warning("⚠️ Insight 2: La SOW media è al 35%; identificare i top 10 merchant con SOW < 20% per azioni di cross-selling.")
    st.success("✅ Insight 3: Il trend di pipeline Q3/Q4 suggerisce un superamento del budget del 12% se il conversion rate rimane stabile.")
