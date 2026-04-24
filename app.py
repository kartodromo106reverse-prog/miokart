import streamlit as st
import pandas as pd
import time

# --- CONFIGURAZIONE PAGINA E SICUREZZA ---
st.set_page_config(page_title="Kart Strategy - War Room", layout="wide", initial_sidebar_state="expanded")

# Inizializzazione variabili di sessione (Stato dell'utente)
if 'auth_status' not in st.session_state:
    st.session_state['auth_status'] = 'guest' # guest, pending, admin, team
if 'team_data' not in st.session_state:
    st.session_state['team_data'] = {}

# --- FUNZIONE: MODULO DI REGISTRAZIONE (IL CANCELLO) ---
def schermata_registrazione():
    st.title("🛡️ Registrazione Strategy Hub")
    st.markdown("""
    Benvenuto nel sistema di gestione corse. 
    L'accesso è riservato ai team autorizzati. Inserisci i tuoi dati per richiedere l'abilitazione.
    """)
    
    with st.form("form_iscrizione"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome e Cognome Pilota/Manager")
            email = st.text_input("Indirizzo Email")
        with col2:
            cellulare = st.text_input("Numero di Cellulare")
            team_nome = st.text_input("Nome della Squadra")
        
        kart_num = st.text_input("Numero del tuo Kart", help="Il sistema isolerà i dati per questo numero")
        note = st.text_area("Note aggiuntive (Gara, Evento, etc.)")
        
        submit = st.form_submit_button("INVIA RICHIESTA DI ACCESSO")
        
        if submit:
            if nome and email and cellulare and team_nome and kart_num:
                # QUI IL SISTEMA SALVA I DATI NEL DATABASE (Es: Supabase/Sheets)
                st.success(f"Grazie {nome}! La tua richiesta per il Team {team_nome} è stata inviata con successo.")
                st.info("Riceverai una notifica non appena l'Amministratore approverà il tuo account.")
                # Per il test attuale, simuliamo l'approvazione immediata al click
                st.session_state['team_data'] = {"nome": team_nome, "kart": kart_num}
                st.session_state['auth_status'] = 'team'
                time.sleep(2)
                st.rerun()
            else:
                st.error("Per favore, compila tutti i campi obbligatori.")

# --- FUNZIONE: WAR ROOM (IL CUORE PRIVATO) ---
def war_room():
    team = st.session_state['team_data']['nome']
    kart = st.session_state['team_data']['kart']
    
    # Sidebar Personalizzata
    st.sidebar.title(f"Box: {team}")
    st.sidebar.markdown(f"🎯 Monitorando Kart: **{kart}**")
    
    st.sidebar.divider()
    opzione = st.sidebar.radio("Navigazione", ["Tabellone Tempi", "Strategia & Pit Stop", "Meteo Radar"])
    
    if st.sidebar.button("LOGOUT / ESCI"):
        st.session_state['auth_status'] = 'guest'
        st.rerun()

    # Layout Principale
    st.title(f"🏁 War Room - {team}")
    
    if opzione == "Tabellone Tempi":
        col1, col2, col3 = st.columns(3)
        col1.metric("Miglior Giro", "45.123", "-0.200")
        col2.metric("Ultimo Giro", "45.450", "+0.127")
        col3.metric("Posizione Cat.", "3°", "PRO")
        
        st.subheader("Classifica Live (Apex Timing)")
        # Simulazione tabella isolata
        df = pd.DataFrame({
            'Pos': [1, 2, 3],
            'Kart': [f"KART {kart}", "KART 12", "KART 05"],
            'Gap': ["--", "+1.2s", "+1.5s"],
            'Status': ["Pista", "In Pit", "Pista"]
        })
        st.table(df)

    elif opzione == "Strategia & Pit Stop":
        st.subheader("Pianificazione Soste")
        tempo_box = st.number_input("Tempo Sosta Obbligatorio (sec)", value=180)
        if st.button("🚀 AVVIA COUNTDOWN PIT STOP"):
            st.warning(f"KART {kart} NEI BOX - USCITA TRA {tempo_box} SECONDI")
            
    elif opzione == "Meteo Radar":
        st.subheader("Monitoraggio Meteo Real-Time")
        st.write("☀️ **Meteo:** Sereno | **Asfalto:** 28°C | **Pioggia:** 2%")

# --- LOGICA DI AVVIO ---
if st.session_state['auth_status'] == 'guest':
    schermata_registrazione()
elif st.session_state['auth_status'] == 'team':
    war_room()
