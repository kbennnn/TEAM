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
    VACCINE_EFFECTIVENESS_LOWER_BOUND = 15
    VACCINE_EFFECTIVENESS_UPPER_BOUND = 65
    DURATION_CORRELATION = 0.8

    MEAN_VACCINE_DURATION = 210
    VACCINE_DURATION_STD = 30.0 #vaccine duration is between 6-8 months, so the mean is 7 months (210 days) and the std is 30 days

    F_STAR = 0.01

    VACCINE_PROTECTION_DELAY = 14 #how much time after vaccination the protection is effective (2 weeks)
    VACCINE_WANING_HALF_LIFE = 90 #vaccine half life (3 months)

    MIN_VACCINE_DURATION = 90   # Minimum duration: 3 months
    MAX_VACCINE_DURATION = 330  # Maximum duration: 11 months

    @classmethod
    def update_duration_correlation(cls, new_value: float):
        """Update correlation between effectiveness and duration."""
   
        if not -1 <= new_value <= 1:
            raise ValueError("DURATION_CORRELATION must be between -1 and 1")
        
        cls.DURATION_CORRELATION = new_value

    @classmethod
    def update_f_star(cls, new_value: float):
        """Update reference infection rate threshold."""
        cls.F_STAR = new_value

    @classmethod
    def update_vaccine_effectiveness_lower_bound(cls, new_value: float):
        """Update the lower bound of vaccine effectiveness."""
        cls.VACCINE_EFFECTIVENESS_LOWER_BOUND = new_value

    @classmethod
    def update_vaccine_effectiveness_upper_bound(cls, new_value: float):
        """Update the upper bound of vaccine effectiveness."""
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
            stochastic vaccination propensity value based on population willingness.
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

        lower = BehaviorModel.VACCINE_EFFECTIVENESS_LOWER_BOUND
        upper = BehaviorModel.VACCINE_EFFECTIVENESS_UPPER_BOUND

        effectiveness_percent = random.uniform(lower, upper)

        vaccine_effectiveness = effectiveness_percent / 100

        mean_duration = BehaviorModel.MEAN_VACCINE_DURATION
        duration_std = BehaviorModel.VACCINE_DURATION_STD

        effectiveness_mean = (lower + upper) / 2
        effectiveness_std = (upper - lower) / np.sqrt(12)

        z_effectiveness = (effectiveness_percent - effectiveness_mean) / effectiveness_std

        z_random = np.random.normal(0, 1)

        correlation = BehaviorModel.DURATION_CORRELATION

        z_duration = (
            correlation * z_effectiveness
            + np.sqrt(1 - correlation**2) * z_random
        )

        duration = mean_duration + duration_std * z_duration

        duration = max(
            BehaviorModel.MIN_VACCINE_DURATION,
            min(duration, BehaviorModel.MAX_VACCINE_DURATION)
        )

        return vaccine_effectiveness, int(round(duration))

    @staticmethod
    def get_current_vaccine_effectiveness(initial_effectiveness, days_since_vaccination):

        """
        Calculate the effective vaccine protection at a given time since vaccination.

        Protection is zero during the initial protection delay. After that delay,
        vaccine effectiveness decreases exponentially according to the configured
        waning half-life.

        Args:
            initial_effectiveness (float): Vaccine effectiveness assigned at vaccination,
                expressed as a fraction between 0 and 1.
            days_since_vaccination (int): Number of days elapsed since vaccination.

        Returns:
            float: Current vaccine effectiveness as a fraction between 0 and the
                initially assigned effectiveness.
        """

        if initial_effectiveness <= 0:
            return 0.0

        if days_since_vaccination < BehaviorModel.VACCINE_PROTECTION_DELAY:
            return 0.0

        days_of_protection = (days_since_vaccination - BehaviorModel.VACCINE_PROTECTION_DELAY)

        waning_factor = 0.5 ** (days_of_protection / BehaviorModel.VACCINE_WANING_HALF_LIFE)

        return initial_effectiveness * waning_factor