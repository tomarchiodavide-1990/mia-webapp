import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Retail Pipeline Master Platform 2026", layout="wide", page_icon="🏢")

st.title("🏢 Retail Pipeline Master Platform 2026")
st.markdown("### Piattaforma Strategica di Monitoraggio Acquiring & E-commerce per il Team Retail")

# -----------------------------------------------------------------------------
# LETTURA SICURA DELL'EXCEL
# -----------------------------------------------------------------------------
@st.cache_data
def load_real_data_safe():
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if not files:
        return None, None, None, "Nessun file .xlsx trovato nella cartella"
    
    file_path = files[0]
    try:
        xls = pd.ExcelFile(file_path, engine='openpyxl')
        sheets = xls.sheet_names
        
        df_p = pd.read_excel(file_path, sheet_name="PIPELINE", engine='openpyxl') if "PIPELINE" in sheets else pd.read_excel(file_path, sheet_name=0, engine='openpyxl')
        df_t = pd.read_excel(file_path, sheet_name="CB + DBS IR", engine='openpyxl') if "CB + DBS IR" in sheets else pd.DataFrame()
        df_s = pd.read_excel(file_path, sheet_name="SOW 2025", engine='openpyxl') if "SOW 2025" in sheets else pd.DataFrame()
        
        return df_p, df_t, df_s, file_path
    except Exception as e:
        return None, None, None, str(e)

df_pipeline, df_team_raw, df_sow, status_msg = load_real_data_safe()

if df_pipeline is None:
    st.error(f"⚠️ Errore nel caricamento: {status_msg}")
    st.stop()

st.sidebar.success(f"📁 Collegato a: {status_msg}")

# -----------------------------------------------------------------------------
# TRATTAMENTO INDISTRUTTIBILE DEL FOGLIO BUDGET (CB + DBS IR)
# -----------------------------------------------------------------------------
df_team = pd.DataFrame()
if not df_team_raw.empty:
    try:
        nomi_team = ['Dalla Torre', 'Mariani', 'Tomarchio', 'Luzzio']
        riga_inizio = None
        colonna_nomi = None
        
        # Cerchiamo dove si trovano i commerciali nelle prime 20 righe
        for r in range(min(len(df_team_raw), 20)):
            for c in range(len(df_team_raw.columns)):
                valore = str(df_team_raw.iloc[r, c]).strip()
                if any(nome in valore for nome in nomi_team):
                    riga_inizio = r
                    colonna_nomi = c
                    break
            if riga_inizio is not None:
                break
                
        if riga_inizio is not None:
            # Recuperiamo le intestazioni di colonna
            intestazioni = df_team_raw.iloc[riga_inizio - 1].tolist()
            if all(pd.isna(x) for x in intestazioni) or riga_inizio == 0:
                intestazioni = df_team_raw.iloc[riga_inizio].tolist()
                
            df_pulito = df_team_raw.iloc[riga_inizio:].copy()
            df_pulito.columns = [str(h).strip() for h in intestazioni]
            
            col_target_name = df_pulito.columns[colonna_nomi]
            
            # Filtriamo solo i membri del team
            df_team = df_pulito[df_pulito[col_target_name].astype(str).str.contains('|'.join(nomi_team), na=False)].copy()
            df_team.rename(columns={col_target_name: "Commerciale"}, inplace=True)
            
            # CONVERSIONE NUMERICA BLINDATA COLONNA PER COLONNA (Risolve il TypeError)
            for col in df_team.columns:
                if col != "Commerciale":
                    df_team[col] = df_team[col].apply(pd.to_numeric, errors='coerce')
        else:
            df_team = df_team_raw.copy()
    except Exception as e:
        # Fallback totale se l'excel è formattato in modo imprevisto
        df_team = df_team_raw.copy()

# -----------------------------------------------------------------------------
# PULIZIA COLONNE PIPELINE
# -----------------------------------------------------------------------------
df_pipeline.columns = [str(c).strip() for c in df_pipeline.columns]
col_account = next((c for c in df_pipeline.columns if c.upper() == 'ACCOUNT'), None)
col_status = next((c for c in df_pipeline.columns if c.upper() == 'STATUS'), None)
col_ricavi = next((c for c in df_pipeline.columns if c.upper() == 'RICAVI'), None)

# Filtri barra laterale
st.sidebar.header("🎛️ Pannello di Controllo & Filtri")
df_filtered = df_pipeline.copy()

if col_account:
    commerciali = list(df_pipeline[col_account].dropna().unique())
    acc_sel = st.sidebar.multiselect("Visualizza Account Team:", options=commerciali, default=commerciali)
    if acc_sel:
        df_filtered = df_filtered[df_filtered[col_account].isin(acc_sel)]

if col_status:
    stati = list(df_pipeline[col_status].dropna().unique())
    st_sel = st.sidebar.multiselect("Stato del Deal:", options=stati, default=stati)
    if st_sel:
        df_filtered = df_filtered[df_filtered[col_status].isin(st_sel)]

#
