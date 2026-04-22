import streamlit as st
import pandas as pd
import time

# 1. CONFIGURAZIONE LAYOUT
st.set_page_config(page_title="WAR ROOM - TOTAL CONTROL", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS DEFINITIVO (NON TOCCARE LE LINEE E I MARGINI)
st.markdown("""
    <style>
    .main .block-container { padding: 0px !important; background-color: #000; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    /* GRIGLIA EXCEL PIXEL PERFECT */
    .grid-row { 
        display: flex; 
        border-bottom: 1px solid #333; 
        align-items: center; 
        min-height: 55px; /* Aumentato per touch migliore */
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
    
    /* TESTO GIGANTE E ALLINEATO */
    .big-num { font-size: 26px !important; font-weight: 800 !important; color: #FFF; }
    .team-btn-text { font-size: 18px !important; font-weight: bold; text-align: left; width: 100%; }

    /* BOTTONI BOX - OTTIMIZZATI PER TOUCH */
    .stButton>button {
        border-radius: 10px !important;
        padding: 22px 5px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        width: 100% !important;
        margin-bottom: 15px !important; /* Spazio per non sbagliare click */
        color: white !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* COLORI CORSIE BOX */
    .btn-verde > div > button { border: 4px solid #28a745 !important; background-color: #0a2b12 !important; }
    .btn-rossa > div > button { border: 4px solid #dc3545 !important; background-color: #2b0a0a !important; }
    .btn-gialla > div > button { border: 4px solid #ffc107 !important; background-color: #332b00 !important; color: #ffc107 !important; }
    .btn-blu > div > button { border: 4px solid #007bff !important; background-color: #001a33 !important; }

    /* TABS */
    header, footer { visibility: hidden; }
    .stTabs [data-baseweb="tab-list"] { background-color: #111; padding: 10px; border-bottom: 1px solid #444; gap: 20px; }
    .stTabs [data-baseweb="tab"] { height: 50px; font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. PERSISTENZA DATI
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
if 'apex_url' not in st.session_state: st.session_state.apex_url = ""
if 'sel_idx' not in st.session_state: st.session_state.sel_idx = 0

# --- SIDEBAR (CONTROLLI SEMPRE PRESENTI) ---
with st.sidebar:
    st.header("🏁 SETTINGS")
    st.session_state.tempo_pit = st.number_input("DURATA PIT (sec)", value=st.session_state.tempo_pit)
    st.session_state.corsie_attive = st.multiselect("ATTIVA CORSIE", ["VERDE", "ROSSA", "GIALLA", "BLU"], default=st.session_state.corsie_attive)
    st.session_state.apex_url = st.text_input("LINK APEX LIVE", st.session_state.apex_url)
    
    st.write("---")
    idx = st.session_state.sel_idx
    row = st.session_state.data.iloc[idx]
    st.subheader(f"MODIFICA K{row['KART']}")
    
    st.session_state.data.at[idx, 'TEAM'] = st.text_input("NOME TEAM", row['TEAM'])
    if st.button("⭐ STELLA (ON/OFF)"):
        st.session_state.data.at[idx, 'STAR'] = not row['STAR']; st.rerun()
    
    st.session_state.data.at[idx, 'CAT'] = st.radio("CATEGORIA", ["NONE", "PRO", "SEMI", "AMA"], horizontal=True)

    st.write("---")
    if not row['IN_PIT']:
        st.write("MANDA IN BOX:")
        for c_name in st.session_state.corsie_attive:
            if st.button(f"➡️ IN {c_name}", key=f"move_{c_name}"):
                st.session_state.data.at[idx, 'IN_PIT'], st.session_state.data.at[idx, 'LANE'], st.session_state.data.at[idx, 'PIT_START'] = True, c_name, time.time()
                st.rerun()
    else:
        if st.button("✅ LIBERA KART / TORNA IN PISTA", type="primary"):
            st.session_state.data.at[idx, 'IN_PIT'] = False; st.rerun()

# --- INTERFACCIA A TAB ---
tab1, tab2, tab3 = st.tabs(["🏎️ LIVE PISTA", "🚧 BOX LIVE", "🌐 APEX WEB"])

with tab1:
    # Header Excel Style
    st.markdown("""<div class="grid-row" style="background-color:#222; border-bottom: 2px solid #555;">
        <div class="grid-cell" style="width:15%; font-size:12px;">KART</div>
        <div class="grid-cell" style="width:45%; font-size:12px;">TEAM / CAT</div>
        <div class="grid-cell" style="width:20%; font-size:12px;">MEDIA</div>
        <div class="grid-cell" style="width:20%; border-right:none; font-size:12px;">ULTIMO</div>
    </div>""", unsafe_allow_html=True)
    
    df_pista = st.session_state.data[st.session_state.data['IN_PIT'] == False]
    for i, r in df_pista.iterrows():
        cols = st.columns([0.6, 2, 1, 1])
        star = "⭐" if r['STAR'] else ""
        dot_color = {"PRO":"#FF3131","SEMI":"#1E90FF","AMA":"#00FF7F","NONE":"#444"}[r['CAT']]
        
        with cols[0]: 
            st.markdown(f'<div class="grid-row"><div class="grid-cell big-num" style="width:100%; border-right:none;">{star}{r["KART"]}</div></div>', unsafe_allow_html=True)
        with cols[1]:
            label = f"● {r['TEAM']}"
            if st.button(label, key=f"t_{i}"):
                st.session_state.sel_idx = i; st.rerun()
        with cols[2]: 
            st.markdown(f'<div class="grid-row"><div class="grid-cell big-num" style="width:100%; border-right:none; color:#00FF7F;">{r["MEDIA"]:.2f}</div></div>', unsafe_allow_html=True)
        with cols[3]: 
            st.markdown(f'<div class="grid-row"><div class="grid-cell big-num" style="width:100%; border-right:none; color:#555;">{r["ULTIMO"]:.1f}</div></div>', unsafe_allow_html=True)

with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    n_c = len(st.session_state.corsie_attive)
    if n_c > 0:
        cols_box = st.columns(n_c)
        for i, c_name in enumerate(st.session_state.corsie_attive):
            with cols_box[i]:
                c_color = {"VERDE":"#28a745","ROSSA":"#dc3545","GIALLA":"#ffc107","BLU":"#007bff"}[c_name]
                css_tag = {"VERDE":"btn-verde","ROSSA":"btn-rossa","GIALLA":"btn-gialla","BLU":"btn-blu"}[c_name]
                st.markdown(f"<h3 style='color:{c_color}; text-align:center; border-bottom: 2px solid {c_color};'>{c_name}</h3>", unsafe_allow_html=True)
                
                q = st.session_state.data[(st.session_state.data['IN_PIT'] == True) & (st.session_state.data['LANE'] == c_name)]
                for idx, r in q.iterrows():
                    rem = max(0, st.session_state.tempo_pit - (time.time() - r['PIT_START']))
                    m, s = divmod(int(rem), 60)
                    st.markdown(f'<div class="{css_tag}">', unsafe_allow_html=True)
                    if st.button(f"K{r['KART']}\n⏳ {m:02d}:{s:02d}", key=f"bx_{idx}"):
                        st.session_state.data.at[idx, 'IN_PIT'] = False; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    if st.session_state.apex_url:
        st.markdown(f'<iframe src="{st.session_state.apex_url}" width="100%" height="900px" style="border:none;"></iframe>', unsafe_allow_html=True)
    else:
        st.info("Inserisci il link di Apex Timing nella barra laterale.")

time.sleep(5)
st.rerun()
