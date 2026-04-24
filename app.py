import streamlit as st
import pandas as pd
import time

# ==========================================
# 1. LOGICA DI CONVERSIONE TEMPI (PROFESSIONALE)
# ==========================================
def converti_in_secondi(tempo_testo):
    try:
        tempo_testo = str(tempo_testo).strip().replace(',', '.')
        if ':' in tempo_testo:
            minuti, secondi = tempo_testo.split(':')
            return int(minuti) * 60 + float(secondi)
        return float(tempo_testo)
    except:
        return 999.999

# ==========================================
# 2. CONFIGURAZIONE LAYOUT E TOUCH-SENSITIVITY
# ==========================================
st.set_page_config(page_title="WAR ROOM 106 - FULL PRO", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    
    /* TASTO APEX GIGANTE PER IL POLLICE */
    .stLinkButton>a { 
        width: 100% !important; height: 100px !important; display: flex !important; 
        align-items: center !important; justify-content: center !important; 
        font-size: 26px !important; background-color: #ff4b4b !important; 
        color: white !important; font-weight: bold !important; border-radius: 20px !important;
        text-decoration: none !important; border: 3px solid white !important;
    }
    
    /* AUMENTO SENSIBILITÀ TOUCH (Celle alte 60px) */
    [data-testid="stDataEditor"] div div div div {
        line-height: 40px !important;
        font-size: 22px !important;
    }
    
    /* INPUT TESTO GRANDI */
    input {
        height: 60px !important;
        font-size: 22px !important;
    }

    /* BOX ESTETICI PER RECORD E TIMER */
    .record-box { 
        background-color: #1e2129; border-left: 10px solid #ff4b4b; 
        padding: 20px; border-radius: 12px; margin-bottom: 10px; font-size: 22px; 
    }
    .timer-wait { color: #FF3131; font-weight: bold; font-size: 26px; animation: blinker 1.5s linear infinite; }
    .timer-ok { color: #00FF7F; font-weight: bold; font-size: 26px; }
    @keyframes blinker { 50% { opacity: 0.3; } }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. COLLEGAMENTO APEX TIMING
# ==========================================
st.link_button("🚀 APRI LIVE TIMING APEX", "https://live.apex-timing.com/kartodromo106reverse/")

# ==========================================
# 4. PARAMETRI TARGET
# ==========================================
st.subheader("🎯 Obiettivi e Strategia")
target_input = st.text_input("Soglia Record (es. 43.500 o 1:12.000):", value="43.500")
target_val = converti_in_secondi(target_input)

# ==========================================
# 5. DATABASE DINAMICO (KART SBLOCCATI)
# ==========================================
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(15)],
        'GIRO_TESTO': ["99.999"] * 15,
        'IN_PIT': [False] * 15,
        'PIT_START': [0.0] * 15
    })

st.subheader("⏱️ Tabella Gestione Live")
st.caption("Clicca sui numeri per cambiarli (es. 50, 60). Spunta 'BOX' per il countdown 3 min.")

# TABELLA MODIFICABILE E ADATTA AL TOUCH
edited_df = st.data_editor(
    st.session_state.data,
    column_config={
        "KART": st.column_config.TextColumn("N° KART", disabled=False), # SBLOCCATO
        "GIRO_TESTO": st.column_config.TextColumn("MIGLIOR GIRO"),
        "IN_PIT": st.column_config.CheckboxColumn("BOX (3m)", width="medium"),
    },
    hide_index=True,
    use_container_width=True,
    num_rows="dynamic"
)

# Calcolo Valori Numerici
edited_df['GIRO_NUM'] = edited_df['GIRO_TESTO'].apply(converti_in_secondi)

# Logica Timer Box 180s (3 minuti)
for i in range(len(edited_df)):
    if edited_df.at[i, 'IN_PIT'] and not st.session_state.data.at[i, 'IN_PIT']:
        edited_df.at[i, 'PIT_START'] = time.time()
    if not edited_df.at[i, 'IN_PIT']:
        edited_df.at[i, 'PIT_START'] = 0.0

if st.button("💾 SALVA DATI E AGGIORNA CLASSIFICA"):
    st.session_state.data = edited_df
    st.rerun()

# ==========================================
# 6. DASHBOARD RISULTATI (RECORD + TIMER)
# ==========================================
st.divider()
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🌟 Radar Kart Veloci")
    # Filtra e ordina per i più veloci sotto il target
    veloci = edited_df[edited_df['GIRO_NUM'] <= target_val].sort_values('GIRO_NUM')
    if not veloci.empty:
        for _, row in veloci.iterrows():
            st.markdown(f"""
                <div class='record-box'>
                    <b>KART {row['KART']}</b><br>
                    <span style='color:#ff4b4b;'>Tempo: {row['GIRO_TESTO']}</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.write("Nessun kart nel radar.")

with col_right:
    st.subheader("🚧 Status Pit Stop")
    pit_active = edited_df[edited_df['IN_PIT'] == True]
    if not pit_active.empty:
        for _, row in pit_active.iterrows():
            rimanente = 180 - (time.time() - row['PIT_START'])
            if rimanente > 0:
                m, s = divmod(int(rimanente), 60)
                st.markdown(f"KART **{row['KART']}**: <span class='timer-wait'>FERMO ({m:02d}:{s:02d})</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"KART **{row['KART']}**: <span class='timer-ok'>✅ PUÒ USCIRE!</span>", unsafe_allow_html=True)
    else:
        st.write("Nessun kart ai box.")

# Refresh ogni 10 secondi per aggiornare i timer senza scaricare la batteria
time.sleep(10)
st.rerun()
