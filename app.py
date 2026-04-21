import streamlit as st
import pandas as pd

# Configurazione Google Sheets
SHEET_ID = "1KWICIXtWv-L79HRyh1OZkYJHnsIwHLIGYcjDj1xfkZY"
PISTE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1748281313"

st.set_page_config(page_title="Strategy Hub", page_icon="🏎️")

def carica_piste():
    try:
        df_piste = pd.read_csv(PISTE_URL)
        return pd.Series(df_piste["Link Apex"].values, index=df_piste["Nome Pista"]).to_dict()
    except:
        return {"Misanino": "https://www.apex-timing.com/live-timing/misanino-kart/"}

piste = carica_piste()

# Inizializziamo la memoria della sessione
if "registrato" not in st.session_state:
    st.session_state.registrato = False

st.title("🏎️ Strategy Hub")

# Se il pilota è già passato di qui...
if st.session_state.registrato:
    st.success(f"Bentornato {st.session_state.nome}!")
    link_veloce = piste.get(st.session_state.pista, "#")
    st.markdown(f"### 🏁 [RE-INSERISCITI NEL LIVE TIMING DI {st.session_state.pista.upper()}]({link_veloce})")
    if st.button("Modifica dati o Cambia Pista"):
        st.session_state.registrato = False
        st.rerun()

# Se è la prima volta o vuole cambiare...
else:
    pista_scelta = st.selectbox("Seleziona il circuito:", list(piste.keys()))
    
    with st.form("registro_veloce"):
        nome = st.text_input("Nome e Cognome")
        team = st.text_input("Nome Team")
        kart = st.number_input("Numero Kart", min_value=1, step=1)
        submit = st.form_submit_button("🚀 REGISTRA E APRI")

        if submit:
            if nome and team:
                # Salviamo in memoria
                st.session_state.registrato = True
                st.session_state.nome = nome
                st.session_state.pista = pista_scelta
                
                st.balloons()
                link_apex = piste[pista_scelta]
                st.markdown(f"### ✅ [CLICCA QUI PER IL LIVE TIMING]({link_apex})")
                st.info("I tuoi dati sono stati salvati. Se chiudi l'app, li ricorderò!")
            else:
                st.error("Inserisci Nome e Team!")
