import streamlit as st
import pandas as pd
import time
import random
from streamlit_autorefresh import st_autorefresh

# 1. SETUP
st.set_page_config(page_title="WAR ROOM PRO", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS (compatto)
st.markdown(
    """
<style>
.main .block-container { padding: 2px 5px !important; }
[data-testid="stVerticalBlock"] { gap: 0rem !important; }
.num-kart { font-size: 14px; font-weight: bold; margin: 0; line-height: 1.2; }
.tempo-text { font-size: 13px; font-weight: bold; color: white; margin: 0; text-align: right; }
.stButton>button {
    padding: 1px 4px !important;
    height: 24px !important;
    font-size: 11px !important;
    min-width: 100% !important;
}
.t-pro { color: #FF3131 !important; }
.t-semi { color: #1E90FF !important; }
.t-ama { color: #00FF7F !important; }
header, footer { visibility: hidden; }
</style>
""",
    unsafe_allow_html=True,
)

# 3. STATO DATI
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(
        {
            "KART": [f"{i+1:02d}" for i in range(50)],
            "TEAM": [f"T{i+1}" for i in range(50)],
            "CAT": ["NONE"] * 50,
            "STAR": [False] * 50,
            "ULTIMO": [0.0] * 50,
            "MEDIA": [0.0] * 50,
            "IN_PIT": [False] * 50,
            "LANE": ["VERDE"] * 50,
            "PIT_START": [0.0] * 50,
        }
    )

if "pista_nome" not in st.session_state:
    st.session_state.pista_nome = ""
if "best_lap_pista" not in st.session_state:
    st.session_state.best_lap_pista = 45.00
if "apex_url" not in st.session_state:
    st.session_state.apex_url = ""
if "sel_idx" not in st.session_state:
    st.session_state.sel_idx = 0

# --- SIDEBAR (CONFIGURAZIONE PISTE + BEST LAP + APEX) ---
with st.sidebar:
    st.header("🏁 GESTIONE PISTA")
    st.session_state.pista_nome = st.text_input(
        "NOME PISTA", st.session_state.pista_nome,
