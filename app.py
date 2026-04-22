import streamlit as st
import pandas as pd
import time
import random
import numpy as np

# 1. SETUP - SIDEBAR APERTA PER LEGENDA
st.set_page_config(page_title="WAR ROOM - MANUAL CONTROL", layout="wide", initial_sidebar_state="expanded")

# 2. CSS PER ALLERTA E BOTTONI
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    /* Alert lampeggiante per i box */
    @keyframes blink { 0% {opacity: 1;} 50% {opacity: 0.3;} 100% {opacity: 1;} }
    .alert-timer { color: #FF3131; font-weight: bold; animation: blink 1s infinite; font-size: 25px; }
    
    .pit-card { border: 2px solid #FFD700; padding: 15px; border-radius: 10px; background-color: #1a1a00; margin-bottom: 10px; }
    .k-pro { color: #FF3131; font-weight: bold; font-size: 22px; }
    .k-semi { color: #1E90FF; font-weight: bold; font-size: 22px; }
    .k-ama { color: #00FF7F; font-weight: bold; font-size: 22px; }
    
    button[data-baseweb="tab"] { height: 60px; width: 100%; font-size: 18px !important; }
    .stButton>button { height: 45px !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. LEGENDA NEL SOTTOMENU
with st.sidebar:
    st.header("📋 MANUALE OPERATIVO")
    st.write("---")
    st.subheader("1. Segna i Kart")
    st.write("Usa ⭐ per i kart veloci. Il segno resta anche dopo il Pit Stop.")
    st.subheader("2. Ingresso Box")
    st.write("Premi **ENTRA PIT** solo quando vedi fisicamente il kart entrare.")
    st.subheader("3. Allerta Uscita")
    st.write("Nella scheda **BOX**, il timer lampeggerà quando mancano meno di 30s.")
    st.subheader("4. Presa nuovo Team")
    st.write("Premi **LIBERA** solo quando il kart viene assegnato e riparte.")

# 4. INIZIALIZZAZIONE DATI
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i:02d}" for i in range(1, 51)],
        'CAT': ["NONE"] * 50,
        'STAR': [False] * 50,
        'ULTIMO': [0.0] * 50,
        'MEDIA_15': [45.0] * 50,
        'COST': [0.2] * 50,
        'IN_PIT': [False] * 50,
        'PIT_START': [0.0] * 50,
        'STORICO': [[] for _ in range(50)]
    })

# AGGIORNAMENTO LIVE (Solo fuori dai box)
for i in range(50):
    if not st.session_state.data.at[i, 'IN_PIT']:
        t = 44.0 + random.uniform(0.5, 2.5)
        h = st.session_state.data.at[i, 'STORICO']
        h.append(t); 
        if len(h) > 15: h.pop(0)
        st.session_state.data.at[i, 'ULTIMO'] = t
        st.session_state.data.at[i, 'MEDIA_15'] = np.mean(h)
        st.session_state.data.at[i, 'COST'] = np.std(h)

# --- INTERFACCIA ---
tab_pista, tab_box = st.tabs(["🏎️ PISTA (LIVE)", "🚧 BOX (MANUALE)"])

with tab_pista:
    # Ordiniamo per media, ma mettiamo i "Preferiti (Star)" in cima se possibile
    df_display = st.session_state.data[st.session_state.data['IN_PIT'] == False].sort_values(by='MEDIA_15')
    
    st.caption("Classifica ordinata per MEDIA. Aggiornamento ogni 10 secondi.")
    
    for i, row in df_display.iterrows():
        c = st.columns([0.5, 0.7, 0.8, 1.2, 0.8, 1.5])
        
        # Stella
        if c[0].button("⭐" if row['STAR'] else "☆", key=f"s_{row['KART']}"):
            st.session_state.data.at[i, 'STAR'] = not st.session_state.data.at[i, 'STAR']
            st.rerun()
            
        # Numero e Colore
        style = "k-none"
        if row['CAT'] == "PRO": style = "k-pro"
        elif row['CAT'] == "SEMI": style = "k-semi"
        elif row['CAT'] == "AMAT": style = "k-ama"
        c[1].markdown(f"<span class='{style}'>{row['KART']}</span>", unsafe_allow_html=True)
        
        # Categoria (Bottone ciclico)
        if c[2].button(f"{row['CAT'][0]}", key=f"c_{row['KART']}"):
            cats = ["NONE", "PRO", "SEMI", "AMAT"]
            cur = cats.index(row['CAT'])
            st.session_state.data.at[i, 'CAT'] = cats[(cur + 1) % 4]
            st.rerun()

        c[3].write(f"**{row['MEDIA_15']:.2f}**")
        c[4].write("🟢" if row['COST'] < 0.15 else "🔴")
        
        # Allerta Entrata
        if c[5].button("ENTRA PIT 🏁", key=f"p_{row['KART']}"):
            st.session_state.data.at[i, 'IN_PIT'] = True
            st.session_state.data.at[i, 'PIT_START'] = time.time()
            st.rerun()

with tab_box:
    pit_karts = st.session_state.data[st.session_state.data['IN_PIT'] == True]
    
    if pit_karts.empty:
        st.info("Nessun kart ai box. Segnali l'ingresso dalla scheda PISTA.")
    else:
        for idx, row in pit_karts.iterrows():
            rem = max(0, 180 - (time.time() - row['PIT_START']))
            m, s = divmod(int(rem), 60)
            
            with st.container():
                # Definiamo se mostrare l'allerta lampeggiante
                timer_class = "alert-timer" if rem < 30 else ""
                
                st.markdown(f"""
                <div class='pit-card'>
                    <span style='font-size:24px;'>{"⭐" if row['STAR'] else ""} KART <b>{row['KART']}</b></span> | 
                    <span style='font-size:24px;' class='{timer_class}'>⏳ {m:02d}:{sec_rem:02d if 'sec_rem' in locals() else s:02d}</span>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"LIBERA KART {row['KART']} (Preso da Team) ✅", key=f"out_{row['KART']}"):
                    st.session_state.data.at[idx, 'IN_PIT'] = False
                    st.rerun()
            st.write("")

# REFRESH 10 SECONDI
time.sleep(10)
st.rerun()
