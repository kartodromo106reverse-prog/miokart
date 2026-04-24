import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# Configurazione Pagina
st.set_page_config(page_title="War Room 15 Kart", layout="wide")

# CSS Personalizzato per evitare sovrapposizioni su Mobile
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTable { font-size: 14px !important; }
    /* Fix per sovrapposizioni mobile */
    @media (max-width: 600px) {
        .stTable { font-size: 12px !important; }
        div[data-testid="stMetricValue"] { font-size: 18px !important; }
        .row-style { padding: 5px 0px; border-bottom: 1px solid #333; }
    }
    .asterisk { color: #ff4b4b; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏎️ War Room Kart - Live Stats")

# --- SEZIONE APEX ---
st.subheader("Live Timing Apex")
# Sostituisci l'URL qui sotto con il tuo link Apex reale se diverso
apex_url = "https://static.apex-timing.com/web-tv/?karting=kartodromo-106-reverse" 
components.iframe(apex_url, height=500, scrolling=True)

# --- LOGICA DATI ---
# Inizializziamo i dati per 15 Kart
if 'laps_data' not in st.session_state:
    st.session_state.laps_data = pd.DataFrame({
        'Kart': [f"{i:02d}" for i in range(1, 16)],
        'Ultimo Giro': [0.00] * 15,
        'Best': [99.99] * 15
    })

# --- STATISTICHE VELOCI ---
st.subheader("🏆 Leaderboard")
best_overall = st.session_state.laps_data.loc[st.session_state.laps_data['Best'].idxmin()]

col1, col2 = st.columns(2)
with col1:
    st.metric("Kart più Veloce", f"Kart {best_overall['Kart']}")
with col2:
    st.metric("Miglior Tempo", f"{best_overall['Best']}s")

# --- TABELLA 15 KART ---
st.subheader("Monitoraggio Kart")

# Soglia per l'asterisco (es. sotto i 45 secondi o il tempo record attuale)
soglia_record = best_overall['Best'] 

def format_kart_display(row):
    # Se il Best del kart è uguale al record assoluto, aggiungi l'asterisco
    suffix = " ⭐" if row['Best'] <= soglia_record and row['Best'] < 99 else ""
    return f"{row['Kart']}{suffix}"

# Visualizzazione tabella semplificata
edited_df = st.data_editor(
    st.session_state.laps_data,
    column_config={
        "Kart": st.column_config.TextColumn("Kart", disabled=True),
        "Ultimo Giro": st.column_config.NumberColumn("Ultimo (sec)", format="%.2f"),
        "Best": st.column_config.NumberColumn("Best (sec)", format="%.2f"),
    },
    hide_index=True,
    use_container_width=True
)

if st.button("Aggiorna Tempi"):
    st.session_state.laps_data = edited_df
    st.rerun()

st.info("Nota: I Kart con l'asterisco ⭐ sono quelli che hanno raggiunto il miglior tempo della sessione.")
