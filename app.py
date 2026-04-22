import streamlit as st
import pandas as pd
import time

# 1. CONFIGURAZIONE GENERALE
st.set_page_config(page_title="KARTING WAR ROOM PRO", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS DEFINITIVO (STRUTTURA, GRIGLIA E TOUCH)
st.markdown("""
    <style>
    .main .block-container { padding: 0px !important; background-color: #000; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    /* GRIGLIA EXCEL PIXEL PERFECT */
    .grid-row { 
        display: flex; border-bottom: 1px solid #333; 
        align-items: center; min-height: 55px; background-color: #000; 
    }
    .grid-cell { 
        border-right: 1px solid #333; padding: 0px 10px; 
        height: 100%; display: flex; align-items: center; justify-content: center; 
    }
    
    /* CARATTERI E ICONE */
    .big-num { font-size: 26px !important; font-weight: 800 !important; color: #FFF; }
    .star-icon { color: #FFD700; font-size: 20px; margin-right: 5px; }

    /* BOTTONI BOX - OTTIMIZZATI PER TOUCH */
    .stButton>button {
        border-radius: 8px !important;
        padding: 22px 5px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        width: 100% !important;
        margin-bottom: 12px !important;
        color: white !important;
    }
    
    /* COLORI CORSIE BOX */
    .btn-verde > div > button { border: 3px solid #28a745 !important; background-color: #0a2b12 !important; }
    .btn-rossa > div > button { border: 3px solid #dc3545 !important; background-color: #2b0a0a !important; }
    .btn-gialla > div > button { border: 3px solid #ffc107 !important; background-color: #332b00 !important; color: #ffc107 !important; }
    .btn-blu > div > button { border: 3px solid #007bff !important; background-color: #001a33 !important; }

    /* NAVIGAZIONE (TABS) */
    header, footer { visibility: hidden; }
    .stTabs [data-baseweb="tab-list"] { background-color: #111; padding: 10px; border-bottom: 1px solid #444; gap: 15px; }
    .stTabs [data-baseweb="tab"] { height: 50px; font-size: 18px !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. GESTIONE STATO (DATABASE DELL'APP)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(50)],
        'TEAM': [f"TEAM {i+1}" for i in range(50)],
        'CAT': ["NONE"] * 50, 
        'STAR': [False] * 50,
        'IN_PIT': [False] * 50, 
        'LANE': ["VERDE"] * 50, 
        'PIT_START': [0.0] * 50,
        'MEDIA': [0.0] * 50, 
        'ULTIMO': [0.0] * 50
    })

if 'tempo_pit' not in st.session_state: st.session_state.tempo_pit = 180
if 'corsie_attive' not in st.session_state: st.session_state.corsie_attive = ["VERDE", "ROSSA"]
if 'apex_url' not in st.session_state: st.session_state.apex_url = ""
if 'sel_idx' not in st.session_state: st.session_state.sel_idx = 0

# --- SIDEBAR: TUTTE LE CARTELLE DI SELEZIONE ---
with st.sidebar:
    st.header("🏁 CONFIGURAZIONE PISTA")
    st.session_state.tempo_pit = st.number_input("DURATA PIT STOP (Secondi)", value=st.session_state.tempo_pit)
    st.session_state.corsie_attive = st.multiselect("ATTIVA CORSIE BOX", ["VERDE", "ROSSA", "GIALLA", "BLU"], default=st.session_state.corsie_attive)
    st.session_state.apex_url = st.text_input("LINK APEX TIMING", st.session_state.apex_url, placeholder="Incolla URL...")
    
    st.write("---")
    # CARTELLA SELEZIONE KART
    idx = st.session_state.sel_idx
    row = st.session_state.data.iloc[idx]
    st.subheader(f"🛠️ EDIT KART {row['KART']}")
    
    st.session_state.data.at[idx, 'TEAM'] = st.text_input("NOME TEAM", row['TEAM'])
    
    col_fav, col_clear = st.columns(2)
    if col_fav.button("⭐ PREFERITO"):
        st.session_state.data.at[idx, 'STAR'] = not row['STAR']; st.rerun()
    
    # CARTELLA CATEGORIE
    cat_scelta = st.radio("CATEGORIA (PALLINO)", ["NONE", "PRO", "SEMI", "AMA"], index=["NONE", "PRO", "SEMI", "AMA"].index(row['CAT']), horizontal=True)
    st.session_state.data.at[idx, 'CAT'] = cat_scelta

    st.write("---")
    # MOVIMENTO BOX
    if not row['IN_PIT']:
        st.write("MANDA NEI BOX:")
        for c_name in st.session_state.corsie_attive:
            if st.button(f"➡️ IN CORSIA {c_name}", key=f"btn_pit_{c_name}"):
                st.session_state.data.at[idx, 'IN_PIT'], st.session_state.data.at[idx, 'LANE'], st.session_state.data.at[idx, 'PIT_START'] = True, c_name, time.time()
                st.rerun()
    else:
        if st.button("✅ KART USCITO (TORNA IN PISTA)", type="primary"):
            st.session_state.data.at[idx, 'IN_PIT'] = False; st.rerun()

# --- INTERFACCIA PRINCIPALE ---
tab1, tab2, tab3 = st.tabs(["🏎️ LIVE PISTA", "🚧 GESTIONE BOX", "🌐 APEX TIMING"])

with tab1:
    # INTESTAZIONE TABELLA EXCEL
    st.markdown("""<div class="grid-row" style="background-color:#111; border-bottom: 2px solid #555;">
        <div class="grid-cell" style="width:15%; font-size:12px; color:#888;">KART</div>
        <div class="grid-cell" style="width:45%; font-size:12px; color:#888;">TEAM / CATEGORIA</div>
        <div class="grid-cell" style="width:20%; font-size:12px; color:#888;">MEDIA</div>
        <div class="grid-cell" style="width:20%; border-right:none; font-size:12px; color:#888;">ULTIMO</div>
    </div>""", unsafe_allow_html=True)
    
    df_pista = st.session_state.data[st.session_state.data['IN_PIT'] == False]
    for i, r in df_pista.iterrows():
        cols = st.columns([0.6, 2, 1, 1])
        star_icon = "⭐" if r['STAR'] else ""
        dot_color = {"PRO":"#FF3131","SEMI":"#1E90FF","AMA":"#00FF7F","NONE":"#444"}[r['CAT']]
        
        with cols[0]: 
            st.markdown(f'<div class="grid-row"><div class="grid-cell big-num" style="width:100%; border-right:none;">{star_icon}{r["KART"]}</div></div>', unsafe_allow_html=True)
        with cols[1]:
            # Pulsante Team con Pallino Categoria
            label = f"● {r['TEAM']} ({r['CAT']})"
            if st.button(label, key=f"live_t_{i}"):
                st.session_state.sel_idx = i; st.rerun()
        with cols[2]: 
            st.markdown(f'<div class="grid-row"><div class="grid-cell big-num" style="width:100%; border-right:none; color:#00FF7F;">{r["MEDIA"]:.2f}</div></div>', unsafe_allow_html=True)
        with cols[3]: 
            st.markdown(f'<div class="grid-row"><div class="grid-cell big-num" style="width:100%; border-right:none; color:#555;">{r["ULTIMO"]:.1f}</div></div>', unsafe_allow_html=True)

with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    num_attive = len(st.session_state.corsie_attive)
    if num_attive > 0:
        cols_box = st.columns(num_attive)
        for i, c_name in enumerate(st.session_state.corsie_attive):
            with cols_box[i]:
                color_code = {"VERDE":"#28a745","ROSSA":"#dc3545","GIALLA":"#ffc107","BLU":"#007bff"}[c_name]
                css_class = {"VERDE":"btn-verde","ROSSA":"btn-rossa","GIALLA":"btn-gialla","BLU":"btn-blu"}[c_name]
                st.markdown(f"<h3 style='color:{color_code}; text-align:center; border-bottom: 2px solid {color_code}; padding-bottom:5px;'>{c_name}</h3>", unsafe_allow_html=True)
                
                q_box = st.session_state.data[(st.session_state.data['IN_PIT'] == True) & (st.session_state.data['LANE'] == c_name)]
                for idx_box, r_box in q_box.iterrows():
                    tempo_trascorso = time.time() - r_box['PIT_START']
                    rimanente = max(0, st.session_state.tempo_pit - tempo_trascorso)
                    m, s = divmod(int(rimanente), 60)
                    
                    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                    if st.button(f"K{r_box['KART']}\n⏳ {m:02d}:{s:02d}", key=f"pit_btn_{idx_box}"):
                        st.session_state.data.at[idx_box, 'IN_PIT'] = False; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Attiva le corsie necessarie nella Sidebar.")

with tab3:
    if st.session_state.apex_url:
        st.markdown(f'<iframe src="{st.session_state.apex_url}" width="100%" height="900px" style="border:none;"></iframe>', unsafe_allow_html=True)
    else:
        st.info("Inserisci l'URL di Apex Timing nella Sidebar per attivare il monitor.")

# REFRESH AUTOMATICO OGNI 5 SECONDI
time.sleep(5)
st.rerun()
