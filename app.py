import streamlit as st
import pandas as pd
import time

# --- 1. CONFIGURAZIONE PAGINA E STILE GIGANTE ---
st.set_page_config(page_title="WAR ROOM 106 - PERSISTENT", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stLinkButton>a { 
        width: 100% !important; height: 90px !important; display: flex !important; 
        align-items: center !important; justify-content: center !important; 
        font-size: 26px !important; background-color: #ff4b4b !important; 
        color: white !important; font-weight: bold !important; border-radius: 20px !important;
    }
    [data-testid="stDataEditor"] div div div div { line-height: 55px !important; font-size: 22px !important; }
    .timer-wait { color: #FF3131; font-weight: bold; font-size: 32px; background: #000; padding: 10px; border-radius: 8px; border: 2px solid #FF3131; }
    .timer-ok { color: #00FF7F; font-weight: bold; font-size: 32px; background: #000; padding: 10px; border-radius: 8px; border: 2px solid #00FF7F; }
    .radar-card { background: #1e2129; border-left: 10px solid #ff4b4b; padding: 15px; border-radius: 12px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNZIONE PER NON PERDERE I DATI (PERSISTENZA) ---
# Usiamo @st.cache_resource per mantenere i dati vivi anche se ricarichi la pagina
@st.cache_resource
def get_persistent_data():
    return pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(20)],
        'BEST': ["99.999"] * 20,
        'CAMBI': [0] * 20,
        'IN_PIT': [False] * 20,
        'PIT_START': [0.0] * 20,
        'PISTA_START': [time.time()] * 20
    })

# Carichiamo i dati persistenti nella sessione attuale
if 'data' not in st.session_state:
    st.session_state.data = get_persistent_data()

# --- 3. LOGICA CONVERSIONE ---
def to_sec(t):
    try:
        t = str(t).strip().replace(',', '.')
        if ':' in t:
            m, s = t.split(':')
            return int(m) * 60 + float(s)
        return float(t)
    except: return 999.9

# --- 4. TENDINA PISTE ---
circuiti = {
    "Kart 106 Reverse": "https://live.apex-timing.com/kartodromo106reverse/",
    "Kart 106 Standard": "https://live.apex-timing.com/kartodromo106/",
    "Circuito di Siena": "https://live.apex-timing.com/siena/"
}

col_p, col_l = st.columns([1,1])
with col_p:
    pista_scelta = st.selectbox("📍 CIRCUITO:", list(circuiti.keys()))
with col_l:
    st.link_button("🚀 APEX LIVE", circuiti[pista_scelta])

# --- 5. EDITOR DATI ---
st.subheader("📊 Pannello Strategia")
target_in = st.text_input("🎯 SOGLIA RADAR:", value="43.500")
t_val = to_sec(target_in)

# L'editor modifica direttamente la sessione di stato
edited_df = st.data_editor(
    st.session_state.data,
    column_config={
        "KART": st.column_config.TextColumn("KART", disabled=False),
        "BEST": st.column_config.TextColumn("MIGLIOR GIRO"),
        "CAMBI": st.column_config.NumberColumn("🔁", disabled=True),
        "IN_PIT": st.column_config.CheckboxColumn("BOX"),
    },
    hide_index=True, use_container_width=True, key="editor_gara"
)

# --- 6. LOGICA DEI TIMER E DEI CAMBI (RIFATTA DA ZERO) ---
for i in range(len(edited_df)):
    # Rileva quando il box viene spuntato (Entrata)
    if edited_df.at[i, 'IN_PIT'] and not st.session_state.data.at[i, 'IN_PIT']:
        edited_df.at[i, 'PIT_START'] = time.time()
    
    # Rileva quando il box viene tolto (Uscita)
    if not edited_df.at[i, 'IN_PIT'] and st.session_state.data.at[i, 'IN_PIT']:
        edited_df.at[i, 'CAMBI'] += 1
        edited_df.at[i, 'PISTA_START'] = time.time()

# Sovrascriviamo i dati per non perderli
st.session_state.data = edited_df

# --- 7. DASHBOARD LIVE (RADAR + BOX) ---
st.divider()
c1, c2 = st.columns(2)

with c1:
    st.subheader("🌟 RADAR KART VELOCI")
    edited_df['V'] = edited_df['BEST'].apply(to_sec)
    veloci = edited_df[(edited_df['V'] <= t_val) & (edited_df['IN_PIT'] == False)].sort_values('V')
    
    if not veloci.empty:
        for _, r in veloci.iterrows():
            minuti_pista = (time.time() - r['PISTA_START']) / 60
            st.markdown(f"""
                <div class='radar-card'>
                    <b>KART {r['KART']}</b> — <span style='color:#ff4b4b;'>{r['BEST']}s</span><br>
                    <small>In pista da: {minuti_pista:.1f} min | Soste: {r['CAMBI']}</small>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.write("Nessun rivale sotto soglia.")

with c2:
    st.subheader("🚧 COUNTDOWN BOX (3 MIN)")
    in_pit = edited_df[edited_df['IN_PIT'] == True]
    
    if not in_pit.empty:
        for _, r in in_pit.iterrows():
            trascorso = time.time() - r['PIT_START']
            rimanente = 180 - trascorso # 180 secondi = 3 minuti
            
            if rimanente > 0:
                m, s = divmod(int(rimanente), 60)
                st.markdown(f"KART {r['KART']}: <span class='timer-wait'>{m:02d}:{s:02d}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"KART {r['KART']}: <span class='timer-ok'>✅ ESCI ORA!</span>", unsafe_allow_html=True)
    else:
        st.write("Nessun kart in sosta.")

# --- 8. REFRESH AUTOMATICO (INDISPENSABILE PER IL COUNTDOWN) ---
# Senza queste due righe, il timer rimane fermo a 02:59
time.sleep(1)
st.rerun()
