import streamlit as st
import pandas as pd
import time
import random
import numpy as np

# 1. SETUP
st.set_page_config(page_title="WAR ROOM PRO", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS (Parametri bloccati: font 12-14px, compatto)
st.markdown("""
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
if 'pista_nome' not in st.session_state: st.session_state.pista_nome = ""
if 'best_lap_pista' not in st.session_state: st.session_state.best_lap_pista = 45.00
if 'apex_url' not in st.session_state: st.session_state.apex_url = ""
if 'sel_idx' not in st.session_state: st.session_state.sel_idx = 0

# --- SIDEBAR (CONFIGURAZIONE PISTE + BEST LAP + APEX) ---
with st.sidebar:
    st.header("🏁 GESTIONE PISTA")
    st.session_state.pista_nome = st.text_input("NOME PISTA", st.session_state.pista_nome, placeholder="Es. Pomposa")
    st.session_state.best_lap_pista = st.number_input("MIGLIOR TEMPO (Rif.)", value=st.session_state.best_lap_pista, step=0.01, format="%.2f")
    
    st.write("---")
    st.session_state.apex_url = st.text_input("LINK APEX TIMING", st.session_state.apex_url)
    
    st.write("---")
    # EDIT KART
    idx = st.session_state.sel_idx
    st.subheader(f"EDIT KART {st.session_state.data.at[idx, 'KART']}")
    st.session_state.data.at[idx, 'KART'] = st.text_input("N°", st.session_state.data.at[idx, 'KART'])
    st.session_state.data.at[idx, 'TEAM'] = st.text_input("TEAM", st.session_state.data.at[idx, 'TEAM'])
    
    if st.button("⭐ SEGNA STELLA"):
        st.session_state.data.at[idx, 'STAR'] = not st.session_state.data.at[idx, 'STAR']
        st.rerun()

    st.write("---")
    st.subheader("🏁 BOX")
    if not st.session_state.data.at[idx, 'IN_PIT']:
        c = st.columns(2)
        l_list = [("🟢 VERDE", "VERDE"), ("🟡 GIALLO", "GIALLO"), ("🔴 ROSSO", "ROSSO"), ("🔵 BLU", "BLU")]
        for i, (lab, name) in enumerate(l_list):
            if c[i%2].button(lab):
                st.session_state.data.at[idx, 'IN_PIT'], st.session_state.data.at[idx, 'LANE'], st.session_state.data.at[idx, 'PIT_START'] = True, name, time.time()
                st.rerun()
    else:
        if st.button("✅ TORNA IN PISTA", type="primary"): 
            st.session_state.data.at[idx, 'IN_PIT'] = False; st.rerun()

# --- MAIN ---
st.caption(f"Pista: {st.session_state.pista_nome} | Rif: {st.session_state.best_lap_pista}s")

tab1, tab2, tab3 = st.tabs(["🏎️ LIVE", "🚧 BOX", "🌐 APEX"])

with tab1:
    h = st.columns([0.8, 2, 1, 1])
    h[0].caption("K")
    h[1].caption("TEAM")
    h[2].caption("MEDIA")
    h[3].caption("ULT")

    # Simuliamo il comportamento dei kart basandoci sul Best Lap della pista
    for i in range(50):
        if not st.session_state.data.at[i, 'IN_PIT']:
            # L'ultimo tempo oscilla intorno al tempo di riferimento della pista
            st.session_state.data.at[i, 'ULTIMO'] = st.session_state.best_lap_pista + random.uniform(0.1, 2.5)
            # La media si aggiorna di conseguenza
            if st.session_state.data.at[i, 'MEDIA'] == 0:
                st.session_state.data.at[i, 'MEDIA'] = st.session_state.data.at[i, 'ULTIMO']
            else:
                st.session_state.data.at[i, 'MEDIA'] = (st.session_state.data.at[i, 'MEDIA'] * 0.9) + (st.session_state.data.at[i, 'ULTIMO'] * 0.1)

    df_pista = st.session_state.data[st.session_state.data['IN_PIT'] == False].sort_values('MEDIA')
    
    for i, row in df_pista.iterrows():
        cols = st.columns([0.8, 2, 1, 1])
        star = "⭐" if row['STAR'] else ""
        cat_c = f"t-{row['CAT'].lower()}"
        
        cols[0].markdown(f"<p class='num-kart {cat_c}'>{star}{row['KART']}</p>", unsafe_allow_html=True)
        if cols[1].button(f"{row['TEAM']}", key=f"btn_{i}"):
            st.session_state.sel_idx = i
            st.rerun()
            
        cols[2].markdown(f"<p class='tempo-text'>{row['MEDIA']:.2f}</p>", unsafe_allow_html=True)
        cols[3].markdown(f"<p class='tempo-text' style='color:#555;'>{row['ULTIMO']:.1f}</p>", unsafe_allow_html=True)

with tab2:
    for lane in ["VERDE", "GIALLO", "ROSSO", "BLU"]:
        st.markdown(f"<div style='font-size:11px; font-weight:bold; color:#777; margin-top:5px;'>CORSIA {lane}</div>", unsafe_allow_html=True)
        q = st.session_state.data[(st.session_state.data['IN_PIT'] == True) & (st.session_state.data['LANE'] == lane)]
        for idx, r in q.iterrows():
            rem = max(0, 180 - (time.time() - r['PIT_START']))
            m, s = divmod(int(rem), 60)
            if st.button(f"K{r['KART']} - {r['TEAM']} | {m:02d}:{s:02d}", key=f"box_{idx}"):
                st.session_state.sel_idx = idx
                st.rerun()

with tab3:
    if st.session_state.apex_url:
        st.markdown(f'<iframe src="{st.session_state.apex_url}" width="100%" height="800px"></iframe>', unsafe_allow_html=True)
    else:
        st.info("Nessun link Apex caricato. Usa i dati manuali della Sidebar.")

time.sleep(10)
st.rerun()
