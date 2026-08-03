from parameters import Parameters 
from gpu_runner import run_repeated
import ga_config

BEST_PARAMETERS = [
    #Create Parameters from previous runs, to validate them
    Parameters.from_dict({
        "hospitalization_prob": 0.0395307953331156,
        "v1_growth_prob": 0.0404708200983901,
        "antiv_kill_prob": 0.00144612384403613,
        "prudence_parameter": 0.675177455388794,
        "incubation_v1": 30,
        "infection_v1": 279,
        "recovered_antivesp": 67,
        "symptoms_progression": 511,
        "f_star": 0.0827695192383221,
    }),

    Parameters.from_dict({
        "hospitalization_prob": 0.0395307953331156,
        "v1_growth_prob": 0.0404708200983901,
        "antiv_kill_prob": 0.00144612384403613,
        "prudence_parameter": 0.715053806917569,
        "incubation_v1": 24,
        "infection_v1": 279,
        "recovered_antivesp": 67,
        "symptoms_progression": 696,
        "f_star": 0.0827695192383221,
    }),

    Parameters.from_dict({
        "hospitalization_prob": 0.0395307953331156,
        "v1_growth_prob": 0.0404708200983901,
        "antiv_kill_prob": 0.00144612384403613,
        "prudence_parameter": 0.675177455388794,
        "incubation_v1": 30,
        "infection_v1": 279,
        "recovered_antivesp": 67,
        "symptoms_progression": 511,
        "f_star": 0.0827695192383221,
    }),

]

for params in BEST_PARAMETERS: #Launch the same validation
    run_repeated(
        params=params,
        rep=3,
        days=ga_config.DAYS
    )