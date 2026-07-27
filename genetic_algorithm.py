import random
from deap import base, creator, tools
from parameters import Parameters
import ga_config


class GeneticAlgorithm:

    def __init__(self):

        self.toolbox = base.Toolbox()
        self._setup_deap()


    def _setup_deap(self):

        # Fitness: minimise the score
        creator.create(
            "FitnessMin",
            base.Fitness,
            weights=(-1.0,)
        )

        creator.create(
            "Individual",
            list,
            fitness=creator.FitnessMin
        )


        self.toolbox.register(
            "individual",
            self.create_individual
        )

        self.toolbox.register(
            "population",
            tools.initRepeat,
            list,
            self.toolbox.individual
        )


        self.toolbox.register(
            "mate",
            tools.cxUniform,
            indpb=ga_config.UNIFORM_CROSSOVER_INDPB
        )


        self.toolbox.register(
            "mutate",
            self.mutate_uniform
        )


        self.toolbox.register(
            "select",
            tools.selTournament,
            tournsize=ga_config.TOURNAMENT_SIZE
        )


    def create_individual(self):

        params = Parameters.random()
        return creator.Individual(
            params.to_vector()
        )


    def create_population(self):

        return self.toolbox.population(
            n=ga_config.POPULATION_SIZE
        )


    def mutate_uniform(self, individual):

        for index, name in enumerate(Parameters.PARAMETER_BOUNDS.keys()):
            if random.random() < ga_config.MUTATION_GENE_PROBABILITY:
                low, high = Parameters.PARAMETER_BOUNDS[name]
                individual[index] = random.uniform(
                    low,
                    high
                )

        return individual,


    def evolve_population(self, population):

        # Elitism
        elites = tools.selBest(
            population,
            ga_config.ELITE_SIZE
        )

        # Parent selection
        offspring = self.toolbox.select(
            population,
            len(population) - ga_config.ELITE_SIZE
        )


        offspring = list(
            map(self.toolbox.clone, offspring)
        )

        # Crossover
        for child1, child2 in zip(
            offspring[::2],
            offspring[1::2]
        ):

            if random.random() < ga_config.CROSSOVER_PROBABILITY:

                self.toolbox.mate(
                    child1,
                    child2
                )

                del child1.fitness.values
                del child2.fitness.values

        # Mutation
        for mutant in offspring:

            if random.random() < ga_config.MUTATION_PROBABILITY:

                self.toolbox.mutate(mutant)

                del mutant.fitness.values

        # New generation
        offspring.extend(elites)

        return offspring