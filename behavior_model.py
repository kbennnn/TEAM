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
    F_STAR = 0.01

    @classmethod
    def update_duration_correlation(cls, new_value: float):
        """Update correlation between effectiveness and duration."""
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
