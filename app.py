import streamlit as st
import pandas as pd

# Configurazione Pagina (Ottimizzata per Samsung Z Flip 5)
st.set_page_config(page_title="War Room 106", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #ff4b4b; color: white; font-weight: bold; font-size: 18px; }
    .stDataEditor { font-size: 16px !important; }
    .highlight { color: #ff4b4b; font-weight: bold; font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏎️ War Room - 106 Reverse")

# --- AGGIORNAMENTO SOLO LINK APEX ---
# Questo è il link esatto ricavato dal tuo QR Code
apex_link = "https://www.apex-timing.com/live-timing/kartodromo106/index.html"

col_link, col_btn = st.columns([1, 1])
with col_link:
    st.write("📊 **Monitor Apex Live**")
with col_btn:
    st.link_button("🚀 APRI LIVE INTERO", apex_link)

# Riquadro Live Timing (Iframe)
st.components.v1.iframe(apex_link, height=500, scrolling=True)

st.divider()

# --- TABELLA 15 KART (NESSUNA MODIFICA ALLA LOGICA) ---
st.subheader("⏱️ Inserimento Tempi (15 Kart)")

if 'laps_data' not in st.session
