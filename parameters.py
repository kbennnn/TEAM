from dataclasses import dataclass, asdict, replace
from simulation import Simulation
from infection_rules import InfectionRules
from behavior_model import BehaviorModel
import os, csv
import random


@dataclass
class Parameters:

    # InfectionRules
    hospitalization_prob: float = 0.03
    v1_growth_prob: float = 0.035
    antiv_kill_prob: float = 0.001
    prudence_parameter: float = 0.9
    # Viral load thresholds
    incubation_v1: int = 5
    infection_v1: int = 200
    recovered_antivesp: int = 40
    symptoms_progression: int = 700 
    # Behaviour model
    f_star: float = 0.01


    @classmethod
    def random(cls):
        params = cls()

        for name, (low, high) in PARAMETER_BOUNDS.items():
            current_value = getattr(params, name)
            if isinstance(current_value, int):
                value = random.randint(low, high) # int values
            else:
                value = random.uniform(low, high) #real values

            setattr(params, name, value)

        return params


    def apply(self):

        # InfectionRules parameters
        InfectionRules.update_hospitalization_prob(
            self.hospitalization_prob
        )
        InfectionRules.update_v1_growth_prob(
            self.v1_growth_prob
        )
        InfectionRules.update_antiv_kill_prob(
            self.antiv_kill_prob
        )
        InfectionRules.update_prudence_parameter(
            self.prudence_parameter
        )
        # Viral load thresholds
        InfectionRules.update_incubation_v1(
            self.incubation_v1
        )
        InfectionRules.update_infection_v1(
            self.infection_v1
        )
        InfectionRules.update_recovered_antivesp(
            self.recovered_antivesp
        )
        InfectionRules.update_symptoms_progression(
            self.symptoms_progression
        )     
        # BehaviorModel parameters
        BehaviorModel.update_f_star(
            self.f_star
        )


    def save_result(self, simulation_csv: str, score: float):
        result_file = "curve_score.csv"

        simulation_name = os.path.basename(simulation_csv) #extract the name of the simulation

        row = {
            "simulation": simulation_name,
            **asdict(self),        # add all parameters
            "score": score
        }

        file_exists = os.path.exists(result_file)

        with open(result_file, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())

            if not file_exists:
                writer.writeheader()

            writer.writerow(row)


    def __str__(self): # for printing the values
        lines = ["Parameters:"]
        for key, value in asdict(self).items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)   


PARAMETER_BOUNDS = {
    # Infection
    "hospitalization_prob": (0.01, 0.10),
    "v1_growth_prob": (0.01, 0.06),
    "antiv_kill_prob": (0.0001, 0.01),
    "symptoms_progression": (500, 800),
    "incubation_v1": (1, 30),
    "infection_v1": (50, 300),
    "recovered_antivesp": (10, 70),
    "prudence_parameter": (0.6, 1.0),
    # Behaviour
    "f_star": (0.0005, 0.2),
}