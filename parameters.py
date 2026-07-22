from dataclasses import dataclass, asdict
from simulation import Simulation
from infection_rules import InfectionRules
from behavior_model import BehaviorModel
import os, csv


@dataclass
class Parameters:

    # Simulation
    init_infection_per_province: int = 10
    vaccine_coverage: float = 0

    # InfectionRules
    incubation_period: int = 2
    hospitalization_period: int = 7
    hospitalization_prob: float = 0.03
    icu_prob: float = 0.05
    caution_factor: float = 0.001
    v1_growth_prob: float = 0.035
    antiv_kill_prob: float = 0.001
    infection_reduction_factor: float = 1.15

    # Behaviour model
    vaccine_effectiveness_lower_bound: int = 30
    vaccine_effectiveness_upper_bound: int = 60
    duration_correlation: float = 0.8
    f_star: float = 0.01


    def apply(self):

        # Simulation
        Simulation.INIT_INFECTIONS_PER_PROVINCE = self.init_infection_per_province
        Simulation.VACCINE_COVERAGE = self.vaccine_coverage

        # InfectionRules
        InfectionRules.INCUBATION_PERIOD = self.incubation_period
        InfectionRules.HOSPITALIZATION_PERIOD = self.hospitalization_period
        InfectionRules.HOSPITALIZATION_PROB = self.hospitalization_prob
        InfectionRules.ICU_PROB = self.icu_prob
        InfectionRules.CAUTION_FACTOR = self.caution_factor
        InfectionRules.V1_GROWTH_PROB = self.v1_growth_prob
        InfectionRules.ANTIV_KILL_PROB = self.antiv_kill_prob
        InfectionRules.INFECTION_REDUCTION_FACTOR = self.infection_reduction_factor

        # Behaviour model
        BehaviorModel.VACCINE_EFFECTIVENESS_LOWER_BOUND = self.vaccine_effectiveness_lower_bound
        BehaviorModel.VACCINE_EFFECTIVENESS_UPPER_BOUND = self.vaccine_effectiveness_upper_bound
        BehaviorModel.DURATION_CORRELATION = self.duration_correlation
        BehaviorModel.F_STAR = self.f_star

    def apply(self):

        # ==========================
        # Simulation parameters
        # ==========================
        Simulation.update_initial_infection_per_province(
            self.init_infection_per_province
        )

        Simulation.update_vaccine_coverage(
            self.vaccine_coverage
        )

        # ==========================
        # InfectionRules parameters
        # ==========================
        InfectionRules.update_incubation_period(
            self.incubation_period
        )

        InfectionRules.update_hospitalization_period(
            self.hospitalization_period
        )

        InfectionRules.update_hospitalization_prob(
            self.hospitalization_prob
        )

        InfectionRules.update_icu_prob(
            self.icu_prob
        )

        InfectionRules.update_caution_factor(
            self.caution_factor
        )

        InfectionRules.update_v1_growth_prob(
            self.v1_growth_prob
        )

        InfectionRules.update_antiv_kill_prob(
            self.antiv_kill_prob
        )

        InfectionRules.update_infection_reduction_factor(
            self.infection_reduction_factor
        )

        # ==========================
        # BehaviorModel parameters
        # ==========================
        BehaviorModel.update_vaccine_effectiveness_lower_bound(
            self.vaccine_effectiveness_lower_bound
        )

        BehaviorModel.update_vaccine_effectiveness_upper_bound(
            self.vaccine_effectiveness_upper_bound
        )

        BehaviorModel.update_duration_correlation(
            self.duration_correlation
        )

        BehaviorModel.update_f_star(
            self.f_star
        )


    def save_result(self, simulation_csv: str, score: float):
        result_file = "curve_score"

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


PARAMETER_BOUNDS = {

    # Simulation
    "init_infection_per_province": (1, 100),
    "vaccine_coverage": (0.0, 1.0),

    # Infection
    "incubation_period": (1, 10),
    "hospitalization_period": (1, 30),
    "hospitalization_prob": (0.0, 0.20),
    "icu_prob": (0.0, 0.20),
    "caution_factor": (0.0, 0.05),
    "v1_growth_prob": (0.0, 0.10),
    "antiv_kill_prob": (0.0, 0.10),
    "infection_reduction_factor": (1.0, 5.0),

    # Behaviour
    "vaccine_effectiveness_lower_bound": (40, 80),
    "vaccine_effectiveness_upper_bound": (60, 100),
    "duration_correlation": (0.0, 1.0),
    "f_star": (0.001, 0.03),
}