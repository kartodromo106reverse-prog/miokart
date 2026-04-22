import streamlit as st
import pandas as pd
import time
import random
import numpy as np

# CONFIGURAZIONE UNIVERSALE (Android, iOS, PC)
st.set_page_config(page_title="WAR ROOM AI STRATEGY", layout="wide", initial_sidebar_state="collapsed")

# STILE OLED HIGH-CONTRAST
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    .target-box { border: 2px solid #FF3131; padding: 15px; border-radius: 10px; background-color: #111; text-align: center; }
    .kart-font { font-family: 'Courier New', monospace; font-size: 22px; font-weight: bold; }
    .stButton>button { width: 100%; height: 50px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (Sottomenu Meteo e Pista) ---
with st.sidebar:
    st.header("🛠️ Sottomenu Tecnici")
    st.selectbox("Seleziona Pista", ["SOLE LUNA VITTORIA", "106 REVERSE", "NAPOLI"])
    st.slider("Temperatura Asfalto", 10, 50, 25)
    st.radio("Meteo", ["Asciutto", "Umidità", "Pioggia"])

# --- LOGICA CORE & AI SWITCH ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i:02d}" for i in range(1, 51)],
        'CAT': ["NONE"] * 50,
        'ULTIMO': [0.0] * 50,
        'MEDIA_15': [46.0] * 50,
        'COSTANZA': [0.2] * 50,
        'CORSIA': [random.choice(['A', 'B', 'C']) for _ in range(50)],
        'GIRI_STINT': [0] * 50,
        'STORICO': [[] for _ in range(50)]
    })

def update_ai_engine():
    for i in range(50):
        t = 45.0 + random.uniform(0, 3)
        storico = st.session_state.data.at[i, 'STORICO']
        storico.append(t)
        if len(storico) > 15: storico.pop(0)
        st.session_state.data.at[i, 'ULTIMO'] = t
        st.session_state.data.at[i, 'MEDIA_15'] = np.mean(storico)
        st.session_state.data.at[i, 'COSTANZA'] = np.std(storico)
        st.session_state.data.at[i, 'GIRI_STINT'] += 1

update_ai_engine()

# --- INTERFACCIA: AI STRATEGY ASSISTANT ---
st.title("🏎️ AI War Room: Strategia Switch")

# BOX AI: Suggerimento Pescata Kart Veloci
st.subheader("🎯 ASSISTENTE AL CAMBIO (Suggerimenti Pescata)")
# Trova i kart con la media migliore (veloci) e costanti (scarto basso)
targets = st.session_state.data.sort_values(by=['MEDIA_15', 'COSTANZA']).head(3)
c_ai = st.columns(3)

for idx, (i, row) in enumerate(targets.iterrows()):
    with c_ai[idx]:
        st.markdown(f"""
        <div class="target-box">
            <h2 style="color:#FF3131; margin:0;">PESCA: KART {row['KART']}</h2>
            <p>Media: <b>{row['MEDIA_15']:.3f}</b> | Corsia: <b>{row['CORSIA']}</b><br>
            Giri Stint: <b>{row['GIRI_STINT']}</b></p>
        </div>
        """, unsafe_allow_html=True)
        if row['GIRI_STINT'] >= 25:
            st.warning(f"⚠️ KART {row['KART']} IN USCITA: PREPARARSI!")

st.write("---")

# --- TABELLA MONITORAGGIO UNIVERSALE ---
cols = st.columns([0.8, 1.2, 2, 1.8, 1.8, 1.5, 0.8, 0.8])
headers = ["POS", "KART", "CATEGORIA", "ULTIMO", "MEDIA 15G", "COST.", "PIT", "G"]
for col, h in zip(cols, headers):
    col.caption(h)

df_sorted = st.session_state.data.sort_values(by='MEDIA_15').reset_index(drop=True)

for i, row in df_sorted.iterrows():
    c = st.columns([0.8, 1.2, 2, 1.8, 1.8, 1.5, 0.8, 0.8])
    
    # Colore Categoria
    colore = "#FFF"
    if row['CAT'] == "PRO": colore = "#FF4B4B"
    elif row['CAT'] == "SEMI": colore = "#1E90FF"
    elif row['CAT'] == "GENT": colore = "#00FF7F"
    
    c[0].write(f"{i+1:02d}")
    c[1].markdown(f"<span class='kart-font' style='color:{colore};'>{row['KART']}</span>", unsafe_allow_html=True)
    
    # Switch Categoria Touch
    if c[2].button(f"{row['CAT']}", key=f"btn_{row['KART']}"):
        cats = ["NONE", "PRO", "SEMI", "GENT"]
        cur = cats.index(row['CAT'])
        orig_idx = st.session_state.data[st.session_state.data['KART'] == row['KART']].index[0]
        st.session_state.data.at[orig_idx, 'CAT'] = cats[(cur + 1) % 4]
        st.rerun()

    c[3].write(f"{row['ULTIMO']:.3f}")
    c[4].write(f"**{row['MEDIA_15']:.3f}**")
    c[5].write(f"{'🟢' if row['COSTANZA'] < 0.15 else '🟡'}{row['COSTANZA']:.2f}")
    c[6].write(row['CORSIA'])
    c[7].write(row['GIRI_STINT'])

# Refresh LIVE
time.sleep(2)
st.rerun()
