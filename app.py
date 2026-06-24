import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Retail Pipeline Master Platform 2026", layout="wide", page_icon="🏢")

st.title("🏢 Retail Pipeline Master Platform 2026")
st.markdown("### Piattaforma Strategica di Monitoraggio Acquiring & E-commerce per il Team Retail")

# -----------------------------------------------------------------------------
# FUNZIONE DI PULIZIA NUMERICA ULTRA RESTRITTIVA (Risolve il valore troppo alto)
# -----------------------------------------------------------------------------
def clean_numeric_col_final(series):
    # Forza la conversione in testo, rimuove spazi, simboli € e gestisce i formati
    s = series.astype(str).str.replace('€', '', regex=False)
    s = s.str.replace(r'\s+', '', regex=True)
    
    # Se il dato è letto come float con formato scientifico (es. 1.2e+05) lo lasciamo convertire nativamente
    # Altrimenti, se è nel formato italiano "1.200,00", togliamo il punto e cambiamo la virgola in punto
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
# ALLINEAMENTO DATI PIPELINE
# -----------------------------------------------------------------------------
df_pipeline = df_pipeline_raw.copy()
df_pipeline.columns = [str(c).strip() for c in df_pipeline.columns]

col_account = next((c for c in df_pipeline.columns if c.upper() in ['ACCOUNT', 'COMMERCIALE']), 'Account')
col_status = next((c for c in df_pipeline.columns if c.upper() in ['STATUS', 'STATO']), 'STATUS')
col_ricavi = next((c for c in df_pipeline.columns if c.upper() in ['RICAVI', 'VALORE']), 'RICAVI')
col_merchant = next((c for c in df_pipeline.columns if c.upper() in ['MERCHANT', 'CLIENTE']), 'Merchant')
col_categoria = next((c for c in df_pipeline.columns if c.upper() in ['CATEGORIA', 'CATEGORIA DEAL', 'PRODOTTO']), 'CATEGORIA DEAL')

# Applica la pulizia restrittiva sui ricavi
if col_ricavi in df_pipeline.columns:
    df_pipeline[col_ricavi] = clean_numeric_col_final(df
