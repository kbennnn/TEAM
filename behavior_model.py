import random
import numpy as np

class BehaviorModel:
    """
    Models vaccination behavior in a population during an epidemic.

    This class provides methods to calculate vaccination willingness based on
    infection rates and to assign vaccine effectiveness with correlated duration.

    Class Constants:
    - VACCINE_EFFECTIVENESS_LOWER_BOUND: Minimum vaccine efficacy percentage
    - VACCINE_EFFECTIVENESS_UPPER_BOUND: Maximum vaccine efficacy percentage
    - DURATION_CORRELATION: Correlation coefficient between vaccine effectiveness and duration
    - F_STAR: Reference infection rate for calibrating willingness calculations
    """
    VACCINE_EFFECTIVENESS_LOWER_BOUND = 15 #MODIFICATO
    VACCINE_EFFECTIVENESS_UPPER_BOUND = 65 #MODIFICATO
    DURATION_CORRELATION = 0.8

    MEAN_VACCINE_DURATION = 210 #SPOSTATO QUI
    VACCINE_DURATION_STD = 30.0 #durata del vaccino è fra 6 e 8 mesi, in media 7

    F_STAR = 0.01

    #AGGIUNTO
    VACCINE_PROTECTION_DELAY = 14 #quanto tempo dopo la vaccinazione si attiva la protezione
    VACCINE_WANING_HALF_LIFE = 90 #la half life del vaccino (3 mesi)

    @classmethod
    def update_duration_correlation(cls, new_value: float):
        """Update correlation between effectiveness and duration."""
        #AGGIUNTO: gestisce valori illegali di DURATION_CORRELATION
        if not -1 <= new_value <= 1:
            raise ValueError("DURATION_CORRELATION must be between -1 and 1")
        
        cls.DURATION_CORRELATION = new_value

    @classmethod
    def update_f_star(cls, new_value: float):
        """Update reference infection rate threshold."""
        cls.F_STAR = new_value

    @classmethod
    def update_vaccine_effectiveness_lower_bound(cls, new_value: float):
        """Update reference infection rate threshold."""
        cls.VACCINE_EFFECTIVENESS_LOWER_BOUND = new_value

    @classmethod
    def update_vaccine_effectiveness_upper_bound(cls, new_value: float):
        """Update reference infection rate threshold."""
        cls.VACCINE_EFFECTIVENESS_UPPER_BOUND = new_value

    '''    @staticmethod
    def caution_factor(M, N, a):
        """
        Calculate individuals' caution level as infection rates change.

        Args:
            M (int): Currently infected individuals
            N (int): Total population
            a (float): Sensitivity parameter for caution response

        Returns:
            float: Caution factor between 0-1 (lower when more infected)
        """
        return 1 / (1 + a * M / N) if N else 0.0
        '''

    @staticmethod
    def vaccination_willingness(M, N):
        """
        Calculate population's willingness to get vaccinated based on infection rate.

        Formula uses a sigmoid-like response where willingness increases as
        infection rate exceeds a threshold (F_STAR).

        Args:
            M (int): Currently infected individuals
            N (int): Total population

        Returns:
            float: Willingness factor (1.0-2.0)
        """
        f = M / N
        x = f / BehaviorModel.F_STAR
        return 1 + (x ** 2) / (1 + x ** 2)

    @staticmethod
    def get_vaccination_probability(M, N):
        """
        Calculate probability an individual will get vaccinated.

        Combines both population willingness and individual randomness.

        Args:
            M (int): Currently infected individuals
            N (int): Total population

        Returns:
            float: Probability value between 0-2
        """
        return random.uniform(0, 1) * BehaviorModel.vaccination_willingness(M, N)

    @staticmethod
    def assign_vaccine_effectiveness():
        """
        Generate random vaccine effectiveness value.

        Returns:
            float: Effectiveness percentage between configured bounds
        """
        return random.uniform(BehaviorModel.VACCINE_EFFECTIVENESS_LOWER_BOUND,
                              BehaviorModel.VACCINE_EFFECTIVENESS_UPPER_BOUND)

    @staticmethod
    def assign_vaccine_effectiveness_with_duration():
        """
        Generate correlated vaccine effectiveness and duration values.

        Models the relationship where higher effectiveness tends to
        correlate with longer protection duration.

        Returns:
            tuple: (vaccine_effectiveness, duration_in_days)
        """

        """
        
        OLD VERSION:


        vaccine_effectiveness = random.uniform(
            BehaviorModel.VACCINE_EFFECTIVENESS_LOWER_BOUND,
            BehaviorModel.VACCINE_EFFECTIVENESS_UPPER_BOUND
        ) / 100

        # Mean duration set to 210 days
        mean_duration = 210

        # Create covariance matrix for correlated variables
        cov_matrix = np.array([
            [1.0, BehaviorModel.DURATION_CORRELATION],
            [BehaviorModel.DURATION_CORRELATION, 1.0]
        ])

        # Generate correlated random variable
        duration = np.random.multivariate_normal([mean_duration, mean_duration], cov_matrix)[0]

        return vaccine_effectiveness, int(duration)

        """

        lower = BehaviorModel.VACCINE_EFFECTIVENESS_LOWER_BOUND
        upper = BehaviorModel.VACCINE_EFFECTIVENESS_UPPER_BOUND

        effectiveness_percent = random.uniform(lower, upper)

        vaccine_effectiveness = effectiveness_percent / 100

        mean_duration = BehaviorModel.MEAN_VACCINE_DURATION
        duration_std = BehaviorModel.VACCINE_DURATION_STD

        #fino a qua è tutto uguale, solo suddiviso in variabili più chiare

        effectiveness_mean = (lower + upper) / 2
        effectiveness_std = (upper - lower) / np.sqrt(12)

        z_effectiveness = (effectiveness_percent - effectiveness_mean) / effectiveness_std

        z_random = np.random.normal(0, 1)

        correlation = BehaviorModel.DURATION_CORRELATION

        z_duration = (
            correlation * z_effectiveness #parte legata a durata
            + np.sqrt(1 - correlation**2) * z_random #parte casuale
        )

        duration = mean_duration + duration_std * z_duration

        # ora durata ed efficacia sono correlate. Prima DURATION_CORRELATION non influenzava nulla

        return vaccine_effectiveness, int(round(duration))

    @staticmethod
    def get_current_vaccine_effectiveness(initial_effectiveness, days_since_vaccination):

        if initial_effectiveness <= 0:
            return 0.0

        if days_since_vaccination < BehaviorModel.VACCINE_PROTECTION_DELAY:
            return 0.0

        days_of_protection = (days_since_vaccination - BehaviorModel.VACCINE_PROTECTION_DELAY)

        waning_factor = 0.5 ** (days_of_protection / BehaviorModel.VACCINE_WANING_HALF_LIFE)

        return initial_effectiveness * waning_factor