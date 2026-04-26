import random
import time
import requests
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURAZIONE E STILE (FIXED)
st.set_page_config(page_title="WAR ROOM 106", layout="wide")

st.markdown("""
    <style>
    .main .block-container { padding: 8px 12px !important; background-color: #0f1116; }
    .stButton > button { width: 100% !important; border-radius: 10px !important; font-weight: 700; }
    .touch-card { border: 1px solid #2f3640; border-radius: 10px; padding: 10px; margin-bottom: 8px; text-align: center; }
    .touch-fast { background: linear-gradient(135deg, #0f5132, #146c43); border: 1px solid #00FF7F; }
    .touch-mid { background: linear-gradient(135deg, #5c4a1f, #8c6d1f); border: 1px solid #FFD700; }
    .touch-slow { background: linear-gradient(135deg, #6b1f1f, #9b2226); border: 1px solid #ff4b4b; }
    .touch-pit { background: linear-gradient(135deg, #1f3b6b, #2b59a2); opacity: 0.6; }
    .kpi-box { border: 1px solid #2f3640; background: #141923; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
    .lane-title { font-weight: 800; text-align: center; padding: 8px; border-radius: 8px; color: white; margin-bottom: 10px; }
    .lane-verde { background: #146c43; } 
    .lane-rosso { background: #9b2226; } 
    .lane-giallo { background: #8c6d1f; } 
    .lane-blu { background: #2b59a2; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNZIONI TECNICHE
def _safe_float(value):
    try: return float(str(value).replace(",", "."))
    except: return 99.999

def _format_mmss(total_seconds):
    mm, ss = divmod(max(0, int(total_seconds)), 60)
    return f"{mm:02d}:{ss:02d}"

def _lane_css(lane):
    return f"lane-{lane.lower()}"

def fetch_apex_data(url):
    if not url: return None
    try:
        r = requests.get(url, timeout=3, headers={'User-Agent': 'Mozilla/5.0'})
        return r.json()
    except: return None

# 3. STATO SESSIONE
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame({'KART': [f"{i+1:02d}" for i in range(50)], 'BEST': ["99.999"] * 50})

if "pit_events" not in st.session_state: st.session_state.pit_events = []
if "live_karts" not in st.session_state: st.session_state.live_karts = []
if "apex_url" not in st.session_state: st.session_state.apex_url = ""
if "tempo_pit" not in st.session_state: st.session_state.tempo_pit = 180

# 4. LOGICA CLASSIFICA
def get_top_15():
    if st.session_state.live_karts:
        return st.session_state.live_karts[:15]
    df_m = st.session_state.data.copy()
    df_m['V'] = df_m['BEST'].apply(_safe_float)
    df_m = df_m[df_m['V'] < 90].sort_values('V').head(15)
    res = []
    for i, r in df_m.iterrows():
        res.append({"KART": r['KART'], "TIME": r['V'], "POS": len(res)+1})
    return res

# 5. INTERFACCIA
st_autorefresh(interval=1500, key="refresh")

tab1, tab2, tab3 = st.tabs(["🏎️ LIVE", "🚧 BOX", "⚙️ SETUP"])

with tab1:
    st.subheader("Top 15 Live")
    top = get_top_15()
    if not top: st.info("Nessun tempo registrato.")
    cols = st.columns(4)
    for i, k in enumerate(top):
        with cols[i % 4]:
            t = float(k['TIME'])
            style = "touch-fast" if t < 44.0 else "touch-mid" if t < 45.0 else "touch-slow"
            if any(p['KART'] == k['KART'] for p in st.session_state.pit_events): style = "touch-pit"
            st.markdown(f'<div class="touch-card {style}"><b>KART {k["KART"]}</b><br>{t:.3f}s</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("Gestione Soste")
    c1, c2, c3 = st.columns([2,2,1])
    with c1: knum = st.text_input("N. Kart (1-100):", key="k_manual")
    with c2: lane = st.selectbox("Corsia:", ["VERDE", "ROSSO", "GIALLO", "BLU"])
    with c3: 
        st.write("##")
        if st.button("ENTRA"):
            if knum:
                st.session_state.pit_events.append({"KART": knum.zfill(2), "START": time.time(), "LANE": lane})
                st.rerun()
    
    st.divider()
    lcols = st.columns(4)
    for i, l in enumerate(["VERDE", "ROSSO", "GIALLO", "BLU"]):
        with lcols[i]:
            st.markdown(f'<div class="lane-title {_lane_css(l)}">{l}</div>', unsafe_allow_html=True)
            for ev in [e for e in st.session_state.pit_events if e['LANE'] == l]:
                rim = st.session_state.tempo_pit - (time.time() - ev['START'])
                color = "#ef4444" if rim > 0 else "#22c55e"
                st.markdown(f'<div class="kpi-box" style="border-left:5px solid {color}"><b>K {ev["KART"]}</b><br><span style="color:{color}; font-size:20px;">{_format_mmss(rim) if rim > 0 else "ESCI!"}</span></div>', unsafe_allow_html=True)
                if st.button("LIBERA", key=f"rel_{ev['KART']}_{ev['START']}"):
                    st.session_state.pit_events.remove(ev)
                    st.rerun()

with tab3:
    st.session_state.apex_url = st.text_input("Link JSON Apex:", value=st.session_state.apex_url)
    st.session_state.tempo_pit = st.number_input("Secondi Sosta:", value=st.session_state.tempo_pit)
    st.divider()
    st.subheader("Radar Manuale")
    st.session_state.data = st.data_editor(st.session_state.data, use_container_width=True, hide_index=True)
