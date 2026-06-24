import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Retail Pipeline Master Platform 2026", layout="wide", page_icon="🏢")

# Palette Colori Istituzionale Nexi
NEXI_COLORS = ['#E30613', '#1D1D1B', '#555555', '#8A8A8A', '#CCCCCC']

# -----------------------------------------------------------------------------
# 1. HEADER CON LOGO UFFICIALE NEXI (URL)
# -----------------------------------------------------------------------------
logo_col, title_col = st.columns([1, 4])
with logo_col:
    st.image("https://assets.norbr.io/image/partners/Nexi_colorbg@2x.png", width=180)

with title_col:
    st.markdown("""
        <div style="padding-top: 15px;">
            <span style="font-size: 34px; font-weight: bold; color: #1e1e1e; font-family: sans-serif;">Retail & Luxury</span>
            <br><span style="font-size: 14px; color: #555555; font-family: sans-serif;">RETAIL PIPELINE MASTER PLATFORM 2026 | Gestione Performance & SOW</span>
        </div>
    """, unsafe_allow_html=True)
st.markdown("---")

# -----------------------------------------------------------------------------
# 2. LOGICA DATI
# -----------------------------------------------------------------------------
def clean_numeric(series):
    return pd.to_numeric(series.astype(str).str.replace(r'[€\s]', '', regex=True).str.replace(',', '.'), errors='coerce').fillna(0.0)

@st.cache_data
def load_data():
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if not files: return None, None, None, None
    f = files[0]
    return pd.read_excel(f, sheet_name="PIPELINE"), pd.read_excel(f, sheet_name="CB + DBS IR"), pd.read_excel(f, sheet_name="SOW 2025"), f

df_p_raw, df_t_raw, df_s_raw, f_name = load_data()
if df_p_raw is None: st.stop()

# Pipeline Setup
df_p = df_p_raw.copy()
df_p.columns = [str(c).strip() for c in df_p.columns]
col_acc = next((c for c in df_p.columns if 'ACCOUNT' in c.upper() or 'SALES' in c.upper()), df_p.columns[0])
col_status = next((c for c in df_p.columns if 'STATUS' in c.upper() or 'STATO' in c.upper()), df_p.columns[1])
col_ric = next((c for c in df_p.columns if 'RICAVI' in c.upper() or 'VALORE' in c.upper()), df_p.columns[2])
col_merch = next((c for c in df_p.columns if 'MERCHANT' in c.upper() or 'CLIENTE' in c.upper()), df_p.columns[3])
df_p[col_ric] = clean_numeric(df_p[col_ric])

# Sidebar Filters
with st.sidebar:
    st.header("🎛️ Filtri Globali")
    acc_list = sorted([str(x) for x in df_p[col_acc].dropna().unique()])
    acc_sel = st.multiselect("Account Team:", acc_list, default=acc_list)
    df_f = df_p[df_p[col_acc].isin(acc_sel)]

# -----------------------------------------------------------------------------
# 3. TABS
# -----------------------------------------------------------------------------
tabs = st.tabs(["🎯 Pipeline", "📈 Dashboard", "👥 Budget", "🦅 SOW"])

with tabs[0]:
    st.metric("Valore Totale", f"€ {df_f[col_ric].sum():,.0f}")
    st.dataframe(df_f, use_container_width=True)

with tabs[1]:
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(px.bar(df_f, x=col_acc, y=col_ric, color=col_status, color_discrete_sequence=NEXI_COLORS), use_container_width=True)
    with c2: st.plotly_chart(px.pie(df_f, values=col_ric, names=col_status, color_discrete_sequence=NEXI_COLORS, hole=0.4), use_container_width=True)

with tabs[2]:
    df_t = df_t_raw.copy()
    # Pulizia intelligente intestazioni
    for i in range(min(5, len(df_t))):
        if df_t.iloc[i].astype(str).str.contains('Target|Commerciale', case=False).any():
            df_t.columns = df_t.iloc[i]
            df_t = df_t[i+1:]
            break
    df_t = df_t.loc[:, ~df_t.columns.astype(str).str.contains('^Unnamed')]
    st.dataframe(df_t, use_container_width=True)

with tabs[3]:
    df_s = df_s_raw.copy()
    col_m = next((c for c in df_s.columns if 'MERCHANT' in c.upper() or 'CLIENTE' in c.upper()), df_s.columns[0])
    col_n = next((c for c in df_s.columns if 'NEXI' in c.upper()), df_s.columns[-1])
    
    # Filtro: solo merchant in pipeline
    clienti_ok = df_f[col_merch].astype(str).unique()
    df_s['Match'] = df_s[col_m].astype(str).apply(lambda x: any(c in x for c in clienti_ok))
    df_s_final = df_s[df_s['Match'] == True]
    
    st.subheader("SOW Clienti del Nostro Team")
    st.dataframe(df_s_final[[col_m, col_n]], use_container_width=True)
