import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configurazione della pagina ad alta densità informativa
st.set_page_config(page_title="Retail Pipeline Master Platform 2026", layout="wide", page_icon="🏢")

st.title("🏢 Retail Pipeline Master Platform 2026")
st.markdown("### Piattaforma Strategica di Monitoraggio Acquiring & E-commerce per il Team Retail")

# -----------------------------------------------------------------------------
# CARICAMENTO COMPLETO E STRUTTURATO DEI DATI REALI (Dai tuoi Fogli Excel)
# -----------------------------------------------------------------------------
@st.cache_data
def load_full_market_data():
    # Database Unico della Pipeline Commerciale 2026 (Estratto dal foglio PIPELINE)
    pipeline_rows = [
        {"PRIORITA'": 1, "Merchant": "PRENATAL", "Account": "Tomarchio", "Nome Deal": "Repricing ISP", "STATUS": "WIP", "RICAVI": 215000, "KPI": "VOLUMI", "valore KPI": 430000000, "Categoria": "REPRICING", "Canale": "FISICO", "Banca": "ISP", "Scadenza": "2026-07-15", "Settore": "Puericultura", "Note": "Repricing da 2.5bps a 7bps (Artsana)"},
        {"PRIORITA'": 1, "Merchant": "PRENATAL", "Account": "Tomarchio", "Nome Deal": "DCC", "STATUS": "WIP", "RICAVI": 34400, "KPI": "VOLUMI", "valore KPI": 430000000, "Categoria": "REPRICING", "Canale": "FISICO", "Banca": "ISP", "Scadenza": "2026-07-15", "Settore": "Puericultura", "Note": "Margine extra su carte estere"},
        {"PRIORITA'": 2, "Merchant": "D.M.O. S.P.A", "Account": "Tomarchio", "Nome Deal": "CNP Beauty Star", "STATUS": "WIP", "RICAVI": 600, "KPI": "VOLUMI", "valore KPI": 1000000, "Categoria": "CAMPAGNA ECOMMERCE", "Canale": "ECOMMERCE", "Banca": "DIRETTA", "Scadenza": "2026-07-15", "Settore": "Pet shop / Beauty", "Note": "Fatta offerta if++6 + DCC, attesa riscontro"},
        {"PRIORITA'": 1, "Merchant": "ACQUA & SAPONE", "Account": "Tomarchio", "Nome Deal": "Svecchiamento POS '26 MPS", "STATUS": "WIP", "RICAVI": 0, "KPI": "RICAVI", "valore KPI": 0, "Categoria": "RINNOVO POS", "Canale": "FISICO", "Banca": "ISP", "Scadenza": "2026-07-10", "Settore": "Health & Beauty", "Note": "Bundle tender"},
        {"PRIORITA'": 1, "Merchant": "ACQUA & SAPONE", "Account": "Tomarchio", "Nome Deal": "Tender Card Present BPER", "STATUS": "WIP", "RICAVI": 1500, "KPI": "RICAVI", "valore KPI": 0, "Categoria": "RINNOVO POS", "Canale": "FISICO", "Banca": "BPER", "Scadenza": "2026-07-10", "Settore": "Health & Beauty", "Note": "Fatta proposta if++"},
        {"PRIORITA'": 3, "Merchant": "1000FARMACIE", "Account": "Mariani", "Nome Deal": "CNP + wallet", "STATUS": "WIP", "RICAVI": 12000, "KPI": "VOLUMI", "valore KPI": 5000000, "Categoria": "VOLUMI NO CAMPAGNA", "Canale": "ECOMMERCE", "Banca": "DIRETTA", "Scadenza": "2026-10-01", "Settore": "Pharmacy", "Note": "Scritto wp attesa risposta"},
        {"PRIORITA'": 1, "Merchant": "CISALFA", "Account": "Mariani", "Nome Deal": "Ecom Integration", "STATUS": "WIN", "RICAVI": 45000, "KPI": "VOLUMI", "valore KPI": 12000000, "Categoria": "CAMPAGNA ECOMMERCE", "Canale": "ECOMMERCE", "Banca": "DIRETTA", "Scadenza": "2026-05-20", "Settore": "Sport", "Note": "Chiuso e integrato"},
        {"PRIORITA'": 1, "Merchant": "DECATHLON ITALIA", "Account": "Dalla Torre", "Nome Deal": "SoftPOS rollout", "STATUS": "WIN", "RICAVI": 80000, "KPI": "RICAVI", "valore KPI": 80000, "Categoria": "SOFTPOS", "Canale": "FISICO", "Banca": "ISP", "Scadenza": "2026-04-15", "Settore": "Sport", "Note": "Attivati primi 150 terminali"},
        {"PRIORITA'": 2, "Merchant": "GRUPPO INDITEX - ZARA", "Account": "Tomarchio", "Nome Deal": "Gateway Ecom", "STATUS": "WIN", "RICAVI": 120000, "KPI": "VOLUMI", "valore KPI": 35000000, "Categoria": "
