import streamlit as st
import pandas as pd
import time

# 1. SETUP - LAYOUT
st.set_page_config(page_title="War Room 106 Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    /* Tasto APEX Gigante */
    .stLinkButton>a { 
        width: 100% !important; height: 70px !important; display: flex !important; 
        align-items: center !important; justify-content: center !important; 
        font-size: 20px !important; background-color: #ff4b4b !important; 
        color: white !important; font-weight: bold !important; border-radius: 12px !important;
        text-decoration: none !important; margin-bottom: 15px !important;
    }
    /* Schede Statistiche Veloci */
    .stat-card {
        background-color: #1e2129; border-left: 6px solid #ff4b4b;
        padding: 10px; border-radius: 8px; margin-bottom: 8px;
    }
    .stat-number { font-size: 20px; font-weight: bold; color: white; }
    .stat-time { font-size: 18px; color: #ff4b4b; font-weight: bold; float: right; }
    /* Box Timer */
    .box-card {
        background-color: #262730; border-top: 4px solid #ff4b4b;
        padding: 10px; border-radius: 5px; margin-bottom: 5px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏎️ War Room 106 - Statistiche & Box")

# 2. LINK APEX FISSO
apex_link = "https://live.apex-timing.com/kartodromo106reverse/"
st.link_button("🚀 APRI LIVE TIMING APEX", apex_link)

# 3. GESTIONE DATI DINAMICA
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'KART': [f"{i+1:02d}" for i in range(15)],
        'BEST': [99.999] * 15,
        'IN_PIT': [False] * 15,
        'PIT_START': [0.0] * 15
    })

# 4. TABELLA OPERATIVA (Inserimento Dati)
st.subheader("⏱️ Gestione Live (Pista e Box)")
st.caption("Usa 'IN_PIT' per mandare un kart ai box e far partire il timer")

edited_df = st.data_editor(
    st.session_state.data,
    column_config={
        "KART": st.column_config.TextColumn("N° KART", width="small"),
        "BEST": st.column_config.NumberColumn("MIGLIOR GIRO", format="%.3f"),
        "IN_PIT": st.column_config.CheckboxColumn("AI BOX?"),
    },
    hide_index=True,
    use_container_width=True,
    num_rows="dynamic"
)

# Logica per salvare i tempi di inizio Pit
for i in range(len(edited_df)):
    if edited_df.at[i, 'IN_PIT'] and not st.session_state.data.at[i, 'IN_PIT']:
        edited_df.at[i, 'PIT_START'] = time.time()

if st.button("💾 AGGIORNA TUTTO"):
    st.session_state.data = edited_df
    st.rerun()

# 5. VISUALIZZAZIONE DOPPIA: STATISTICHE + BOX
st.divider()
col_stats, col_box = st.columns(2)

with col_stats:
    st.subheader("🌟 I Più Veloci")
    # Filtra chi è in pista (non ai box) e ha un tempo valido
    classifica = edited_df[(edited_df['BEST'] < 99) & (edited_df['IN_PIT'] == False)].sort_values('BEST').head(5)
    
    if not classifica.empty:
        tempo_record = classifica['BEST'].min()
        for i, row in classifica.iterrows():
            icona = "⭐" if row['BEST'] == tempo_record else "🏁"
            st.markdown(f"""
                <div class='stat-card'>
                    <span class='stat-number'>{icona} KART {row['KART']}</span>
                    <span class='stat-time'>{row['BEST']:.3f}s</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.write("Inserisci i tempi per vedere la statistica.")

with col_box:
    st.subheader("🚧 Monitor Box")
    # Filtra solo chi è ai box
    box_karts = edited_df[edited_df['IN_PIT'] == True]
    
    if not box_karts.empty:
        for i, row in box_karts.iterrows():
            elapsed = time.time() - row['PIT_START']
            mins, secs = divmod(int(elapsed), 60)
            st.markdown(f"""
                <div class='box-card'>
                    <b style='color:#ff4b4b;'>KART {row['KART']}</b><br>
                    <span>Fermo da: {mins:02d}:{secs:02d}</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.write("Nessun kart ai box.")

# Refresh automatico ogni 15 secondi per aggiornare i timer dei box
time.sleep(15)
st.rerun()
