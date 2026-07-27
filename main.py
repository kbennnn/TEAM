'''
from parameters import Parameters
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

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
'''

from genetic_algorithm import GeneticAlgorithm
import ga_config

def main():
    ga = GeneticAlgorithm()

    population = ga.create_population()

    for generation in range(ga_config.GENERATIONS):

        ga.evaluate_population(population, ga_config.DAYS)

        population = ga.evolve_population(population)



if __name__ == "__main__":
    main()