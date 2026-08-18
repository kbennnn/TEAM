import random
from behavior_model import BehaviorModel

# Configuration values differ between paper and code implementation
# XML rules file uses lower infection and mortality rates, resulting in less extreme simulations
class InfectionRules:
    # Disease progression parameters
    INCUBATION_PERIOD = 2 #MODIFICATO was 5 for covid 
    HOSPITALIZATION_PERIOD = 7

    # Simulation control flags
    BEHAVIOR_TRIGGER = True     # Enable behavioral adaptation based on infection rates
    VACCINATION_TRIGGER = True  # Enable vaccination effects CAMBIATO
    VIRAL_LOAD = True           # Enable viral load mechanics
    ICU_PRESENCE = True         # Enable ICU mechanics

    # Healthcare parameters
    HOSPITALIZATION_PROB = 0.03 # Probability of hospitalization
    ICU_PROB = 0.05             # Probability of direct ICU admission with E4 symptoms

    # Virus dynamics
    #CAUTION_FACTOR = 0.1      # Impact of caution on infection spread
    V1_GROWTH_PROB = 0.035      # Probability of viral load growth
    ANTIV_KILL_PROB = 0.001     # Probability of antibodies neutralizing virus

    # Age and symptom-based antibody production probabilities
    # Format: ANTIVESP_[AGE]_[SYMPTOM LEVEL]_PROB
    ANTIVESP_YOUNG_RATIO = 6
    ANTIVESP_ADULT_RATIO = 3
    ANTIVESP_ELDERLY_E2_PROB = 0.004
    ANTIVESP_YOUNG_E2_PROB = ANTIVESP_ELDERLY_E2_PROB * ANTIVESP_YOUNG_RATIO
    ANTIVESP_ADULT_E2_PROB = ANTIVESP_ELDERLY_E2_PROB * ANTIVESP_ADULT_RATIO
    ANTIVESP_ELDERLY_E3_PROB = 0.003
    ANTIVESP_YOUNG_E3_PROB = ANTIVESP_ELDERLY_E3_PROB * ANTIVESP_YOUNG_RATIO
    ANTIVESP_ADULT_E3_PROB =  ANTIVESP_ELDERLY_E3_PROB * ANTIVESP_ADULT_RATIO
    ANTIVESP_ELDERLY_E4_PROB = 0.002
    ANTIVESP_YOUNG_E4_PROB = ANTIVESP_ELDERLY_E4_PROB * ANTIVESP_YOUNG_RATIO
    ANTIVESP_ADULT_E4_PROB =  ANTIVESP_ELDERLY_E4_PROB * ANTIVESP_ADULT_RATIO
    

    # Viral load thresholds
    INCUBATION_V1 = 5           # Initial viral load during incubation
    INFECTION_V1 = 200          # Viral load threshold for infection
    RECOVERED_ANTIVESP = 40     # Antibody threshold for recovery
    SYMPTOMS_PROGRESSION = 700  # Viral load threshold for symptoms growth

    # Behavioral parameters
    PRUDENCE_PARAMETER = 0.9    # Controls social distancing (0=no caution, 1=complete isolation with E2)

    # Configuration update methods
    @classmethod
    def update_incubation_period(cls, new_value: int):
        cls.INCUBATION_PERIOD = new_value

    @classmethod
    def update_hospitalization_period(cls, new_value: int):
        cls.HOSPITALIZATION_PERIOD = new_value

    @classmethod
    def update_hospitalization_prob(cls, new_value: int):
        cls.HOSPITALIZATION_PROB = new_value

    @classmethod
    def update_icu_prob(cls, new_value: int):
        cls.ICU_PROB = new_value

    #@classmethod
    #def update_caution_factor(cls, new_value: float):
    #    cls.CAUTION_FACTOR = new_value

    @classmethod
    def update_prudence_parameter(cls, new_value: float):
        cls.PRUDENCE_PARAMETER = new_value

    @classmethod
    def update_behavior_trigger(cls, new_value: bool):
        cls.BEHAVIOR_TRIGGER = new_value

    @classmethod
    def update_vaccine_trigger(cls, new_value: bool):
        cls.VACCINATION_TRIGGER = new_value

    @classmethod
    def update_viral_load(cls, new_value: bool):
        cls.VIRAL_LOAD = new_value

    @classmethod
    def update_ICU_presence(cls, new_value: bool):
        cls.ICU_PRESENCE = new_value

    @classmethod
    def update_v1_growth_prob(cls, new_value: bool):
        cls.V1_GROWTH_PROB = new_value

    @classmethod
    def update_antiv_kill_prob(cls, new_value: bool):
        cls.ANTIV_KILL_PROB = new_value

    @classmethod
    def update_antivesp_young_ratio(cls, new_value: bool):
        cls.ANTIVESP_YOUNG_RATIO = new_value

    @classmethod
    def update_antivesp_adult_ratio(cls, new_value: bool):
        cls.ANTIVESP_ADULT_RATIO = new_value


    # Viral load thresholds
    @classmethod
    def update_incubation_v1(cls, new_value: bool):
        cls.INCUBATION_V1 = new_value

    @classmethod
    def update_infection_v1(cls, new_value: bool):
        cls.INFECTION_V1 = new_value

    @classmethod
    def update_recovered_antivesp(cls, new_value: bool):
        cls.RECOVERED_ANTIVESP = new_value

    @classmethod
    def update_symptoms_progression(cls, new_value: bool):
        cls.SYMPTOMS_PROGRESSION = new_value

  

    @staticmethod
    def infect_individuals(individuals, infection_rate, number_of_infected, total_in_membrane, province_membrane):
        """
        Simulates infection spread among individuals based on current conditions.

        Args:
            individuals: List of Individual objects to process for potential infection
            infection_rate: Base rate of infection for the environment
            number_of_infected: Count of infected individuals in the current place membrane
            total_in_membrane: Total population in the current place membrane
            province_membrane: Province data containing population statistics

        Returns:
            int: Number of new infections that occurred during this simulation step
        """
        new_infections = 0

        # Get province-level infection metrics
        m = province_membrane.total_infected()
        n = province_membrane.total_population()

        # Apply global infection reduction factor
        #adjusted_infection_rate = infection_rate / InfectionRules.INFECTION_REDUCTION_FACTOR

        # Process each susceptible individual
        for individual in individuals:
            if individual.status != "Healthy":
                continue

            # Calculate infection probability based on local conditions
            probability_of_infection = infection_rate

            # Apply behavioral adaptation factor if enabled
            if InfectionRules.BEHAVIOR_TRIGGER:
                local_infection_ratio = number_of_infected / total_in_membrane
                #caution_multiplier = BehaviorModel.caution_factor(m, n, InfectionRules.CAUTION_FACTOR)
                probability_of_infection *= local_infection_ratio #* caution_multiplier

            # Apply vaccination protection if enabled and individual is vaccinated
            if InfectionRules.VACCINATION_TRIGGER and individual.vaccination_days_left > 0:
                probability_of_infection *= (1 - individual.vaccine_effectiveness)

            # Determine if infection occurs
            if probability_of_infection >= random.random():
                individual.status = "Incubation"
                new_infections += 1

                # Initialize viral load or incubation timer based on simulation mode
                if InfectionRules.VIRAL_LOAD:
                    individual.v1 = InfectionRules.INCUBATION_V1
                    individual.inf += 1
                else:
                    individual.incubation_days_left = InfectionRules.INCUBATION_PERIOD

        return new_infections


def handle_infection(individuals, v1_growth_prob, antiv_kill_prob):
    """
    Processes viral load dynamics and immune response for infected individuals.

    Args:
        individuals: List of infected Individual objects to process
        v1_growth_prob: Probability of viral load increase per unit
        antiv_kill_prob: Probability of antibody neutralizing virus
    """
    for individual in sorted(individuals, key=lambda x: x.number):
        if individual.v1 <= 0:
            continue

        # Accumulate infection score based on viral load
        individual.inf += individual.v1

        # Process antibody neutralization of virus
        antivesp_kill = min(individual.antivesp, individual.v1)
        individual.v1 -= antivesp_kill

        # Check for recovery due to complete viral clearance
        if individual.v1 == 0:
            individual.recover()
            continue

        # Calculate antibody production based on age and symptom severity
        # Each 200 units of v1 and antiv can produce one new antibody unit
        max_possible_antibodies = min(individual.v1 // 200, individual.antiv // 200)

        if max_possible_antibodies > 0:
            # Select appropriate antibody production rate based on age and symptoms
            antivesp_prob = _get_antivesp_probability(individual)
            antivesp_prob *= 3  # Increased antibody production rate

            # Stochastically determine new antibody production
            new_antivesp = sum(1 for _ in range(max_possible_antibodies)
                               if random.random() < antivesp_prob)

            # Reduce viral load for antibody production
            individual.v1 -= new_antivesp * 200
        else:
            new_antivesp = 0

        # Process direct antibody neutralization of virus
        antiv_neutralizations = sum(1 for _ in range(min(individual.v1, individual.antiv))
                                    if random.random() < antiv_kill_prob)
        individual.v1 -= antiv_neutralizations

        # Calculate viral replication
        v1_growth = sum(1 for _ in range(individual.v1)
                        if random.random() < v1_growth_prob)

        # Update viral and immune parameters
        individual.v1 += v1_growth + new_antivesp * 199
        individual.v1_ino += antivesp_kill + antiv_neutralizations + new_antivesp

        # Check for recovery based on antibody threshold
        if individual.antivesp >= InfectionRules.RECOVERED_ANTIVESP:
            individual.recover()

        # Update immune system resources
        individual.antiv -= new_antivesp
        individual.antivesp += new_antivesp

        # Enforce system bounds
        _clamp_individual_parameters(individual)


def _get_antivesp_probability(individual):
    """
    Helper function to determine antibody production probability
    based on individual's age and symptom severity.

    Args:
        individual: Individual object with age_group and symptoms attributes

    Returns:
        float: Probability of antibody production
    """
    if individual.age_group == "young":
        if individual.symptoms == "E2": return InfectionRules.ANTIVESP_YOUNG_E2_PROB
        if individual.symptoms == "E3": return InfectionRules.ANTIVESP_YOUNG_E3_PROB
        if individual.symptoms == "E4": return InfectionRules.ANTIVESP_YOUNG_E4_PROB
    elif individual.age_group == "adult":
        if individual.symptoms == "E2": return InfectionRules.ANTIVESP_ADULT_E2_PROB
        if individual.symptoms == "E3": return InfectionRules.ANTIVESP_ADULT_E3_PROB
        if individual.symptoms == "E4": return InfectionRules.ANTIVESP_ADULT_E4_PROB
    elif individual.age_group == "elderly":
        if individual.symptoms == "E2": return InfectionRules.ANTIVESP_ELDERLY_E2_PROB
        if individual.symptoms == "E3": return InfectionRules.ANTIVESP_ELDERLY_E3_PROB
        if individual.symptoms == "E4": return InfectionRules.ANTIVESP_ELDERLY_E4_PROB
    return 0  # Default case


def _clamp_individual_parameters(individual):
    """
    Helper function to ensure individual's biological parameters
    stay within valid ranges.

    Args:
        individual: Individual object to constrain parameters for
    """
    individual.v1 = clamp(individual.v1, 0, 1000)
    individual.v1_ino = clamp(individual.v1_ino, 0, 1000)
    individual.antiv = clamp(individual.antiv, 0, 1000)
    individual.antivesp = clamp(individual.antivesp, 0, 1000)


def phag_eating(individuals):
    """
    Processes phagocytosis of neutralized virus by immune cells.

    Args:
        individuals: List of Individual objects to process
    """
    for individual in individuals:
        if individual.v1_ino > 0:
            # Phagocytes consume neutralized virus particles
            consumed = min(individual.v1_ino, individual.phag)
            individual.v1_ino -= consumed
            individual.v1_ino = clamp(individual.v1_ino, 0, 1000)


def clamp(value, min_value, max_value):
    """
    Constrains a value between minimum and maximum bounds.

    Args:
        value: The value to constrain
        min_value: Lower bound
        max_value: Upper bound

    Returns:
        The value constrained between bounds
    """
    return max(min_value, min(value, max_value))


def handle_symptoms(individuals):
    """
    Updates symptom severity based on accumulated infection score.

    Args:
        individuals: List of Individual objects to process
    """
    for individual in sorted(individuals, key=lambda x: x.number):
        if individual.inf >= InfectionRules.SYMPTOMS_PROGRESSION:
            # Symptom progression probabilities (values differ from paper)
            if individual.symptoms == "E3" and random.random() < 0.001:  # Paper: 0.0025
                individual.symptoms = "E4"
            elif individual.symptoms == "E2" and random.random() < 0.0015:  # Paper: 0.003
                individual.symptoms = "E3"
            elif individual.symptoms == "E1":
                individual.symptoms = "E2"  # Automatic progression from E1 to E2
        else:
            individual.symptoms = "E1"  # Reset symptoms if infection score is low

        # Reset infection score for next cycle
        individual.inf = 0