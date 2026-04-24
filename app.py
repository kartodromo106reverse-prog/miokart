import streamlit as st
import pandas as pd
import time

# 1. SETUP E STRUTTURA (Invariata)
st.set_page_config(page_title="War Room 106 Endurance", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stLinkButton>a { 
        width: 100% !important; height: 70px !important; display: flex !important; 
        align-items: center !important; justify-content: center !important; 
        font-size: 20px !important; background-color: #ff4b4b !important; 
        color: white !important; font-weight: bold !important; border-radius: 12px !important;
        text-decoration: none !important;
    }
    /* Countdown Styling */
    .timer-ok { color: #00FF7F; font-weight: bold; font-size: 22px; }
    .timer-wait { color: #FF3131; font-weight: bold; font-size: 22px; }
    .record-box { background-color: #1e2129; border-left: 5px solid #ff4b4b; padding: 10px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 2. TASTO APEX (Invariato)
st.link_button("🚀 APRI LIVE TIMING APEX", "https://live.apex-timing.com/kartodromo106reverse/")

# 3. NUOVA LOGICA: TARGET TIME
st.subheader("🎯 Obiettivo della Sessione")
target_time = st.number_input("Tempo da monitorare (sec):", value=43.500, format="%.3f")

# 4. TABELLA GESTIONE (Aggiornata con Pit Stop)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(15)],
        'BEST': [99.999] * 15,
        'IN_PIT': [False] * 15,
        'PIT_START': [0.0] * 15
    })

edited_df = st.data_editor(
    st.session_state.data,
    column_config={
        "KART": st.column_config.TextColumn("N° KART", disabled=True),
        "BEST": st.column_config.NumberColumn("MIGLIOR GIRO", format="%.3f"),
        "IN_PIT": st.column_config.CheckboxColumn("BOX (3 MIN)"),
    },
    hide_index=True,
    use_container_width=True
)

# Calcolo automatico entrata box
for i in range(len(edited_df)):
    if edited_df.at[i, 'IN_PIT'] and not st.session_state.data.at[i, 'IN_PIT']:
        edited_df.at[i, 'PIT_START'] = time.time()
    if not edited_df.at[i, 'IN_PIT']:
        edited_df.at[i, 'PIT_START'] = 0.0

if st.button("💾 AGGIORNA E CALCOLA"):
    st.session_state.data = edited_df
    st.rerun()

# 5. STATISTICHE E COUNTDOWN
st.divider()
col_stats, col_timer = st.columns(2)

with col_stats:
    st.subheader("🌟 Radar Kart Veloci")
    # Mostra solo i kart sotto il target
    veloci = edited_df[edited_df['BEST'] <= target_time].sort_values('BEST')
    if not veloci.empty:
        for _, row in veloci.iterrows():
            st.markdown(f"<div class='record-box'><b>KART {row['KART']}</b>: {row['BEST']:.3f}s</div>", unsafe_allow_html=True)
    else:
        st.write("Nessun kart sotto la soglia.")

with col_timer:
    st.subheader("🚧 Countdown Pit Stop")
    pit_karts = edited_df[edited_df['IN_PIT'] == True]
    if not pit_karts.empty:
        for _, row in pit_karts.iterrows():
            rimanente = 180 - (time.time() - row['PIT_START'])
            if rimanente > 0:
                m, s = divmod(int(rimanente), 60)
                st.markdown(f"KART **{row['KART']}**: <span class='timer-wait'>ATTENDERE {m:02d}:{s:02d}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"KART **{row['KART']}**: <span class='timer-ok'>✅ PUÒ USCIRE!</span>", unsafe_allow_html=True)
    else:
        st.write("Nessun kart ai box.")

# Refresh automatico ogni 10 secondi per il timer
time.sleep(10)
st.rerun()
