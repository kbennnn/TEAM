from simulation import Simulation
from parameters import Parameters
from curve_evaluator import CurveEvaluator
from concurrent.futures import ProcessPoolExecutor
import time, os, random, ga.ga_config as ga_config
import numpy as np

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)

def run_one_sim(idx, params: Parameters, days, generation, algorithm, seed = ga_config.RANDOM_SEED[0],):
    set_seed(seed)
    t0 = time.time()
    # Print and apply parameters
    print(params)
    params.apply()
    # Run simulation
    sim = Simulation()
    sim.create_scenario()
    weekly_csv = sim.run_simulation(days=days, GPU_idx=idx, generation=generation, algorithm=algorithm)
    # Evaluate result against the 4 seasons, use the "sum" metric for this run
    evaluator = CurveEvaluator({
        "2022": "lombardy/incidence_strain_2022-2023.csv",
        "2023": "lombardy/incidence_strain_2023-2024.csv",
        "2024": "lombardy/incidence_strain_2024-2025.csv",
        "2025": "lombardy/incidence_strain_2025-2026.csv",
    })
    result = evaluator.evaluate(weekly_csv)
    score = result["sum"] #Change into minimax or maxmax for different metrics
    # Save all 3 results
    params.save_result(weekly_csv, result)
    elapsed = time.time() - t0

    return idx, score, elapsed, os.getpid()




def run_multi_seed(params: Parameters, algorithm: str, days: int, rep: int = None, gen: int = -1, max_workers: int = None):
    # Launch the same simulation in parallel across multiple seeds
    if rep is None:
        rep = len(ga_config.RANDOM_SEED)
    if max_workers is None:
        max_workers = rep

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
                    gen,
                    algorithm,
                    ga_config.RANDOM_SEED[idx]
                )
            )

        for future in futures:
            idx, score, elapsed, pid = future.result()
            print(f"Sim {idx} (seed={ga_config.RANDOM_SEED[idx]}): score={score:.5f}, elapsed={elapsed:.2f}s, pid={pid}")
            results.append((idx, score, elapsed, pid))

    return results