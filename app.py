# ==========================================
# 3. GESTIONE MULTI-PISTA (TENDINA APEX)
# ==========================================
st.subheader("📍 Seleziona Circuito")

# Dizionario dei circuiti: puoi aggiungere altri link qui sotto
circuiti = {
    "Kartodromo 106 Reverse": "https://live.apex-timing.com/kartodromo106reverse/",
    "Kartodromo 106 Standard": "https://live.apex-timing.com/kartodromo106/",
    "Altra Pista 1": "https://live.apex-timing.com/esempio1/",
    "Altra Pista 2": "https://live.apex-timing.com/esempio2/"
}

# Creazione della tendina
nome_pista = st.selectbox("Scegli la pista attiva:", list(circuiti.keys()))
link_selezionato = circuiti[nome_pista]

# Tasto dinamico che cambia in base alla scelta nella tendina
st.link_button(f"🚀 APRI LIVE {nome_pista.upper()}", link_selezionato)
