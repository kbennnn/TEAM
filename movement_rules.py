import logging
import random

from infection_rules import InfectionRules
from membrane import ProvinceMembrane


class MovementRules:
    """
    Handles movement of individuals between provinces based on various conditions including
    infection status, age group, and destination preferences.
    """
    def __init__(self):
        self.infection_rules = InfectionRules()


    @staticmethod
    def move_students_between_provinces(origin_province, destination_province):
        """
        Moves students (young age group) from origin to destination province.

        Similar to general movement but specifically targets the 'young' age group.
        Movement probability is affected by infection rates and individual symptoms.

        Parameters:
        - origin_province (str): Province ID where students are currently located
        - destination_province (str): Target province ID for movement

        Returns:
        - int: Number of students moved
        """
        destination_province_membrane = ProvinceMembrane.get_province_membrane_by_label(destination_province)
        origin_province_membrane = ProvinceMembrane.get_province_membrane_by_label(origin_province)

        if destination_province_membrane is None or origin_province_membrane is None:
            logging.warning(f"Could not find one or both provinces: {origin_province} or {destination_province}")
            return 0

        individuals_to_move = []

        # Find eligible students across all locations in origin province
        for place in (origin_province_membrane.schools + origin_province_membrane.workplaces
                      + origin_province_membrane.leisure_centers + origin_province_membrane.common_areas + origin_province_membrane.houses):
            for individual in place.individuals_inside:
                # Filter for young individuals (students) with matching destination and early symptoms
                if (individual.province_destination == destination_province and
                        individual.age_group == 'young' and
                        individual.symptoms in ("E1", "E2")):

                    # Calculate movement probability based on destination infection rate
                    if destination_province_membrane.total_population() != 0:
                        prob_of_moving = 1 - (destination_province_membrane.total_infected() /
                                              destination_province_membrane.total_population())
                    else:
                        prob_of_moving = 1

                    # Apply additional prudence factor for E2 symptomatic individuals
                    if individual.symptoms == "E2":
                        prob_of_moving = prob_of_moving * (1 - InfectionRules.PRUDENCE_PARAMETER)**2

                    if prob_of_moving >= random.random():
                        individuals_to_move.append((place, individual))

        # Process actual movements
        move_count = 0
        for place, individual in individuals_to_move:
            place.remove_individual(individual)
            destination_province_membrane.move_to_province(individual)
            move_count += 1

        return move_count

    @staticmethod
    def move_workers_between_provinces(origin_province, destination_province):
        """
        Moves adult workers from origin to destination province.

        Specifically targets 'adult' age group with appropriate destination preferences.
        Movement probability decreases with higher infection rates in destination.

        Parameters:
        - origin_province (str): Province ID where workers are currently located
        - destination_province (str): Target province ID for movement

        Returns:
        - int: Number of workers moved (implicitly, function returns None)
        """
        destination_province_membrane = ProvinceMembrane.get_province_membrane_by_label(destination_province)
        origin_province_membrane = ProvinceMembrane.get_province_membrane_by_label(origin_province)

        if destination_province_membrane is None or origin_province_membrane is None:
            logging.warning(f"Could not find one or both provinces: {origin_province} or {destination_province}")
            return 0

        individuals_to_move = []

        # Find eligible workers across all locations in origin province
        for place in (origin_province_membrane.schools + origin_province_membrane.workplaces
                      + origin_province_membrane.leisure_centers + origin_province_membrane.common_areas + origin_province_membrane.houses):
            for individual in place.individuals_inside:
                # Filter for adult individuals with matching destination and early symptoms
                if (individual.province_destination == destination_province and
                        individual.age_group == 'adult' and
                        individual.symptoms in ("E1", "E2")):

                    # Calculate movement probability based on destination infection rate
                    if destination_province_membrane.total_population() != 0:
                        prob_of_moving = 1 - (destination_province_membrane.total_infected() /
                                              destination_province_membrane.total_population())
                    else:
                        prob_of_moving = 1

                    # Apply additional prudence factor for E2 symptomatic individuals
                    if individual.symptoms == "E2":
                        prob_of_moving = prob_of_moving * (1 - InfectionRules.PRUDENCE_PARAMETER)**2

                    if prob_of_moving >= random.random():
                        individuals_to_move.append((place, individual))

        # Process actual movements
        move_count = 0
        for place, individual in individuals_to_move:
            place.remove_individual(individual)
            destination_province_membrane.move_to_province(individual)
            move_count += 1

            # Debug check for incorrectly moving symptomatic individuals
            if individual.symptoms in ("E3", "E4"):
                logging.error(f"Error: Moving a worker with advanced symptoms {individual.symptoms}")

        return move_count

    @staticmethod
    def move_elderly_between_provinces(origin_province, destination_province):
        """
        Moves elderly individuals between provinces with a probability-based approach.

        Only 17% of eligible elderly are considered for movement. Each moved individual
        is assigned a return time of 1-3 hours based on weighted probabilities.

        Parameters:
        - origin_province (str): Province ID where elderly are currently located
        - destination_province (str): Target province ID for movement

        Returns:
        - list: Pairs of (individual_number, return_hours) for tracking returns
        """
        destination_province_membrane = ProvinceMembrane.get_province_membrane_by_label(destination_province)
        origin_province_membrane = ProvinceMembrane.get_province_membrane_by_label(origin_province)
        return_hours = []

        if destination_province_membrane is None or origin_province_membrane is None:
            logging.warning(f"Could not find one or both provinces: {origin_province} or {destination_province}")
            return return_hours

        individuals_to_move = []

        # Find eligible elderly across all locations in origin province
        for place in (origin_province_membrane.schools + origin_province_membrane.workplaces
                      + origin_province_membrane.leisure_centers + origin_province_membrane.common_areas + origin_province_membrane.houses):
            for individual in place.individuals_inside:
                # Filter for elderly with matching destination, early symptoms, and random 17% selection
                if (individual.age_group == 'elderly' and
                        individual.symptoms in ("E1", "E2") and
                        random.uniform(0, 1) < 0.17 and
                        individual.province_destination == destination_province):

                    # Calculate movement probability based on destination infection rate
                    if destination_province_membrane.total_population() != 0:
                        prob_of_moving = 1 - (destination_province_membrane.total_infected() /
                                              destination_province_membrane.total_population())
                    else:
                        prob_of_moving = 1

                    # Apply additional prudence factor for E2 symptomatic individuals
                    if individual.symptoms == "E2":
                        prob_of_moving = prob_of_moving * (1 - InfectionRules.PRUDENCE_PARAMETER)**2

                    if prob_of_moving >= random.random():
                        # Assign return hours with weighted probabilities: 40% for 1hr, 24% for 2hrs, 36% for 3hrs
                        return_time = random.choices([1, 2, 3], weights=[0.4, 0.24, 0.36], k=1)[0]
                        return_hours.append((individual.number, return_time))
                        individuals_to_move.append((place, individual))

        # Process actual movements
        for place, individual in individuals_to_move:
            place.remove_individual(individual)
            destination_province_membrane.move_to_province(individual)

        return return_hours

    @staticmethod
    def get_home_students(current_province, students_to_move):
        """
        Relocates students from common areas back to their houses in the current province.

        Parameters:
        - current_province (ProvinceMembrane): The current province membrane object
        - students_to_move (list): List of student individuals to be moved home
        """
        if not students_to_move:
            return

        # Create copy to avoid modifying list during iteration
        students_to_move_copy = students_to_move.copy()

        for common_area in current_province.common_areas:
            for individual in students_to_move_copy:
                if individual in common_area.individuals_inside:
                    # Only add to house if not already there
                    if individual not in individual.house.individuals_inside:
                        common_area.remove_individual(individual)
                        individual.house.individuals_inside.append(individual)
                    students_to_move.remove(individual)

    @staticmethod
    def get_home_from_hospital(individual):
        """
        Places an individual directly into their house, typically after hospital discharge.

        Parameters:
        - individual: The individual object to be placed in their house
        """
        individual.house.individuals_inside.append(individual)