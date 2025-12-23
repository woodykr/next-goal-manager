import streamlit as st

st.set_page_config(page_title="Next Goal 4-Step", page_icon="⚽", layout="centered")

# Parametri base
BANKROLL_CICLO_DEFAULT = 25.0
PROGRESSIONE_DEFAULT = [3.0, 5.0, 7.0, 10.0]

# Stato iniziale
if "step" not in st.session_state:
    st.session_state.step = 1
if "perdite" not in st.session_state:
    st.session_state.perdite = 0.0
if "storico" not in st.session_state:
    st.session_state.storico = []

st.title("⚽ Next Goal 4-Step Manager")

st.markdown(
    "Sistema tipo **Masaniello** a 4 step con progressione aggressiva 3–5–7–10.\n"
    "Imposti quota ed esito di ogni step e l'app ti dice quanto puntare dopo."
)

# Sidebar parametri
st.sidebar.header("Parametri ciclo")
bankroll_ciclo = st.sidebar.number_input(
    "Bankroll per ciclo (€)",
    min_value=1.0,
    value=BANKROLL_CICLO_DEFAULT,
    step=1.0,
)
prog1 = st.sidebar.number_input("Step 1 (€)", min_value=0.1, value=PROGRESSIONE_DEFAULT[0], step=0.5)
prog2 = st.sidebar.number_input("Step 2 (€)", min_value=0.1, value=PROGRESSIONE_DEFAULT[1], step=0.5)
prog3 = st.sidebar.number_input("Step 3 (€)", min_value=0.1, value=PROGRESSIONE_DEFAULT[2], step=0.5)
prog4 = st.sidebar.number_input("Step 4 (€)", min_value=0.1, value=PROGRESSIONE_DEFAULT[3], step=0.5)

progressione = [prog1, prog2, prog3, prog4]
tot_prog = sum(progressione)

st.sidebar.write(f"Rischio totale per ciclo: **{tot_prog:.2f} €**")

if tot_prog > bankroll_ciclo:
    st.sidebar.error("Attenzione: progressione > bankroll ciclo")

# Info ciclo corrente
st.subheader("Ciclo corrente")

step_corrente = st.session_state.step
stake_corrente = progressione[step_corrente - 1]

col1, col2 = st.columns(2)
with col1:
    st.metric("Step corrente", step_corrente)
with col2:
    st.metric("Stake consigliato", f"{stake_corrente:.2f} €")

st.write(f"Perdite cumulative nel ciclo: **{st.session_state.perdite:.2f} €**")

quota = st.number_input("Quota giocata su questo step", min_value=1.01, value=1.80, step=0.01)
esito = st.selectbox("Esito dello step", ["--", "Vinto", "Perso"])

if st.button("Registra esito"):
    step = step_corrente
    stake = stake_corrente

    if esito == "--":
        st.warning("Seleziona un esito (Vinto/Perso).")
    elif esito == "Vinto":
        ritorno = stake * quota
        costo_totale = st.session_state.perdite + stake
        pnl_ciclo = ritorno - costo_totale

        st.session_state.storico.append(
            {
                "Step": step,
                "Quota": quota,
                "Stake": stake,
                "Esito": "Vinto",
                "Perdite prima (€)": st.session_state.perdite,
                "P&L ciclo (€)": pnl_ciclo,
            }
        )

        st.success(f"Ciclo CHIUSO: profitto netto {pnl_ciclo:.2f} €")
        # reset ciclo
        st.session_state.step = 1
        st.session_state.perdite = 0.0

    elif esito == "Perso":
        st.session_state.perdite += stake

        st.session_state.storico.append(
            {
                "Step": step,
                "Quota": quota,
                "Stake": stake,
                "Esito": "Perso",
                "Perdite prima (€)": st.session_state.perdite - stake,
                "P&L ciclo (€)": -st.session_state.perdite,
            }
        )

        if step < 4:
            st.session_state.step += 1
            st.warning(
                f"Step {step} perso. Passa allo step {st.session_state.step} con stake aggiornato."
            )
        else:
            st.error(f"Ciclo PERSO: -{st.session_state.perdite:.2f} €")
            # chiudi ciclo e reset
            st.session_state.step = 1
            st.session_state.perdite = 0.0

if st.button("Reset ciclo"):
    st.session_state.step = 1
    st.session_state.perdite = 0.0
    st.info("Ciclo resettato.")

st.subheader("Storico step")
if st.session_state.storico:
    st.dataframe(st.session_state.storico)
else:
    st.write("Nessuno step registrato ancora.")
