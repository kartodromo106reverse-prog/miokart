import streamlit as st
import pandas as pd

# 1. Configurazione Pagina (NON MODIFICARE)
st.set_page_config(page_title="War Room 106", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stLinkButton>a { 
        width: 100% !important; 
        height: 80px !important; 
        display: flex !important; 
        align-items: center !important; 
        justify-content: center !important; 
        font-size: 22px !important; 
        background-color: #ff4b4b !important; 
        color: white !important; 
        font-weight: bold !important;
        border-radius: 12px !important;
        text-decoration: none !important;
    }
    .highlight { color: #ff4b4b; font-weight: bold; font-size: 24px; border-left: 5px solid #ff4b4b; padding-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏎️ War Room - 106 Reverse")

# 2. Aggiornamento Link Apex (Dalle tue foto)
apex_link = "https://live.apex-timing.com/kartodromo106reverse/"
st.link_button("🚀 APRI LIVE TIMING APEX", apex_link)

st.divider()

# 3. Gestione Tabella (15 Kart base, espandibile)
st.subheader("📊 Tabella Tempi")

if 'laps_data' not in st.session_state:
    st.session_state.laps_data = pd.DataFrame({
        'Kart': [f"{i:02d}" for i in range(1, 16)],
        'Miglior Giro': [99.999] * 15
    })

# Editor dinamico (permette di aggiungere righe se ci sono più di 15 kart)
edited_df = st.data_editor(
    st.session_state.laps_data,
    column_config={
        "Kart": st.column_config.TextColumn("N° Kart"),
        "Miglior Giro": st.column_config.NumberColumn("Best Lap (sec)", format="%.3f"),
    },
    hide_index=True,
    use_container_width=True,
    num_rows="dynamic" 
)

if st.button("💾 SALVA E AGGIORNA CLASSIFICA"):
    st.session_state.laps_data = edited_df
    st.rerun()

# 4. Classifica Record con Stella ⭐
st.divider()
st.subheader("🌟 Record della Sessione")

# Filtra solo chi ha un tempo inserito
valid_times = edited_df[edited_df['Miglior Giro'] < 99].sort_values('Miglior Giro')

if not valid_times.empty:
    min_time = valid_times['Miglior Giro'].min()
    for i, (idx, row) in enumerate(valid_times.head(5).iterrows()):
        # Assegna la stella solo al record assoluto
        prefisso = "⭐ RECORD:" if row['Miglior Giro'] == min_time else f"{i+1}."
        st.markdown(f"<div class='highlight'>{prefisso} Kart {row['Kart']} — {row['Miglior Giro']}s</div>", unsafe_allow_html=True)
else:
    st.write("Inserisci i tempi per vedere la classifica.")
