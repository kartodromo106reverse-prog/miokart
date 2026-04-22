import streamlit as st
import pandas as pd
import time
import random
import numpy as np

# 1. SETUP
st.set_page_config(page_title="WAR ROOM - TOUCH CONTROL", layout="wide", initial_sidebar_state="expanded")

# 2. CSS PER TOUCH RAPIDO E SPAZIATURA
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    .main .block-container { padding: 5px !important; }
    
    /* Righe Classifica come Bottoni */
    .stButton>button.row-btn {
        width: 100% !important;
        background-color: transparent !important;
        border: none !important;
        border-bottom: 1px solid #222 !important;
        color: white !important;
        text-align: left !important;
        padding: 5px !important;
        height: auto !important;
        border-radius: 0px !important;
    }
    .stButton>button.row-btn:hover { background-color: #111 !important; }
    
    /* Colori Testo Categorie */
    .t-pro { color: #FF3131; font-weight: bold; }
    .t-semi { color: #1E90FF; font-weight: bold; }
    .t-ama { color: #00FF7F; font-weight: bold; }
    .t-none { color: #FFFFFF; }

    /* Lane Headers */
    .l-green { border-left: 5px solid #28a745; padding-left: 10px; margin-top: 10px; font-weight: bold; }
    .l-yellow { border-left: 5px solid #ffc107; padding-left: 10px; margin-top: 10px; font-weight: bold; }
    .l-red { border-left: 5px solid #dc3545; padding-left: 10px; margin-top: 10px; font-weight: bold; }
    .l-blue { border-left: 5px solid #007bff; padding-left: 10px; margin-top: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. STATO DATI
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(50)],
        'TEAM': [f"Team {i+1}" for i in range(50)],
        'CAT': ["NONE"] * 50,
        'STAR': [False] * 50,
        'ULTIMO': [0.0] * 50,
        'MEDIA_15': [44.0 + random.uniform(0.5, 3.0) for _ in range(50)],
        'COST': [0.2] * 50,
        'IN_PIT': [False] * 50,
        'LANE': ["VERDE"] * 50,
        'PIT_START': [0.0] * 50
    })
if 'selected_idx' not in st.session_state:
    st.session_state.selected_idx = 0

# SIMULAZIONE TEMPI (Molto leggera)
for i in range(50):
    if not st.session_state.data.at[i, 'IN_PIT']:
        st.session_state.data.at[i, 'ULTIMO'] = 44.0 + random.uniform(0.5, 2.5)

# --- SIDEBAR: IL PANNELLO CHE SI AGGIORNA AL TOCCO ---
with st.sidebar:
    idx = st.session_state.selected_idx
    st.header(f"🛠️ EDIT: KART {st.session_state.data.at[idx, 'KART']}")
    
    # Campi Modifica veloci
    new_k = st.text_input("Numero Kart:", st.session_state.data.at[idx, 'KART'])
    new_t = st.text_input("Nome Team:", st.session_state.data.at[idx, 'TEAM'])
    
    st.session_state.data.at[idx, 'KART'] = new_k
    st.session_state.data.at[idx, 'TEAM'] = new_t
    
    c1, c2 = st.columns(2)
    if c1.button("⭐ STELLA", use_container_width=True):
        st.session_state.data.at[idx, 'STAR'] = not st.session_state.data.at[idx, 'STAR']
        st.rerun()
    
    cat_list = ["NONE", "PRO", "SEMI", "AMAT"]
    st.session_state.data.at[idx, 'CAT'] = st.selectbox("CAT:", cat_list, index=cat_list.index(st.session_state.data.at[idx, 'CAT']))

    st.write("---")
    st.subheader("🏁 MOVIMENTO PIT")
    if not st.session_state.data.at[idx, 'IN_PIT']:
        cols = st.columns(2)
        lanes = [("🟢 VERDE", "VERDE"), ("🟡 GIALLO", "GIALLO"), ("🔴 ROSSO", "ROSSO"), ("🔵 BLU", "BLU")]
        for i, (label, l_name) in enumerate(lanes):
            if cols[i % 2].button(label, use_container_width=True):
                st.session_state.data.at[idx, 'IN_PIT'], st.session_state.data.at[idx, 'LANE'], st.session_state.data.at[idx, 'PIT_START'] = True, l_name, time.time()
                st.rerun()
    else:
        if st.button("✅ TORNA IN PISTA", use_container_width=True, type="primary"):
            st.session_state.data.at[idx, 'IN_PIT'] = False
            st.rerun()

# --- MAIN INTERFACE ---
tab_pista, tab_box = st.tabs(["🏎️ PISTA (Tocca per Edit)", "🚧 PIT LANES"])

with tab_pista:
    df_p = st.session_state.data[st.session_state.data['IN_PIT'] == False].sort_values(by='MEDIA_15')
    
    for i, row in df_p.iterrows():
        # Creiamo un bottone invisibile per tutta la riga
        star_icon = "⭐" if row['STAR'] else ""
        cat_class = f"t-{row['CAT'].lower()}"
        
        # Testo della riga
        label = f"{star_icon} {row['KART']} | {row['TEAM']} | MED: {row['MEDIA_15']:.2f} | ULT: {row['ULTIMO']:.1f}"
        
        if st.button(label, key=f"row_{i}", css_class="row-btn"):
            st.session_state.selected_idx = i
            st.rerun()

with tab_box:
    for l_name, l_class in [("VERDE", "l-green"), ("GIALLO", "l-yellow"), ("ROSSO", "l-red"), ("BLU", "l-blue")]:
        st.markdown(f"<div class='{l_class}'>CORSIA {l_name}</div>", unsafe_allow_html=True)
        q = st.session_state.data[(st.session_state.data['IN_PIT'] == True) & (st.session_state.data['LANE'] == l_name)]
        for idx, row in q.iterrows():
            rem = max(0, 180 - (time.time() - row['PIT_START']))
            m, s = divmod(int(rem), 60)
            if st.button(f"K{row['KART']} ({row['TEAM']}) - ⏳ {m:02d}:{s:02d}", key=f"pitrow_{idx}", css_class="row-btn"):
                st.session_state.selected_idx = idx
                st.rerun()

time.sleep(10)
st.rerun()
