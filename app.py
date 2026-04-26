def get_top_15():
    # 1. Se Apex è connesso, usa i dati di Apex
    se st.session_state.live_karts e non st.session_state.apex_error:
        restituisce st.session_state.live_karts[:15]
    
    # 2. SE APEX È OFFLINE: Crea la classificazione dai dati manuali
    # Prende tutti i kart che hanno un tempo diverso da 99.999
    df_manual = st.session_state.data.copy()
    df_manual['TIME_FLOAT'] = df_manual['BEST'].apply(_safe_float)
    
    # Filtra chi non ha tempo e ordina dal più veloce
    top_manual = df_manual[df_manual['TIME_FLOAT'] < 99.0].sort_values('TIME_FLOAT')
    
    # Trasforma in formato compatibile con i pulsanti
    risultati = []
    per me, entra in fila top_manual.head(15).iterrows():
results.append({
"KART": row['KART'],

"TIME": row['TIME_FLOAT'],

"POS": len(results) + 1

})
return rimport random
import time
import requests
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ===========================================
# 1. CONFIGURAZIONE E STILE
# ===========================================
st.set_page_config(
page_title="WAR ROOM 106 - V.ULTIMATE",
layout="wide",

initial_sidebar_state="expanded",

)

st.markdown("""

<style>

.main .block-container { padding: 8px 12px !important; background-color: #0f1116; }

.stButton > button { width: 100% !important; border-radius: 10px !important; font-weight: 700; }

.touch-card { border: 1px solid #2f3640; border-radius: 10px; padding: 10px; margin-bottom: 8px; text-align: center; }

.touch-fast { background: linear-gradient(135deg, #0f5132, #146c43); border: 1px solid #00FF7F; }

.touch-mid { background: linear-gradient(135deg, #5c4a1f, #8c6d1f); bordo: 1px solido #FFD700; }

.touch-slow { sfondo: gradiente lineare(135deg, #6b1f1f, #9b2226); bordo: 1px solido #ff4b4b; }

.touch-pit { sfondo: gradiente lineare(135deg, #1f3b6b, #2b59a2); opacità: 0.6; }

.kpi-box { bordo: 1px solido #2f3640; sfondo: #141923; raggio del bordo: 10px; spaziatura interna: 10px; margine inferiore: 10px; }

.lane-title { peso del carattere: 800; allineamento del testo: centro; spaziatura interna: 8px; raggio del bordo: 8px; colore: bianco; margine inferiore: 10px; }

.lane-verde { background: #146c43; } .lane-rosso { background: #9b2226; } 

.lane-giallo { background: #8c6d1f; } .lane-blu { background: #2b59a2; }

</style>
"", unsafe_allow_html=True)

# ===========================================
# 2. FUNZIONI TECNICHE (APEX & UTILIZZAZIONI)
# ===========================================
def _safe_float(value):

try: return float(str(value).replace(",", "."))

except: return 999.999

def _format_mmss(total_seconds):

mm, ss = divmod(max(0, int(total_seconds)), 60)
return f"{mm:02d}:{ss:02d}"

def fetch_apex_data(api_url):

if not api_url: return None
try:

response = requests.get(api_url, timeout=4, headers={'User-Agent': 'Mozilla/5.0'})

return response.json()
except: return None

def parse_apex_live_karts(payload):

if not payload: return []

# Logica semplificata per estrarre i kart dal JSON Apex
live = []

try:

items = payload.get("karts") or payload.get("drivers") or []

for i, item in enumerate(items, 1):

k = str(item.get("kart") or item.get("number") or i).zfill(2)

t = _safe_float(item.get("lastLap") or item.get("time"))

live.append({"KART": k, "TIME": t, "POS": i})

eccetto: pass

return sorted(live, key=lambda x: x["POS"])

# ===========================================
# 3. INIZIALIZZAZIONE STATO
# ==========================================
if "data" not in st.session_state:

st.session_state.data = pd.DataFrame({

'KART': [f"{i+1:02d}" for i in range(50)],

'BEST': ["99.999"] * 50,

'IN_PIT': [False] * 50

})

for key, val in {

"auth_status": "admin", "pista_nome": "Kartodromo 106",

"best_lap_pista": 43.500, "lap_green_threshold": 43.800,

"lap_yellow_threshold": 44.400, "tempo_pit": 180,

"pit_events": [], "live_karts": [], "apex_api_url": "",

"corsie_attive": ["VERDE", "ROSSO", "GIALLO", "BLU"]
}.items():

if key not in st.session_state: st.session_state[key] = val

# ==========================================
# 4. LOGICA TOP 15 (IBRIDA)
# ===========================================
def get_top_15():

# 1. Prova con dati Apex Live
if st.session_state.live_karts:

return st.session_state.live_karts[:15]

# 2. Backup: Classifica Manuale

df_m = st.session_state.data.copy()

df_m['V'] = df_m['BEST'].apply(_safe_float)

df_m = df_m[df_m['V'] < 99].sort_values('V').head(15)

res = []

for i, r in df_m.iterrows():

res.append({"KART": r['KART'], "TIME": r['V'], "POS": len(res)+1})

return res

# ===========================================
# 5. PAGINE PRINCIPALI6⁶
# ==========================================
def war_room():

st_autorefresh(interval=1000, key="global_refresh")

s 
