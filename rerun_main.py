from parameters import Parameters 
from gpu_runner import run_repeated
import ga_config

BEST_PARAMETERS = [
    #Create Parameters from previous runs, to validate them
    Parameters.from_dict({
        "hospitalization_prob": 0.054647629,
        "v1_growth_prob": 0.056732805,
        "antiv_kill_prob": 0.003343156,
        "prudence_parameter": 0.748592965,
        "incubation_v1": 7,
        "infection_v1": 97,
        "recovered_antivesp": 54,
        "symptoms_progression": 744,
        "f_star": 0.075674097,
    }),

    Parameters.from_dict({
        "hospitalization_prob": 0.097985298,
        "v1_growth_prob": 0.042946878,
        "antiv_kill_prob": 0.003343156,
        "prudence_parameter": 0.748592965,
        "incubation_v1": 14,
        "infection_v1": 92,
        "recovered_antivesp": 61,
        "symptoms_progression": 501,
        "f_star": 0.075674097,
    }),

    Parameters.from_dict({
        "hospitalization_prob": 0.054647629,
        "v1_growth_prob": 0.056732805,
        "antiv_kill_prob": 0.009469018,
        "prudence_parameter": 0.748592965,
        "incubation_v1": 14,
        "infection_v1": 92,
        "recovered_antivesp": 61,
        "symptoms_progression": 649,
        "f_star": 0.177037772,
    }),

    Parameters.from_dict({
        "hospitalization_prob": 0.083360503,
        "v1_growth_prob": 0.057125109,
        "antiv_kill_prob": 0.009469018,
        "prudence_parameter": 0.748592965,
        "incubation_v1": 14,
        "infection_v1": 130,
        "recovered_antivesp": 53,
        "symptoms_progression": 744,
        "f_star": 0.075674097,
    }),
]

for params in BEST_PARAMETERS: #Launch the same validation
    run_repeated(
        params=params,
        repetitions=3,
        days=ga_config.DAYS
    )