from genetic_algorithm import GeneticAlgorithm


ga = GeneticAlgorithm()

population = ga.create_population()


for i, individual in enumerate(population):
    print(i, individual)


population = ga.evolve_population(population)

print("NEXT GENERATION")

for individual in population:
    print(individual)