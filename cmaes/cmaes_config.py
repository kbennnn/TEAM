# Simulation
DAYS = 364

# Generations (CMA-ES calls these "iterations")
GENERATIONS = 8

# Population size per generation ("lambda" in CMA-ES literature).
# Leave as None to use pycma's default heuristic: 4 + floor(3*ln(N))
# where N = number of parameters (11 here -> default popsize).
POPULATION_SIZE = 20

# Initial step size (in normalized [0,1] search space, not real units).
# Roughly: how far from the center CMA-ES should initially spread its
# samples. 0.3 is a common default (covers most of [0,1] early on).
SIGMA0 = 0.3