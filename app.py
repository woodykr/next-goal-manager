import streamlit as st
import pandas as pd

st.set_page_config(page_title="Next Goal 4-Step", page_icon="⚽", layout="centered")

# Parametri base
PROFIT_TARGETS = [1.5, 1.5, 1.5, 0]  # Utile target per step 1-3, pari allo step 4
PROGRESSIONE_FISSA = [3.0, 5.0, 7.0, 10.0]

# Stato iniziale
if "step" not in st.session_state:
    st.session_state.step = 1
if "perdite" not in st.session_state:
    st.session_state.perdite = 0.0
if "storico" not in st.session_state:
    st.session_state.storico = []

st.title("⚽ Next Goal 4-Step Manager")

st.markdown(
    "Sistema tipo **Masaniello** a 4 step con recupero dinamico.\n"
    "Scegli modalità di calcolo, inserisci quota ed esito di ogni step."
)

# Sidebar parametri
st.sidebar.header("⚙️ Parametri")
modalita = st.sidebar.radio(
    "Modalità calcolo stake",
    options=["Progressione Fissa (3-5-7-10)", "Recupero Dinamico"],
    index=1
)

# Info modalità
if modalita == "Recupero Dinamico":
    st.sidebar.info(
        "**Recupero Dinamico**: calcola gli stake per darti +€1.50 di utile ai step 1-3, "
        "e recupero pari al step 4."
    )
else:
    st.sidebar.info(
        "**Progressione Fissa**: usa sempre gli stake 3-5-7-10."
    )

st.divider()

# Info ciclo corrente
st.subheader("📊 Ciclo corrente")

step_corrente = st.session_state.step
perdite_cumulative = st.session_state.perdite

st.write(f"**Step**: {step_corrente} | **Perdite cumulative**: €{perdite_cumulative:.2f}")

st.divider()

# Form per registrare esito
st.subheader("📝 Registra esito dello step")

col1, col2 = st.columns(2)
with col1:
    quota = st.number_input("Quota giocata", min_value=1.01, value=1.80, step=0.01)
with col2:
    esito = st.selectbox("Esito", ["--", "Vinto", "Perso"])

# Calcola stake consigliato
if modalita == "Progressione Fissa":
    stake_consigliato = PROGRESSIONE_FISSA[step_corrente - 1]
else:
    # Calcolo dinamico: stake = (perdite + target) / (quota - 1)
    profit_target = PROFIT_TARGETS[step_corrente - 1]
    stake_consigliato = round((perdite_cumulative + profit_target) / (quota - 1), 2)

st.info(f"**Stake consigliato per Step {step_corrente}**: €{stake_consigliato:.2f}")

if st.button("✅ Registra esito", type="primary", use_container_width=True):
    step = step_corrente
    stake = stake_consigliato

    if esito == "--":
        st.error("❌ Seleziona un esito (Vinto/Perso).")
    elif esito == "Vinto":
        ritorno = stake * quota
        costo_totale = perdite_cumulative + stake
        pnl_ciclo = ritorno - costo_totale

        st.session_state.storico.append(
            {
                "Step": step,
                "Quota": round(quota, 2),
                "Stake": round(stake, 2),
                "Incasso": round(ritorno, 2),
                "Esito": "✅ Vinto",
                "P&L ciclo (€)": round(pnl_ciclo, 2),
            }
        )

        st.success(f"🎉 **Ciclo CHIUSO!** Profitto netto: **€{pnl_ciclo:.2f}**")
        st.session_state.step = 1
        st.session_state.perdite = 0.0
        st.rerun()

    elif esito == "Perso":
        st.session_state.perdite += stake
        pnl_ciclo_perso = -st.session_state.perdite

        st.session_state.storico.append(
            {
                "Step": step,
                "Quota": round(quota, 2),
                "Stake": round(stake, 2),
                "Incasso": 0,
                "Esito": "❌ Perso",
                "P&L ciclo (€)": round(pnl_ciclo_perso, 2),
            }
        )

        if step < 4:
            st.session_state.step += 1
            st.warning(
                f"Step {step} perso ❌. Passa allo **Step {st.session_state.step}** con stake aggiornato."
            )
        else:
            st.error(f"💔 **Ciclo PERSO!** Perdita totale: **-€{st.session_state.perdite:.2f}**")
            st.session_state.step = 1
            st.session_state.perdite = 0.0
        
        st.rerun()

st.divider()

# Storico e statistiche
st.subheader("📈 Storico step")

if st.session_state.storico:
    df = pd.DataFrame(st.session_state.storico)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.divider()
    st.subheader("📊 Statistiche")
    
    cicli_vinti = len([x for x in st.session_state.storico if x['Esito'] == "✅ Vinto"])
    cicli_persi = len([x for x in st.session_state.storico if x['P&L ciclo (€)'] < -10])
    profitto_totale = sum([x['P&L ciclo (€)'] for x in st.session_state.storico if x['Esito'] == "✅ Vinto"])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Cicli vinti", cicli_vinti)
    with col2:
        st.metric("Cicli persi", cicli_persi)
    with col3:
        if cicli_vinti + cicli_persi > 0:
            win_rate = round(cicli_vinti / (cicli_vinti + cicli_persi) * 100, 1)
            st.metric("Win rate", f"{win_rate}%")
    with col4:
        st.metric("Profitto", f"€{profitto_totale:.2f}")
else:
    st.write("Nessuno step registrato ancora.")

st.divider()

# Bottoni di reset
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Reset ciclo", use_container_width=True):
        st.session_state.step = 1
        st.session_state.perdite = 0.0
        st.rerun()

with col2:
    if st.button("🗑️ Cancella storico", use_container_width=True):
        st.session_state.storico = []
        st.session_state.step = 1
        st.session_state.perdite = 0.0
        st.rerun()
