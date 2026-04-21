import streamlit as st

# Configurazione Accesso
PASSWORD_CORRETTA = "Kart2024"
# Link ai tempi (Sostituisci questo link se ne hai uno specifico)
LINK_LIVE_TIMING = "https://speedhive.mylaps.com/" 

st.set_page_config(page_title="Strategy Hub", page_icon="🏎️")
st.title("Registrazione Strategy Hub")

nome = st.text_input("Nome e Cognome")
kart_n = st.text_input("Numero Kart")
password_inserita = st.text_input("Codice Accesso Team", type="password")

if st.button("ACCEDI ALLA TELEMETRIA"):
    if not nome or not kart_n:
        st.warning("Inserisci Nome e Numero Kart.")
    elif password_inserita == PASSWORD_CORRETTA:
        st.success(f"Accesso Autorizzato! Ciao {nome}")
        st.markdown(f"""
            <a href="{LINK_LIVE_TIMING}" target="_blank">
                <button style="width:100%; height:50px; background-color:#FF4B4B; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold;">
                    CLICCA QUI PER I TEMPI LIVE 🏁
                </button>
            </a>
        """, unsafe_allow_html=True)
    else:
        st.error("Codice Accesso errato.")
