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

st.title("🏎️ Strategy Hub")

pista_scelta = st.selectbox("Seleziona il circuito attuale:", list(piste.keys()))

with st.form("registro_gara", clear_on_submit=True):
    nome = st.text_input("Nome e Cognome Pilota")
    team = st.text_input("Nome Team")
    kart = st.number_input("Numero Kart", min_value=1, max_value=999, step=1)
    submit = st.form_submit_button("🚀 REGISTRA E APRI LIVE TIMING")

    if submit:
        if nome and team:
            st.success(f"Registrato con successo!")
            st.balloons()
            link_apex = piste[pista_scelta]
            st.markdown(f"### [👉 CLICCA QUI PER IL LIVE TIMING DI {pista_scelta.upper()}]({link_apex})")
        else:
            st.error("Compila tutti i campi!")
