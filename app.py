import streamlit as st
import pandas as pd
import time

# ==========================================
# 1. CONFIGURAZIONE CORE E PERSISTENZA DATI
# ==========================================
st.set_page_config(
    page_title="WAR ROOM 106 - v.COMPLETE", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Inizializzazione Session State per non perdere i dati al refresh
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(50)],
        'CATEGORIA': ['PRO' if i < 25 else 'GENTLEMAN' for i in range(50)],
        'BEST': ["99.999"] * 50,
        'CAMBI': [0] * 50,
        'IN_PIT': [False] * 50,
        'PIT_START': [0.0] * 50,
        'PISTA_START': [time.time()] * 50
    })

# ==========================================
# 2. STILE CSS (ALERT LUMINOSI E TOUCH)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; height: 85px; font-size: 26px !important; font-weight: bold; border-radius: 20px; background-color: #ff4b4b !important; color: white; border: 2px solid white; }
    /* Timer Alert Lampeggiante */
    .timer-red { color: #ff4b4b; font-size: 55px; font-weight: bold; animation: blinker 1s linear infinite; background: black; padding: 15px; border-radius: 15px; text-align: center; border: 3px solid #ff4b4b; }
    .timer-green { color: #00FF7F; font-size: 55px; font-weight: bold; text-align: center; border: 5px solid #00FF7F; background: black; padding: 15px; border-radius: 15px; }
    @keyframes blinker { 50% { opacity: 0.2; } }
    /* Ingrandimento tabelle per dita grandi */
    [data-testid="stDataEditor"] div div div div { line-height: 55px !important; font-size: 24px !important; }
    </style>
    """, unsafe_allow_html=True)

# Logica conversione tempi
def to_sec(t):
    try:
        t = str(t).strip().replace(',', '.')
        if ':' in t:
            m, s = t.split(':')
            return int(m) * 60 + float(s)
        return float(t)
    except: return 999.9

# ==========================================
# 3. NAVIGAZIONE (SIDEBAR)
# ==========================================
st.sidebar.title("🏁 STRATEGIA PRO")
page = st.sidebar.radio("NAVIGAZIONE:", ["📡 RADAR PISTA", "🚧 GESTIONE BOX", "📊 ANALISI RECORD"])

# ==========================================
# 4. PAGINA 1: RADAR PISTA (50 KART)
# ==========================================
if page == "📡 RADAR PISTA":
    st.title("📡 Radar Totale 50 Kart")
    
    # Tendina Piste Apex
    circuiti = {
        "106 Reverse": "https://live.apex-timing.com/kartodromo106reverse/",
        "106 Standard": "https://live.apex-timing.com/kartodromo106/",
        "Siena": "https://live.apex-timing.com/siena/",
        "Mugellino": "https://live.apex-timing.com/mugellino/"
    }
    col_p, col_l = st.columns(2)
    with col_p:
        pista_scelta = st.selectbox("📍 SELEZIONA CIRCUITO:", list(circuiti.keys()))
    with col_l:
        st.link_button("🚀 APRI APEX LIVE", circuiti[pista_scelta])

    st.divider()
    
    # Soglia Radar
    target_radar = st.text_input("⭐ SOGLIA RECORD (Asterisco):", value="43.500")
    t_val = to_sec(target_radar)

    # Editor Dati Principale
    edited = st.data_editor(
        st.session_state.data,
        column_config={
            "KART": st.column_config.TextColumn("KART", disabled=False),
            "BEST": st.column_config.TextColumn("BEST LAP"),
            "CATEGORIA": st.column_config.SelectboxColumn("CAT", options=["PRO", "GENTLEMAN"]),
            "IN_PIT": st.column_config.CheckboxColumn("BOX"),
            "CAMBI": st.column_config.NumberColumn("🔁", disabled=True),
        },
        hide_index=True, use_container_width=True, key="main_editor"
    )
    
    # Sincronizzazione Logica (Cambi e Timer)
    for i, row in edited.iterrows():
        # Ingresso Box
        if row['IN_PIT'] and not st.session_state.data.at[i, 'IN_PIT']:
            st.session_state.data.at[i, 'PIT_START'] = time.time()
        # Uscita Box
        if not row['IN_PIT'] and st.session_state.data.at[i, 'IN_PIT']:
            st.session_state.data.at[i, 'CAMBI'] += 1
            st.session_state.data.at[i, 'PISTA_START'] = time.time()
    
    st.session_state.data = edited

# ==========================================
# 5. PAGINA 2: GESTIONE BOX (CORSIA MULTIPLA)
# ==========================================
elif page == "🚧 GESTIONE BOX":
    st.title("🚧 Strategia Corsie Box")
    
    num_corsie = st.slider("Numero corsie visualizzate:", 1, 4, 2)
    in_pit = st.session_state.data[st.session_state.data['IN_PIT'] == True]
    
    if not in_pit.empty:
        cols = st.columns(num_corsie)
        for i, (idx, r) in enumerate(in_pit.iterrows()):
            with cols[i % num_corsie]:
                rimanente = 180 - (time.time() - r['PIT_START'])
                st.markdown(f"### 🏎️ KART {r['KART']}")
                if rimanente > 0:
                    m, s = divmod(int(rimanente), 60)
                    st.markdown(f"<p class='timer-red'>{m:02d}:{s:02d}</p>", unsafe_allow_html=True)
                    if rimanente < 20: st.error("⚠️ PREPARA PILOTA!")
                else:
                    st.markdown("<p class='timer-green'>✅ ESCI ORA!</p>", unsafe_allow_html=True)
                    st.balloons()
    else:
        st.info("Nessun kart ai box. Attiva la spunta 'BOX' nel Radar.")

# ==========================================
# 6. PAGINA 3: ANALISI RECORD
# ==========================================
elif page == "📊 ANALISI RECORD":
    st.title("📊 Classifica e Analisi Soste")
    df_ana = st.session_state.data.copy()
    df_ana['V_NUM'] = df_ana['BEST'].apply(to_sec)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏆 Migliori 10 Tempi")
        st.dataframe(df_ana.sort_values('V_NUM')[['KART', 'BEST', 'CATEGORIA']].head(10))
    with c2:
        st.subheader("🔄 Soste per Kart")
        st.bar_chart(df_ana.set_index('KART')['CAMBI'])

# ==========================================
# 7. REFRESH AUTOMATICO (INDISPENSABILE)
# ==========================================
time.sleep(1)
st.rerun()
