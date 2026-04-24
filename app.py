import streamlit as st
import pandas as pd

# 1. Configurazione Pagina
st.set_page_config(page_title="War Room 106", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #ff4b4b; color: white; font-weight: bold; font-size: 18px; }
    .stDataEditor { font-size: 16px !important; }
    .highlight { color: #ff4b4b; font-weight: bold; font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏎️ War Room - 106 Reverse")

# 2. Sezione Apex (Link dal tuo QR Code)
apex_link = "https://www.apex-timing.com/live-timing/kartodromo106/index.html"

col_link, col_btn = st.columns([1, 1])
with col_link:
    st.write("📊 **Monitor Apex Live**")
with col_btn:
    st.link_button("🚀 APRI LIVE INTERO", apex_link)

st.components.v1.iframe(apex_link, height=500, scrolling=True)

st.divider()

# 3. Tabella 15 Kart
st.subheader("⏱️ Inserimento Tempi (15 Kart)")

if 'laps_data' not in st.session_state:
    st.session_state.laps_data = pd.DataFrame({
        'Kart': [f"{i:02d}" for i in range(1, 16)],
        'Miglior Giro': [99.99] * 15
    })

edited_df = st.data_editor(
    st.session_state.laps_data,
    column_config={
        "Kart": st.column_config.TextColumn("N°", disabled=True),
        "Miglior Giro": st.column_config.NumberColumn("Tempo (sec)", format="%.3f"),
    },
    hide_index=True,
    use_container_width=True
)

if st.button("💾 SALVA E AGGIORNA CLASSIFICA"):
    st.session_state.laps_data = edited_df
    st.rerun()

# 4. Classifica con Asterisco ⭐
st.divider()
st.subheader("🌟 I più veloci in pista")

min_time = edited_df['Miglior Giro'].min()
top_5 = edited_df[edited_df['Miglior Giro'] < 99].sort_values('Miglior Giro').head(5)

if not top_5.empty:
    for i, (idx, row) in enumerate(top_5.iterrows()):
        is_record = "⭐" if row['Miglior Giro'] == min_time else f"{i+1}."
        st.markdown(f"<p class='highlight'>{is_record} Kart {row['Kart']} — {row['Miglior Giro']}s</p>", unsafe_allow_html=True)
else:
    st.write("Inserisci i tempi sopra per vedere la classifica.")
