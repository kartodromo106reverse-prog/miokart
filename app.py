import streamlit as st
import pandas as pd
import time

# 1. SETUP - LAYOUT OTALE
st.set_page_config(page_title="WAR ROOM - 4 LANES PRO", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS: GRAFICA PULITA E LINEE PIXEL PERFECT
st.markdown("""
    <style>
    .main .block-container { padding: 0px !important; background-color: #000; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    /* GRIGLIA EXCEL PROFESSIONALE */
    .grid-row { 
        display: flex; 
        border-bottom: 1px solid #333; 
        align-items: center; 
        min-height: 50px; 
        background-color: #000; 
    }
    .grid-cell { 
        border-right: 1px solid #333; 
        padding: 0px 10px; 
        height: 100%; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
    }
    
    /* TESTO GIGANTE */
    .big-num { font-size: 26px !important; font-weight: 800 !important; color: #FFF; }
    .star-icon { color: #FFD700; margin-right: 5px; font-size: 20px; }

    /* BOTTONI BOX GIGANTI E PULITI */
    .stButton>button {
        border-radius: 8px !important;
        padding: 20px 5px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        width: 100% !important;
        margin-bottom: 10px !important;
        color: white !important;
    }
    
    /* Bordi Corsie */
    .btn-verde > div > button { border: 3px solid #28a745 !important; background-color: #0a2b12 !important; }
    .btn-rossa > div > button { border: 3px solid #dc3545 !important; background-color: #2b0a0a !important; }
    .btn-gialla > div > button { border: 3px solid #ffc107 !important; background-color: #332b00 !important; color: #ffc107 !important; }
    .btn-blu > div > button { border: 3px solid #007bff !important; background-color: #001a33 !important; }

    header, footer { visibility: hidden; }
    .stTabs [data-baseweb="tab-list"] { background-color: #111; padding: 10px; border-bottom: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# 3. STATO DATI
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(50)],
        'TEAM': [f"TEAM {i+1}" for i in range(50)],
        'CAT': ["NONE"] * 50, 'STAR': [False] * 50,
        'IN_PIT': [False] * 50, 'LANE': ["VERDE"] * 50, 'PIT_START': [0.0] * 50,
        'MEDIA': [0.0] * 50, 'ULTIMO': [0.0] * 50
    })

if 'tempo_pit' not in st.session_state: st.session_state.tempo_pit = 180
if 'corsie_attive' not in st.session_state: st.session_state.corsie_attive = ["VERDE", "ROSSA"]
if 'sel_idx' not in st.session_state: st.session_state.sel_idx = 0

# --- SIDEBAR: CONTROLLO MANUALE ---
with st.sidebar:
    st.header("⚙️ CONFIG PISTA")
    st.session_state.tempo_pit = st.number_input("SECONDI PIT STOP", value=st.session_state.tempo_pit)
    st.session_state.corsie_attive = st.multiselect("ATTIVA CORSIE", ["VERDE", "ROSSA", "GIALLA", "BLU"], default=st.session_state.corsie_attive)
    
    st.write("---")
    idx = st.session_state.sel_idx
    row = st.session_state.data.iloc[idx]
    st.subheader(f"EDIT K{row['KART']}")
    st.session_state.data.at[idx, 'TEAM'] = st.text_input("NOME TEAM", row['TEAM'])
    
    if st.button("⭐ STELLA (ON/OFF)"):
        st.session_state.data.at[idx, 'STAR'] = not row['STAR']; st.rerun()
    
    cat = st.selectbox("CATEGORIA", ["NONE", "PRO", "SEMI", "AMA"])
    st.session_state.data.at[idx, 'CAT'] = cat

    st.write("---")
    if not row['IN_PIT']:
        st.write("MANDA IN BOX:")
        for c_name in st.session_state.corsie_attive:
            if st.button(f"➡️ {c_name}"):
                st.session_state.data.at[idx, 'IN_PIT'], st.session_state.data.at[idx, 'LANE'], st.session_state.data.at[idx, 'PIT_START'] = True, c_name, time.time()
                st.rerun()
    else:
        if st.button("✅ LIBERA KART", type="primary"):
            st.session_state.data.at[idx, 'IN_PIT'] = False; st.rerun()

# --- INTERFACCIA ---
tab1, tab2 = st.tabs(["🏎️ LIVE PISTA", "🚧 BOX LIVE"])

with tab1:
    # Header Tabella
    st.markdown("""<div class="grid-row" style="background-color:#111; border-bottom: 2px solid #555;">
        <div class="grid-cell" style="width:15%; font-size:12px; color:#888;">KART</div>
        <div class="grid-cell" style="width:45%; font-size:12px; color:#888;">TEAM / CATEGORIA</div>
        <div class="grid-cell" style="width:20%; font-size:12px; color:#888;">MEDIA</div>
        <div class="grid-cell" style="width:20%; border-right:none; font-size:12px; color:#888;">ULTIMO</div>
    </div>""", unsafe_allow_html=True)
    
    df_p = st.session_state.data[st.session_state.data['IN_PIT'] == False]
    for i, r in df_p.iterrows():
        cols = st.columns([0.6, 2, 1, 1])
        star = "⭐" if r['STAR'] else ""
        dot_color = {"PRO":"#FF3131","SEMI":"#1E90FF","AMA":"#00FF7F","NONE":"#444"}[r['CAT']]
        
        with cols[0]: 
            st.markdown(f'<div class="grid-row"><div class="grid-cell big-num" style="width:100%; border-right:none;">{star}{r["KART"]}</div></div>', unsafe_allow_html=True)
        with cols[1]:
            if st.button(f"● {r['TEAM']} ({r['CAT']})", key=f"t_{i}"):
                st.session_state.sel_idx = i; st.rerun()
        with cols[2]: 
            st.markdown(f'<div class="grid-row"><div class="grid-cell big-num" style="width:100%; border-right:none; color:#00FF7F;">{r["MEDIA"]:.2f}</div></div>', unsafe_allow_html=True)
        with cols[3]: 
            st.markdown(f'<div class="grid-row"><div class="grid-cell big-num" style="width:100%; border-right:none; color:#777;">{r["ULTIMO"]:.1f}</div></div>', unsafe_allow_html=True)

with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    n_corsie = len(st.session_state.corsie_attive)
    if n_corsie > 0:
        cols_box = st.columns(n_corsie)
        for i, c_name in enumerate(st.session_state.corsie_attive):
            with cols_box[i]:
                c_color = {"VERDE":"#28a745","ROSSA":"#dc3545","GIALLA":"#ffc107","BLU":"#007bff"}[c_name]
                css_c = {"VERDE":"btn-verde","ROSSA":"btn-rossa","GIALLA":"btn-gialla","BLU":"btn-blu"}[c_name]
                st.markdown(f"<h3 style='color:{c_color}; text-align:center; border-bottom: 2px solid {c_color}; padding-bottom:5px;'>{c_name}</h3>", unsafe_allow_html=True)
                
                q = st.session_state.data[(st.session_state.data['IN_PIT'] == True) & (st.session_state.data['LANE'] == c_name)]
                for idx, r in q.iterrows():
                    rem = max(0, st.session_state.tempo_pit - (time.time() - r['PIT_START']))
                    m, s = divmod(int(rem), 60)
                    st.markdown(f'<div class="{css_c}">', unsafe_allow_html=True)
                    if st.button(f"K{r['KART']}\n⏳ {m:02d}:{s:02d}", key=f"bx_{idx}"):
                        st.session_state.data.at[idx, 'IN_PIT'] = False; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

time.sleep(5)
st.rerun()
