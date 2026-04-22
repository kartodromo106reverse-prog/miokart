import streamlit as st
import pandas as pd
import time
import random
import numpy as np

# CONFIGURAZIONE
st.set_page_config(page_title="WAR ROOM STRATEGY", layout="wide", initial_sidebar_state="collapsed")

# CSS PER BLOCCO COLONNE E COLORI
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="column"] { display: flex; flex-direction: column; min-width: 45px !important; align-items: center; }
    .main .block-container { padding: 5px; }
    .kart-font { font-size: 20px !important; font-weight: bold; font-family: monospace; }
    .small-font { font-size: 13px !important; }
    .stButton>button { height: 40px; font-size: 12px !important; font-weight: bold; border-radius: 5px; }
    div[data-testid="stVerticalBlock"] > div { gap: 0.2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE DATI (Persistenti) ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i:02d}" for i in range(1, 51)],
        'CAT': ["NONE"] * 50,
        'ULTIMO': [0.0] * 50,
        'MEDIA_15': [46.0] * 50,
        'COST': [0.2] * 50,
        'PIT': [random.choice(['A', 'B', 'C']) for _ in range(50)],
        'G': [0] * 50,
        'STORICO': [[] for _ in range(50)]
    })

# AGGIORNAMENTO DATI (Rallentato logicamente)
for i in range(50):
    t = 45.0 + random.uniform(0.1, 2.5)
    hist = st.session_state.data.at[i, 'STORICO']
    hist.append(t)
    if len(hist) > 15: hist.pop(0)
    st.session_state.data.at[i, 'ULTIMO'] = t
    st.session_state.data.at[i, 'MEDIA_15'] = np.mean(hist)
    st.session_state.data.at[i, 'COST'] = np.std(hist)
    st.session_state.data.at[i, 'G'] += 1

# --- INTERFACCIA ---
st.title("🏎️ AI STRATEGY ASSISTANT")

# BOX SUGGERIMENTI (Check 15 giri)
st.subheader("🎯 CONSIGLI CAMBIO (Switch)")
targets = st.session_state.data.sort_values(by=['MEDIA_15', 'COST']).head(2)
c_ai = st.columns(2)
for idx, (i, row) in enumerate(targets.iterrows()):
    with c_ai[idx]:
        st.markdown(f"""<div style="border:2px solid red; padding:10px; border-radius:8px; text-align:center; background:#111;">
        <span style="color:red; font-weight:bold; font-size:18px;">PESCA: {row['KART']}</span><br>
        <span style="font-size:14px;">Media: {row['MEDIA_15']:.2f} | Corsia: {row['PIT']}</span></div>""", unsafe_allow_html=True)

st.write("---")

# TABELLA CLASSIFICA
cols = st.columns([0.6, 1, 1.5, 1.2, 1.2, 0.8, 0.6, 0.6])
headers = ["P", "KR", "CATEGORIA", "ULT", "MED", "CST", "PT", "G"]
for col, h in zip(cols, headers):
    col.markdown(f"<p class='small-font' style='color:grey; margin:0;'>{h}</p>", unsafe_allow_html=True)

# Ordine per Media (Chi è veloce davvero)
df_sorted = st.session_state.data.sort_values(by='MEDIA_15').reset_index(drop=True)

for i, row in df_sorted.iterrows():
    c = st.columns([0.6, 1, 1.5, 1.2, 1.2, 0.8, 0.6, 0.6])
    
    c[0].write(f"{i+1:02d}")
    
    # Gestione Colore Dinamico basato sulla Categoria salvata
    color_map = {"NONE": "#FFFFFF", "PRO": "#FF4B4B", "SEMI": "#1E90FF", "AMAT": "#00FF7F"}
    current_color = color_map.get(row['CAT'], "#FFFFFF")
    
    c[1].markdown(f"<span class='kart-font' style='color:{current_color};'>{row['KART']}</span>", unsafe_allow_html=True)
    
    # BOTTONE CAMBIO CATEGORIA (Ciclo: NONE -> PRO -> SEMI -> AMAT)
    if c[2].button(f"{row['CAT'] if row['CAT'] != 'NONE' else 'CAMBIA'}", key=f"btn_{row['KART']}"):
        cats = ["NONE", "PRO", "SEMI", "AMAT"]
        # Troviamo l'indice del kart nel dataframe originale usando il numero del kart
        idx_originale = st.session_state.data[st.session_state.data['KART'] == row['KART']].index[0]
        current_cat_idx = cats.index(st.session_state.data.at[idx_originale, 'CAT'])
        new_cat = cats[(current_cat_idx + 1) % 4]
        st.session_state.data.at[idx_originale, 'CAT'] = new_cat
        st.rerun()

    c[3].markdown(f"<p class='small-font'>{row['ULTIMO']:.2f}</p>", unsafe_allow_html=True)
    c[4].markdown(f"<p class='small-font'><b>{row['MEDIA_15']:.2f}</b></p>", unsafe_allow_html=True)
    
    stabilità = "🟢" if row['COST'] < 0.15 else "🟡" if row['COST'] < 0.3 else "🔴"
    c[5].write(stabilità)
    c[6].write(row['PIT'])
    c[7].write(row['G'])

# RALLENTAMENTO REFRESH (5 Secondi per una lettura migliore)
time.sleep(5)
st.rerun()
