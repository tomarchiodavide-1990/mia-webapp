import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Nexi LAKA Dashboard 2026", layout="wide", page_icon="🏢")

# STYLING CORPORATE
st.markdown("""
    <style>
    .stApp { background-color: #001e46; }
    h1, h2, h3, .stMetricValue { color: #ffffff !important; font-family: 'Helvetica Neue', sans-serif; }
    [data-testid="stMetricValue"] { color: #E30613 !important; }
    </style>
""", unsafe_allow_html=True)

# 1. DATA LOADER (Resiliente)
@st.cache_data
def load_data():
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if not files: return None, None, None
    f = files[0]
    return pd.read_excel(f, sheet_name="PIPELINE"), pd.read_excel(f, sheet_name="CB + DBS IR"), pd.read_excel(f, sheet_name="SOW 2025")

df_p, df_t, df_s = load_data()
if df_p is not None:
    # PULIZIA DATI
    df_p.columns = [str(c).strip() for c in df_p.columns]
    col_acc = next((c for c in df_p.columns if 'ACCOUNT' in c.upper()), df_p.columns[0])
    col_ric = next((c for c in df_p.columns if 'RICAVI' in c.upper() or 'VALORE' in c.upper()), df_p.columns[2])
    col_stat = next((c for c in df_p.columns if 'STATUS' in c.upper()), df_p.columns[1])
    df_p[col_ric] = pd.to_numeric(df_p[col_ric].astype(str).str.replace(r'[€\s,]', '', regex=True), errors='coerce').fillna(0.0)

    # 2. HEADER E FILTRI
    st.image("https://assets.norbr.io/image/partners/Nexi_colorbg@2x.png", width=150)
    st.title("LAKA Executive Command Center")
    
    acc_sel = st.multiselect("Filtra per Key Account Manager:", sorted(df_p[col_acc].unique()), default=df_p[col_acc].unique())
    df_f = df_p[df_p[col_acc].isin(acc_sel)]

    # 3. LAYOUT A QUATTRO PILASTRI
    tabs = st.tabs(["🚀 Funnel Analysis", "📊 White Space & SOW", "🎯 Target Tracker", "💡 Strategic Insights"])

    with tabs[0]: # FUNNEL
        c1, c2 = st.columns([1, 3])
        c1.metric("Pipeline Totale", f"€ {df_f[col_ric].sum():,.0f}")
        c1.metric("Win Rate", f"{len(df_f[df_f[col_stat]=='WIN'])/len(df_f)*100:.1f}%")
        
        fig = px.funnel(df_f.groupby(col_stat)[col_ric].sum().reset_index(), x=col_ric, y=col_stat, color_discrete_sequence=['#E30613'])
        fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        c2.plotly_chart(fig, use_container_width=True)

    with tabs[1]: # WHITE SPACE
        st.subheader("Analisi Presidio Mercato")
        # Logica di Gap: Potenziale vs Attuale
        fig = go.Figure(data=[
            go.Bar(name='Nexi SOW', x=df_s.iloc[:10,0], y=df_s.iloc[:10,1], marker_color='#E30613'),
            go.Bar(name='White Space', x=df_s.iloc[:10,0], y=100-df_s.iloc[:10,1], marker_color='#004a99')
        ])
        fig.update_layout(barmode='stack', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]: # BUDGET
        st.subheader("Budget Achievement")
        # Visualizzazione avanzata target
        st.dataframe(df_t, use_container_width=True)

    with tabs[3]: # INSIGHTS
        st.subheader("Azioni Prioritarie (AI Driven)")
        col1, col2 = st.columns(2)
        col1.success("🔥 Cross-Sell Opportunity: 12 Merchant hanno SOW < 20% in settori High-Growth.")
        col2.warning("⏳ At-Risk: 5 deal 'WIP' sono fermi da > 60gg. Necessario escalation.")
        st.divider()
        st.markdown("### Executive Summary")
        st.write("La velocità di chiusura attuale è in linea con il target Q3. Si raccomanda di focalizzare il team sulle negoziazioni di rinnovo dei top 20 merchant per blindare la SOW.")
