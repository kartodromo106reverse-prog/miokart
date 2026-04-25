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
    page_title="WAR ROOM MONITOR - KARTING",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- STILI CSS AVANZATI ---
st.markdown(
    """
    <style>
    .main .block-container { padding: 8px 12px !important; background-color: #0f1116; }
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    
    /* Touch Cards */
    .touch-card {
        border: 2px solid #2f3640;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 8px;
        text-align: center;
        transition: transform 0.1s;
    }
    .touch-card:active { transform: scale(0.96); }
    
    .touch-fast { background: linear-gradient(135deg, #0f5132, #198754); border-color: #22c55e; }
    .touch-mid { background: linear-gradient(135deg, #5c4a1f, #b08a26); border-color: #f59e0b; }
    .touch-slow { background: linear-gradient(135deg, #6b1f1f, #bc2f2f); border-color: #ef4444; }
    .touch-pit { background: linear-gradient(135deg, #1f3b6b, #3b82f6); border-color: #60a5fa; animation: pulse 2s infinite; }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }

    .lane-title {
        font-weight: 800;
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        color: white;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .lane-verde { background: #146c43; }
    .lane-rosso { background: #9b2226; }
    .lane-giallo { background: #8c6d1f; }
    .lane-blu { background: #2b59a2; }

    .timer-critical { color: #ef4444; font-weight: 900; font-size: 1.4rem; }
    .timer-ok { color: #22c55e; font-weight: 700; font-size: 1.2rem; }
    
    header, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- COSTANTI ---
LANE_OPTIONS = ["VERDE", "ROSSO", "GIALLO", "BLU"]
CAT_OPTIONS = ["NONE", "PRO", "SEMI", "AMA"]

# --- UTILS ---
def _safe_float(value):
    try:
        return float(str(value).replace(",", ".")) if value is not None else None
    except: return None

def _safe_kart(value):
    if not value: return None
    raw = str(value).strip()
    return raw.zfill(2) if raw.isdigit() else raw

def _format_mmss(total_seconds):
    mm, ss = divmod(max(0, int(total_seconds)), 60)
    return f"{mm:02d}:{ss:02d}"

# --- CORE LOGIC ---
def init_state():
    if "auth_status" not in st.session_state: st.session_state.auth_status = "guest"
    if "data" not in st.session_state:
        st.session_state.data = pd.DataFrame({
            "KART": [f"{i+1:02d}" for i in range(50)],
            "TEAM": ["-"] * 50,
            "CAT": ["NONE"] * 50,
            "ULTIMO": [0.0] * 50,
            "MEDIA": [0.0] * 50,
            "BEST": [999.0] * 50,
            "LAPS": [0] * 50,
            "IN_PIT": [False] * 50,
            "LANE": ["VERDE"] * 50,
            "PIT_START": [0.0] * 50,
            "PIT_COUNT": [0] * 50,
            "ALERT": ["N/A"] * 50
        })
    if "lap_history" not in st.session_state: st.session_state.lap_history = []
    if "pista_nome" not in st.session_state: st.session_state.pista_nome = "Circuit"
    if "best_lap_pista" not in st.session_state: st.session_state.best_lap_pista = 45.0
    if "lap_green_threshold" not in st.session_state: st.session_state.lap_green_threshold = 45.5
    if "lap_yellow_threshold" not in st.session_state: st.session_state.lap_yellow_threshold = 46.5
    if "tempo_pit" not in st.session_state: st.session_state.tempo_pit = 180
    if "corsie_attive" not in st.session_state: st.session_state.corsie_attive = ["VERDE"]
    if "apex_url" not in st.session_state: st.session_state.apex_url = ""
    if "live_karts" not in st.session_state: st.session_state.live_karts = []

def sync_data(live_list):
    now = time.time()
    for item in live_list:
        k = _safe_kart(item['KART'])
        t = _safe_float(item['TIME'])
        mask = st.session_state.data["KART"] == k
        if mask.any() and t:
            idx = st.session_state.data[mask].index[0]
            if st.session_state.data.at[idx, "IN_PIT"]: continue
            
            # Aggiornamento statistiche
            old_avg = st.session_state.data.at[idx, "MEDIA"]
            st.session_state.data.at[idx, "ULTIMO"] = t
            st.session_state.data.at[idx, "MEDIA"] = t if old_avg == 0 else (old_avg * 0.8 + t * 0.2)
            st.session_state.data.at[idx, "BEST"] = min(st.session_state.data.at[idx, "BEST"], t)
            st.session_state.data.at[idx, "LAPS"] += 1
            
            # Alert
            if t <= st.session_state.lap_green_threshold: alert = "FAST"
            elif t <= st.session_state.lap_yellow_threshold: alert = "MID"
            else: alert = "SLOW"
            st.session_state.data.at[idx, "ALERT"] = alert
            
            # History (limitata a 1000 per performance)
            st.session_state.lap_history.append({"KART": k, "TIME": t, "TS": now})
            if len(st.session_state.lap_history) > 1000: st.session_state.lap_history.pop(0)

# --- UI COMPONENTS ---
def render_login():
    st.title("🛡️ STRATEGY HUB LOGIN")
    with st.form("login"):
        team = st.text_input("Nome Team")
        kart = st.text_input("Kart ID")
        if st.form_submit_button("ACCEDI"):
            st.session_state.auth_status = "team"
            st.session_state.team_name = team
            st.rerun()

def render_war_room():
    st_autorefresh(interval=2000, key="global_refresh")
    
    # Sidebar per controlli rapidi
    with st.sidebar:
        st.header("⚙️ Settings")
        st.session_state.best_lap_pista = st.number_input("Rif. Pista", value=st.session_state.best_lap_pista)
        st.session_state.tempo_pit = st.number_input("Tempo Pit (sec)", value=st.session_state.tempo_pit)
        st.session_state.corsie_attive = st.multiselect("Corsie Box", LANE_OPTIONS, default=st.session_state.corsie_attive)
        if st.button("RESET DATI"):
            st.session_state.data["LAPS"] = 0
            st.rerun()

    t1, t2, t3 = st.tabs(["🏎️ LIVE TRACK", "🚧 PIT BOARD", "📊 ANALYTICS"])
    
    with t1:
        # Simulazione o API Apex (Qui puoi inserire la tua fetch_apex_data)
        # Per ora usiamo una simulazione per test immediato
        sim_data = [{"KART": f"{i+1:02d}", "TIME": round(st.session_state.best_lap_pista + random.uniform(0, 2), 3)} for i in range(12)]
        sync_data(sim_data)
        
        cols = st.columns(4)
        for i, row in enumerate(sim_data):
            k_id = row['KART']
            k_time = row['TIME']
            with cols[i % 4]:
                style = "touch-fast" if k_time <= st.session_state.lap_green_threshold else "touch-slow"
                st.markdown(f"<div class='touch-card {style}'><b>KART {k_id}</b><br>{k_time:.3f}s</div>", unsafe_allow_html=True)
                if st.button(f"BOX {k_id}", key=f"btn_{k_id}"):
                    idx = st.session_state.data[st.session_state.data["KART"] == k_id].index[0]
                    st.session_state.data.at[idx, "IN_PIT"] = True
                    st.session_state.data.at[idx, "PIT_START"] = time.time()
                    st.rerun()

    with t2:
        st.subheader("Gestione Corsie")
        p_cols = st.columns(len(st.session_state.corsie_attive))
        for i, lane in enumerate(st.session_state.corsie_attive):
            with p_cols[i]:
                st.markdown(f"<div class='lane-title lane-{lane.lower()}'>{lane}</div>", unsafe_allow_html=True)
                pit_karts = st.session_state.data[st.session_state.data["IN_PIT"] == True]
                for idx, r in pit_karts.iterrows():
                    elapsed = time.time() - r["PIT_START"]
                    rem = st.session_state.tempo_pit - elapsed
                    color = "timer-critical" if rem < 30 else "timer-ok"
                    st.markdown(f"**KART {r['KART']}**")
                    st.markdown(f"<span class='{color}'>{_format_mmss(rem)}</span>", unsafe_allow_html=True)
                    if st.button(f"RELEASE {r['KART']}", key=f"rel_{idx}"):
                        st.session_state.data.at[idx, "IN_PIT"] = False
                        st.session_state.data.at[idx, "PIT_COUNT"] += 1
                        st.rerun()
                    st.divider()

    with t3:
        st.dataframe(st.session_state.data[st.session_state.data["LAPS"] > 0].sort_values("BEST"), use_container_width=True)

# --- RUN ---
init_state()
if st.session_state.auth_status == "guest":
    render_login()
else:
    render_war_room()
