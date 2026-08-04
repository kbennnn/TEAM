import random
from parameters import Parameters
from gpu_runner import run_one_sim
from concurrent.futures import ProcessPoolExecutor
import de_config


class Individual(list):
    """
    Lightweight stand-in for DEAP's Individual: a list of gene values
    plus a fitness score. fitness=None means "not evaluated yet".
    """

    def __init__(self, vector):
        super().__init__(vector)
        self.fitness = None


class DifferentialEvolution:

    def __init__(self):
        self.bounds = Parameters.PARAMETER_BOUNDS

    def create_individual(self):
        params = Parameters.random()
        return Individual(params.to_vector())

    def create_population(self):
        return [
            self.create_individual()
            for _ in range(de_config.POPULATION_SIZE)
        ]

    # Launch the simulations for every individual that doesn't have a
    # fitness yet (mirrors the "don't re-evaluate elites" fix from the GA).
    def evaluate_population(self, population, days, generation):
        to_evaluate = [ind for ind in population if ind.fitness is None]

        if not to_evaluate:
            return

        with ProcessPoolExecutor(max_workers=len(to_evaluate)) as exe:
            futures = []
            for idx, individual in enumerate(to_evaluate):

                params = Parameters.from_vector(individual)
                futures.append(
                    exe.submit(
                        run_one_sim,
                        idx,
                        params,
                        days,
                        generation
                    )
                )

            for future, individual in zip(futures, to_evaluate):
                idx, score, elapsed, pid = future.result()
                individual.fitness = score

        best = min(population, key=lambda ind: ind.fitness)
        print(
            f"Generation {generation}: "
            f"best score = {best.fitness:.6f}"
        )

    def _clip_and_cast(self, index, name, value):
        low, high = self.bounds[name]
        value = min(max(value, low), high)
        if isinstance(low, int) and isinstance(high, int):
            value = int(round(value))
        return value

    def _make_trial(self, target, population, target_index):
        # Pick 3 distinct donors, none of which is the target itself.
        candidates = [
            i for i in range(len(population)) if i != target_index
        ]
        r1, r2, r3 = random.sample(candidates, 3)
        a, b, c = population[r1], population[r2], population[r3]

        names = list(self.bounds.keys())
        j_rand = random.randrange(len(names))  # guarantees >=1 gene from donor

        trial = Individual(target)  # start as a copy of target's genes

        for j, name in enumerate(names):
            if random.random() < de_config.CR or j == j_rand:
                donor_value = a[j] + de_config.F * (b[j] - c[j])
                trial[j] = self._clip_and_cast(j, name, donor_value)
            # else: keep target's gene (already copied above)

        return trial

    # One full DE generation: build + evaluate trial vectors, then
    # greedily replace target individuals that the trial beats.
    def evolve_population(self, population, days, generation):
        trials = [
            self._make_trial(population[i], population, i)
            for i in range(len(population))
        ]

        self.evaluate_population(trials, days, generation)

        next_population = []
        for target, trial in zip(population, trials):
            if trial.fitness < target.fitness:
                next_population.append(trial)
            else:
                next_population.append(target)

        return next_population