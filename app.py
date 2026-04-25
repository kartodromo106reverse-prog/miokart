import random
import time
from html import escape
from statistics import mean
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="WAR ROOM MONITOR - COMPLETE",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- STILI CSS ---
st.markdown(
    """
    <style>
    .main .block-container { padding: 8px 12px !important; background-color: #0f1116; }
    [data-testid="stVerticalBlock"] { gap: 0.55rem !important; }
    .stButton > button {
        width: 100% !important;
        border-radius: 10px !important;
        min-height: 44px;
        font-weight: 700;
    }
    .touch-card {
        border: 1px solid #2f3640;
        border-radius: 10px;
        padding: 8px;
        margin-bottom: 6px;
        text-align: center;
    }
    .touch-fast { background: linear-gradient(135deg, #0f5132, #146c43); }
    .touch-mid { background: linear-gradient(135deg, #5c4a1f, #8c6d1f); }
    .touch-slow { background: linear-gradient(135deg, #6b1f1f, #9b2226); }
    .touch-pit { background: linear-gradient(135deg, #1f3b6b, #2b59a2); }
    .kpi-box {
        border: 1px solid #2f3640;
        background: #141923;
        border-radius: 10px;
        padding: 8px 10px;
        text-align: center;
    }
    .lane-title {
        font-weight: 800;
        text-align: center;
        padding: 6px;
        border-radius: 8px;
        color: white;
        margin-bottom: 10px;
    }
    .lane-verde { background: #146c43; }
    .lane-rosso { background: #9b2226; }
    .lane-giallo { background: #8c6d1f; color: #fff; }
    .lane-blu { background: #2b59a2; }
    .alert-ok { color: #22c55e; font-weight: 700; }
    .alert-warn { color: #f59e0b; font-weight: 700; }
    .alert-danger { color: #ef4444; font-weight: 700; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.3; } }
    header, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- COSTANTI ---
LANE_OPTIONS = ["VERDE", "ROSSO", "GIALLO", "BLU"]
CAT_OPTIONS = ["NONE", "PRO", "SEMI", "AMA"]

# --- FUNZIONI UTILI ---
def _safe_float(value):
    try:
        if value is None: return None
        return float(str(value).replace(",", "."))
    except: return None

def _safe_kart(value):
    if value is None: return None
    raw = str(value).strip()
    return raw.zfill(2) if raw.isdigit() else raw

def _format_mmss(total_seconds):
    mm, ss = divmod(max(0, int(total_seconds)), 60)
    return f"{mm:02d}:{ss:02d}"

# --- STATO SESSIONE ---
def init_state():
    if "auth_status" not in st.session_state: st.session_state.auth_status = "guest"
    if "pista_nome" not in st.session_state: st.session_state.pista_nome = "Kartodromo 106"
    if "best_lap_pista" not in st.session_state: st.session_state.best_lap_pista = 43.500
    if "lap_green_threshold" not in st.session_state: st.session_state.lap_green_threshold = 43.800
    if "lap_yellow_threshold" not in st.session_state: st.session_state.lap_yellow_threshold = 44.400
    if "tempo_pit" not in st.session_state: st.session_state.tempo_pit = 180
    if "corsie_attive" not in st.session_state: st.session_state.corsie_attive = LANE_OPTIONS.copy()
    if "data" not in st.session_state:
        st.session_state.data = pd.DataFrame({
            "KART": [f"{i + 1:02d}" for i in range(50)],
            "TEAM": [f"T{i + 1}" for i in range(50)],
            "CAT": ["NONE"] * 50,
            "ULTIMO": [0.0] * 50,
            "MEDIA": [0.0] * 50,
            "BEST": [999.0] * 50,
            "LAPS": [0] * 50,
            "IN_PIT": [False] * 50,
            "LANE": ["VERDE"] * 50,
            "PIT_START": [0.0] * 50,
            "PIT_COUNT": [0] * 50,
            "ALERT": ["N/A"] * 50,
        })

# --- AZIONI ---
def send_to_box(kart_id, lane="VERDE"):
    mask = st.session_state.data["KART"] == _safe_kart(kart_id)
    if mask.any():
        idx = st.session_state.data[mask].index[0]
        st.session_state.data.at[idx, "IN_PIT"] = True
        st.session_state.data.at[idx, "LANE"] = lane
        st.session_state.data.at[idx, "PIT_START"] = time.time()
        st.session_state.data.at[idx, "PIT_COUNT"] += 1

def release_from_box(idx):
    st.session_state.data.at[idx, "IN_PIT"] = False

# --- COMPONENTI UI ---
def render_live_tab():
    st.subheader("🏎️ Live Timing Touch")
    # Griglia per i pulsanti dei Kart
    cols = st.columns(4)
    for i in range(16):
        k_id = f"{i+1:02d}"
        mask = st.session_state.data["KART"] == k_id
        in_pit = st.session_state.data[mask]["IN_PIT"].iloc[0] if mask.any() else False
        
        with cols[i % 4]:
            if in_pit:
                st.markdown(f"<div class='touch-card touch-pit'>KART {k_id}<br>AI BOX</div>", unsafe_allow_html=True)
                st.button(f"SBLOCCA {k_id}", key=f"unl_{k_id}", on_click=release_from_box, args=(st.session_state.data[mask].index[0],))
            else:
                st.markdown(f"<div class='touch-card touch-fast'>KART {k_id}<br>IN PISTA</div>", unsafe_allow_html=True)
                if st.button(f"BOX {k_id}", key=f"box_{k_id}"):
                    send_to_box(k_id)
                    st.rerun()

def render_box_tab():
    st.subheader("🚧 GESTIONE BOX")
    lanes = st.session_state.corsie_attive
    cols = st.columns(len(lanes))
    for i, lane in enumerate(lanes):
        with cols[i]:
            st.markdown(f"<div class='lane-title lane-{lane.lower()}'>CORSIA {lane}</div>", unsafe_allow_html=True)
            in_lane = st.session_state.data[(st.session_state.data["IN_PIT"] == True) & (st.session_state.data["LANE"] == lane)]
            for idx, row in in_lane.iterrows():
                elapsed = int(time.time() - row["PIT_START"])
                rem = st.session_state.tempo_pit - elapsed
                color = "alert-danger" if rem < 30 else "alert-ok"
                st.markdown(f"**K{row['KART']}** | <span class='{color}'>{_format_mmss(rem)}</span>", unsafe_allow_html=True)
                if st.button(f"RELEASE K{row['KART']}", key=f"rel_{idx}"):
                    release_from_box(idx)
                    st.rerun()
                st.divider()

def render_war_room():
    st_autorefresh(interval=2000, key="refresh")
    with st.sidebar:
        st.header("⚙️ Config")
        st.session_state.tempo_pit = st.number_input("Tempo Pit (sec)", value=st.session_state.tempo_pit)
        st.session_state.corsie_attive = st.multiselect("Corsie Box", LANE_OPTIONS, default=st.session_state.corsie_attive)
        if st.button("RESET GARA"):
            st.session_state.data["IN_PIT"] = False
            st.rerun()

    t1, t2 = st.tabs(["🏎️ LIVE TIMING", "🚧 GESTIONE BOX"])
    with t1: render_live_tab()
    with t2: render_box_tab()

# --- MAIN ---
init_state()
if st.session_state.auth_status == "guest":
    st.title("🛡️ Accesso War Room")
    if st.button("ENTRA"):
        st.session_state.auth_status = "team"
        st.rerun()
else:
    render_war_room()
