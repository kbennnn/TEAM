from genetic_algorithm import GeneticAlgorithm
import ga_config

def main():
    ga = GeneticAlgorithm()
    population = ga.create_population()

    for generation in range(ga_config.GENERATIONS):
        print("GA: starting the generation number", generation)
        ga.evaluate_population(population, ga_config.DAYS, generation)
        population = ga.evolve_population(population)

if __name__ == "__main__":
    main()