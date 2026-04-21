import streamlit as st
import pandas as pd
import time
import random

# Configurazione per tutto lo schermo (Z Flip5)
st.set_page_config(page_title="Kart War Room", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: black; color: white; }
    .big-font { font-size:18px !important; font-family: 'Courier New', Courier, monospace; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🏎️ Accesso War Room")
    pwd = st.text_input("Password Team", type="password")
    if st.button("Entra"):
        if pwd == "kart2024": # Puoi cambiare la password qui
            st.session_state.auth = True
            st.rerun()
    st.stop()

st.title("📊 Strategy Engine Live")

# Dati simulati
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'POS': range(1, 51),
        'NOME': [f"KART {random.randint(1,99)}" for _ in range(50)],
        'CAT': ["NONE"] * 50,
        'GAP': ["0.00"] * 50,
        'TEMPO': [46.0 + random.uniform(0, 5) for _ in range(50)],
        'C': [0] * 50,
        'STINT': [60] * 50
    })

# Header Spaziata
cols = st.columns([1, 2, 2, 2, 2, 1, 1])
fields = ["POS", "NOME", "CAT", "GAP", "TEMPO", "C", "STINT"]
for col, field in zip(cols, fields):
    col.write(f"**{field}**")

# Righe
for i, row in st.session_state.data.iterrows():
    c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 2, 2, 2, 2, 1, 1])
    c1.write(f"{row['POS']}")
    
    color = "white"
    if row['CAT'] == "PRO": color = "#FF4444"
    elif row['CAT'] == "SEMI": color = "#4444FF"
    elif row['CAT'] == "GENT": color = "#44FF44"
    
    c2.markdown(f"<span style='color:{color}; font-weight:bold;'>{row['NOME']}</span>", unsafe_allow_html=True)
    
    if c3.button(f"{row['CAT']}", key=f"btn_{i}"):
        cats = ["NONE", "PRO", "SEMI", "GENT"]
        idx = cats.index(row['CAT'])
        st.session_state.data.at[i, 'CAT'] = cats[(idx + 1) % 4]
        st.rerun()

    c4.write(row['GAP'])
    c5.write(f"{row['TEMPO']:.3f}")
    c6.write(str(row['C']))
    c7.write(f"{row['STINT']}m")

time.sleep(2)
st.rerun()
