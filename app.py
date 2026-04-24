import streamlit as st
import pandas as pd
import time
import random

# 1. SETUP - LAYOUT OTALE (Il tuo stile per Z Flip 5)
st.set_page_config(page_title="TELEMETRIA PRO 106", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS UNIFICATO (Apex + Telemetria)
st.markdown("""
    <style>
    .main .block-container { padding: 5px 10px !important; }
    /* Il tuo tasto Apex grande */
    .stLinkButton>a { 
        width: 100% !important; height: 70px !important; display: flex !important; 
        align-items: center !important; justify-content: center !important; 
        font-size: 20px !important; background-color: #ff4b4b !important; 
        color: white !important; font-weight: bold !important; border-radius: 12px !important;
        text-decoration: none !important; margin-bottom: 15px !important;
    }
    /* Stili Tabella Telemetria */
    .num-kart { font-size: 16px; font-weight: bold; margin: 0; }
    .tempo-text { font-size: 15px; font-weight: bold; color: white; text-align: right; }
    .t-pro { color: #FF3131 !important; }
    .t-semi { color: #1E90FF !important; }
    .t-ama { color: #00FF7F !important; }
    .t-none { color: #FFFFFF !important; }
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 3. GESTIONE DATI (Inizializzazione 50 Kart)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(50)],
        'TEAM': [f"TEAM {i+1}" for i in range(50)],
        'CAT': ["NONE"] * 50, 
        'STAR': [False] * 50,
        'BEST': [99.99] * 50,
        'IN_PIT': [False] * 50, 
        'LANE': ["VERDE"] * 50, 
        'PIT_START': [0.0] * 50
    })
if 'sel_idx' not in st.session_state: st.session_state.sel_idx = 0

# --- INTERFACCIA SUPERIORE (APEX) ---
st.title("🏎️ War Room 106 Reverse")
# Il link che abbiamo verificato dalle tue foto
apex_link = "https://live.apex-timing.com/kartodromo106reverse/"
st.link_button("🚀 APRI LIVE TIMING APEX", apex_link)

# --- SIDEBAR DI EDITING (Compare quando clicchi un Team) ---
with st.sidebar:
    idx = st.session_state.sel_idx
    st.header(f"MODIFICA KART {st.session_state.data.at[idx, 'KART']}")
    st.session_state.data.at[idx, 'KART'] = st.text_input("N° KART", st.session_state.data.at[idx, 'KART'])
    st.session_state.data.at[idx, 'TEAM'] = st.text_input("NOME TEAM", st.session_state.data.at[idx, 'TEAM'])
    st.session_state.data.at[idx, 'BEST'] = st.number_input("MIGLIOR TEMPO", value=float(st.session_state.data.at[idx, 'BEST']), format="%.3f")
    
    if st.button("⭐ ASSEGNA/TOGLI STELLA"): 
        st.session_state.data.at[idx, 'STAR'] = not st.session_state.data.at[idx, 'STAR']
        st.rerun()
    
    st.session_state.data.at[idx, 'CAT'] = st.selectbox("CATEGORIA", ["NONE", "PRO", "SEMI", "AMAT"], 
                                                     index=["NONE", "PRO", "SEMI", "AMAT"].index(st.session_state.data.at[idx, 'CAT']))
    
    st.write("---")
    st.subheader("🏁 GESTIONE BOX")
    if not st.session_state.data.at[idx, 'IN_PIT']:
        cols_pit = st.columns(2)
        lanes = [("🟢 VERDE", "VERDE"), ("🟡 GIALLO", "GIALLO"), ("🔴 ROSSO", "ROSSO"), ("🔵 BLU", "BLU")]
        for i, (lab, name) in enumerate(lanes):
            if cols_pit[i%2].button(lab):
                st.session_state.data.at[idx, 'IN_PIT'] = True
                st.session_state.data.at[idx, 'LANE'] = name
                st.session_state.data.at[idx, 'PIT_START'] = time.time()
                st.rerun()
    else:
        if st.button("✅ TORNA IN PISTA", type="primary"): 
            st.session_state.data.at[idx, 'IN_PIT'] = False
            st.rerun()

# --- PANNELLO CENTRALE ---
tab_live, tab_box = st.tabs(["🏎️ LIVE TRACK", "🚧 PIT LANE"])

with tab_live:
    # Header Tabella
    h = st.columns([1, 2, 1])
    h[0].caption("KART")
    h[1].caption("TEAM (CLICCA PER EDIT)")
    h[2].caption("BEST LAP")

    # Mostra solo i kart in pista ordinati per tempo
    df_pista = st.session_state.data[st.session_state.data['IN_PIT'] == False].sort_values('BEST')
    
    for i, row in df_pista.iterrows():
        cols = st.columns([1, 2, 1])
        
        # Kart e Stella
        star = "⭐" if row['STAR'] else ""
        cat_class = f"t-{row['CAT'].lower()}"
        cols[0].markdown(f"<p class='num-kart {cat_class}'>{star}{row['KART']}</p>", unsafe_allow_html=True)
        
        # Bottone Team per modificare
        if cols[1].button(f"{row['TEAM']}", key=f"track_{i}"):
            st.session_state.sel_idx = i
            # Apre automaticamente la sidebar su mobile
            st.write("<- Modifica i dati nella barra laterale") 
            
        # Tempo
        t_display = "---" if row['BEST'] >= 99 else f"{row['BEST']:.3f}"
        cols[2].markdown(f"<p class='tempo-text'>{t_display}s</p>", unsafe_allow_html=True)

with tab_box:
    for lane in ["VERDE", "GIALLO", "ROSSO", "BLU"]:
        st.markdown(f"<p style='color:#777; font-weight:bold; margin-top:10px;'>CORSIA {lane}</p>", unsafe_allow_html=True)
        q = st.session_state.data[(st.session_state.data['IN_PIT'] == True) & (st.session_state.data['LANE'] == lane)]
        for idx, r in q.iterrows():
            elapsed = time.time() - r['PIT_START']
            mins, secs = divmod(int(elapsed), 60)
            if st.button(f"KART {r['KART']} | {mins:02d}:{secs:02d}", key=f"box_btn_{idx}"):
                st.session_state.sel_idx = idx
                st.rerun()

# Auto-refresh ogni 30 secondi per non consumare troppa batteria sul Flip 5
time.sleep(30)
st.rerun()
