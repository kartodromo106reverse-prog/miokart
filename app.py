import streamlit as st
import pandas as pd
import time
import requests # Serve per "leggere" Apex in automatico

# Configurazione Display
st.set_page_config(page_title="WAR ROOM MONITOR", layout="wide")

# --- RECUPERO DATI AUTOMATICO (ESEMPIO) ---
def fetch_apex_data(api_url):
    try:
        # Qui Cursor dovrà inserire il link JSON ufficiale della tua pista
        response = requests.get(api_url)
        data = response.json()
        return data # Ritorna la classifica live
    except:
        return None

# --- INTERFACCIA A "BOTTONI" (TOUCH FRIENDLY) ---
st.title("📱 Monitor Strategico Live")

# Simuliamo i dati che arrivano da Apex
if 'live_karts' not in st.session_state:
    # Questa lista si aggiornerà da sola con l'API
    st.session_state.live_karts = [
        {"KART": "05", "TIME": "43.120", "POS": 1},
        {"KART": "12", "TIME": "43.450", "POS": 2},
        # ... altri kart
    ]

st.subheader("⚡ Tocca un Kart per mandarlo ai Box o segnarlo")

# Creiamo una griglia di pulsanti giganti basata sulla classifica LIVE
karts = st.session_state.live_karts
cols = st.columns(4) # 4 kart per riga, perfetti per l'iPhone

for i, k in enumerate(karts):
    with cols[i % 4]:
        # Il colore del bordo cambia se il tempo è sotto il target
        label = f"KART {k['KART']}\n⏱️ {k['TIME']}"
        
        if st.button(label, key=f"btn_{k['KART']}"):
            # AZIONE IMMEDIATA: Lo manda ai box o apre la sosta
            st.session_state.current_pit = k['KART']
            st.toast(f"Kart {k['KART']} selezionato!")

# --- AREA BOX DINAMICA ---
st.divider()
st.subheader("🚧 Gestione Sosta Attiva")
if 'current_pit' in st.session_state:
    st.error(f"GESTIONE KART: {st.session_state.current_pit}")
    if st.button("🏁 AVVIA TIMER 3 MIN"):
        # Parte il countdown...
        pass
