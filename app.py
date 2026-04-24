import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh
# --- 1. CONFIGURAZIONE E LAYOUT ---
st.set_page_config(page_title="WAR ROOM ENDURANCE - ULTIMATE", layout="wide", initial_sidebar_state="collapsed")
# --- 2. CSS PROFESSIONALE (LINEE SOTTILI, TOUCH GIGANTE, COLORI CORSIE) ---
st.markdown("""
    <style>
    .main .block-container { padding: 0px !important; background-color: #111; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    /* GRIGLIA STILE EXCEL (Linee sottili e pulite) */
    .grid-row { 
        display: flex; 
        border-bottom: 1px solid #333; 
        align-items: center; 
        min-height: 65px; 
        background-color: #000; 
    }
    .grid-cell { 
        border-right: 1px solid #333; 
        padding: 0px 15px; 
        height: 100%; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
    }
    
    /* TESTO E ICONE */
    .big-num { font-size: 30px !important; font-weight: 800 !important; color: #FFF; }
    .team-text { font-size: 20px !important; font-weight: bold; color: #EEE; }
    /* BOTTONI BOX - OTTIMIZZAZIONE TOUCH (Distanziati e Grandi) */
    .stButton>button {
        border-radius: 12px !important;
        padding: 25px 5px !important;
        font-size: 22px !important;
        font-weight: bold !important;
        width: 100% !important;
        margin-bottom: 15px !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.6);
    }
    
    /* BORDURA CORSIE BOX DINAMICHE */
    .btn-verde > div > button { border: 5px solid #28a745 !important; background-color: #0a2b12 !important; }
    .btn-rossa > div > button { border: 5px solid #dc3545 !important; background-color: #2b0a0a !important; }
    .btn-gialla > div > button { border: 5px solid #ffc107 !important; background-color: #332b00 !important; color: #ffc107 !important; }
    .btn-blu > div > button { border: 5px solid #007bff !important; background-color: #001a33 !important; }
    /* TABS E SIDEBAR */
    header, footer { visibility: hidden; }
    .stTabs [data-baseweb="tab-list"] { background-color: #000; padding: 15px; border-bottom: 2px solid #444; gap: 20px; }
    .stTabs [data-baseweb="tab"] { height: 60px; font-size: 22px !important; font-weight: bold !important; }
    .streamlit-expanderHeader { background-color: #222 !important; font-size: 18px !important; border-radius: 8px !important; }
    /* SIDEBAR: expander più visibili e distanziati */
    section[data-testid="stSidebar"] [data-testid="stExpander"] { 
        margin-bottom: 12px !important; 
        border: 1px solid #2f2f2f !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        background: #141414 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary { 
        padding: 12px 14px !important; 
        font-weight: 800 !important;
        letter-spacing: 0.2px;
    }
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover { 
        background: #1f1f1f !important; 
    }
    section[data-testid="stSidebar"] [data-testid="stExpander"] details[open] summary { 
        border-bottom: 1px solid #2f2f2f !important; 
    }
    /* MOBILE: evita sovrapposizioni (kart/tempi) + più spazio tra righe */
    @media (max-width: 768px) {
        .grid-row {
            min-height: 72px !important;
            margin-bottom: 6px !important;
        }
        .grid-cell {
            padding: 6px 10px !important;
        }
        .big-num {
            font-size: 22px !important;
            line-height: 1.15 !important;
            white-space: nowrap !important;
        }
        .team-text { font-size: 16px !important; }
        /* Bottoni box: testo su 2 righe senza “schiacciarsi” */
        .stButton>button {
            padding: 18px 8px !important;
            font-size: 18px !important;
            line-height: 1.2 !important;
            white-space: pre-line !important;
            margin-bottom: 12px !important;
        }
        /* Sidebar: expander più touch-friendly */
        section[data-testid="stSidebar"] [data-testid="stExpander"] summary {
            font-size: 16px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
# --- 3. DATABASE PERSISTENTE ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(40)],
        'TEAM': [f"TEAM {i+1}" for i in range(40)],
        'CAT': ["NONE"] * 40, 
        'STAR': [False] * 40,
        'IN_PIT': [False] * 40, 
        'LANE': ["VERDE"] * 40, 
        'PIT_START': [0.0] * 40,
        'MEDIA': [0.0] * 40, 
        'ULTIMO': [0.0] * 40
    })
if 'tempo_pit' not in st.session_state: st.session_state.tempo_pit = 180
if 'corsie_attive' not in st.session_state: st.session_state.corsie_attive = ["VERDE", "ROSSA"]
if 'apex_url' not in st.session_state: st.session_state.apex_url = ""
if 'sel_idx' not in st.session_state: st.session_state.sel_idx = 0
# --- 4. SIDEBAR: TUTTE LE TENDINE INTEGRATE ---
with st.sidebar:
    st.title("🕹️ WAR ROOM CTRL")
    # BOX ASSEGNAZIONE RAPIDA
    with st.expander("⚡ ASSEGNAZIONE RAPIDA (KART / TEAM)", expanded=True):
        # Selezione kart veloce
        kart_list = st.session_state.data["KART"].tolist()
        default_kart = (
            st.session_state.data.iloc[st.session_state.sel_idx]["KART"]
            if 0 <= st.session_state.sel_idx < len(st.session_state.data)
            else kart_list[0]
        )
        kart_sel = st.selectbox(
            "SELEZIONA KART",
            kart_list,
            index=kart_list.index(default_kart) if default_kart in kart_list else 0,
            key="quick_kart_sel",
        )
        quick_idx = int(st.session_state.data.index[st.session_state.data["KART"] == kart_sel][0])
        quick_team = st.text_input(
            "TEAM (MODIFICA VELOCE)",
            value=str(st.session_state.data.at[quick_idx, "TEAM"]),
            key="quick_team",
        )
        quick_cat_options = ["NONE", "PRO", "SEMI", "AMA"]
        curr_cat = str(st.session_state.data.at[quick_idx, "CAT"])
        quick_cat_index = quick_cat_options.index(curr_cat) if curr_cat in quick_cat_options else 0
        quick_cat = st.radio(
            "CATEGORIA",
            quick_cat_options,
            index=quick_cat_index,
            horizontal=True,
            key="quick_cat",
        )
        quick_star = st.checkbox(
            "⭐ PREFERITO",
            value=bool(st.session_state.data.at[quick_idx, "STAR"]),
            key="quick_star",
        )
        st.divider()
        st.caption("Box manuale: imposta corsia e stato IN/OUT senza passare dai pulsanti.")
        lane_sel = st.selectbox(
            "CORSIA",
            ["VERDE", "ROSSA", "GIALLA", "BLU"],
            index=["VERDE", "ROSSA", "GIALLA", "BLU"].index(str(st.session_state.data.at[quick_idx, "LANE"])) if str(st.session_state.data.at[quick_idx, "LANE"]) in ["VERDE", "ROSSA", "GIALLA", "BLU"] else 0,
            key="quick_lane",
        )
        in_pit_now = st.toggle(
            "IN BOX",
            value=bool(st.session_state.data.at[quick_idx, "IN_PIT"]),
            key="quick_in_pit",
        )
        if st.button("✅ SALVA / APPLICA", type="primary", key="quick_apply"):
            st.session_state.sel_idx = quick_idx
            st.session_state.data.at[quick_idx, "TEAM"] = quick_team.strip() if quick_team else ""
            st.session_state.data.at[quick_idx, "CAT"] = quick_cat
            st.session_state.data.at[quick_idx, "STAR"] = quick_star
            st.session_state.data.at[quick_idx, "LANE"] = lane_sel
            if in_pit_now and not bool(st.session_state.data.at[quick_idx, "IN_PIT"]):
                st.session_state.data.at[quick_idx, "IN_PIT"] = True
                st.session_state.data.at[quick_idx, "PIT_START"] = time.time()
            elif (not in_pit_now) and bool(st.session_state.data.at[quick_idx, "IN_PIT"]):
                st.session_state.data.at[quick_idx, "IN_PIT"] = False
            st.rerun()
    
    # TENDINA IMPOSTAZIONI GARA
    with st.expander("⚙️ CONFIGURAZIONE PISTA", expanded=True):
        st.session_state.tempo_pit = st.number_input("TEMPO BOX (SEC)", value=st.session_state.tempo_pit)
        st.session_state.corsie_attive = st.multiselect(
            "ATTIVA CORSIE",
            ["VERDE", "ROSSA", "GIALLA", "BLU"],
            default=st.session_state.corsie_attive,
        )
        st.session_state.apex_url = st.text_input("LINK APEX TIMING", st.session_state.apex_url, placeholder="Incolla URL...")
    # TENDINA MODIFICA KART
    with st.expander("🏎️ GESTIONE KART & TEAM", expanded=True):
        idx = st.session_state.sel_idx
        row = st.session_state.data.iloc[idx]
        st.subheader(f"KART {row['KART']}")
        st.session_state.data.at[idx, 'TEAM'] = st.text_input("NOME TEAM", row['TEAM'])
        
        if st.button("⭐ SEGNA COME PREFERITO (ON/OFF)"):
            st.session_state.data.at[idx, 'STAR'] = not row['STAR']
            st.rerun()
        
        cat_options = ["NONE", "PRO", "SEMI", "AMA"]
        try:
            cat_index = cat_options.index(str(row["CAT"]))
        except ValueError:
            cat_index = 0
        cat = st.radio(
            "CATEGORIA PALLINO",
            cat_options,
            index=cat_index,
            horizontal=True,
            key=f"cat_{idx}",
        )
        st.session_state.data.at[idx, "CAT"] = cat
    # TENDINA COMANDI RAPIDI BOX
    with st.expander("🚧 MOVIMENTI BOX", expanded=True):
        if not st.session_state.data.at[idx, 'IN_PIT']:
            for c_name in st.session_state.corsie_attive:
                if st.button(f"➡️ ENTRA IN {c_name}", key=f"pit_{c_name}"):
                    st.session_state.data.at[idx, 'IN_PIT'] = True
                    st.session_state.data.at[idx, 'LANE'] = c_name
                    st.session_state.data.at[idx, 'PIT_START'] = time.time()
                    st.rerun()
        else:
            if st.button("✅ USCITA BOX (PISTA)", type="primary"):
                st.session_state.data.at[idx, 'IN_PIT'] = False
                st.rerun()
# --- 5. INTERFACCIA PRINCIPALE ---
tab1, tab2, tab3 = st.tabs(["🏎️ LIVE PISTA", "🚧 GESTIONE BOX", "🌐 APEX LIVE"])
with tab1:
    # Header Tabella Excel
    st.markdown(
        """<div class="grid-row" style="background-color:#222;"><div class="grid-cell" style="width:15%;">K</div><div class="grid-cell" style="width:45%;">TEAM / CAT</div><div class="grid-cell" style="width:20%;">MED</div><div class="grid-cell" style="width:20%; border:none;">ULT</div></div>""",
        unsafe_allow_html=True,
    )
    
    df_pista = st.session_state.data[st.session_state.data['IN_PIT'] == False]
    for i, r in df_pista.iterrows():
        cols = st.columns([0.6, 2, 1, 1])
        star = "⭐" if r['STAR'] else ""
        
        with cols[0]:
            st.markdown(
                f'<div class="grid-row"><div class="grid-cell big-num" style="width:100%; border:none;">{star}{r["KART"]}</div></div>',
                unsafe_allow_html=True,
            )
        with cols[1]:
            if st.button(f"● {r['TEAM']} ({r['CAT']})", key=f"btn_pista_{i}"):
                st.session_state.sel_idx = i
                st.rerun()
        with cols[2]:
            st.markdown(
                f'<div class="grid-row"><div class="grid-cell big-num" style="width:100%; color:#00FF7F; border:none;">{r["MEDIA"]:.2f}</div></div>',
                unsafe_allow_html=True,
            )
        with cols[3]:
            st.markdown(
                f'<div class="grid-row"><div class="grid-cell big-num" style="width:100%; color:#666; border:none;">{r["ULTIMO"]:.1f}</div></div>',
                unsafe_allow_html=True,
            )
with tab2:
    # Refresh non bloccante per mantenere i countdown fluidi (solo in Box)
    st_autorefresh(interval=1000, key="box_refresh")
    n_attive = len(st.session_state.corsie_attive)
    if n_attive > 0:
        cols_box = st.columns(n_attive)
        for i, c_name in enumerate(st.session_state.corsie_attive):
            with cols_box[i]:
                c_color = {"VERDE":"#28a745","ROSSA":"#dc3545","GIALLA":"#ffc107","BLU":"#007bff"}[c_name]
                css_tag = {"VERDE":"btn-verde","ROSSA":"btn-rossa","GIALLA":"btn-gialla","BLU":"btn-blu"}[c_name]
                st.markdown(
                    f"<h2 style='color:{c_color}; text-align:center; border-bottom: 3px solid {c_color}; padding-bottom:10px;'>{c_name}</h2>",
                    unsafe_allow_html=True,
                )
                
                q = st.session_state.data[
                    (st.session_state.data['IN_PIT'] == True) & (st.session_state.data['LANE'] == c_name)
                ]
                for idx_b, r_b in q.iterrows():
                    m, s = divmod(
                        int(max(0, st.session_state.tempo_pit - (time.time() - r_b['PIT_START']))),
                        60,
                    )
                    st.markdown(f'<div class="{css_tag}">', unsafe_allow_html=True)
                    if st.button(f"K{r_b['KART']}\n⏳ {m:02d}:{s:02d}", key=f"btn_box_{idx_b}"):
                        st.session_state.data.at[idx_b, 'IN_PIT'] = False
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Seleziona le corsie box attive nella Sidebar.")
with tab3:
    if st.session_state.apex_url:
        st.markdown(
            f'<iframe src="{st.session_state.apex_url}" width="100%" height="900px" style="border:none;"></iframe>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Inserisci il link di Apex Timing nella Sidebar.")
