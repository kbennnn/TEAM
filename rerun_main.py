from parameters import Parameters 
from gpu_runner import run_one_sim
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
    })

]

for params in BEST_PARAMETERS: #Launch the same validation

    idx, score, elapsed, pid = run_one_sim(
            idx=-1,  
            params=params,
            days=ga_config.DAYS,
            generation=-1,
            algorithm=""
        )