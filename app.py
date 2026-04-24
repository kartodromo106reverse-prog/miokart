import streamlit as st
import pandas as pd
import time

# ==========================================
# 1. CONFIGURAZIONE CORE E PERSISTENZA
# ==========================================
st.set_page_config(page_title="WAR ROOM 106 - ULTIMATE", layout="wide", initial_sidebar_state="expanded")

# Inizializzazione Session State per evitare perdita dati al refresh
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
# 2. STILE CSS (ALERT, TOUCH, ANIMAZIONI)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    /* Tasti Giganti per Touch */
    .stButton>button { width: 100%; height: 80px; font-size: 24px !important; font-weight: bold; border-radius: 15px; }
    /* Timer Alert Lampeggiante */
    .timer-red { color: #ff4b4b; font-size: 45px; font-weight: bold; animation: blinker 1s linear infinite; background: black; padding: 10px; border-radius: 10px; text-align: center; }
    .timer-green { color: #00FF7F; font-size: 45px; font-weight: bold; border: 4px solid #00FF7F; padding: 10px; border-radius: 10px; text-align: center; background: black; }
    @keyframes blinker { 50% { opacity: 0.2; } }
    /* Tabelle High-Visibility */
    [data-testid="stDataEditor"] div div div div { line-height: 50px !important; font-size: 22px !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LOGICA DI CONVERSIONE TEMPI
# ==========================================
def to_sec(t):
    try:
        t = str(t).strip().replace(',', '.')
        if ':' in t:
            m, s = t.split(':')
            return int(m) * 60 + float(s)
        return float(t)
    except: return 999.9

# ==========================================
# 4. NAVIGAZIONE SIDEBAR
# ==========================================
st.sidebar.title("🎮 CONTROLLO GARA")
page = st.sidebar.radio("NAVIGAZIONE:", ["📡 RADAR PISTA", "🚧 GESTIONE BOX", "📊 ANALISI RECORD"])

# ==========================================
# 5. PAGINA 1: RADAR PISTA (50 KART + CATEGORIE)
# ==========================================
if page == "📡 RADAR PISTA":
    st.title("📡 Radar Totale Kart")
    
    # Gestione Link Multi-Pista
    circuiti = {
        "106 Reverse": "https://live.apex-timing.com/kartodromo106reverse/",
        "106 Standard": "https://live.apex-timing.com/kartodromo106/",
        "Siena": "https://live.apex-timing.com/siena/",
        "Mugellino": "https://live.apex-timing.com/mugellino/"
    }
    col_p, col_l = st.columns(2)
    with col_p:
        pista = st.selectbox("Seleziona Circuito Apex:", list(circuiti.keys()))
    with col_l:
        st.link_button("🚀 APRI LIVE TIMING", circuiti[pista])

    # Filtri Categoria
    cat_filter = st.multiselect("Mostra Categorie:", ["PRO", "GENTLEMAN"], default=["PRO", "GENTLEMAN"])
    target_radar = st.text_input("Soglia Asterisco ⭐ (es. 43.500):", value="43.500")
    t_val = to_sec(target_radar)

    # Editor Dati Principale
    df_filtered = st.session_state.data[st.session_state.data['CATEGORIA'].isin(cat_filter)]
    edited = st.data_editor(
        df_filtered,
        column_config={
            "KART": st.column_config.TextColumn("KART", disabled=False),
            "BEST": st.column_config.TextColumn("TEMPO"),
            "CATEGORIA": st.column_config.SelectboxColumn("CAT", options=["PRO", "GENTLEMAN"]),
            "IN_PIT": st.column_config.CheckboxColumn("BOX"),
            "CAMBI": st.column_config.NumberColumn("🔁", disabled=True),
        },
        hide_index=True, use_container_width=True, key="radar_editor"
    )
    
    # Sincronizzazione Back-end e Logica Cambi/Timer
    for i, row in edited.iterrows():
        idx = st.session_state.data.index[st.session_state.data['KART'] == row['KART']][0]
        
        # Logica Cambio Pilota (Sincronizzata con spunta BOX)
        if row['IN_PIT'] and not st.session_state.data.at[idx, 'IN_PIT']:
            st.session_state.data.at[idx, 'PIT_START'] = time.time()
        if not row['IN_PIT'] and st.session_state.data.at[idx, 'IN_PIT']:
            st.session_state.data.at[idx, 'CAMBI'] += 1
            st.session_state.data.at[idx, 'PISTA_START'] = time.time()
        
        # Aggiornamento Best Lap e Stato
        st.session_state.data.at[idx, 'BEST'] = row['BEST']
        st.session_state.data.at[idx, 'IN_PIT'] = row['IN_PIT']
        st.session_state.data.at[idx, 'CATEGORIA'] = row['CATEGORIA']

# ==========================================
# 6. PAGINA 2: GESTIONE BOX (CORSIE E ALERT)
# ==========================================
elif page == "🚧 GESTIONE BOX":
    st.title("🚧 Gestione Corsie Box")
    num_corsie = st.slider("Visualizza Corsie:", 1, 4, 2)
    
    in_pit = st.session_state.data[st.session_state.data['IN_PIT'] == True]
    
    if not in_pit.empty:
        cols_box = st.columns(num_corsie)
        for i, (idx, r) in enumerate(in_pit.iterrows()):
            with cols_box[i % num_corsie]:
                # Countdown 3 Minuti (180 secondi)
                rimanente = 180 - (time.time() - r['PIT_START'])
                st.markdown(f"### 🏎️ KART {r['KART']} ({r['CATEGORIA']})")
                if rimanente > 0:
                    m, s = divmod(int(rimanente), 60)
                    st.markdown(f"<p class='timer-red'>{m:02d}:{s:02d}</p>", unsafe_allow_html=True)
                    if rimanente < 20: st.error("⚠️ PREPARA PILOTA - USCITA IMMINENTE")
                else:
                    st.markdown("<p class='timer-green'>✅ ESCI ORA!</p>", unsafe_allow_html=True)
                    st.toast(f"KART {r['KART']} PRONTO!", icon="🏁")
    else:
        st.info("Nessun Kart ai box. Attiva la spunta 'BOX' nel Radar.")

# ==========================================
# 7. PAGINA 3: ANALISI RECORD
# ==========================================
elif page == "📊 ANALISI RECORD":
    st.title("📊 Classifiche e Analisi Cambi")
    df_ana = st.session_state.data.copy()
    df_ana['V_NUM'] = df_ana['BEST'].apply(to_sec)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏆 Top 15 Assoluta")
        st.dataframe(df_ana.sort_values('V_NUM')[['KART', 'BEST', 'CATEGORIA', 'CAMBI']].head(15), use_container_width=True)
    
    with c2:
        st.subheader("🔁 Riepilogo Soste Effettuate")
        st.bar_chart(df_ana.set_index('KART')['CAMBI'])

# ==========================================
# 8. SISTEMA REFRESH (LOOP INFINITO)
# ==========================================
# Refresh ogni secondo per mantenere i timer attivi
time.sleep(1)
st.rerun()
