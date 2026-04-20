import streamlit as st

st.title("🏎️ Registro Tempi Kart")
tempo = st.number_input("Inserisci il tuo tempo:", format="%.3f")

if st.button("Salva"):
    st.success(f"Giro di {tempo}s salvato!")
    st.balloons()
