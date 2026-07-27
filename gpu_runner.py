from simulation import Simulation
from parameters import Parameters
from curve_evaluator import CurveEvaluator
import time, os

def run_one_sim(idx, params: Parameters, days):
    t0 = time.time()
    # Print and apply parameters
    print(params) 
    params.apply()
    # Run simulation
    sim = Simulation() 
    sim.create_scenario()
    weekly_csv = sim.run_simulation(days=days, GPU_idx=idx)
    # Evaluate result
    evaluator = CurveEvaluator("lombardy/incidenza_ILI_2025-2026.csv") 
    score = evaluator.evaluate(weekly_csv)
    # Save result
    params.save_result(weekly_csv, score) 
    elapsed = time.time() - t0

    return idx, score, elapsed, os.getpid()