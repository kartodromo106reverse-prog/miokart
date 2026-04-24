import streamlit as st
import pandas as pd
import time

# 1. FUNZIONE CONVERSIONE (Sempre presente per i tempi 1:13.xxx)
def converti_in_secondi(tempo_testo):
    try:
        tempo_testo = str(tempo_testo).strip().replace(',', '.')
        if ':' in tempo_testo:
            minuti, secondi = tempo_testo.split(':')
            return int(minuti) * 60 + float(secondi)
        return float(tempo_testo)
    except:
        return 999.999

# 2. CONFIGURAZIONE E STILE TOUCH (Z FLIP 5)
st.set_page_config(page_title="STRATEGIA 106 ENDURANCE", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stLinkButton>a { 
        width: 100% !important; height: 90px !important; display: flex !important; 
        align-items: center !important; justify-content: center !important; 
        font-size: 24px !important; background-color: #ff4b4b !important; 
        color: white !important; font-weight: bold !important; border-radius: 15px !important;
        border: 2px solid white !important;
    }
    /* Righe tabella molto alte per il touch */
    [data-testid="stDataEditor"] div div div div { line-height: 45px !important; font-size: 20px !important; }
    
    .timer-wait { color: #FF3131; font-weight: bold; font-size: 24px; }
    .timer-ok { color: #00FF7F; font-weight: bold; font-size: 24px; }
    .stat-card { background-color: #1e2129; border-left: 8px solid #ff4b4b; padding: 15px; border-radius: 10px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. TASTO APEX (Sempre visibile)
st.link_button("🚀 APRI LIVE TIMING APEX", "https://live.apex-timing.com/kartodromo106reverse/")

# 4. INIZIALIZZAZIONE DATI (Persistenza dei Cambi e Tempi)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(15)],
        'BEST_T': ["99.999"] * 15,
        'CAMBI': [0] * 15,
        'IN_PIT': [False] * 15,
        'PIT_START': [0.0] * 15,
        'PISTA_START': [time.time()] * 15
    })

# 5. TARGET E TABELLA
target_in = st.text_input("🎯 Soglia Radar (es. 43.500):", value="43.500")
t_val = converti_in_secondi(target_in)

st.subheader("📋 Gestione Strategia")
edited_df = st.data_editor(
    st.session_state.data,
    column_config={
        "KART": st.column_config.TextColumn("N°", disabled=False),
        "BEST_T": st.column_config.TextColumn("BEST"),
        "CAMBI": st.column_config.NumberColumn("🔁", disabled=True),
        "IN_PIT": st.column_config.CheckboxColumn("BOX"),
    },
    hide_index=True, use_container_width=True
)

# --- LOGICA AUTOMATICA CAMBI E TIMER ---
for i in range(len(edited_df)):
    # Caso: Entra ai Box
    if edited_df.at[i, 'IN_PIT'] and not st.session_state.data.at[i, 'IN_PIT']:
        edited_df.at[i, 'PIT_START'] = time.time()
    
    # Caso: Esce dai Box (Aggiunge un cambio e resetta timer pista)
    if not edited_df.at[i, 'IN_PIT'] and st.session_state.data.at[i, 'IN_PIT']:
        edited_df.at[i, 'CAMBI'] += 1
        edited_df.at[i, 'PISTA_START'] = time.time()

if st.button("💾 SALVA STATISTICHE"):
    st.session_state.data = edited_df
    st.rerun()

# 6. DASHBOARD DOPPIA
st.divider()
col_sx, col_dx = st.columns(2)

with col_sx:
    st.subheader("🌟 Radar & Pista")
    edited_df['VAL'] = edited_df['BEST_T'].apply(converti_in_secondi)
    # Mostra i più veloci che sono in pista
    veloci = edited_df[(edited_df['VAL'] <= t_val) & (edited_df['IN_PIT'] == False)].sort_values('VAL')
    for _, r in veloci.iterrows():
        pista_sec = time.time() - r['PISTA_START']
        mp, sp = divmod(int(pista_sec), 60)
        st.markdown(f"""
            <div class='stat-card'>
                <b>KART {r['KART']}</b> | {r['BEST_T']}s<br>
                <small>In pista da: {mp}m {sp}s | Cambi: {r['CAMBI']}</small>
            </div>
        """, unsafe_allow_html=True)

with col_dx:
    st.subheader("🚧 Countdown Box")
    in_pit = edited_df[edited_df['IN_PIT'] == True]
    for _, r in in_pit.iterrows():
        rimanente = 180 - (time.time() - r['PIT_START'])
        if rimanente > 0:
            m, s = divmod(int(rimanente), 60)
            st.markdown(f"KART **{r['KART']}**: <span class='timer-wait'>STOP ({m:02d}:{s:02d})</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"KART **{r['KART']}**: <span class='timer-ok'>✅ ESCI!</span>", unsafe_allow_html=True)

# REFRESH TOTALE OGNI SECONDO (Per i timer e per seguire Apex)
time.sleep(1)
st.rerun()
