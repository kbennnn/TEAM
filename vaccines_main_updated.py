import sys
import os
import pandas as pd

# Import ufficiali corretti
import behavior_model
from behavior_model import BehaviorModel

import simulation
from simulation import Simulation

from gpu_runner import run_one_sim
from parameters import Parameters
import ga.ga_config as ga_config

# --- 1. PARAMETRI FISSI DELLA SIMULAZIONE SCELTA ---
BEST_PARAMS = Parameters.from_dict({
    "hospitalization_prob": 0.039794085,
    "v1_growth_prob": 0.038817637,
    "antiv_kill_prob": 0.007896532,
    "prudence_parameter": 0.881876167,
    "antivesp_young_ratio": 7,
    "antivesp_adult_ratio": 2,
    "incubation_v1": 12,
    "infection_v1": 297,
    "recovered_antivesp": 44,
    "symptoms_progression": 589,
})

# --- 2. VALORI BASE DI DEFAULT ---
DEFAULT_EFF_LOWER = 15.0          # Lower effectiveness bound (%)
DEFAULT_EFF_UPPER = 65.0          # Upper effectiveness bound (%)
DEFAULT_DURATION = 210.0          # Mean protection duration (days)
DEFAULT_START_WEEK = 8            # Campaign start (simulation week)
DEFAULT_END_WEEK = 21             # Campaign end (simulation week)

#aggiunti:
DEFAULT_COVERAGE = 0.55           # Target fraction of elderly individuals vaccinated
DEFAULT_DAILY_CAP = 0.01          # Maximum daily fraction of elderly individuals vaccinated
DEFAULT_DURATION_STD = 30.0       # Standard deviation of vaccine duration (days)
DEFAULT_DURATION_CORRELATION = 0.8 # Effectiveness-duration correlation
DEFAULT_PROTECTION_DELAY = 14     # Days before vaccine protection begins
DEFAULT_F_STAR = 0.01             # Infection-rate threshold for vaccination willingness

# Tenere su False finché si settano i parametri, impostare su True per lanciare simulazioni
RUN_SIMULATIONS = False


def apply_vaccine_config(eff_low=DEFAULT_EFF_LOWER, eff_upp=DEFAULT_EFF_UPPER,
                         duration=DEFAULT_DURATION, start_wk=DEFAULT_START_WEEK,
                         end_wk=DEFAULT_END_WEEK, coverage=DEFAULT_COVERAGE,
                         daily_cap=DEFAULT_DAILY_CAP, duration_std=DEFAULT_DURATION_STD,
                         duration_correlation=DEFAULT_DURATION_CORRELATION,
                         protection_delay=DEFAULT_PROTECTION_DELAY,
                         f_star=DEFAULT_F_STAR):
    """
    Aggiorna i parametri relativi al vaccino su classi e moduli.
    """
    # Valori illegali:
    if not 0 <= eff_low < eff_upp <= 100:
        raise ValueError("Effectiveness bounds must satisfy 0 <= lower < upper <= 100")
    if duration <= 30:
        raise ValueError("Mean duration must exceed 30 days for the current half-life formula")
    if duration_std < 0:
        raise ValueError("Duration standard deviation cannot be negative")
    if not 0 <= coverage <= 1:
        raise ValueError("Coverage must be between 0 and 1")
    if not 0 <= daily_cap <= 1:
        raise ValueError("Daily vaccination cap must be between 0 and 1")
    if not -1 <= duration_correlation <= 1:
        raise ValueError("Duration correlation must be between -1 and 1")
    if protection_delay < 0 or f_star <= 0:
        raise ValueError("Protection delay must be nonnegative and F_STAR positive")
    if not 0 <= start_wk <= end_wk:
        raise ValueError("Campaign weeks must satisfy 0 <= start <= end")

    # 1. Aggiornamento Vaccine Efficacy (classe + modulo)
    if hasattr(BehaviorModel, 'update_vaccine_effectiveness_lower_bound'):
        BehaviorModel.update_vaccine_effectiveness_lower_bound(eff_low)
    else:
        BehaviorModel.VACCINE_EFFECTIVENESS_LOWER_BOUND = eff_low

    if hasattr(BehaviorModel, 'update_vaccine_effectiveness_upper_bound'):
        BehaviorModel.update_vaccine_effectiveness_upper_bound(eff_upp)
    else:
        BehaviorModel.VACCINE_EFFECTIVENESS_UPPER_BOUND = eff_upp

    behavior_model.VACCINE_EFFECTIVENESS_LOWER_BOUND = eff_low
    behavior_model.VACCINE_EFFECTIVENESS_UPPER_BOUND = eff_upp

    # 2. Aggiornamento Vaccine Duration e param correlati (classe + modulo)
    behavior_model.MEAN_VACCINE_DURATION = duration
    BehaviorModel.MEAN_VACCINE_DURATION = duration
    BehaviorModel.VACCINE_DURATION_STD = duration_std
    BehaviorModel.DURATION_CORRELATION = duration_correlation
    BehaviorModel.VACCINE_PROTECTION_DELAY = protection_delay
    BehaviorModel.F_STAR = f_star

    # 3. Vaccination coverage e daily cap
    Simulation.VACCINE_COVERAGE = coverage
    Simulation.DAILY_VACCINATION_CAP_FRACTION = daily_cap

    # 4. Calcolo e aggiornamento GIORNI d'inizio e fine campagna (risoluzione bug)
    start_day = 7 * (start_wk - 1) + 1 if start_wk > 0 else 1
    end_day = 7 * end_wk

    # Aggiornamento modulo simulation
    simulation.VACCINATION_START_WEEK = start_wk
    simulation.VACCINATION_END_WEEK = end_wk
    simulation.VACCINATION_START_DAY = start_day
    simulation.VACCINATION_END_DAY = end_day

    # Aggiornamento classe Simulation
    Simulation.VACCINATION_START_WEEK = start_wk
    Simulation.VACCINATION_END_WEEK = end_wk
    Simulation.VACCINATION_START_DAY = start_day
    Simulation.VACCINATION_END_DAY = end_day


def print_active_parameters(tag=""):
    print(f"\n--- [VERIFICA PARAMETRI ATTIVI: {tag}] ---")
    print(f"  > Coverage         : {Simulation.VACCINE_COVERAGE}")
    print(f"  > Daily cap        : {Simulation.DAILY_VACCINATION_CAP_FRACTION}")
    print(f"  > Eff Lower Bound  : {BehaviorModel.VACCINE_EFFECTIVENESS_LOWER_BOUND}")
    print(f"  > Eff Upper Bound  : {BehaviorModel.VACCINE_EFFECTIVENESS_UPPER_BOUND}")
    print(f"  > Mean Duration    : {BehaviorModel.MEAN_VACCINE_DURATION}")
    print(f"  > Duration Std     : {BehaviorModel.VACCINE_DURATION_STD}")
    print(f"  > Duration Corr    : {BehaviorModel.DURATION_CORRELATION}")
    print(f"  > Protection Delay : {BehaviorModel.VACCINE_PROTECTION_DELAY}")
    print(f"  > F_STAR           : {BehaviorModel.F_STAR}")
    print(f"  > Start Week/Day   : Wk {Simulation.VACCINATION_START_WEEK} (Day {Simulation.VACCINATION_START_DAY})")
    print(f"  > End Week/Day     : Wk {Simulation.VACCINATION_END_WEEK} (Day {Simulation.VACCINATION_END_DAY})")
    print("-" * 60)


# --- 3. DEFINIZIONE DELLE NUOVE RUN PER I 3 GRAFICI COMPARATIVI ---

experiments = [
    # --- GRUPPO 1: VACCINATION WEEKS ---

    #test precedenti:
    #{
    #    "name": "weeks_0_13",
    #    "config": {"eff_low": 15.0, "eff_upp": 65.0, "duration": 210.0, "start_wk": 0, "end_wk": 13}
    #},
    #{
    #    "name": "weeks_16_29",
    #    "config": {"eff_low": 15.0, "eff_upp": 65.0, "duration": 210.0, "start_wk": 16, "end_wk": 29}
    #},
    #{
    #    "name": "weeks_24_37",
    #    "config": {"eff_low": 15.0, "eff_upp": 65.0, "duration": 210.0, "start_wk": 24, "end_wk": 37}
    #},

    #nuove proposte:

    # mantenendo fissa la durata totale ma anticipando o posticipando la campagna:
    {
        "name": "weeks_6_19",
        "config": {"start_wk": 6, "end_wk": 19} #Da metà settembre a fine dicembre. Motivo: alcune fonti suggeriscono di iniziare la campagna già a settembre,
        #specialmente se si prevede un picco anticipato
    },
    {
        "name": "weeks_10_23",
        "config": {"start_wk": 10, "end_wk": 23} #Da metà ottobre a metà gennaio. Motivo: è un delay di solo 2 settimane rispetto alla baseline e quindi realistico
    },
    {
        "name": "weeks_12_25",
        "config": {"start_wk": 12, "end_wk": 25} #Da fine ottobre a inizio febbraio. Motivo: è un delay più importante (un mese) ma comunque nei limiti del realismo.
        # ritardi più grandi rispetto alla baseline possono essere comunque interessanti da studiare, ma sono del tutto irrealistici
    },

    # cambiando la durata totale:
    {
        "name": "weeks_8_15", #fine anticipata
        "config": {"start_wk": 8, "end_wk": 15} # Motivo: la maggior parte delle persone si vaccinano entro dicembre
                                                # attenzione che il daily cap è fisso a 1% degli anziani ogni giorno, dunque difficilmente si riuscirà a raggiungere
                                                #la coverage del 0.55 per gli anziani
    },
    {
        "name": "weeks_8_29", # fine posticipata
        "config": {"start_wk": 8, "end_wk": 29} #Motivo: studiare cosa succede se la campagna vaccinale prosegue fino a febbraio
                                                # attenzione a due aspetti:
                                                #1. la coverage massima di 0.55 potrebbe far sì che le vaccinazioni comunque non aumentino dopo un certo giorno
                                                #2. potrebbero avvenire rivaccinazioni perché gli anziani che si sono vaccinati a inizio campagna potrebbero avere finito la protezione quando
                                                #   la campagna è ancora in corso e dunque avere una seconda dose
    },

    {
        "name": "weeks_6_21", # inizio anticipato
        "config": {"start_wk": 6, "end_wk": 21} # Motivo: alcune fonti suggeriscono di iniziare la campagna già a settembre, specialmente se si prevede un picco anticipato
    },
    {
        "name": "weeks_10_21", # inizio posticipato
        "config": {"start_wk": 10, "end_wk": 21} #Motivo: è un delay di solo 2 settimane rispetto alla baseline e quindi realistico
    },


    # --- GRUPPO 2: MEAN VACCINE DURATION ---
    # attenzione: variando la durata varierà anche il decadimento dell'efficacia. Durata maggiore = emivita più alta = efficacia dura di più
    # inoltre, per testare accuratamente questi scenari bisogna avere la porzione di codice che rende il decadimento dell'efficacia proporzionale alla durata media del vaccino (è sul main di git)
    {
        "name": "duration_120",
        "config": {"duration": 120.0} #Motivo: 4 mesi sono uno scenario molto pessimista ma realistico. Attenzione: tenendo la std a 30 giorni si rendono possibili
                                     # rivaccinazioni, siccome la campagna vaccinale dura circa 3 mesi e alcune persone riceveranno una durata vaccinale inferiore a 3 mesi
    },
    {
        "name": "duration_150",
        "config": {"duration": 150.0} # mantenuto. Motivo: 5 mesi sono 2 mesi in meno rispetto alla baseline, interessante per studiare uno scenario pessimista
    },
    {
        "name": "duration_270",
        "config": {"duration": 270.0} #Motivo:9 mesi sono 2 mesi in più rispetto alla baseline, interessante per studiare uno scenario ottimista. Oltre 9 mesi diventa irrealistico.
    },



    # --- GRUPPO 3: VACCINE EFFECTIVENESS ---
    # non dovrebbero esserci effetti sulla durata: una durata vaccinale alta viene assegnata più spesso a chi riceve una protezione con efficacia relativamente (!) alta

    # range ristretto o allargato:
    {
        "name": "eff_0_80",
        "config": {"eff_low": 0.0, "eff_upp": 80.0} # Mantenuto: amplia il range mantenendo una media del 40%
    },
    {
        "name": "eff_30_50",
        "config": {"eff_low": 30.0, "eff_upp": 50.0} # aggiunto: restringe il range mantenendo una media del 40%
    },

    # upper e lower bound abbassati o alzati mantenendo la stessa ampiezza del range baseline:
    {
        "name": "eff_5_55",
        "config": {"eff_low": 5.0, "eff_upp": 55.0} # Motivo: per avere una media del 30% (contro il 40% della baseline)
    },
    {
        "name": "eff_25_75",
        "config": {"eff_low": 25.0, "eff_upp": 75.0} # Motivo: per avere una media del 50% (contro il 40% della baseline)
    },
    {
        "name": "eff_35_85",
        "config": {"eff_low": 35.0, "eff_upp": 85.0} # Motivo: per avere una media del 60% (contro il 40% della baseline)
    },
    
    # potrebbe essere interessante anche impostare dei valori di efficacia presi dallo storico: https://www.cdc.gov/flu-vaccines-work/php/effectiveness-studies/index.html



    # --- GRUPPO 4: VACCINATION COVERAGE ---
    {
        "name": "coverage_0",
        "config": {"coverage": 0.0} # Motivo: confrontare gli output con una simulazione in cui il vaccino non è disponibile/non si vaccina nessuno
    },
    {
        "name": "coverage_45",
        "config": {"coverage": 0.45} # Motivo: è il valore effettivamente raggiunto per le persone over 60 in molte delle annate precedenti
    },
    {
        "name": "coverage_65",
        "config": {"coverage": 0.65} # Motivo: è il valore raggiunto durante il COVID (e poi mai più)
    },
    {
        "name": "coverage_75",
        "config": {"coverage": 0.75} # Motivo: è il target italiano minimo (mai raggiunto)
    },
    {
        "name": "coverage_95",
        "config": {"coverage": 0.95} # Motivo: è il target italiano obiettivo (mai raggiunto). Attenzione: il daily cap all'1% potrebbe impedire il raggiungimento di questo obiettivo.
                                        # Avevo fatto una simulazione senza daily cap e si era comunque raggiunto un valore vicino a 90%
    },



    # --- GRUPPO 5: DAILY CAP ---
    # interessante per capire cosa succede avendo una maggiore capacità di vaccinazione giornaliera (e quindi probabilmente facendo in modo che molte persone si vaccinino all'inizio della campagna)
    # e cosa succede avendo invece una ridotta capacità di vaccinazione giornaliera (e quindi distriubuendo le vaccinazioni più uniformemente nella campagna).

    #Attenzione: con valori più alti del cap, la coverage potrebbe essere raggiunta molto prima della fine della campagna vaccinale. Con valori più bassi, potrebbe non venire raggiunta in tempo.
    {   
        "name": "daily_cap_006",
        "config": {"daily_cap": 0.006} # Motivo: è il minimo target che permette teoricamente di raggiungere una coverage del 55% con una campagna di circa 3 mesi
    },
    {
        "name": "daily_cap_008",
        "config": {"daily_cap": 0.008} # Motivo: è una via di mezzo fra 0.006 e 0.01 (la baseline)
    },
    {
        "name": "daily_cap_015",
        "config": {"daily_cap": 0.015} # Motivo: è una via di mezzo fra 0.01 (la baseline) e 0.02
    },
    {
        "name": "daily_cap_020",
        "config": {"daily_cap": 0.02} # Motivo: è una capacità raddoppiata rispetto alla baseline. Oltre al 2% di anziani vaccinati ogni giorno diventa davvero irrealistico
    },


    # --- GRUPPO 6: PARAMETRI COMBINATI ---
    {
        "name": "coverage_75_cap_015",
        "config": {"coverage": 0.75, "daily_cap": 0.015} # Motivo: testare lo scenario della coverage al 75% senza che il cap impedisca il suo raggiungimento,
                                                        # e contemporaneamente testare lo scenario del cap al 1.5% senza che la coverage impedisca di vederne gli effetti
    },
    {
        "name": "eff_low_duration_short", # Motivo: è sensato che abbassando l'efficacia si abbassi anche la durata della protezione
        "config": {
            "eff_low": 5.0,
            "eff_upp": 55.0,
            "duration": 150.0
        }
    },
    {
        "name": "eff_high_duration_long", # Motivo: è sensato che con un'efficacia più alta si alzi anche la durata della protezione
        "config": {
            "eff_low": 25.0,
            "eff_upp": 75.0,
            "duration": 270.0
        }
    },



    # --- GRUPPO 7: ALTRI PARAMETRI DEL VACCINO ---
    # sono altri parametri meno interessanti che potremmo considerare in futuro

    #{
    #    "name": "duration_std_variant",
    #    "config": {"duration_std": None}
    #},
    #{
    #    "name": "duration_correlation_variant",
    #    "config": {"duration_correlation": None}
    #},
    #{
    #    "name": "protection_delay_variant",
    #    "config": {"protection_delay": None}
    #},
    #{
    #    "name": "f_star_variant",
    #    "config": {"f_star": None}
    #},
]


# --- 4. ENGINE DI ESECUZIONE ---
print("==================================================")
print("   INIZIO NUOVE RUN ESPERIMENTI VACCINI (6 TEST)  ")
print("==================================================")

for exp in experiments:
    print(f"\n==================================================")
    print(f"  LANCIO SIMULAZIONE: {exp['name']}")
    print(f"==================================================")

    # ricordarsi di impostare RUN_SIMULATIONS su True
    pending = [key for key, value in exp["config"].items() if value is None]
    if pending:
        print(f"[PENDING] Missing values: {', '.join(pending)}")
        continue

    if not RUN_SIMULATIONS:
        apply_vaccine_config(**exp["config"])
        print_active_parameters(tag=exp["name"])
        print("[CHECK OK] Parameters applied successfully.")
        continue

    # 1. Configurazione dei parametri
    apply_vaccine_config(**exp["config"])

    # 2. Stampa di verifica pre-lancio
    print_active_parameters(tag=exp["name"])

    # 3. Chiamata alla simulazione su GPU
    idx, score, elapsed, pid = run_one_sim(
        idx=-1,
        params=BEST_PARAMS,
        days=ga_config.DAYS,
        generation=-1,
        algorithm=f"VACCINE_{exp['name']}"
    )

    print(f"\n[ESITO {exp['name']}] -> Score MSE: {score:.6f} | Tempo: {elapsed:.2f}s | PID: {pid}")

# Ripristino pulito dello stato di default a fine esecuzione
apply_vaccine_config()
print("\n==================================================")
print("     TUTTI I 6 NUOVI TEST SONO STATI COMPLETATI   ")
print("==================================================")