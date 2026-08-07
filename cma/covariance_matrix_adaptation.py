import numpy as np
import cma
from parameters import Parameters
from gpu_runner import run_one_sim
from concurrent.futures import ProcessPoolExecutor
import cma_config


class CMAES:

    def __init__(self):
        self.bounds = Parameters.PARAMETER_BOUNDS
        self.names = list(self.bounds.keys())

        self.low = np.array(
            [self.bounds[name][0] for name in self.names],
            dtype=float
        )
        self.high = np.array(
            [self.bounds[name][1] for name in self.names],
            dtype=float
        )
        self.is_int = [
            isinstance(self.bounds[name][0], int)
            and isinstance(self.bounds[name][1], int)
            for name in self.names
        ]

        # Start at the center of normalized [0,1] space for every gene.
        x0 = [0.5] * len(self.names)

        opts = {
            "bounds": [0.0, 1.0],  # normalized search space bounds
            "verbose": -9,         # silence pycma's own logging
        }
        if cma_config.POPULATION_SIZE:
            opts["popsize"] = cma_config.POPULATION_SIZE

        self.es = cma.CMAEvolutionStrategy(x0, cma_config.SIGMA0, opts)

    def decode(self, normalized_vector):
        """Map a normalized [0,1]^n CMA-ES sample to real Parameter values."""
        clipped = np.clip(normalized_vector, 0.0, 1.0)
        real = self.low + clipped * (self.high - self.low)

        values = []
        for value, is_int in zip(real, self.is_int):
            values.append(int(round(value)) if is_int else float(value))

        return values

    # Launch all simulations for one generation's sampled population in parallel
    def evaluate(self, normalized_population, days, generation):
        with ProcessPoolExecutor(max_workers=len(normalized_population)) as exe:
            futures = []
            for idx, normalized_vector in enumerate(normalized_population):

                vector = self.decode(normalized_vector)
                params = Parameters.from_vector(vector)
                futures.append(
                    exe.submit(
                        run_one_sim,
                        idx,
                        params,
                        days,
                        generation
                    )
                )

            scores = [None] * len(normalized_population)
            for idx, future in enumerate(futures):
                _, score, elapsed, pid = future.result()
                scores[idx] = score

        print(f"Generation {generation}: best score = {min(scores):.6f}")
        return scores

    # One full CMA-ES iteration: sample, evaluate, update the distribution.
    def run_generation(self, days, generation):
        solutions = self.es.ask()
        fitnesses = self.evaluate(solutions, days, generation)
        self.es.tell(solutions, fitnesses) # Handles the entire distribution update internally