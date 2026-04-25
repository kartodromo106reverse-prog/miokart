import streamlit as st
import pandas as pd
import time
import random
import requests
from streamlit_autorefresh import st_autorefresh

# CONFIGURAZIONE
st.set_page_config(page_title="WAR ROOM MONITOR", layout="wide")

# CSS OTTIMIZZATO
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold; }
    .pit-card { 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #30363d; 
        background: #161b22;
        margin-bottom: 10px;
    }
    .timer-red { color: #ff4b4b; font-size: 20px; font-weight: bold; }
    .timer-green { color: #00eb93; font-size: 20px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# INIZIALIZZAZIONE STATO
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [str(i).zfill(2) for i in range(1, 31)],
        'IN_PIT': [False] * 30,
        'PIT_START': [0.0] * 30,
        'BEST': [0.0] * 30
    })

if 'target_time' not in st.session_state:
    st.session_state.target_time = 180  # Default 3 minuti

# REFRESH AUTOMATICO (Ogni 2 secondi)
st_autorefresh(interval=2000, key="datarefresh")

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏁 Comandi Box")
    st.session_state.target_time = st.number_input("Tempo Target Pit (sec)", value=180)
    if st.button("Reset Generale"):
        st.session_state.data['IN_PIT'] = False
        st.rerun()

# --- MAIN UI ---
st.title("🏎️ Real-Time Strategy Monitor")

col_track, col_pit = st.columns([2, 1])

with col_track:
    st.subheader("Pista (Live)")
    # Simulazione dati (Sostituisci con fetch_apex_data se hai l'URL API)
    for i in range(0, 10, 2):
        c1, c2 = st.columns(2)
        for idx, col in enumerate([c1, c2]):
            kart_idx = i + idx
            kart_no = st.session_state.data.iloc[kart_idx]['KART']
            is_in_pit = st.session_state.data.iloc[kart_idx]['IN_PIT']
            
            if not is_in_pit:
                if col.button(f"ENTRA BOX K{kart_no}", key=f"in_{kart_no}"):
                    st.session_state.data.at[kart_idx, 'IN_PIT'] = True
                    st.session_state.data.at[kart_idx, 'PIT_START'] = time.time()
                    st.rerun()

with col_pit:
    st.subheader("🚧 In Gestione Box")
    pit_now = st.session_state.data[st.session_state.data['IN_PIT'] == True]
    
    if pit_now.empty:
        st.info("Nessun kart ai box")
    else:
        for idx, row in pit_now.iterrows():
            elapsed = time.time() - row['PIT_START']
            remaining = st.session_state.target_time - elapsed
            
            with st.container():
                st.markdown(f"""
                <div class="pit-card">
                    <b>KART {row['KART']}</b><br>
                    Tempo trascorso: {int(elapsed)}s<br>
                    Mancante: <span class="{'timer-red' if remaining < 20 else 'timer-green'}">{int(remaining)}s</span>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"RELEASE K{row['KART']}", key=f"rel_{row['KART']}"):
                    st.session_state.data.at[idx, 'IN_PIT'] = False
                    st.rerun()
