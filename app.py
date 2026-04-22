import streamlit as st
import pandas as pd
import time
import random
import numpy as np

# 1. SETUP - NON MODIFICARE
st.set_page_config(page_title="WAR ROOM", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS: AGGIUNGIAMO SOLO LE LINEE DELLA GRIGLIA E FONT 10-12px
st.markdown("""
    <style>
    /* Manteniamo le tue tendine e menu, riduciamo solo i font dei dati */
    .main .block-container { padding: 2px 5px !important; background-color: #000000; }
    
    /* Griglia stile Excel per le righe dei Kart */
    .grid-container {
        display: flex;
        border-bottom: 1px solid #333; /* Linea orizzontale */
        align-items: center;
        height: 26px;
    }
    .grid-cell {
        border-right: 1px solid #333; /* Linea verticale */
        padding: 0px 4px;
        height: 100%;
        display: flex;
        align-items: center;
    }
    
    /* Font richiesti 10-12px */
    .f-data { font-size: 12px; font-weight: bold; color: white; }
    .f-label { font-size: 10px; color: #777; }
    
    /* Bottoni trasparenti per i nomi Team */
    .stButton>button {
        background: transparent !important;
        border: none !important;
        color: #4488ff !important;
        font-size: 11px !important;
        text-align: left !important;
        padding: 0 !important;
        height: 100% !important;
    }
    
    .t-pro { color: #FF3131; }
    .t-semi { color: #1E90FF; }
    .t-ama { color: #00FF7F; }
    
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 3. STATO DATI (Invariato)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(50)],
        'TEAM': [f"TEAM {i+1}" for i in range(50)],
        'CAT': ["NONE"] * 50, 'STAR': [False] * 50,
        'ULTIMO': [0.0] * 50, 'MEDIA': [0.0] * 50,
        'IN_PIT': [False] * 50, 'LANE': ["V"] * 50, 'PIT_START': [0.0] * 50
    })
if 'pista' not in st.session_state: st.session_state.pista = "Nome Pista"
if 'rif' not in st.session_state: st.session_state.rif = 45.00
if 'apex' not in st.session_state: st.session_state.apex = ""
if 'sel_idx' not in st.session_state: st.session_state.sel_idx = 0

# --- SIDEBAR (I TUOI MENU - NON MODIFICATI) ---
with st.sidebar:
    st.header("⚙️ CONFIGURAZIONE")
    st.session_state.pista = st.text_input("PISTA", st.session_state.pista)
    st.session_state.rif = st.number_input("BEST RIF", value=st.session_state.rif)
    st.session_state.apex = st.text_input("APEX LINK", st.session_state.apex)
    st.write("---")
    idx = st.session_state.sel_idx
    st.subheader(f"EDIT K{st.session_state.data.at[idx, 'KART']}")
    st.session_state.data.at[idx, 'TEAM'] = st.text_input("TEAM NAME", st.session_state.data.at[idx, 'TEAM'])
    if st.button("⭐ STELLA"): st.session_state.data.at[idx, 'STAR'] = not st.session_state.data.at[idx, 'STAR']; st.rerun()
    st.session_state.data.at[idx, 'CAT'] = st.selectbox("CAT", ["NONE", "PRO", "SEMI", "AMA"], index=["NONE", "PRO", "SEMI", "AMA"].index(st.session_state.data.at[idx, 'CAT']))
    
    if not st.session_state.data.at[idx, 'IN_PIT']:
        c = st.columns(2)
        if c[0].button("🟢 VERDE"): 
            st.session_state.data.at[idx, 'IN_PIT'], st.session_state.data.at[idx, 'LANE'], st.session_state.data.at[idx, 'PIT_START'] = True, "VERDE", time.time()
            st.rerun()
        if c[1].button("🔴 ROSSO"): 
            st.session_state.data.at[idx, 'IN_PIT'], st.session_state.data.at[idx, 'LANE'], st.session_state.data.at[idx, 'PIT_START'] = True, "ROSSO", time.time()
            st.rerun()
    else:
        if st.button("✅ TORNA IN PISTA"): st.session_state.data.at[idx, 'IN_PIT'] = False; st.rerun()

# --- MAIN INTERFACE ---
st.caption(f"📍 {st.session_state.pista} | Riferimento: {st.session_state.rif}s")
tab1, tab2, tab3 = st.tabs(["🏎️ LIVE", "🚧 BOX", "🌐 APEX"])

with tab1:
    # INTESTAZIONE GRIGLIA
    st.markdown("""
        <div class="grid-container" style="background-color: #111;">
            <div class="grid-cell f-label" style="width: 10%;">K</div>
            <div class="grid-cell f-label" style="width: 50%;">TEAM</div>
            <div class="grid-cell f-label" style="width: 20%;">MEDIA</div>
            <div class="grid-cell f-label" style="width: 20%; border-right: none;">ULT</div>
        </div>
    """, unsafe_allow_html=True)

    df = st.session_state.data[st.session_state.data['IN_PIT'] == False].copy()
    # Simulazione rapida
    for i in df.index:
        st.session_state.data.at[i, 'ULTIMO'] = st.session_state.rif + random.uniform(0.1, 1.0)
        st.session_state.data.at[i, 'MEDIA'] = st.session_state.rif + 0.2
    
    df_sorted = df.sort_values('MEDIA')

    for i, row in df_sorted.iterrows():
        cols = st.columns([0.4, 2, 0.8, 0.8])
        star = "⭐" if row['STAR'] else ""
        cat_c = f"t-{row['CAT'].lower()}"
        
        # Colonna Kart con bordo
        with cols[0]:
            st.markdown(f'<div class="grid-container"><div class="grid-cell f-data {cat_c}" style="width:100%; border-right:none;">{star}{row["KART"]}</div></div>', unsafe_allow_html=True)
        # Colonna Team (Bottone) con bordo
        with cols[1]:
            if st.button(f"{row['TEAM']}", key=f"t_{i}"):
                st.session_state.sel_idx = i
                st.rerun()
        # Colonna Media con bordo
        with cols[2]:
            st.markdown(f'<div class="grid-container"><div class="grid-cell f-data" style="width:100%; border-right:none; justify-content:flex-end;">{row["MEDIA"]:.2f}</div></div>', unsafe_allow_html=True)
        # Colonna Ultimo
        with cols[3]:
            st.markdown(f'<div class="grid-container"><div class="grid-cell f-data" style="width:100%; border-right:none; justify-content:flex-end; color:#777;">{row["ULTIMO"]:.1f}</div></div>', unsafe_allow_html=True)
        
        # Linea di chiusura orizzontale
        st.markdown('<div style="border-bottom: 1px solid #333; margin-top:-1px;"></div>', unsafe_allow_html=True)

with tab2:
    for lane in ["VERDE", "ROSSO"]:
        st.markdown(f"<div style='font-size:10px; color:#555; margin-top:5px;'>CORSIA {lane}</div>", unsafe_allow_html=True)
        q = st.session_state.data[(st.session_state.data['IN_PIT'] == True) & (st.session_state.data['LANE'] == lane)]
        for idx, r in q.iterrows():
            rem = max(0, 180 - (time.time() - r['PIT_START']))
            m, s = divmod(int(rem), 60)
            if st.button(f"K{r['KART']} - {r['TEAM']} | ⏳ {m:02d}:{s:02d}", key=f"box_{idx}"):
                st.session_state.sel_idx = idx
                st.rerun()

with tab3:
    if st.session_state.apex:
        st.markdown(f'<iframe src="{st.session_state.apex}" width="100%" height="600px"></iframe>', unsafe_allow_html=True)

time.sleep(10)
st.rerun()
