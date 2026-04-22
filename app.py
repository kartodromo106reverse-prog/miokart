import streamlit as st
import pandas as pd
import time
import random
import numpy as np

# 1. SETUP SCHERMO INTERO
st.set_page_config(page_title="WAR ROOM PURE", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS PER LAYOUT PROFESSIONALE (Anti-impilamento mobile)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    .main .block-container { padding: 5px; max-width: 100%; }
    
    /* Header Tabella */
    .header-text { font-size: 11px; color: #666; text-align: center; margin: 0; }

    /* Classi Colore Numeri Kart */
    .k-none { color: #FFFFFF; font-weight: bold; font-size: 18px; }
    .k-pro { color: #FF3131; font-weight: bold; font-size: 20px; text-shadow: 0 0 5px #FF0000; }
    .k-semi { color: #1E90FF; font-weight: bold; font-size: 20px; text-shadow: 0 0 5px #0000FF; }
    .k-ama { color: #00FF7F; font-weight: bold; font-size: 20px; text-shadow: 0 0 5px #00FF00; }

    /* Box AI Suggerimenti */
    .ai-card {
        border: 1px solid #444;
        padding: 5px;
        border-radius: 4px;
        background-color: #111;
        text-align: center;
    }

    /* Bottoni Categoria */
    .stButton>button {
        width: 100% !important;
        height: 28px !important;
        font-size: 10px !important;
        background-color: #222;
        color: white;
        border: 1px solid #444;
        padding: 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGICA DATI
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i:02d}" for i in range(1, 51)],
        'CAT': ["NONE"] * 50,
        'ULTIMO': [0.0] * 50,
        'MEDIA_15': [45.0] * 50,
        'COST': [0.2] * 50,
        'PIT': [random.choice(['A', 'B', 'C']) for _ in range(50)],
        'G': [0] * 50,
        'STORICO': [[] for _ in range(50)]
    })

# AGGIORNAMENTO TEMPI (Simulazione ogni 5 sec)
for i in range(50):
    t = 44.0 + random.uniform(0.5, 2.5)
    h = st.session_state.data.at[i, 'STORICO']
    h.append(t)
    if len(h) > 15: h.pop(0)
    st.session_state.data.at[i, 'ULTIMO'] = t
    st.session_state.data.at[i, 'MEDIA_15'] = np.mean(h)
    st.session_state.data.at[i, 'COST'] = np.std(h)
    st.session_state.data.at[i, 'G'] += 1

# --- INTERFACCIA ---

st.title("🏎️ WAR ROOM STRATEGY")

# SECTION: TARGET SWITCH (AI)
st.markdown("<p style='color:#888; font-size:12px; margin-bottom:2px;'>🎯 SUGGERIMENTI CAMBIO</p>", unsafe_allow_html=True)
best_karts = st.session_state.data.sort_values(by=['MEDIA_15', 'COST']).head(2)
cols_ai = st.columns(2)
for idx, (i, r) in enumerate(best_karts.iterrows()):
    with cols_ai[idx]:
        st.markdown(f"""
        <div class="ai-card">
            <b style="color:#FF3131; font-size:14px;">KART {r['KART']}</b><br>
            <span style="font-size:11px;">M: {r['MEDIA_15']:.2f} | PIT: {r['PIT']}</span>
        </div>
        """, unsafe_allow_html=True)

st.write("---")

# SECTION: TABELLA CLASSIFICA
# Intestazioni Header
h_cols = st
