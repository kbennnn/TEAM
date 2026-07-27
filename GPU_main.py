from simulation import Simulation
from parameters import Parameters
from curve_evaluator import CurveEvaluator
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

def run_one_sim(idx, params: Parameters, days):
    t0 = time.time()
    
    print(params) # Print parameters
    params.apply() # Apply parameters

    sim = Simulation() # Run simulation
    sim.create_scenario()
    weekly_csv = sim.run_simulation(days=days, GPU_idx=idx)

    evaluator = CurveEvaluator("lombardy/incidenza_ILI_2025-2026.csv") # Evaluate result
    score = evaluator.evaluate(weekly_csv)

    params.save_result(weekly_csv, score) # Save result
    elapsed = time.time() - t0

    return idx, score, elapsed, os.getpid()


def main(n_runs, days, max_workers):

    t_start = time.time()
    results = []

    # Generate one Parameters object for each simulation
    population = [
        Parameters.random() # create a random individual
        for _ in range(n_runs)
    ]

    with ProcessPoolExecutor(max_workers=max_workers) as exe:

        # Launch all the simulations
        futures = [
            exe.submit(run_one_sim, i, population[i], days)
            for i in range(n_runs)
        ]

        # Retrieve the results
        for fut in as_completed(futures):
            idx, score, elapsed, pid = fut.result()

            print(
                f"Sim {idx}: score={score:.4f}, "
                f"time={elapsed:.1f}s (pid={pid})"
            )

            results.append((idx, score, elapsed, pid))

    total = time.time() - t_start

    print(f"Total wall time for {n_runs} sims: {total:.1f}s")

    return results



if __name__ == "__main__":
    main(n_runs=5, days=200, max_workers=5)