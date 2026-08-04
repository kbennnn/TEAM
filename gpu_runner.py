from simulation import Simulation
from parameters import Parameters
from curve_evaluator import CurveEvaluator
from concurrent.futures import ProcessPoolExecutor
import time, os, random, ga_config
import numpy as np

def set_seed():
    random.seed(ga_config.RANDOM_SEED)
    np.random.seed(ga_config.RANDOM_SEED)

def run_one_sim(idx, params: Parameters, days, generation):
    set_seed()
    t0 = time.time()
    # Print and apply parameters
    print(params)
    params.apply()
    # Run simulation
    sim = Simulation()
    sim.create_scenario()
    weekly_csv = sim.run_simulation(days=days, GPU_idx=idx, generation=generation)
    # Evaluate result against the 4 seasons, use the "sum" metric for this run
    evaluator = CurveEvaluator({
        "2022": "lombardy/incidence_2022-2023.csv",
        "2023": "lombardy/incidence_2023-2024.csv",
        "2024": "lombardy/incidence_2024-2025.csv",
        "2025": "lombardy/incidence_2025-2026.csv",
    })
    result = evaluator.evaluate(weekly_csv)
    score = result["sum"] #Change into minimax or maxmax for different metrics
    # Save all 3 results
    params.save_result(weekly_csv, result)
    elapsed = time.time() - t0

    return idx, score, elapsed, os.getpid()



def run_repeated(params: Parameters, rep: int, days: int, gen: int = -1, max_workers: int = 3):
    #Launch the same simulation with generation -1 in ordeer to check the variance of the results
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as exe:
        futures = []

        for idx in range(rep):
            futures.append(
                exe.submit(
                    run_one_sim,
                    idx,
                    params,
                    days,
                    gen
                )
            )

        for future in futures:
            idx, score, elapsed, pid = future.result()

            print(
                f"Sim {idx}: score={score:.5f}, "
            )

            results.append((idx, score, elapsed, pid))

    return results