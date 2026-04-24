import streamlit as st
import pandas as pd
import time

# --- LOGICA DI CONVERSIONE ---
def to_sec(t):
    try:
        t = str(t).strip().replace(',', '.')
        if ':' in t:
            m, s = t.split(':')
            return int(m) * 60 + float(s)
        return float(t)
    except: return 999.9

# --- CONFIGURAZIONE PRO ---
st.set_page_config(page_title="WAR ROOM AUTOMATIC", layout="wide")

# CSS per rendere tutto GIGANTE e sensibile al touch
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stSelectbox div { height: 60px !important; font-size: 20px !important; }
    .stButton button { width: 100%; height: 80px; font-size: 25px !important; background-color: #ff4b4b !important; }
    .css-1offfwp { font-size: 22px !important; } /* Ingrandisce i testi della tabella */
    </style>
    """, unsafe_allow_html=True)

# 1. TENDINA PISTE
circuiti = {
    "106 Reverse": "https://live.apex-timing.com/kartodromo106reverse/",
    "106 Standard": "https://live.apex-timing.com/kartodromo106/"
}
pista = st.selectbox("📍 SELEZIONA PISTA", list(circuiti.keys()))

# 2. IL DOPPIO SCHERMO (IFRAME)
# Questo visualizza Apex direttamente dentro la tua app!
st.subheader("📺 Live Timing Apex (Sincronizzato)")
st.components.v1.iframe(circuiti[pista], height=400, scrolling=True)

st.divider()

# 3. GESTIONE STRATEGIA (Invariata ma con refresh più rapido)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(15)],
        'BEST': ["99.99"] * 15,
        'CAMBI': [0] * 15,
        'IN_PIT': [False] * 15,
        'PIT_START': [0.0] * 15
    })

# Tabella per inserire i tempi (finché non attiviamo lo scraping totale)
st.subheader("📊 Radar e Controllo Box")
edited_df = st.data_editor(
    st.session_state.data,
    column_config={
        "KART": st.column_config.TextColumn("N°", width="small"),
        "BEST": st.column_config.TextColumn("TEMPO"),
        "IN_PIT": st.column_config.CheckboxColumn("BOX"),
    },
    hide_index=True, use_container_width=True
)

# --- LOGICA AUTOMATICA ---
for i in range(len(edited_df)):
    if edited_df.at[i, 'IN_PIT'] and not st.session_state.data.at[i, 'IN_PIT']:
        edited_df.at[i, 'PIT_START'] = time.time()
    if not edited_df.at[i, 'IN_PIT'] and st.session_state.data.at[i, 'IN_PIT']:
        edited_df.at[i, 'CAMBI'] += 1

st.session_state.data = edited_df

# Dashboard Box
c1, c2 = st.columns(2)
with c1:
    st.subheader("🏎️ Top 3 In Pista")
    edited_df['V'] = edited_df['BEST'].apply(to_sec)
    top = edited_df.sort_values('V').head(3)
    for _, r in top.iterrows():
        if r['V'] < 90:
            st.error(f"⭐ KART {r['KART']} - {r['BEST']}")

with c2:
    st.subheader("🚧 Box (3 Min)")
    for _, r in edited_df[edited_df['IN_PIT']].iterrows():
        rimanente = 180 - (time.time() - r['PIT_START'])
        if rimanente > 0:
            m, s = divmod(int(rimanente), 60)
            st.warning(f"KART {r['KART']}: {m:02d}:{s:02d}")
        else:
            st.success(f"KART {r['KART']}: ✅ ESCI!")

# REFRESH CONTINUO (Ogni 2 secondi per precisione)
time.sleep(2)
st.rerun()
