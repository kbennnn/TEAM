from parameters import Parameters 
from gpu_runner import run_repeated
import ga.ga_config as ga_config

BEST_PARAMETERS = [
    #Create Parameters from previous runs, to validate them across different seeds

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

    Parameters.from_dict({
        "hospitalization_prob": 0.072022,
        "v1_growth_prob": 0.04899,
        "antiv_kill_prob": 0.005378,
        "prudence_parameter": 0.616406,
        "antivesp_young_ratio": 7,
        "antivesp_adult_ratio": 1,
        "incubation_v1": 25,
        "infection_v1": 234,
        "recovered_antivesp": 27,
        "symptoms_progression": 659,
    }),

    Parameters.from_dict({
        "hospitalization_prob": 0.074472,
        "v1_growth_prob": 0.053939,
        "antiv_kill_prob": 0.001439,
        "prudence_parameter": 0.675205,
        "antivesp_young_ratio": 6,
        "antivesp_adult_ratio": 2,
        "incubation_v1": 16,
        "infection_v1": 147,
        "recovered_antivesp": 39,
        "symptoms_progression": 767,
    }),

    Parameters.from_dict({
        "hospitalization_prob": 0.064572,
        "v1_growth_prob": 0.034902,
        "antiv_kill_prob": 0.004084,
        "prudence_parameter": 0.721649,
        "antivesp_young_ratio": 6,
        "antivesp_adult_ratio": 2,
        "incubation_v1": 28,
        "infection_v1": 166,
        "recovered_antivesp": 33,
        "symptoms_progression": 724,
    }),

    Parameters.from_dict({
        "hospitalization_prob": 0.059682,
        "v1_growth_prob": 0.030966,
        "antiv_kill_prob": 0.000437,
        "prudence_parameter": 0.647488,
        "antivesp_young_ratio": 3,
        "antivesp_adult_ratio": 1,
        "incubation_v1": 13,
        "infection_v1": 255,
        "recovered_antivesp": 38,
        "symptoms_progression": 743,
    }),

    Parameters.from_dict({
        "hospitalization_prob": 0.039007,
        "v1_growth_prob": 0.04934,
        "antiv_kill_prob": 0.002861,
        "prudence_parameter": 0.617793,
        "antivesp_young_ratio": 7,
        "antivesp_adult_ratio": 2,
        "incubation_v1": 30,
        "infection_v1": 154,
        "recovered_antivesp": 29,
        "symptoms_progression": 625,
    }),

    Parameters.from_dict({
        "hospitalization_prob": 0.058088,
        "v1_growth_prob": 0.03446,
        "antiv_kill_prob": 0.001824,
        "prudence_parameter": 0.650756,
        "antivesp_young_ratio": 3,
        "antivesp_adult_ratio": 1,
        "incubation_v1": 13,
        "infection_v1": 121,
        "recovered_antivesp": 18,
        "symptoms_progression": 711,
    }),

    Parameters.from_dict({
        "hospitalization_prob": 0.048009,
        "v1_growth_prob": 0.056708,
        "antiv_kill_prob": 0.003992,
        "prudence_parameter": 0.604746,
        "antivesp_young_ratio": 4,
        "antivesp_adult_ratio": 1,
        "incubation_v1": 20,
        "infection_v1": 299,
        "recovered_antivesp": 45,
        "symptoms_progression": 703,
    }),

    Parameters.from_dict({
        "hospitalization_prob": 0.084935,
        "v1_growth_prob": 0.03617,
        "antiv_kill_prob": 0.006309,
        "prudence_parameter": 0.628741,
        "antivesp_young_ratio": 8,
        "antivesp_adult_ratio": 2,
        "incubation_v1": 24,
        "infection_v1": 165,
        "recovered_antivesp": 23,
        "symptoms_progression": 696,
    }),

    Parameters.from_dict({
        "hospitalization_prob": 0.080999,
        "v1_growth_prob": 0.043719,
        "antiv_kill_prob": 0.000109,
        "prudence_parameter": 0.659657,
        "antivesp_young_ratio": 6,
        "antivesp_adult_ratio": 2,
        "incubation_v1": 23,
        "infection_v1": 140,
        "recovered_antivesp": 32,
        "symptoms_progression": 661,
    }),

    Parameters.from_dict({
        "hospitalization_prob": 0.058907,
        "v1_growth_prob": 0.059823,
        "antiv_kill_prob": 0.00165,
        "prudence_parameter": 0.611779,
        "antivesp_young_ratio": 2,
        "antivesp_adult_ratio": 2,
        "incubation_v1": 11,
        "infection_v1": 174,
        "recovered_antivesp": 45,
        "symptoms_progression": 656,
    }),

    Parameters.from_dict({
        "hospitalization_prob": 0.042522,
        "v1_growth_prob": 0.030324,
        "antiv_kill_prob": 0.009891,
        "prudence_parameter": 0.961593,
        "antivesp_young_ratio": 6,
        "antivesp_adult_ratio": 2,
        "incubation_v1": 27,
        "infection_v1": 219,
        "recovered_antivesp": 39,
        "symptoms_progression": 758,
    }),

    Parameters.from_dict({
        "hospitalization_prob": 0.086564,
        "v1_growth_prob": 0.039774,
        "antiv_kill_prob": 0.001784,
        "prudence_parameter": 0.646551,
        "antivesp_young_ratio": 6,
        "antivesp_adult_ratio": 4,
        "incubation_v1": 27,
        "infection_v1": 183,
        "recovered_antivesp": 39,
        "symptoms_progression": 642,
    }),

]

for params in BEST_PARAMETERS: #Launch the same validation
    run_repeated(
        params=params,
        rep=3,
        days=ga_config.DAYS
    )