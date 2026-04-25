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
    }
    .small-muted { color: #9ca3af; font-size: 12px; }
    .lane-title {
        font-weight: 800;
        letter-spacing: 0.5px;
        text-align: center;
        padding: 6px;
        border-radius: 8px;
        color: white;
    }
    .lane-verde { background: #146c43; }
    .lane-rosso { background: #9b2226; }
    .lane-giallo { background: #8c6d1f; color: #fff; }
    .lane-blu { background: #2b59a2; }
    .alert-ok { color: #22c55e; font-weight: 700; }
    .alert-warn { color: #f59e0b; font-weight: 700; }
    .alert-danger { color: #ef4444; font-weight: 700; }
    header, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

LANE_OPTIONS = ["VERDE", "ROSSO", "GIALLO", "BLU"]
CAT_OPTIONS = ["NONE", "PRO", "SEMI", "AMA"]

def _safe_float(value):
    try:
        if value is None: return None
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError): return None

def _safe_kart(value):
    if value is None: return None
    raw = str(value).strip()
    if not raw: return None
    return raw.zfill(2) if raw.isdigit() else raw

def _format_mmss(total_seconds):
    rem = max(0, int(total_seconds))
    mm, ss = divmod(rem, 60)
    return f"{mm:02d}:{ss:02d}"

def _lane_css_class(lane):
    lane_lower = str(lane).strip().lower()
    if lane_lower == "verde": return "lane-verde"
    if lane_lower == "rosso": return "lane-rosso"
    if lane_lower == "giallo": return "lane-giallo"
    return "lane-blu"

def fetch_apex_data(api_url):
    if not api_url: return None
    try:
        response = requests.get(api_url, timeout=4)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError): return None

def parse_apex_live_karts(payload):
    if payload is None: return []
    if isinstance(payload, list):
        candidates = payload
    elif isinstance(payload, dict):
        candidates = (
            payload.get("karts") or payload.get("drivers") or payload.get("results") or 
            payload.get("classification") or payload.get("entries") or payload.get("data") or []
        )
    else: candidates = []
    
    if not isinstance(candidates, list): return []
    live = []
