import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIGURAZIONE E LAYOUT ---
st.set_page_config(page_title="WAR ROOM ENDURANCE - ULTIMATE", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CSS PROFESSIONALE (LINEE SOTTILI, TOUCH GIGANTE, COLORI CORSIE) ---
st.markdown("""
    <style>
    .main .block-container { padding: 0px !important; background-color: #111; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    /* GRIGLIA STILE EXCEL (Linee sottili e pulite) */
    .grid-row { 
        display: flex; 
        border-bottom: 1px solid #333; 
        align-items: center; 
        min-height: 65px; 
        background-color: #000; 
    }
    .grid-cell { 
        border-right: 1px solid #333; 
        padding: 0px 15px; 
        height: 100%; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
    }
    
    /* TESTO E ICONE */
    .big-num { font-size: 30px !important; font-weight: 800 !important; color: #FFF; }
    .team-text { font-size: 20px !important; font-weight: bold; color: #EEE; }

    /* BOTTONI BOX - OTTIMIZZAZIONE TOUCH (Distanziati e Grandi) */
    .stButton>button {
        border-radius: 12px !important;
        padding: 25px 5px !important;
        font-size: 22px !important;
        font-weight: bold !important;
        width: 100% !important;
        margin-bottom: 15px !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.6);
    }
    
    /* BORDURA CORSIE BOX DINAMICHE */
    .btn-verde > div > button { border: 5px solid #28a745 !important; background-color: #0a2b12 !important; }
    .btn-rossa > div > button { border: 5px solid #dc3545 !important; background-color: #2b0a0a !important; }
    .btn-gialla > div > button { border: 5px solid #ffc107 !important; background-color: #332b00 !important; color: #ffc107 !important; }
    .btn-blu > div > button { border: 5px solid #007bff !important; background-color: #001a33 !important; }

    /* TABS E SIDEBAR */
    header, footer { visibility: hidden; }
    .stTabs [data-baseweb="tab-list"] { background-color: #000; padding: 15px; border-bottom: 2px solid #444; gap: 20px; }
    .stTabs [data-baseweb="tab"] { height: 60px; font-size: 22px !important; font-weight: bold !important; }
    .streamlit-expanderHeader { background-color: #222 !important; font-size: 18px !
