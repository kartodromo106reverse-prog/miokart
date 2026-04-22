import streamlit as st
import pandas as pd
import time
import random
import numpy as np

# 1. SETUP - LAYOUT TOTALE
st.set_page_config(page_title="TELEMETRIA PRO", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS RADICALE PER DIMENSIONI MINIME
st.markdown("""
    <style>
    /* Azzeramento margini pagina */
    .main .block-container { padding: 2px 5px !important; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    /* Forza le colonne a non andare a capo */
    [data-testid="column"] { 
        padding: 0px !important;
        margin: 0px !important;
    }

    /* Font piccoli per numeri e testi */
    .num-kart { font-size: 14px; font-weight: bold; margin: 0; line-height: 1.2; }
    .team-text { font-size: 11px; color: #888; margin: 0; overflow: hidden; white-space: nowrap; }
    .tempo-text { font-size: 13px; font-weight: bold; color: white; margin: 0; text-align: right; }
    
    /* Bottoni rimpiccioliti al massimo */
    .stButton>button {
        padding: 1px 4px !important;
        height: 24px !important;
        font-size: 11px !important;
        min-width: 100% !important;
        border: 1px solid #333 !important;
        background-color: #111 !important;
    }

    /* Colori Categorie */
    .t-pro { color: #FF3131 !important; }
    .t-semi { color: #1E90FF !important; }
    .t-ama { color: #00FF7F !important; }
    .t-none { color: #FFFFFF !important; }

    /* Nascondi header Streamlit */
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 3. GESTIONE DATI
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(50)],
        'TEAM': [f"T{i+1}" for i in range(50)],
        'CAT': ["NONE"] * 50, 'STAR': [False] * 50,
        'ULTIMO': [0.0] * 50, 'MEDIA': [45.0] * 50,
        'IN_PIT': [False] * 50, 'LANE': ["VERDE"] * 50, 'PIT_START': [0.0] * 50
    })
if 'sel_idx' not in st.session_state: st.session_state.sel_idx = 0

# SIMULAZIONE LEGGERA
for i in range(50):
    if not st.session_state.data.at[i, 'IN_PIT']:
        st.session_state.data.at[i, 'ULTIMO'] = 44.0 + random.uniform(0.5, 2.5)

# --- SIDEBAR (PANNELLO DI CONTROLLO) ---
with st.sidebar:
    idx = st.session_state.sel_idx
    st.header(f"KART {st.session_state.data.at[idx, 'KART']}")
    st.session_state.data.at[idx, 'KART'] = st.text_input("N° KART", st.session_state.data.at[idx, 'KART'])
    st.session_state.data.at[idx, 'TEAM'] = st.text_input("NOME TEAM", st.session_state.data.at[idx, 'TEAM'])
    if st.button("⭐ SEGNA/TOGLI STELLA"): st.session_state.data.at[idx, 'STAR'] = not st.session_state.data.at[idx, 'STAR']
    st.session_state.data.at[idx, 'CAT'] = st.selectbox("CATEGORIA", ["NONE", "PRO", "SEMI", "AMAT"], index=["NONE", "PRO", "SEMI", "AMAT"].index(st.session_state.data.at[idx, 'CAT']))
    
    st.write("---")
    st.subheader("🏁 MOVIMENTO BOX")
    if not st.session_state.data.at[idx, 'IN_PIT']:
        c = st.columns(2)
        l_list = [("🟢 VERDE", "VERDE"), ("🟡 GIALLO", "GIALLO"), ("🔴 ROSSO", "ROSSO"), ("🔵 BLU", "BLU")]
        for i, (lab, name) in enumerate(l_list):
            if c[i%2].button(lab):
                st.session_state.data.at[idx, 'IN_PIT'], st.session_state.data.at[idx, 'LANE'], st.session_state.data.at[idx, 'PIT_START'] = True, name, time.time()
                st.rerun()
    else:
        if st.button("✅ LIBERA E TORNA IN PISTA", type="primary"): 
            st.session_state.data.at[idx, 'IN_PIT'] = False; st.rerun()

# --- INTERFACCIA PRINCIPALE ---
tab1, tab2 = st.tabs(["🏎️ LIVE", "🚧 BOX"])

with tab1:
    # Intestazione Colonne
    h = st.columns([0.8, 2, 1, 1])
    h[0].caption("K")
    h[1].caption("TEAM (CLICCA)")
    h[2].caption("MEDIA")
    h[3].caption("ULT")

    df_pista = st.session_state.data[st.session_state.data['IN_PIT'] == False].sort_values('MEDIA')
    
    for i, row in df_pista.iterrows():
        cols = st.columns([0.8, 2, 1, 1])
        
        # 1. Stella e Numero (Piccoli)
        star = "⭐" if row['STAR'] else ""
        cat_color = f"t-{row['CAT'].lower()}"
        cols[0].markdown(f"<p class='num-kart {cat_color}'>{star}{row['KART']}</p>", unsafe_allow_html=True)
        
        # 2. Team (È il bottone per l'Edit)
        if cols[1].button(f"{row['TEAM']}", key=f"btn_{i}"):
            st.session_state.sel_idx = i
            st.rerun()
            
        # 3. Tempi
        cols[2].markdown(f"<p class='tempo-text'>{row['MEDIA']:.2f}</p>", unsafe_allow_html=True)
        cols[3].markdown(f"<p class='tempo-text' style='color:#555;'>{row['ULTIMO']:.1f}</p>", unsafe_allow_html=True)

with tab2:
    for lane in ["VERDE", "GIALLO", "ROSSO", "BLU"]:
        st.markdown(f"<div style='font-size:12px; font-weight:bold; color:#777; margin-top:10px;'>CORSIA {lane}</div>", unsafe_allow_html=True)
        q = st.session_state.data[(st.session_state.data['IN_PIT'] == True) & (st.session_state.data['LANE'] == lane)]
        for idx, r in q.iterrows():
            rem = max(0, 180 - (time.time() - r['PIT_START']))
            m, s = divmod(int(rem), 60)
            if st.button(f"K{r['KART']} - {r['TEAM']} | {m:02d}:{s:02d}", key=f"box_{idx}"):
                st.session_state.sel_idx = idx
                st.rerun()

time.sleep(10)
st.rerun()
