import streamlit as st

# Impostazioni di sicurezza
PASSWORD_CORRETTA = "Kart2024"
LINK_LIVE_TIMING = "https://speedhive.mylaps.com/" 

st.set_page_config(page_title="Strategy Hub", page_icon="🏎️")
st.title("Registrazione Strategy Hub")

# Interfaccia Pilota
nome = st.text_input("Nome e Cognome")
kart_n = st.text_input("Numero Kart")
codice = st.text_input("Codice Accesso Team", type="password")

if st.button("ACCEDI ALLA TELEMETRIA"):
    if not nome or not kart_n:
        st.warning("Inserisci Nome e Numero Kart per proseguire.")
    elif codice == PASSWORD_CORRETTA:
        st.success(f"Accesso Autorizzato! Ciao {nome}")
        st.link_button("CLICCA QUI PER I TEMPI LIVE 🏁", LINK_LIVE_TIMING)
    else:
        st.error("Codice Accesso errato. Chiedi al responsabile.")
