import time
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="WAR ROOM - GARA LIVE", layout="wide")

# --- CSS PROFESSIONALE ---
st.markdown("""
    <style>
    .main { background-color: #0f1116; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .lane-title { text-align: center; padding: 8px; border-radius: 8px; color: white; font-weight: 800; margin-bottom: 10px; }
    .lane-verde { background-color: #146c43; }
    .lane-rosso { background-color: #9b2226; }
    .lane-giallo { background-color: #8c6d1f; }
    .lane-blu { background-color: #2b59a2; }
    .box-card { background: #1c2128; border: 1px solid #30363d; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
    header, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# --- INIZIALIZZAZIONE DATI ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(30)],
        'TEAM': ["-"] * 30,
        'BEST': [99.999] * 30,
        'IN_PIT': [False] * 30,
        'PIT_START': [0.0] * 30,
        'LANE': ["VERDE"] * 30
    })

if 'target_pit' not in st.session_state:
    st.session_state.target_pit = 180

if 'url_apex' not in st.session_state:
    st.session_state.url_apex = "https://live.apex-timing.com"

# REFRESH OGNI 2 SECONDI
st_autorefresh(interval=2000, key="refresh")

# --- SIDEBAR: MODIFICA MANUALE ---
with st.sidebar:
    st.header("⚙️ SETTINGS GARA")
    st.session_state.url_apex = st.text_input("Link Apex Timing", st.session_state.url_apex)
    st.session_state.target_pit = st.number_input("Target Pit (sec)", value=st.session_state.target_pit)
    
    st.divider()
    st.subheader("📝 EDIT KART / TEAM")
    sel_idx = st.selectbox("Seleziona Riga", options=range(30), format_func=lambda x: f"Riga {x+1} (K{st.session_state.data.at[x, 'KART']})")
    
    new_k = st.text_input("Cambia Numero Kart", st.session_state.data.at[sel_idx, 'KART'])
    new_t = st.text_input("Cambia Nome Team", st.session_state.data.at[sel_idx, 'TEAM'])
    
    if st.button("SALVA MODIFICHE"):
        st.session_state.data.at[sel_idx, 'KART'] = new_k
        st.session_state.data.at[sel_idx, 'TEAM'] = new_t
        st.rerun()

# --- TAB PRINCIPALI ---
tab_pista, tab_box, tab_apex = st.tabs(["🏎️ LEADERBOARD & PISTA", "🚧 GESTIONE BOX", "🌐 APEX LIVE"])

with tab_pista:
    col_classifica, col_azioni = st.columns([1.2, 2])
    
    with col_classifica:
        st.subheader("🏆 TOP 15 (Migliori Tempi)")
        # Ordina per il tempo BEST inserito
        top15 = st.session_state.data.sort_values('BEST').head(15)
        for i, (idx, r) in enumerate(top15.iterrows()):
            t_col1, t_col2 = st.columns([2, 1])
            with t_col1:
                # Campo per inserire il tempo manualmente per ogni kart
                new_time = st.number_input(f"{i+1}° K{r['KART']}", value=float(r['BEST']), format="%.3f", key=f"time_{idx}")
                if new_time != r['BEST']:
                    st.session_state.data.at[idx, 'BEST'] = new_time
                    st.rerun()
            with t_col2:
                st.write(f"Pos: {i+1}")

    with col_azioni:
        st.subheader("📥 CHIAMA AL BOX")
        grid = st.columns(3)
        for i in range(15):
            kart_id = st.session_state.data.at[i, 'KART']
            with grid[i % 3]:
                if not st.session_state.data.at[i, 'IN_PIT']:
                    c_sel = st.selectbox(f"Corsia", ["VERDE", "ROSSO", "GIALLO", "BLU"], key=f"c_{i}")
                    if st.button(f"ENTRA K{kart_id}", key=f"in_{i}"):
                        st.session_state.data.at[i, 'IN_PIT'] = True
                        st.session_state.data.at[i, 'LANE'] = c_sel
                        st.session_state.data.at[i, 'PIT_START'] = time.time()
                        st.rerun()
                else:
                    st.error(f"K{kart_id} BOX")

with tab_box:
    st.subheader("🚧 MONITOR CORSIE")
    b_cols = st.columns(4)
    lanes = ["VERDE", "ROSSO", "GIALLO", "BLU"]
    for i, l_name in enumerate(lanes):
        with b_cols[i]:
            st.markdown(f"<div class='lane-title lane-{l_name.lower()}'>{l_name}</div>", unsafe_allow_html=True)
            k_in_box = st.session_state.data[(st.session_state.data['IN_PIT'] == True) & (st.session_state.data['LANE'] == l_name)]
            for idx, r in k_in_box.iterrows():
                elapsed = int(time.time() - r['PIT_START'])
                rem = st.session_state.target_pit - elapsed
                st.markdown(f"""<div class='box-card'>
                    <b>KART {r['KART']}</b><br>
                    Mancano: <span style='color:{"#ff4b4b" if rem < 30 else "#00eb93"}; font-size:20px;'>{rem}s</span>
                </div>""", unsafe_allow_html=True)
                if st.button(f"RILASCIA {r['KART']}", key=f"rel_{idx}"):
                    st.session_state.data.at[idx, 'IN_PIT'] = False
                    st.rerun()

with tab_apex:
    st.subheader("🌐 APEX LIVE TIMING")
    st.markdown(f"[CLICCA QUI PER APRIRE APEX IN UNA NUOVA SCHEDA]({st.session_state.url_apex})")
    components.html(f'<iframe src="{st.session_state.url_apex}" width="100%" height="800" style="border:none;"></iframe>', height=800)
