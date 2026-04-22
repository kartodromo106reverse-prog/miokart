import streamlit as st
import pandas as pd
import time
import random

# 1. SETUP
st.set_page_config(page_title="WAR ROOM PRO", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS: GRIGLIA EXCEL E BOX GIGANTI
st.markdown("""
    <style>
    .main .block-container { padding: 0px !important; background-color: #000000; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    /* GRIGLIA EXCEL LIVE */
    .grid-row {
        display: flex;
        border-bottom: 2px solid #444; 
        align-items: center;
        background-color: #000;
        min-height: 40px;
    }
    .grid-cell {
        border-right: 1px solid #444;
        padding: 0px 8px;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* FONT GRANDI */
    .big-num { font-size: 22px !important; font-weight: 900 !important; color: #FFFFFF; }
    .box-timer { font-size: 24px !important; font-weight: bold; color: #FF3131; }
    .box-team { font-size: 18px !important; color: #1E90FF; font-weight: bold; }

    /* BOTTONI BOX GIGANTI */
    .stButton>button {
        background-color: #111 !important;
        border: 1px solid #444 !important;
        color: #FFFFFF !important;
        font-size: 18px !important;
        padding: 15px 10px !important;
        height: auto !important;
        width: 100% !important;
        margin-bottom: 5px !important;
        text-align: left !important;
    }
    
    /* Tabella Live: Bottoni Team */
    .live-team-btn > div > div > button {
        background: transparent !important;
        border: none !important;
        color: #1E90FF !important;
        font-size: 18px !important;
        text-align: left !important;
        padding: 0 !important;
    }

    header, footer { visibility: hidden; }
    .stTabs [data-baseweb="tab-list"] { background-color: #111; padding: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. STATO DATI
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(40)],
        'TEAM': [f"TEAM {i+1}" for i in range(40)],
        'CAT': ["NONE"] * 40, 'STAR': [False] * 40,
        'ULTIMO': [0.0] * 40, 'MEDIA': [0.0] * 40,
        'IN_PIT': [False] * 40, 'LANE': ["V"] * 40, 'PIT_START': [0.0] * 40
    })
if 'apex_url' not in st.session_state: st.session_state.apex_url = ""
if 'sel_idx' not in st.session_state: st.session_state.sel_idx = 0

# --- SIDEBAR ---
with st.sidebar:
    st.header("🏁 CONFIG")
    st.session_state.apex_url = st.text_input("URL APEX", st.session_state.apex_url)
    st.write("---")
    idx = st.session_state.sel_idx
    st.subheader(f"EDIT KART {st.session_state.data.at[idx, 'KART']}")
    st.session_state.data.at[idx, 'TEAM'] = st.text_input("NOME TEAM", st.session_state.data.at[idx, 'TEAM'])
    if st.button("⭐ STELLA"): st.session_state.data.at[idx, 'STAR'] = not st.session_state.data.at[idx, 'STAR']; st.rerun()
    
    if not st.session_state.data.at[idx, 'IN_PIT']:
        c = st.columns(2)
        if c[0].button("🟢 V"): 
            st.session_state.data.at[idx, 'IN_PIT'], st.session_state.data.at[idx, 'LANE'], st.session_state.data.at[idx, 'PIT_START'] = True, "VERDE", time.time()
            st.rerun()
        if c[1].button("🔴 R"): 
            st.session_state.data.at[idx, 'IN_PIT'], st.session_state.data.at[idx, 'LANE'], st.session_state.data.at[idx, 'PIT_START'] = True, "ROSSO", time.time()
            st.rerun()
    else:
        if st.button("✅ ESCI BOX"): st.session_state.data.at[idx, 'IN_PIT'] = False; st.rerun()

# --- INTERFACCIA ---
tab_live, tab_box, tab_apex = st.tabs(["🏎️ LIVE", "🚧 BOX", "🌐 APEX"])

with tab_live:
    # Header Excel
    st.markdown("""
        <div class="grid-row" style="background-color: #222;">
            <div class="grid-cell" style="width: 15%; font-size: 12px;">K</div>
            <div class="grid-cell" style="width: 45%; font-size: 12px;">TEAM</div>
            <div class="grid-cell" style="width: 20%; font-size: 12px;">MEDIA</div>
            <div class="grid-cell" style="width: 20%; border-right: none; font-size: 12px;">ULT</div>
        </div>
    """, unsafe_allow_html=True)

    df_pista = st.session_state.data[st.session_state.data['IN_PIT'] == False]
    for i, row in df_pista.iterrows():
        cols = st.columns([0.6, 2.0, 1.0, 1.0])
        star = "⭐" if row['STAR'] else ""
        with cols[0]: st.markdown(f'<div class="grid-row"><div class="grid-cell big-num" style="width:100%; border-right:none;">{star}{row["KART"]}</div></div>', unsafe_allow_html=True)
        with cols[1]:
            st.markdown('<div class="live-team-btn">', unsafe_allow_html=True)
            if st.button(f"{row['TEAM']}", key=f"btn_{i}"):
                st.session_state.sel_idx = i
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with cols[2]: st.markdown(f'<div class="grid-row"><div class="grid-cell big-num" style="width:100%; border-right:none; color:#00FF7F;">{row["MEDIA"]:.2f}</div></div>', unsafe_allow_html=True)
        with cols[3]: st.markdown(f'<div class="grid-row"><div class="grid-cell big-num" style="width:100%; border-right:none; color:#777;">{row["ULTIMO"]:.1f}</div></div>', unsafe_allow_html=True)

with tab_box:
    col_v, col_r = st.columns(2)
    with col_v:
        st.markdown("<h3 style='color:green; font-size:15px; text-align:center;'>🟢 CORSIA VERDE</h3>", unsafe_allow_html=True)
        q_v = st.session_state.data[(st.session_state.data['IN_PIT'] == True) & (st.session_state.data['LANE'] == "VERDE")]
        for idx, r in q_v.iterrows():
            elapsed = time.time() - r['PIT_START']
            rem = max(0, 180 - elapsed)
            m, s = divmod(int(rem), 60)
            # Bottone GIGANTE per il BOX
            if st.button(f"K{r['KART']} - {r['TEAM']}\n⏳ {m:02d}:{s:02d}", key=f"bx_{idx}"):
                st.session_state.sel_idx = idx
                st.rerun()

    with col_r:
        st.markdown("<h3 style='color:red; font-size:15px; text-align:center;'>🔴 CORSIA ROSSA</h3>", unsafe_allow_html=True)
        q_r = st.session_state.data[(st.session_state.data['IN_PIT'] == True) & (st.session_state.data['LANE'] == "ROSSO")]
        for idx, r in q_r.iterrows():
            elapsed = time.time() - r['PIT_START']
            rem = max(0, 180 - elapsed)
            m, s = divmod(int(rem), 60)
            if st.button(f"K{r['KART']} - {r['TEAM']}\n⏳ {m:02d}:{s:02d}", key=f"bxr_{idx}"):
                st.session_state.sel_idx = idx
                st.rerun()

with tab_apex:
    if st.session_state.apex_url:
        st.markdown(f'<iframe src="{st.session_state.apex_url}" width="100%" height="1000px" style="border:none;"></iframe>', unsafe_allow_html=True)
    else:
        st.info("Incolla l'URL Apex nella Sidebar.")

time.sleep(5) # Refresh più veloce per i box
st.rerun()
