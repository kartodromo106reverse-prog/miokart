import streamlit as st
import pandas as pd
import time

# --- FUNZIONE CONVERSIONE (Supporta 43.123 e 1:12.123) ---
def to_sec(t):
    try:
        t = str(t).strip().replace(',', '.')
        if ':' in t:
            m, s = t.split(':')
            return int(m) * 60 + float(s)
        return float(t)
    except: return 999.9

# --- CONFIGURAZIONE LAYOUT TOUCH ---
st.set_page_config(page_title="WAR ROOM PRO", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stLinkButton>a { width: 100% !important; height: 80px !important; display: flex !important; align-items: center !important; justify-content: center !important; font-size: 22px !important; background-color: #ff4b4b !important; color: white !important; font-weight: bold !important; border-radius: 15px !important; text-decoration: none !important; }
    [data-testid="stDataEditor"] div div div div { line-height: 50px !important; font-size: 22px !important; }
    .timer-wait { color: #FF3131; font-weight: bold; font-size: 30px; }
    .timer-ok { color: #00FF7F; font-weight: bold; font-size: 30px; }
    .radar-card { background-color: #1e2129; border-left: 8px solid #ff4b4b; padding: 15px; border-radius: 10px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- TENDINA PISTE ---
circuiti = {
    "Kart 106 Reverse": "https://live.apex-timing.com/kartodromo106reverse/",
    "Kart 106 Standard": "https://live.apex-timing.com/kartodromo106/",
    "Circuito di Siena": "https://live.apex-timing.com/siena/"
}
scelta = st.selectbox("📍 Seleziona Circuito", list(circuiti.keys()))
st.link_button(f"🚀 APRI LIVE {scelta.upper()}", circuiti[scelta])

# --- DATABASE ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(15)],
        'BEST': ["99.999"] * 15,
        'CAMBI': [0] * 15,
        'IN_PIT': [False] * 15,
        'PIT_START': [0.0] * 15
    })

# --- TABELLA GESTIONE (Sbloccata per cambiare numeri kart) ---
st.subheader("📊 Controllo Strategia")
target_in = st.text_input("🎯 Soglia Record (es. 43.500):", value="43.500")
t_val = to_sec(target_in)

edited_df = st.data_editor(
    st.session_state.data,
    column_config={
        "KART": st.column_config.TextColumn("N°", disabled=False),
        "BEST": st.column_config.TextColumn("TEMPO"),
        "CAMBI": st.column_config.NumberColumn("🔁", disabled=True),
        "IN_PIT": st.column_config.CheckboxColumn("BOX"),
    },
    hide_index=True, use_container_width=True
)

# --- LOGICA CAMBI E COUNTDOWN ---
for i in range(len(edited_df)):
    # Se clicco BOX: registra l'ora
    if edited_df.at[i, 'IN_PIT'] and not st.session_state.data.at[i, 'IN_PIT']:
        edited_df.at[i, 'PIT_START'] = time.time()
    
    # Se tolgo BOX: aggiunge un cambio in automatico
    if not edited_df.at[i, 'IN_PIT'] and st.session_state.data.at[i, 'IN_PIT']:
        edited_df.at[i, 'CAMBI'] += 1

st.session_state.data = edited_df

# --- DASHBOARD STATISTICA ---
st.divider()
c1, c2 = st.columns(2)

with c1:
    st.subheader("🌟 Radar Veloci")
    edited_df['V'] = edited_df['BEST'].apply(to_sec)
    veloci = edited_df[edited_df['V'] <= t_val].sort_values('V')
    if not veloci.empty:
        for _, r in veloci.iterrows():
            st.markdown(f"<div class='radar-card'><b>KART {r['KART']}</b>: {r['BEST']}s (Cambi: {r['CAMBI']})</div>", unsafe_allow_html=True)
    else: st.write("Nessuno sotto soglia.")

with c2:
    st.subheader("🚧 Countdown Box")
    pittati = edited_df[edited_df['IN_PIT']]
    if not pittati.empty:
        for _, r in pittati.iterrows():
            rimanente = 180 - (time.time() - r['PIT_START'])
            if rimanente > 0:
                m, s = divmod(int(rimanente), 60)
                st.markdown(f"KART **{r['KART']}**: <span class='timer-wait'>{m:02d}:{s:02d}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"KART **{r['KART']}**: <span class='timer-ok'>✅ ESCI!</span>", unsafe_allow_html=True)
    else: st.write("Box vuoti.")

# --- IL SEGRETO: REFRESH AUTOMATICO OGNI SECONDO ---
time.sleep(1)
st.rerun()
