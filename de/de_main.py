from de.differential_evolution import DifferentialEvolution
import de.de_config as de_config

def main():
    de = DifferentialEvolution()

    population = de.create_population()

    # Initial evaluation: every individual starts with fitness=None.
    de.evaluate_population(population, de_config.DAYS, generation=0)

    for generation in range(1, de_config.GENERATIONS):
        population = de.evolve_population(
            population,
            de_config.DAYS,
            generation
        )


if __name__ == "__main__":
    main()