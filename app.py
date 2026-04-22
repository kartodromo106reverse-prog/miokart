import streamlit as st
import pandas as pd
import time
import random
import numpy as np

# 1. SETUP
st.set_page_config(page_title="WAR ROOM 10PX", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS (Parametri richiesti: font 10-12px)
st.markdown("""
    <style>
    .main .block-container { padding: 1px 3px !important; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    /* Font Numero Kart e Tempi a 12px */
    .num-kart { font-size: 12px; font-weight: bold; margin: 0; line-height: 1; }
    .tempo-text { font-size: 12px; font-weight: bold; color: white; margin: 0; text-align: right; }
    
    /* Font Team e Caption a 10px */
    .team-btn-text { font-size: 10px !important; }
    .stCaption { font-size: 10px !important; line-height: 1 !important; }

    /* Bottoni ultra-compatti */
    .stButton>button {
        padding: 0px 2px !important;
        height: 20px !important; /* Altezza ridotta per stare nel 12px */
        font-size: 10px !important;
        min-width: 100% !important;
        margin: 0 !important;
    }
    
    /* Colori Categorie */
    .t-pro { color: #FF3131 !important; }
    .t-semi { color: #1E90FF !important; }
    .t-ama { color: #00FF7F !important; }
    
    /* Forza layout orizzontale stretto */
    [data-testid="column"] { padding: 0px 1px !important; }
    
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 3. STATO DATI
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(50)],
        'TEAM': [f"T{i+1}" for i in range(50)],
        'CAT': ["NONE"] * 50, 'STAR': [False] * 50,
        'ULTIMO': [0.0] * 50, 'MEDIA': [0.0] * 50,
        'IN_PIT': [False] * 50, 'LANE': ["VERDE"] * 50, 'PIT_START': [0.0] * 50
    })
if 'pista_nome' not in st.session_state: st.session_state.pista_nome = "Gara"
if 'best_lap_pista' not in st.session_state: st.session_state.best_lap_pista = 45.00
if 'apex_url' not in st.session_state: st.session_state.apex_url = ""
if 'sel_idx' not in st.session_state: st.session_state.sel_idx = 0

# --- SIDEBAR (CONFIGURAZIONE) ---
with st.sidebar:
    st.header("⚙️ MENU")
    st.session_state.pista_nome = st.text_input("PISTA", st.session_state.pista_nome)
    st.session_state.best_lap_pista = st.number_input("BEST RIF.", value=st.session_state.best_lap_pista, format="%.2f")
    st.session_state.apex_url = st.text_input("APEX URL", st.session_state.apex_url)
    st.write("---")
    idx = st.session_state.sel_idx
    st.subheader(f"EDIT K{st.session_state.data.at[idx, 'KART']}")
    st.session_state.data.at[idx, 'KART'] = st.text_input("N°", st.session_state.data.at[idx, 'KART'])
    st.session_state.data.at[idx, 'TEAM'] = st.text_input("TEAM", st.session_state.data.at[idx, 'TEAM'])
    if st.button("⭐ STELLA"): st.session_state.data.at[idx, 'STAR'] = not st.session_state.data.at[idx, 'STAR']; st.rerun()
    st.session_state.data.at[idx, 'CAT'] = st.selectbox("CAT", ["NONE", "PRO", "SEMI", "AMAT"], index=["NONE", "PRO", "SEMI", "AMAT"].index(st.session_state.data.at[idx, 'CAT']))
    if not st.session_state.data.at[idx, 'IN_PIT']:
        c = st.columns(2)
        lanes = [("🟢 V", "VERDE"), ("🟡 G", "GIALLO"), ("🔴 R", "ROSSO"), ("🔵 B", "BLU")]
        for i, (l, n) in enumerate(lanes):
            if c[i%2].button(l):
                st.session_state.data.at[idx, 'IN_PIT'], st.session_state.data.at[idx, 'LANE'], st.session_state.data.at[idx, 'PIT_START'] = True, n, time.time()
                st.rerun()
    else:
        if st.button("✅ ESCI PIT"): st.session_state.data.at[idx, 'IN_PIT'] = False; st.rerun()

# --- MAIN ---
st.caption(f"📍 {st.session_state.pista_nome} | Rif: {st.session_state.best_lap_pista}s")
tab1, tab2, tab3 = st.tabs(["🏎️ PISTA", "🚧 BOX", "🌐 APEX"])

with tab1:
    h = st.columns([0.6, 2.2, 1, 1])
    h[0].caption("K")
    h[1].caption("TEAM")
    h[2].caption("MED")
    h[3].caption("ULT")

    # Aggiornamento simulato
    for i in range(50):
        if not st.session_state.data.at[i, 'IN_PIT']:
            st.session_state.data.at[i, 'ULTIMO'] = st.session_state.best_lap_pista + random.uniform(0.1, 1.5)
            st.session_state.data.at[i, 'MEDIA'] = st.session_state.best_lap_pista + 0.5
    
    df_pista = st.session_state.data[st.session_state.data['IN_PIT'] == False].sort_values('MEDIA')
    
    for i, row in df_pista.iterrows():
        cols = st.columns([0.6, 2.2, 1, 1])
        star = "⭐" if row['STAR'] else ""
        cat_c = f"t-{row['CAT'].lower()}"
        cols[0].markdown(f"<p class='num-kart {cat_c}'>{star}{row['KART']}</p>", unsafe_allow_html=True)
        if cols[1].button(f"{row['TEAM']}", key=f"btn_{i}"):
            st.session_state.sel_idx = i
            st.rerun()
        cols[2].markdown(f"<p class='tempo-text'>{row['MEDIA']:.2f}</p>", unsafe_allow_html=True)
        cols[3].markdown(f"<p class='tempo-text' style='color:#666;'>{row['ULTIMO']:.1f}</p>", unsafe_allow_html=True)

with tab2:
    for lane in ["VERDE", "GIALLO", "ROSSO", "BLU"]:
        st.markdown(f"<div style='font-size:10px; font-weight:bold; color:#555;'>CORSIA {lane}</div>", unsafe_allow_html=True)
        q = st.session_state.data[(st.session_state.data['IN_PIT'] == True) & (st.session_state.data['LANE'] == lane)]
        for idx, r in q.iterrows():
            rem = max(0, 180 - (time.time() - r['PIT_START']))
            m, s = divmod(int(rem), 60)
            if st.button(f"K{r['KART']} - {m:02d}:{s:02d}", key=f"box_{idx}"):
                st.session_state.sel_idx = idx
                st.rerun()

with tab3:
    if st.session_state.apex_url:
        st.markdown(f'<iframe src="{st.session_state.apex_url}" width="100%" height="800px"></iframe>', unsafe_allow_html=True)

time.sleep(10)
st.rerun()
