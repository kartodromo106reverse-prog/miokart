import streamlit as st
import pandas as pd

# 1. SETUP - LAYOUT PROFESSIONALE (Ottimizzato Z Flip 5)
st.set_page_config(page_title="War Room 106 Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    /* Il tuo tasto Apex gigante */
    .stLinkButton>a { 
        width: 100% !important; height: 80px !important; display: flex !important; 
        align-items: center !important; justify-content: center !important; 
        font-size: 22px !important; background-color: #ff4b4b !important; 
        color: white !important; font-weight: bold !important; border-radius: 12px !important;
        text-decoration: none !important; margin-bottom: 20px !important;
    }
    /* Grafica Statistica Kart Veloci */
    .stat-card {
        background-color: #1e2129; border-left: 6px solid #ff4b4b;
        padding: 12px; border-radius: 10px; margin-bottom: 10px;
    }
    .stat-number { font-size: 24px; font-weight: bold; color: white; }
    .stat-time { font-size: 20px; color: #ff4b4b; font-weight: bold; float: right; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏎️ War Room 106 - Statistiche Live")

# 2. LINK APEX (Sempre presente e funzionante)
apex_link = "https://live.apex-timing.com/kartodromo106reverse/"
st.link_button("🚀 APRI LIVE TIMING APEX", apex_link)

# 3. GESTIONE DATI DINAMICA
if 'data' not in st.session_state:
    # Iniziamo con i primi 15, ma puoi cambiarli o aggiungerne altri
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(15)],
        'BEST': [99.999] * 15
    })

# 4. TABELLA DI INSERIMENTO (Veloce)
st.subheader("⏱️ Inserisci i tempi da Apex")
st.caption("Puoi modificare il numero del kart (es. 50, 60) e aggiungere righe col tasto +")

edited_df = st.data_editor(
    st.session_state.data,
    column_config={
        "KART": st.column_config.TextColumn("N° KART", width="small"),
        "BEST": st.column_config.NumberColumn("MIGLIOR GIRO", format="%.3f", width="medium"),
    },
    hide_index=True,
    use_container_width=True,
    num_rows="dynamic"
)

if st.button("💾 AGGIORNA STATISTICHE"):
    st.session_state.data = edited_df
    st.rerun()

# 5. LA TUA STATISTICA (I KART PIÙ VELOCI)
st.divider()
st.subheader("🌟 Classifica Kart Più Veloci")

# Filtriamo solo i kart che hanno un tempo reale e li ordiniamo dal più veloce
classifica = edited_df[edited_df['BEST'] < 99].sort_values('BEST')

if not classifica.empty:
    tempo_record = classifica['BEST'].min()
    
    for i, row in classifica.head(10).iterrows(): # Mostra i primi 10
        # Mette la stella solo al primo assoluto
        icona = "⭐" if row['BEST'] == tempo_record else "🏁"
        
        st.markdown(f"""
            <div class='stat-card'>
                <span class='stat-number'>{icona} KART {row['KART']}</span>
                <span class='stat-time'>{row['BEST']:.3f}s</span>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("Inserisci i tempi nella tabella sopra per generare la statistica.")
