import streamlit as st

# Configurazione Accesso
PASSWORD_CORRETTA = "Kart2024"
LINK_LIVE_TIMING = "https://www.apex-timing.com/live-timing/kartodromo106reverse"

st.set_page_config(page_title="Strategy Hub", page_icon="🏎️")

# Inizializzazione della sessione (La Memoria dell'app)
if 'autenticato' not in st.session_state:
    st.session_state.autenticato = False

st.title("Registrazione Strategy Hub")

# Se l'utente NON è ancora autenticato, mostra il modulo
if not st.session_state.autenticato:
    nome = st.text_input("Nome e Cognome")
    kart_n = st.text_input("Numero Kart")
    password_inserita = st.text_input("Codice Accesso Team", type="password")

    if st.button("ACCEDI ALLA TELEMETRIA"):
        if not nome or not kart_n:
            st.warning("Inserisci Nome e Numero Kart.")
        elif password_inserita == PASSWORD_CORRETTA:
            st.session_state.autenticato = True
            st.session_state.nome_pilota = nome
            st.rerun() # Ricarica l'app per mostrare il tasto
        else:
            st.error("Codice Accesso errato.")

# Se l'utente È autenticato, mostra direttamente il tasto per i tempi
else:
    st.success(f"Bentornato, {st.session_state.nome_pilota}! Accesso attivo.")
    st.link_button("CLICCA QUI PER I TEMPI LIVE 🏁", LINK_LIVE_TIMING)
    
    if st.button("Esci / Cambia Pilota"):
        st.session_state.autenticato = False
        st.rerun()
