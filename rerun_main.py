from parameters import Parameters 
from gpu_runner import run_repeated
import ga.ga_config as ga_config

BEST_PARAMETERS = [
    #Use Parameters from previous runs to validate them across different seeds

    Parameters.from_dict({
        "hospitalization_prob": 0.079076,
        "v1_growth_prob": 0.038788,
        "antiv_kill_prob": 0.002957,
        "prudence_parameter": 0.612331,
        "antivesp_young_ratio": 4,
        "antivesp_adult_ratio": 2,
        "incubation_v1": 18,
        "infection_v1": 242,
        "recovered_antivesp": 31,
        "symptoms_progression": 706,
    }),

    #Declare as many Parameters are needed
    Parameters.from_dict({
        "hospitalization_prob": 0.025472,
        "v1_growth_prob": 0.04158,
        "antiv_kill_prob": 0.003337,
        "prudence_parameter": 0.724557,
        "antivesp_young_ratio": 4,
        "antivesp_adult_ratio": 2,
        "incubation_v1": 29,
        "infection_v1": 160,
        "recovered_antivesp": 37,
        "symptoms_progression": 555,
    }),
]

for params in BEST_PARAMETERS: #Launch the same validation
    run_repeated(
        params=params,
        rep=1, #set rep=1 to launch only 1 run with seed = 42 
        days=ga_config.DAYS
    )