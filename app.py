import random
import time
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="WAR ROOM PRO - APEX",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS CUSTOM ---
st.markdown(
    """
    <style>
    .main .block-container { padding: 8px 12px !important; background-color: #0f1116; }
    .stButton > button { width: 100% !important; border-radius: 8px !important; font-weight: 700; }
    .lane-title { font-weight: 800; text-align: center; padding: 6px; border-radius: 8px; color: white; margin-bottom: 10px; }
    .lane-verde { background: #146c43; }
    .lane-rosso { background: #9b2226; }
    .lane-giallo { background: #8c6d1f; color: #fff; }
    .lane-blu { background: #2b59a2; }
    .kpi-card { background: #1c2128; border: 1px solid #30363d; border-radius: 8px; padding: 10px; text-align: center; }
    .leader-row { border-bottom: 1px solid #30363d; padding: 5px 0; font-family: monospace; }
    header, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- COSTANTI ---
LANE_OPTIONS = ["VERDE", "ROSSO", "GIALLO", "BLU"]

# --- FUNZIONI UTILI ---
def _format_mmss(total_seconds):
    mm, ss = divmod(max(0, int(total_seconds)), 60)
    return f"{mm:02d}:{ss:02d}"

# --- INIZIALIZZAZIONE SESSIONE ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame({
        "KART": [f"{i+1:02d}" for i in range(50)],
        "TEAM": ["-"] * 50,
        "ULTIMO": [0.0] * 50,
        "BEST": [999.0] * 50,
        "IN_PIT": [False] * 50,
        "LANE": ["VERDE"] * 50,
        "PIT_START": [0.0] * 50
    })

if "apex_url" not in st.session_state:
    st.session_state.apex_url = "https://live.apex-timing.com/kartodromo106"

if "tempo_pit" not in st.session_state:
    st.session_state.tempo_pit = 180

# --- REFRESH ---
st_autorefresh(interval=2000, key="global_refresh")

# --- SIDEBAR (MODIFICA MANUALE DATI) ---
with st.sidebar:
    st.header("🛠️ Configurazione")
    st.session_state.apex_url = st.text_input("Link Apex Timing", st.session_state.apex_url)
    st.session_state.tempo_pit = st.number_input("Tempo Pit (sec)", value=st.session_state.tempo_pit)
    
    st.divider()
    st.subheader("📝 Modifica Kart Manuale")
    idx_sel = st.selectbox("Seleziona Kart da modificare", options=st.session_state.data.index, 
                           format_func=lambda x: f"Kart {st.session_state.data.at[x, 'KART']}")
    
    new_kart_no = st.text_input("Cambia Numero Kart", st.session_state.data.at[idx_sel, "KART"])
    new_team_name = st.text_input("Nome Team", st.session_state.data.at[idx_sel, "TEAM"])
    
    if st.button("Aggiorna Dati Kart"):
        st.session_state.data.at[idx_sel, "KART"] = new_kart_no
        st.session_state.data.at[idx_sel, "TEAM"] = new_team_name
        st.success("Aggiornato!")

# --- MAIN LAYOUT ---
t1, t2, t3 = st.tabs(["📊 DASHBOARD & TOP 15", "🚧 GESTIONE BOX", "🌐 LIVE APEX"])

with t1:
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("🏆 Top 15 Leaderboard")
        # Simulazione calcolo veloci (qui andrebbe il parsing Apex se avessi API)
        leaderboard = st.session_state.data.sort_values("BEST").head(15)
        for i, (idx, r) in enumerate(leaderboard.iterrows()):
            st.markdown(f"""<div class='leader-row'>
            <b>{i+1}°</b> KART {r['KART']} - {r['TEAM']} | ⏱️ {r['BEST'] if r['BEST'] < 900 else '--.--'}
            </div>""", unsafe_allow_html=True)

    with c2:
        st.subheader("⚡ Azioni Rapide")
        # Griglia per mandare i kart ai box
        k_cols = st.columns(4)
        for i in range(16): # Mostra i primi 16 per velocità d'uso
            k_id = st.session_state.data.at[i, "KART"]
            is_pit = st.session_state.data.at[i, "IN_PIT"]
            with k_cols[i % 4]:
                if not is_pit:
                    if st.button(f"📥 BOX {k_id}", key=f"quick_box_{i}"):
                        st.session_state.data.at[i, "IN_PIT"] = True
                        st.session_state.data.at[i, "PIT_START"] = time.time()
                        st.rerun()
                else:
                    st.button(f"⏳ K{k_id} BOX", disabled=True, key=f"dis_{i}")

with t2:
    st.subheader("🚧 Monitor Corsie")
    l_cols = st.columns(4)
    for i, lane in enumerate(LANE_OPTIONS):
        with l_cols[i]:
            st.markdown(f"<div class='lane-title lane-{lane.lower()}'>{lane}</div>", unsafe_allow_html=True)
            karts_in_lane = st.session_state.data[(st.session_state.data["IN_PIT"] == True) & (st.session_state.data["LANE"] == lane)]
            for idx, r in karts_in_lane.iterrows():
                elapsed = int(time.time() - r["PIT_START"])
                rem = st.session_state.tempo_pit - elapsed
                st.write(f"**KART {r['KART']}**")
                st.write(f"Mancano: **{_format_mmss(rem)}**")
                if st.button(f"RILASCIA {r['KART']}", key=f"rel_{idx}"):
                    st.session_state.data.at[idx, "IN_PIT"] = False
                    st.rerun()
                st.divider()

with t3:
    st.subheader("🌐 Apex Live Timing")
    if st.session_state.apex_url:
        components.html(f'<iframe src="{st.session_state.apex_url}" width="100%" height="800" style="border:none;"></iframe>', height=800)
    else:
        st.warning("Inserisci un link Apex nella sidebar.")
