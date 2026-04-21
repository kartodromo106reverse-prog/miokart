import streamlit as st
import pandas as pd
import time
import random

# Configurazione Pagina (Usa tutto lo schermo)
st.set_page_config(page_title="Kart Strategy Pro", layout="wide")

# Stile CSS per rendere la tabella gigante e leggibile come su Z Flip5
st.markdown("""
    <style>
    .reportview-container .main .block-container{ padding-top: 1rem; }
    .stButton>button { width: 100%; height: 3em; background-color: #ff4b4b; color: white; }
    .big-font { font-size:20px !important; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🏎️ War Room Login")
    password = st.text_input("Inserisci Password Team", type="password")
    if st.button("Entra"):
        if password: # Qui puoi mettere una logica per password diverse
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- LOGICA APP ---
st.title("📊 Strategy Engine Live")

# Selezione Pista
pista = st.selectbox("Seleziona Circuito", ["SOLE LUNA VITTORIA", "106 REVERSE", "106 STANDARD", "NAPOLI"])

# Generazione Dati (Simulati per ogni team autonomo)
if 'data' not in st.session_state:
    df = pd.DataFrame({
        'POS': range(1, 51),
        'NOME': [f"KART {random.randint(1,99)}" for _ in range(50)],
        'CAT': ["NONE"] * 50,
        'GAP': [0.0] * 50,
        'TEMPO': [46.0 + random.uniform(0, 5) for _ in range(50)],
        'C': [0] * 50,
        'STINT': [60] * 50
    })
    st.session_state.data = df

# Funzione per simulare i tempi
def update_times():
    st.session_state.data['TEMPO'] = st.session_state.data['TEMPO'].apply(lambda x: max(44.0, x + random.uniform(-0.1, 0.1)))
    st.session_state.data = st.session_state.data.sort_values(by='TEMPO').reset_index(drop=True)
    st.session_state.data['POS'] = range(1, 51)
    best = st.session_state.data['TEMPO'].min()
    st.session_state.data['GAP'] = st.session_state.data['TEMPO'].apply(lambda x: f"+{x-best:.2f}" if x > best else "LEAD")

# Visualizzazione Classifica
update_times()

# Tabella Professionale
# Usiamo le colonne di Streamlit per spaziare
cols = st.columns([1, 2, 2, 2, 2, 1, 1])
fields = ["POS", "NOME", "CAT", "GAP", "TEMPO", "C", "STINT"]

# Header
for col, field in zip(cols, fields):
    col.write(f"**{field}**")

# Righe
for i, row in st.session_state.data.iterrows():
    c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 2, 2, 2, 2, 1, 1])
    c1.write(f"{row['POS']}")
    
    # Colore in base alla categoria
    color = "#FFFFFF"
    if row['CAT'] == "PRO": color = "#FF4444"
    elif row['CAT'] == "SEMI": color = "#4444FF"
    elif row['CAT'] == "GENT": color = "#44FF44"
    
    c2.markdown(f"<span style='color:{color}; font-weight:bold;'>{row['NOME']}</span>", unsafe_allow_html=True)
    
    # Bottone per cambiare categoria (Sottomenu)
    if c3.button(f"{row['CAT']}", key=f"btn_{i}"):
        cats = ["NONE", "PRO", "SEMI", "GENT"]
        idx = cats.index(row['CAT'])
        st.session_state.data.at[i, 'CAT'] = cats[(idx + 1) % 4]
        st.rerun()

    c4.write(f"{row['GAP']}")
    c5.write(f"{row['TEMPO']:.3f}")
    c6.write(f"{row['C']}")
    c7.write(f"{row['STINT']}m")

if st.button("RESET TUTTE CATEGORIE"):
    st.session_state.data['CAT'] = "NONE"
    st.rerun()

time.sleep(1)
st.rerun()
