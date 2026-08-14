# Simulation
RANDOM_SEED = [42, 999, 1234]
DAYS = 364

# Population
POPULATION_SIZE = 20
GENERATIONS = 8

# Elitism
ELITE_SIZE = 1 # keep the best individuals for the next generation ---> TODO potrei evitare di rirunnarli (anche se il random li faranno cambiare)

# Selection
TOURNAMENT_SIZE = 2

# Crossover
CROSSOVER_PROBABILITY = 0.8
UNIFORM_CROSSOVER_INDPB = 0.5

# Mutation
MUTATION_PROBABILITY = 0.8
MUTATION_GENE_PROBABILITY = 0.15
MUTATION_STRENGTH  = 0.3   # how a mutation can change a gene, e.g. 10%