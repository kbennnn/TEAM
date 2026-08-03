# Simulation
RANDOM_SEED = 42
DAYS = 210

# Population
POPULATION_SIZE = 10
GENERATIONS = 4

# Elitism
ELITE_SIZE = 1 # keep the best individuals for the next generation ---> TODO potrei evitare di rirunnarli (anche se il random li faranno cambiare)

# Selection
TOURNAMENT_SIZE = 2

# Crossover
CROSSOVER_PROBABILITY = 0.8
UNIFORM_CROSSOVER_INDPB = 0.5

# Mutation
MUTATION_PROBABILITY = 0.8
MUTATION_GENE_PROBABILITY = 0.1
MUTATION_STRENGTH  = 0.1   # how a mutation can change a gene, e.g. 10%