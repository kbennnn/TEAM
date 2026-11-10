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
DEFAULT_EFF_LOWER = 15.0
DEFAULT_EFF_UPPER = 65.0
DEFAULT_DURATION = 210.0
DEFAULT_START_WEEK = 8
DEFAULT_END_WEEK = 21

def apply_vaccine_config(eff_low=DEFAULT_EFF_LOWER, eff_upp=DEFAULT_EFF_UPPER, 
                         duration=DEFAULT_DURATION, start_wk=DEFAULT_START_WEEK, end_wk=DEFAULT_END_WEEK):
    """
    Aggiorna Efficacy, Duration e le Settimane/Giorni di Vaccinazione su classi e moduli.
    """
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

    # 2. Aggiornamento Vaccine Duration (classe + modulo)
    behavior_model.MEAN_VACCINE_DURATION = duration
    BehaviorModel.MEAN_VACCINE_DURATION = duration

    # 3. Calcolo e aggiornamento GIORNI d'inizio e fine campagna (risoluzione bug)
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
    print(f"  > Eff Lower Bound : {getattr(BehaviorModel, 'VACCINE_EFFECTIVENESS_LOWER_BOUND', 'N/A')}")
    print(f"  > Eff Upper Bound : {getattr(BehaviorModel, 'VACCINE_EFFECTIVENESS_UPPER_BOUND', 'N/A')}")
    print(f"  > Mean Duration   : {getattr(behavior_model, 'MEAN_VACCINE_DURATION', 'N/A')}")
    print(f"  > Start Week/Day  : Wk {getattr(Simulation, 'VACCINATION_START_WEEK', 'N/A')} (Day {getattr(Simulation, 'VACCINATION_START_DAY', 'N/A')})")
    print(f"  > End Week/Day    : Wk {getattr(Simulation, 'VACCINATION_END_WEEK', 'N/A')} (Day {getattr(Simulation, 'VACCINATION_END_DAY', 'N/A')})")
    print("-" * 60)

# --- 3. DEFINIZIONE DELLE NUOVE RUN PER I 3 GRAFICI COMPARATIVI ---
# 6 Nuove Simulazioni:
# - Weeks: 0-13, 16-29, 24-37
# - Duration: 150, 250
# - Effectiveness: 0-80
experiments = [
    # --- GRUPPO 1: VACCINATION WEEKS ---
    {
        "name": "weeks_0_13",
        "config": {"eff_low": 15.0, "eff_upp": 65.0, "duration": 210.0, "start_wk": 0, "end_wk": 13}
    },
    {
        "name": "weeks_16_29",
        "config": {"eff_low": 15.0, "eff_upp": 65.0, "duration": 210.0, "start_wk": 16, "end_wk": 29}
    },
    {
        "name": "weeks_24_37",
        "config": {"eff_low": 15.0, "eff_upp": 65.0, "duration": 210.0, "start_wk": 24, "end_wk": 37}
    },

    # --- GRUPPO 2: MEAN VACCINE DURATION ---
    {
        "name": "duration_150",
        "config": {"eff_low": 15.0, "eff_upp": 65.0, "duration": 150.0, "start_wk": 8, "end_wk": 21}
    },
    {
        "name": "duration_250",
        "config": {"eff_low": 15.0, "eff_upp": 65.0, "duration": 250.0, "start_wk": 8, "end_wk": 21}
    },

    # --- GRUPPO 3: VACCINE EFFECTIVENESS ---
    {
        "name": "eff_0_80",
        "config": {"eff_low": 0.0, "eff_upp": 80.0, "duration": 210.0, "start_wk": 8, "end_wk": 21}
    },
]

# --- 4. ENGINE DI ESECUZIONE ---
print("==================================================")
print("   INIZIO NUOVE RUN ESPERIMENTI VACCINI (6 TEST)  ")
print("==================================================")

for exp in experiments:
    print(f"\n==================================================")
    print(f"  LANCIO SIMULAZIONE: {exp['name']}")
    print(f"==================================================")
    
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