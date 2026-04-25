import streamlit as st
import pandas as pd
import time

# ==========================================
# 1. CONFIGURAZIONE E MEMORIA PERSISTENTE (Session State)
# ==========================================
st.set_page_config(page_title="WAR ROOM 106 - STABILE", layout="wide", initial_sidebar_state="expanded")

# Inizializziamo il database solo se non esiste già, per non perdere i dati
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(50)],
        'STATO': ['NEUTRO'] * 50,
        'BEST': ["99.999"] * 50,
        'CAMBI': [0] * 50,
        'IN_PIT': [False] * 50,
        'PIT_START': [0.0] * 50
    })

# Conserviamo la pagina corrente per non far saltare il menu
if 'page' not in st.session_state:
    st.session_state.page = "📡 RADAR PISTA"

# ==========================================
# 2. STILE GRAFICO (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .status-dot { height: 15px; width: 15px; border-radius: 50%; display: inline-block; margin-right: 8px; }
    .dot-green { background-color: #00FF7F; box-shadow: 0 0 10px #00FF7F; }
    .dot-red { background-color: #FF3131; box-shadow: 0 0 15px #FF3131; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.3; } }
    .timer-red { color: #ff4b4b; font-size: 50px; font-weight: bold; animation: blinker 1s linear infinite; text-align: center; background: black; border-radius: 12px; padding: 10px; border: 3px solid #ff4b4b; }
    .timer-green { color: #00FF7F; font-size: 50px; font-weight: bold; text-align: center; border: 4px solid #00FF7F; background: black; border-radius: 12px; padding: 10px; }
    .stButton>button { width: 100%; height: 70px; font-size: 20px !important; font-weight: bold; border-radius: 15px; }
    [data-testid="stDataEditor"] div div div div { line-height: 50px !important; font-size: 22px !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. SIDEBAR E NAVIGAZIONE (Senza perdite)
# ==========================================
with st.sidebar:
    st.title("🏁 MENU STRATEGIA")
    # Usiamo il session_state per la navigazione
    selection = st.radio("VAI A:", ["📡 RADAR PISTA", "🚧 GESTIONE BOX", "📊 ANALISI RECORD"], 
                         index=["📡 RADAR PISTA", "🚧 GESTIONE BOX", "📊 ANALISI RECORD"].index(st.session_state.page))
    st.session_state.page = selection

# ==========================================
# 4. PAGINA 1: RADAR (Inserimento e Monitoraggio)
# ==========================================
if st.session_state.page == "📡 RADAR PISTA":
    st.title("📡 Radar Monitor Live")
    
    circuiti = {
        "106 Reverse": "https://live.apex-timing.com/kartodromo106reverse/",
        "106 Standard": "https://live.apex-timing.com/kartodromo106/",
        "Siena": "https://live.apex-timing.com/siena/"
    }
    col_p, col_l = st.columns(2)
    with col_p:
        st.selectbox("📍 CIRCUITO APEX:", list(circuiti.keys()), key="pista_select")
    with col_l:
        st.link_button("🚀 APRI LIVE TIMING", circuiti[st.session_state.pista_select])

    st.subheader("📋 Gestione Flotta (50 Kart)")
    
    # Visualizziamo l'editor caricando i dati dalla sessione
    edited_df = st.data_editor(
        st.session_state.data,
        column_config={
            "KART": st.column_config.TextColumn("KART", disabled=True),
            "STATO": st.column_config.SelectboxColumn("QUALITÀ", options=["TOP", "NEUTRO", "LENTO"]),
            "BEST": st.column_config.TextColumn("MIGLIOR GIRO"),
            "IN_PIT": st.column_config.CheckboxColumn("BOX"),
            "CAMBI": st.column_config.NumberColumn("🔁 SOSTE", disabled=True),
        },
        hide_index=True, use_container_width=True, key="radar_editor"
    )

    # LOGICA DI AGGIORNAMENTO: Confronto dati vecchi vs nuovi per non perdere nulla
    for i in range(len(edited_df)):
        # Se è appena entrato nel box
        if edited_df.at[i, 'IN_PIT'] and not st.session_state.data.at[i, 'IN_PIT']:
            edited_df.at[i, 'PIT_START'] = time.time()
        # Se è appena uscito dal box
        if not edited_df.at[i, 'IN_PIT'] and st.session_state.data.at[i, 'IN_PIT']:
            edited_df.at[i, 'CAMBI'] += 1
            
    st.session_state.data = edited_df

# ==========================================
# 5. PAGINA 2: GESTIONE BOX (Countdown Real-Time)
# ==========================================
elif st.session_state.page == "🚧 GESTIONE BOX":
    st.title("🚧 Gestione Soste & Sorteggi")
    
    # Filtriamo i kart che sono ai box
    in_pit = st.session_state.data[st.session_state.data['IN_PIT'] == True]
    
    if not in_pit.empty:
        # Layout a corsie dinamiche
        cols_box = st.columns(2)
        for i, (idx, r) in enumerate(in_pit.iterrows()):
            with cols_box[i % 2]:
                trascorso = time.time() - r['PIT_START']
                rimanente = 180 - trascorso # 3 minuti
                
                colore_kart = "#00FF7F" if r['STATO'] == "TOP" else "white"
                st.markdown(f"### <span style='color:{colore_kart};'>🏎️ KART {r['KART']}</span> ({r['STATO']})", unsafe_allow_html=True)

                if rimanente > 0:
                    m, s = divmod(int(rimanente), 60)
                    st.markdown(f"<p class='timer-red'>{m:02d}:{s:02d}</p>", unsafe_allow_html=True)
                else:
                    st.markdown("<p class='timer-green'>✅ ESCI!</p>", unsafe_allow_html=True)
    else:
        st.info("Nessun kart ai box. Spunta 'BOX' nella pagina Radar.")

# ==========================================
# 6. PAGINA 3: ANALISI
# ==========================================
elif st.session_state.page == "📊 ANALISI RECORD":
    st.title("📊 Classifica Gara")
    st.dataframe(st.session_state.data.sort_values('BEST'), use_container_width=True)

# ==========================================
# 7. AGGIORNAMENTO AUTOMATICO (Indispensabile per i secondi)
# ==========================================
time.sleep(1)
st.rerun()
