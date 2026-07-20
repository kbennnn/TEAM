from simulation import Simulation
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

def run_one_sim(idx, days=200):
    t0 = time.time()
    # ogni processo crea la propria istanza
    sim = Simulation()
    sim.create_scenario()
    sim.run_simulation(days=days, GPU_idx=idx)
    elapsed = time.time() - t0
    return idx, elapsed, os.getpid()

def main(n_runs=2, days=200, max_workers=2):
    t_start = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as exe:
        futures = [exe.submit(run_one_sim, i, days) for i in range(n_runs)]
        for fut in as_completed(futures):
            idx, elapsed, pid = fut.result()
            print(f"Sim {idx} finished in {elapsed:.1f}s (pid={pid})")
            results.append((idx, elapsed, pid))
    total = time.time() - t_start
    print(f"Total wall time for {n_runs} sims: {total:.1f}s")
    return results

if __name__ == "__main__":
    main(n_runs=2, days=200, max_workers=2)
