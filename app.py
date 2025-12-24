import streamlit as st
import pandas as pd

st.set_page_config(page_title="Next Goal 4-Step", page_icon="⚽", layout="centered")

# ----- PARAMETRI BASE -----
PROFIT_TARGETS = [1.5, 1.5, 1.5, 0]      # Utile target step 1-3, pari allo step 4
PROGRESSIONE_FISSA = [2.5, 5.0, 7.0, 10.0]

# ----- STATO INIZIALE -----
if "step" not in st.session_state:
    st.session_state.step = 1
if "perdite" not in st.session_state:
    st.session_state.perdite = 0.0
if "storico" not in st.session_state:
    st.session_state.storico = []

st.title("⚽ Next Goal 4-Step Manager")

st.markdown(
    "Sistema a 4 step per il **prossimo goal**.\n\n"
    "- Step 1: stake fisso 2.5 €.\n"
    "- Step 2-3-4: stake calcolato per recuperare le perdite + utile (1,50 € sui primi 3, pari al 4°).\n"
)

# ----- SIDEBAR -----
st.sidebar.header("⚙️ Parametri")
modalita = st.sidebar.radio(
    "Modalità calcolo stake",
    options=["Progressione Fissa (3-5-7-10)", "Recupero Dinamico (Step1 fisso 3€)"],
    index=1
)

if modalita.startswith("Recupero"):
    st.sidebar.info(
        "Step 1 fisso a 2.5 €.\n"
        "Step 2-3-4: stake = (perdite cumulative + target) / (quota - 1).\n"
        "Target utile: +1,50 € agli step 2-3, pari allo step 4."
    )
else:
    st.sidebar.info(
        "Progressione fissa: stake 2.5-5-7-10 indipendenti dalla quota."
    )

st.divider()

# ----- INFO CICLO CORRENTE -----
st.subheader("📊 Ciclo corrente")

step_corrente = st.session_state.step
perdite_cumulative = st.session_state.perdite

st.write(f"**Step corrente**: {step_corrente}")
st.write(f"**Perdite cumulative nel ciclo**: €{perdite_cumulative:.2f}")

st.divider()

# ----- FORM INSERIMENTO -----
st.subheader("📝 Registra esito dello step")

col1, col2 = st.columns(2)
with col1:
    quota = st.number_input("Quota giocata", min_value=1.01, value=1.80, step=0.01)
with col2:
    esito = st.selectbox("Esito", ["--", "Vinto", "Perso"])

# ----- CALCOLO STAKE CONSIGLIATO -----
if modalita.startswith("Progressione"):
    stake_consigliato = PROGRESSIONE_FISSA[step_corrente - 1]
else:
    if step_corrente == 1:
        # Step 1 fisso 2.5 €
        stake_consigliato = 2.50
    else:
        # Step 2-3-4 dinamici: stake = (perdite + target) / (quota - 1)
        profit_target = PROFIT_TARGETS[step_corrente - 1]
        stake_consigliato = round((perdite_cumulative + profit_target) / (quota - 1), 2)

st.info(f"**Stake consigliato per Step {step_corrente}**: €{stake_consigliato:.2f}")

# ----- BOTTONE REGISTRA ESITO -----
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
        # reset ciclo
        st.session_state.step = 1
        st.session_state.perdite = 0.0
        st.rerun()

    elif esito == "Perso":
        st.session_state.perdite += stake
        nuove_perdite = st.session_state.perdite
        pnl_ciclo_perso = -nuove_perdite

        st.session_state.storico.append(
            {
                "Step": step,
                "Quota": round(quota, 2),
                "Stake": round(stake, 2),
                "Incasso": 0.00,
                "Esito": "❌ Perso",
                "P&L ciclo (€)": round(pnl_ciclo_perso, 2),
            }
        )

        if step < 4:
            st.session_state.step += 1
            st.warning(
                f"Step {step} perso ❌. Vai allo **Step {st.session_state.step}** con nuovo stake calcolato."
            )
        else:
            st.error(f"💔 **Ciclo PERSO**. Perdita totale ciclo: **-€{nuove_perdite:.2f}**")
            # reset ciclo
            st.session_state.step = 1
            st.session_state.perdite = 0.0

        st.rerun()

st.divider()

# ----- STORICO -----
st.subheader("📈 Storico step")

if st.session_state.storico:
    df = pd.DataFrame(st.session_state.storico)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📊 Statistiche ciclo")

    cicli_vinti = len([x for x in st.session_state.storico if x["Esito"] == "✅ Vinto"])
    # consideriamo ciclo perso quando siamo arrivati almeno allo step 4 con P&L molto negativo
    cicli_persi = len([x for x in st.session_state.storico if x["P&L ciclo (€)"] <= -20])
    profitto_totale = sum(
        [x["P&L ciclo (€)"] for x in st.session_state.storico if x["Esito"] == "✅ Vinto"]
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Cicli vinti", cicli_vinti)
    with col2:
        st.metric("Cicli persi (circa)", cicli_persi)
    with col3:
        tot_cicli = cicli_vinti + cicli_persi
        if tot_cicli > 0:
            win_rate = round(cicli_vinti / tot_cicli * 100, 1)
            st.metric("Win rate cicli", f"{win_rate}%")
    with col4:
        st.metric("Profitto totale", f"€{profitto_totale:.2f}")
else:
    st.write("Nessuno step registrato ancora.")

st.divider()

# ----- BOTTONI RESET -----
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
