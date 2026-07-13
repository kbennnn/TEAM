import random
import sys
from behavior_model import BehaviorModel
from infection_rules import InfectionRules

"""
Define a general Membrane class representing a basic structural unit
in the simulation. Each membrane has a unique identifier (label).
This serves as the base class for more specialized membrane types.
"""


class Membrane:
    # Define provinces as class attributes for consistent reference across all instances
    NUM_OF_PROV = 12
    PROVINCES = [f"PV_{i+1}" for i in range(NUM_OF_PROV)]

    @classmethod
    def update_num_of_prov(cls, new_value: int):
        """
        Update the number of provinces in the simulation and regenerate province labels.

        Args:
            new_value (int): New number of provinces to create

        Raises:
            ValueError: If the provided value is not a positive integer

        Note:
            This method will attempt to update the Simulation class provinces if available
        """
        if not isinstance(new_value, int) or new_value < 1:
            raise ValueError("Number of provinces must be a positive integer")
        cls.NUM_OF_PROV = new_value
        cls.PROVINCES = [f"PV_{i+1}" for i in range(new_value)]

        # Dynamically import Simulation to avoid circular import
        try:
            from simulation import Simulation
            Simulation.update_provinces(cls.PROVINCES)
        except ImportError:
            print("Simulation class not available")


    def __init__(self, label):
        """
        Initialize a Membrane instance.

        Args:
            label (str): Unique identifier for the Membrane
        """
        self.label = label

    def __repr__(self):
        """
        Return a string representation of the Membrane instance.

        Returns:
            str: String representation including the label
        """
        return f"Membrane({self.label})"



"""
ProvinceMembrane represents a geographic region containing various places
like schools, workplaces, hospitals, etc. It serves as a container and 
manager for all places and individuals within a province.
"""

class ProvinceMembrane(Membrane):
    # Dictionary to track counts of each place type for automatic labeling
    counters = {"SC": 0, "WP": 0, "HP": 0, "LC": 0, "CA": 0, "ICU": 0, "H": 0}

    # Registry to access provinces by label without passing references
    province_registry = {}

    def __init__(self, label, schools=None, workplaces=None, leisure_centers=None, common_areas=None, hospitals=None, ICUs=None, houses=None):
        """
        Initialize a province with various places.

        Args:
            label (str): Unique identifier for the province
            schools (list, optional): List of SchoolMembrane instances
            workplaces (list, optional): List of WorkPlaceMembrane instances
            leisure_centers (list, optional): List of LeisureCentreMembrane instances
            common_areas (list, optional): List of CommonAreaMembrane instances
            hospitals (list, optional): List of HospitalMembrane instances
            ICUs (list, optional): List of ICUMembrane instances
            houses (list, optional): List of HouseMembrane instances
        """
        super().__init__(label)
        self.hospitals = hospitals if hospitals else []
        self.schools = schools if schools else []
        self.workplaces = workplaces if workplaces else []
        self.leisure_centers = leisure_centers if leisure_centers else []
        self.common_areas = common_areas if common_areas else []
        self.houses = houses if houses else []
        self.ICUs = ICUs if ICUs else []


        #ADDED: cache parameters
        self._cached_infected = 0
        self._cached_population = 0


        # Register this province for global access
        ProvinceMembrane.province_registry[label] = self

    def initialize_houses(self, total_pop):
        """
        Create houses with realistic population distribution.

        Args:
            total_pop (int): Total expected population for all provinces

        Note:
            Creates houses with 1-6 residents with mode of 3 people per house
            Distributes population according to realistic household size distribution
        """
        # Calculate province population share
        province_pop = total_pop // len(self.PROVINCES)
        max_houses = province_pop // 3  # Average of 3 people per house

        # Ensure minimum number of houses for diversity
        min_houses = max(5, max_houses // 10)  # At least 5 houses or 10% of max_houses
        working_houses = max(min_houses, max_houses)

        # Distribution of house sizes (1-6 people)
        target_dist = {1: 0.1, 2: 0.2, 3: 0.4, 4: 0.15, 5: 0.1, 6: 0.05}

        # Calculate number of houses of each size
        house_sizes = {}
        remaining_pop = province_pop
        remaining_houses = working_houses

        # Distribute houses according to target distribution
        for size, prob in list(target_dist.items())[:-1]:  # Process all but last size
            houses_of_size = max(1, int(working_houses * prob))
            if remaining_houses - houses_of_size >= 1:  # Ensure we leave at least 1 house for the last size
                house_sizes[size] = houses_of_size
                remaining_houses -= houses_of_size
                remaining_pop -= houses_of_size * size
            else:
                houses_of_size = max(1, remaining_houses - 1)
                house_sizes[size] = houses_of_size
                remaining_houses = 1
                remaining_pop -= houses_of_size * size

        # Assign remaining houses to last size to accommodate remaining population
        houses_needed_for_remaining = (remaining_pop + 5) // 6  # Using size 6 for last group
        house_sizes[6] = max(remaining_houses, houses_needed_for_remaining)
        remaining_pop -= house_sizes[6] * 6

        # Create houses with their target sizes
        house_count = 1
        for size, count in house_sizes.items():
            for _ in range(count):
                house = HouseMembrane(label=f"H{house_count}_{self.label}", capacity=6)
                house.province = self.label
                house.target_occupants = size
                self.houses.append(house)
                house_count += 1

    @staticmethod
    def get_province_membrane_by_label(province_label):
        """
        Retrieve a province by its label from the registry.

        Args:
            province_label (str): Label of the province to find

        Returns:
            ProvinceMembrane or None: The matching province or None if not found
        """
        return ProvinceMembrane.province_registry.get(province_label, None)

    def getLabel(self):
        """
        Get the label of the province.

        Returns:
            str: The province's label
        """
        return self.label

    def move_to_province(self, individual):
        """
        Add individual to this province's first common area.

        Args:
            individual: The individual to move into this province

        Note:
            Used when an individual migrates between provinces.
            Individual is placed in the first common area of the destination province.
        """
        if self.common_areas:
            self.common_areas[0].add_individual(individual)

    def add_place(self, mem_to_add):
        """
        Add a place to the province and update tracking information.

        Args:
            mem_to_add (PlaceMembrane): The place to add to this province

        Note:
            - Updates the place's label with a sequential number
            - Initializes the place's infection count
            - Sets the place's province reference
            - Adds the place to the appropriate collection in the province
        """
        # Extract place type from label
        membrane_type = mem_to_add.label

        # Verify place type is valid
        if membrane_type not in ProvinceMembrane.counters:
            print("Not a valid PlaceMembrane label")
            return

        # Update counter and assign unique identifier
        ProvinceMembrane.counters[membrane_type] += 1
        counter_value = ProvinceMembrane.counters[membrane_type]
        mem_to_add.label += str(counter_value)

        # Initialize place properties
        mem_to_add.infected = 0
        mem_to_add.province = self.getLabel()

        # Add to appropriate collection based on type
        if membrane_type == "SC":
            self.schools.append(mem_to_add)
        if membrane_type == "WP":
            self.workplaces.append(mem_to_add)
        if membrane_type == "CA":
            self.common_areas.append(mem_to_add)
        if membrane_type == "LC":
            self.leisure_centers.append(mem_to_add)
        if membrane_type == "HP":
            self.hospitals.append(mem_to_add)
        if membrane_type == "ICU":
            self.ICUs.append(mem_to_add)
        if membrane_type == "H":
            self.houses.append(mem_to_add)


    #ADDED: updates cache parameters
    def update_cache(self):
        all_places = (self.schools + self.workplaces + self.leisure_centers +
                  self.common_areas + self.hospitals + self.ICUs + self.houses)
        self._cached_infected = sum(place.get_total_infected() for place in all_places)
        self._cached_population = sum(place.get_total_individuals() for place in all_places)



    def total_infected(self):
        """
        Count infected individuals across all places in the province.

        Returns:
            int: Total number of infected individuals
        """
        
        #old code:
        #return sum(place.get_total_infected() for place in
                   #self.schools + self.workplaces + self.leisure_centers +
                   #self.common_areas + self.hospitals + self.ICUs + self.houses)

  
        return self._cached_infected  # NEW CODE: uses cache value




    def total_vaccinated(self):
        """
        Count vaccinated individuals across all places in the province.

        Returns:
            int: Total number of vaccinated individuals
        """
        return sum(place.get_total_vaccinated() for place in
                   self.schools + self.workplaces + self.leisure_centers +
                   self.common_areas + self.hospitals + self.ICUs + self.houses)

    def total_to_vaccinate(self):
        """
        Count individuals eligible for vaccination across all places.

        Returns:
            int: Total number of individuals eligible for vaccination
        """
        return sum(place.get_total_to_vaccinate() for place in
                   self.schools + self.workplaces + self.leisure_centers +
                   self.common_areas + self.hospitals + self.ICUs + self.houses)

    def total_population(self):
        """
        Count all individuals across all places in the province.

        Returns:
            int: Total population of the province
        """
        #old code:
        #return sum(place.get_total_individuals() for place in
                   #self.schools + self.workplaces + self.leisure_centers +
                   #self.common_areas + self.hospitals + self.ICUs + self.houses)


        return self._cached_population  # NEW CODE: uses cache value



    def vaccinate_population(self, coverage_percent):
        """
        Simulate vaccination campaign for a portion of the eligible population.

        Args:
            coverage_percent (float): Target percentage of eligible population to vaccinate

        Note:
            - Vaccination depends on individual willingness (affected by epidemic severity)
            - Vaccine effectiveness varies and has limited duration
            - Only healthy, unvaccinated individuals are eligible
        """
        # Get all eligible individuals in the province
        all_individuals = [
            individual for place in (self.schools + self.workplaces + self.leisure_centers +
                                     self.common_areas + self.ICUs + self.houses)
            for individual in place.individuals_inside
            if individual.status == "Healthy" and individual.vaccinated is False
        ]

        # Randomize vaccination order
        random.shuffle(all_individuals)

        # Calculate target number based on coverage percentage
        num_to_vaccinate = round(coverage_percent * len(all_individuals))
        num_to_vaccinate = int(num_to_vaccinate)  # Ensure it's an integer

        # Process each eligible individual up to the target number
        for individual in all_individuals[:num_to_vaccinate]:
            # Model willingness based on epidemic severity
            vaccination_probability = BehaviorModel.get_vaccination_probability(
                M=self.total_infected(),
                N=self.total_population()
            )

            # Apply willingness check
            if vaccination_probability >= random.uniform(0, 1):
                individual.vaccinated = True
                individual.vaccine_effectiveness, individual.vaccination_days_left \
                    = BehaviorModel.assign_vaccine_effectiveness_with_duration()

    def trigger_infection_progress(self):
        """
        Progress the infection state for all individuals in the province.

        Note:
            Should be called the day after infection spreading is calculated
            Updates all individuals across all places
        """
        for place in (self.schools + self.workplaces + self.leisure_centers +
                      self.common_areas + self.hospitals + self.ICUs + self.houses):
            place.progress_infections()

    def reduce_all_hospital_day(self):
        """
        Decrease remaining hospital days for all hospitalized individuals.

        Note:
            Checks all hospitals and ICUs for individuals with hospital days remaining
        """
        for place in self.hospitals + self.ICUs:
            place.reduce_hospital_day()

    def reduce_all_vaccine_day(self):
        """
        Decrease remaining immunity days for all vaccinated individuals.

        Note:
            Checks all places for individuals with vaccination days remaining
        """
        for place in (self.schools + self.workplaces + self.leisure_centers +
                      self.common_areas + self.hospitals + self.ICUs + self.houses):
            place.reduce_vaccine_day()

    def update_all_status(self):
        """
        Update the infection status of all individuals in the province.

        Note:
            Updates statuses based on viral load or other infection indicators
            Removes deceased individuals from their places
        """
        for place in (self.schools + self.workplaces + self.leisure_centers +
                      self.common_areas + self.hospitals + self.ICUs + self.houses):
            place.update_status()


class PlaceMembrane(Membrane):
    """
    Base class for all places where individuals can be located.

    Handles common functionality for managing individuals within a location,
    including adding/removing individuals and tracking infections.
    """

    def __init__(self, label, capacity, infected=0):
        """
        Initialize a place with capacity and infection tracking.

        Args:
            label (str): Identifier for this place
            capacity (int): Maximum number of individuals allowed
            infected (int, optional): Initial count of infected individuals
        """
        super().__init__(label)
        self.capacity = capacity
        self.individuals_inside = []  # List of individuals currently in this place
        self.province = None  # Will be set when added to a province
        self.infected = infected
        self.deceased_individuals = []  # Track deceased individuals for statistics

    def add_individual(self, individual):
        """
        Add an individual to this place if capacity allows.

        Args:
            individual: The individual to add

        Note:
            Terminates program if capacity would be exceeded
        """
        if len(self.individuals_inside) < self.capacity:
            self.individuals_inside.append(individual)
        else:
            error_message = f"Error, individual {individual.number} not joined in {self.label}"
            print(error_message)
            print("Individual not in individuals_inside:", individual not in self.individuals_inside)
            print("Current capacity:", len(self.individuals_inside))
            print("Capacity:", self.capacity)
            sys.exit("Terminating program due to error.")

    def remove_individual(self, individual):
        """
        Remove an individual from this place.

        Args:
            individual: The individual to remove
        """
        if individual in self.individuals_inside:
            self.individuals_inside.remove(individual)

    def get_total_individuals(self):
        """
        Get the count of all individuals in this place.

        Returns:
            int: Number of individuals present
        """
        return len(self.individuals_inside)

    def get_total_infected(self):
        """
        Count infected individuals in this place.

        Returns:
            int: Number of individuals with "Infected" status
        """
        infected = sum(1 for individual in self.individuals_inside if individual.status == "Infected")
        return infected

    def get_total_vaccinated(self):
        """
        Count vaccinated individuals in this place.

        Returns:
            int: Number of vaccinated individuals
        """
        vaccinated = sum(1 for individual in self.individuals_inside if individual.vaccinated)
        return vaccinated

    def get_total_to_vaccinate(self):
        """
        Count individuals eligible for vaccination in this place.

        Returns:
            int: Number of healthy, unvaccinated individuals
        """
        to_be_vaccinated = sum(1 for individual in self.individuals_inside
                               if individual.status == "Healthy" and not individual.vaccinated)
        return to_be_vaccinated

    def get_all_individuals(self):
        """
        Get a list of all individuals in this place.

        Returns:
            list: All individuals currently in this place
        """
        return [individual for individual in self.individuals_inside]

    def get_young_individuals(self):
        """
        Get all young individuals in this place.

        Returns:
            list: Individuals with age_group="young"
        """
        return [individual for individual in self.individuals_inside if individual.age_group == "young"]

    def get_adult_individuals(self):
        """
        Get all adult individuals in this place.

        Returns:
            list: Individuals with age_group="adult"
        """
        return [individual for individual in self.individuals_inside if individual.age_group == "adult"]

    def get_elderly_individuals(self):
        """
        Get all elderly individuals in this place.

        Returns:
            list: Individuals with age_group="elderly"
        """
        return [individual for individual in self.individuals_inside if individual.age_group == "elderly"]

    def progress_infections(self):
        """
        Update infection progression for all individuals.

        Note:
            Should be called the day after new infections occur
            Updates counters after processing all individuals
        """
        for individual in self.individuals_inside:
            individual.progress_infection()
        self.update_infected_count()

    def reduce_hospital_day(self):
        """
        Reduce hospitalization days for hospitalized individuals.

        Note:
            When hospital days reach zero, individual is marked as recovered
            Individuals may remain hospitalized after recovery to complete treatment
        """
        for individual in self.individuals_inside:
            if individual.hospitalization_days_left > 0 and (individual.hospitalized or individual.ICU):
                individual.hospitalization_days_left -= 1
            if individual.hospitalization_days_left == 0:
                individual.hospitalized = False
                individual.ICU = False
                individual.recover()

    def reduce_vaccine_day(self):
        """
        Reduce vaccination immunity days for vaccinated individuals.

        Note:
            When vaccine days reach zero, vaccination status is removed
        """
        for individual in self.individuals_inside:
            if individual.vaccination_days_left > 0:
                individual.vaccination_days_left -= 1
            if individual.vaccination_days_left == 0:
                individual.vaccinated = False

    def update_status(self):
        """
        Update individual status based on viral load or remove deceased.

        Note:
            With viral load model: Updates status based on v1 value thresholds
            Always removes deceased individuals from the place
        """
        for individual in self.individuals_inside:
            if InfectionRules.VIRAL_LOAD:
                # Update status based on v1 value
                if individual.status != "Recovered":
                    if individual.status == "Deceased":
                        self.remove_individual(individual)
                    if individual.v1 == 0:
                        individual.status = "Healthy"
                    elif 1 <= individual.v1 < InfectionRules.INFECTION_V1 and individual.status == ("Healthy" or "Incubation"):
                        individual.status = "Incubation"
                    elif individual.v1 >= InfectionRules.INFECTION_V1:
                        individual.status = "Infected"
            elif individual.status == "Deceased":
                self.remove_individual(individual)
        self.update_infected_count()

    def update_infected_count(self):
        """
        Recalculate and update the infected count for this place.
        """
        infected_count = sum(1 for individual in self.individuals_inside if individual.status == "Infected")
        self.infected = infected_count

    def check_hospitalization(self, individual, hospital_membrane):
        """
        Determine if an individual needs hospitalization and transfer if needed.

        Args:
            individual: Individual to check for hospitalization
            hospital_membrane: Hospital to transfer to if needed

        Note:
            Only processes individuals with severe symptoms (E3/E4)
            Uses probability check to determine hospitalization need
            Sets hospitalization duration to 7 days
        """
        if "HP" not in self.label:  # Skip if already in a hospital
            if ((individual.symptoms == "E3" or individual.symptoms == "E4") and
                    individual.status == "Infected" and
                    individual.hospitalization_days_left == 0 and
                    individual.hospitalized == False):

                # Apply hospitalization probability check
                if random.uniform(0, 1) < InfectionRules.HOSPITALIZATION_PROB:
                    # Transfer to hospital
                    self.remove_individual(individual)
                    individual.hospitalization_days_left = 7  # Set hospitalization duration
                    hospital_membrane.add_individual(individual)
                    individual.hospitalized = True

    def check_ICU(self, individual, ICU_membrane):
        """
        Determine if an individual needs ICU care and transfer if needed.

        Args:
            individual: Individual to check for ICU admission
            ICU_membrane: ICU to transfer to if needed

        Note:
            Processes both non-hospitalized individuals and those already in hospitals
            For already hospitalized patients with E4 symptoms, transfers directly to ICU
            For others, uses probability check to determine ICU need
        """
        if "ICU" not in self.label:  # Skip if already in ICU
            # Check non-hospitalized individuals for direct ICU admission
            if (individual.symptoms == "E4" and
                    individual.status == "Infected" and
                    individual.hospitalization_days_left == 0 and
                    individual.hospitalized == False and
                    individual.ICU == False):

                # Apply ICU probability check
                if random.uniform(0, 1) < InfectionRules.ICU_PROB:
                    # Transfer to ICU
                    self.remove_individual(individual)
                    individual.hospitalization_days_left = InfectionRules.HOSPITALIZATION_PERIOD
                    ICU_membrane.add_individual(individual)
                    individual.ICU = True

            # Direct transfer from hospital to ICU for severe cases
            elif (individual.symptoms == "E4" and
                  individual.status == "Infected" and
                  individual.hospitalization_days_left > 0 and
                  individual.hospitalized == True and
                  individual.ICU == False):
                self.remove_individual(individual)
                ICU_membrane.add_individual(individual)
                individual.ICU = True

class LeisureCenterMembrane(PlaceMembrane):
    """
    Represents a leisure center where individuals gather for entertainment.

    Features higher infection rates, especially during evening/night hours.
    """

    def __init__(self, label="LC", capacity=500, infected=0):
        """
        Initialize a leisure center.

        Args:
            label (str, optional): Base identifier for this leisure center
            capacity (int, optional): Maximum capacity (default 500)
            infected (int, optional): Initial infected count
        """
        super().__init__(label, capacity, infected)
        self.individuals_inside = []

    def infect_young_lc(self, hour):
        """
        Calculate infection spread among young individuals based on time of day.

        Args:
            hour (int): Current hour (0-23)

        Note:
            Higher infection rates during night hours (22-5)
        """
        # Higher infection rate at night
        if 5 <= hour <= 22:
            infection_rate = 0.03  # Normal hours
        else:
            infection_rate = 0.06  # Late night hours

        InfectionRules.infect_individuals(
            self.get_young_individuals(),
            infection_rate,
            self.get_total_infected(),
            len(self.individuals_inside),
            ProvinceMembrane.get_province_membrane_by_label(self.province)
        )

    def infect_adult_lc(self, hour):
        """
        Calculate infection spread among adult individuals based on time of day.

        Args:
            hour (int): Current hour (0-23)

        Note:
            Higher infection rates during night hours (22-5)
        """
        # Higher infection rate at night
        if 5 <= hour <= 22:
            infection_rate = 0.03  # Normal hours
        else:
            infection_rate = 0.06  # Late night hours

        InfectionRules.infect_individuals(
            self.get_adult_individuals(),
            infection_rate,
            self.get_total_infected(),
            len(self.individuals_inside),
            ProvinceMembrane.get_province_membrane_by_label(self.province)
        )

    def infect_elderly_lc(self):
        """
        Calculate infection spread among elderly individuals.

        Note:
            Higher base infection rate (0.08) compared to young/adult groups
        """
        InfectionRules.infect_individuals(
            self.get_elderly_individuals(),
            0.08,  # Higher rate for elderly
            self.get_total_infected(),
            len(self.individuals_inside),
            ProvinceMembrane.get_province_membrane_by_label(self.province)
        )

class WorkPlaceMembrane(PlaceMembrane):
    """
    Represents a workplace where adults spend their working hours.
    """

    def __init__(self, label="WP", capacity=1000, infected=0):
        """
        Initialize a workplace.

        Args:
            label (str, optional): Base identifier for this workplace
            capacity (int, optional): Maximum capacity (default 1000)
            infected (int, optional): Initial infected count
        """
        super().__init__(label, capacity, infected)

    def infect_adult_workplace(self):
        """
        Calculate infection spread among adult individuals in the workplace.

        Note:
            Uses a moderate infection rate of 0.02
        """
        InfectionRules.infect_individuals(
            self.get_adult_individuals(),
            0.02,  # Moderate rate for workplace setting
            self.get_total_infected(),
            len(self.individuals_inside),
            ProvinceMembrane.get_province_membrane_by_label(self.province)
        )

class HospitalMembrane(PlaceMembrane):
    """
    Represents a hospital where infected individuals receive treatment.

    Features higher infection rates due to concentration of infected individuals.
    """

    def __init__(self, label="HP", capacity=1000, infected=0):
        """
        Initialize a hospital.

        Args:
            label (str, optional): Base identifier for this hospital
            capacity (int, optional): Maximum capacity (default 1000)
            infected (int, optional): Initial infected count
        """
        super().__init__(label, capacity, infected)

    def infect_young_hospital(self):
        """
        Calculate infection spread among young individuals in the hospital.

        Note:
            Uses higher infection rate (0.05) due to hospital environment
        """
        InfectionRules.infect_individuals(
            self.get_young_individuals(),
            0.05,  # Higher due to hospital setting
            self.get_total_infected(),
            len(self.individuals_inside),
            ProvinceMembrane.get_province_membrane_by_label(self.province)
        )

    def infect_adult_hospital(self):
        """
        Calculate infection spread among adult individuals in the hospital.

        Note:
            Uses higher infection rate (0.05) due to hospital environment
        """
        InfectionRules.infect_individuals(
            self.get_adult_individuals(),
            0.05,  # Higher due to hospital setting
            self.get_total_infected(),
            len(self.individuals_inside),
            ProvinceMembrane.get_province_membrane_by_label(self.province)
        )

    def infect_elderly_hospital(self):
        """
        Calculate infection spread among elderly individuals in the hospital.

        Note:
            Uses much higher infection rate (0.5) due to hospital environment
            and elderly vulnerability
        """
        InfectionRules.infect_individuals(
            self.get_elderly_individuals(),
            0.5,  # Significantly higher for elderly in hospital
            self.get_total_infected(),
            len(self.individuals_inside),
            ProvinceMembrane.get_province_membrane_by_label(self.province)
        )

class SchoolMembrane(PlaceMembrane):
    """
    Represents a school where young individuals gather for education.
    """

    def __init__(self, label="SC", capacity=1000, infected=0):
        """
        Initialize a school.

        Args:
            label (str, optional): Base identifier for this school
            capacity (int, optional): Maximum capacity (default 1000)
            infected (int, optional): Initial infected count
        """
        super().__init__(label, capacity, infected)

    def infect_young_school(self):
        """
        Calculate infection spread among young individuals in the school.

        Note:
            Uses moderate infection rate (0.03) reflecting school environment
        """
        InfectionRules.infect_individuals(
            self.get_young_individuals(),
            0.03,  # Moderate rate for school setting
            self.get_total_infected(),
            len(self.individuals_inside),
            ProvinceMembrane.get_province_membrane_by_label(self.province)
        )

class CommonAreaMembrane(PlaceMembrane):
    """
    Represents a public area where individuals of all age groups gather.

    Features different infection rates based on age group vulnerability.
    """

    def __init__(self, label="CA", capacity=1000, infected=0):
        """
        Initialize a common area.

        Args:
            label (str, optional): Base identifier for this common area
            capacity (int, optional): Maximum capacity (default 1000)
            infected (int, optional): Initial infected count
        """
        super().__init__(label, capacity, infected)

    def infect_young_ca(self):
        """
        Calculate infection spread among young individuals in common areas.

        Note:
            Uses lower infection rate (0.02) reflecting lower vulnerability
        """
        InfectionRules.infect_individuals(
            self.get_young_individuals(),
            0.02,  # Lower rate for young in common areas
            self.get_total_infected(),
            len(self.individuals_inside),
            ProvinceMembrane.get_province_membrane_by_label(self.province)
        )

    def infect_adult_ca(self):
        """
        Calculate infection spread among adult individuals in common areas.

        Note:
            Uses lower infection rate (0.02) reflecting standard vulnerability
        """
        InfectionRules.infect_individuals(
            self.get_adult_individuals(),
            0.02,  # Standard rate for adults in common areas
            self.get_total_infected(),
            len(self.individuals_inside),
            ProvinceMembrane.get_province_membrane_by_label(self.province))

    def infect_elderly_ca(self):
        """
        Simulate infection spread among elderly individuals in common areas.
        Uses a 20% infection probability factor due to higher vulnerability.
        """
        InfectionRules.infect_individuals(self.get_elderly_individuals(), 0.2,
                                          self.get_total_infected(),
                                          len(self.individuals_inside),
                                          ProvinceMembrane.get_province_membrane_by_label(self.province))

class ICUMembrane(PlaceMembrane):
    """
    Represents an Intensive Care Unit (ICU) environment in the simulation.
    Models the unique infection dynamics of a hospital ICU setting with
    different transmission patterns based on age groups.
    """

    def __init__(self, label="ICU", capacity=500, infected=0):
        """
        Initialize an ICU environment with specified parameters.

        Parameters:
        - label (str): Unique identifier for this ICU location
        - capacity (int): Maximum number of individuals the ICU can accommodate
        - infected (int): Initial count of infected individuals in this ICU
        """
        super().__init__(label, capacity, infected)

    def infect_young_icu(self):
        """
        Simulate infection spread among young individuals in ICU.
        Uses a lower 5% infection probability due to typically stronger immune systems.
        """
        InfectionRules.infect_individuals(self.get_young_individuals(), 0.05,
                                          self.get_total_infected(),
                                          len(self.individuals_inside),
                                          ProvinceMembrane.get_province_membrane_by_label(self.province))

    def infect_adult_icu(self):
        """
         Simulate infection spread among adult individuals in ICU.
         Uses a 5% infection probability factor reflecting standard ICU protocols.
         """
        InfectionRules.infect_individuals(self.get_adult_individuals(), 0.05,
                                          self.get_total_infected(),
                                          len(self.individuals_inside),
                                          ProvinceMembrane.get_province_membrane_by_label(self.province))

    def infect_elderly_icu(self):
        """
        Simulate infection spread among elderly individuals in ICU.
        Uses a high 50% infection probability factor reflecting age-related vulnerability
        and potential comorbidities despite ICU protocols.
        """
        InfectionRules.infect_individuals(self.get_elderly_individuals(), 0.5,
                                          self.get_total_infected(),
                                          len(self.individuals_inside),
                                          ProvinceMembrane.get_province_membrane_by_label(self.province))

class HouseMembrane(PlaceMembrane):
    """
    Models a residential dwelling where individuals live and interact.

    Houses represent the primary living spaces where close contact occurs among
    household members, making them important transmission vectors. House sizes
    vary from 1-6 individuals, with unique infection dynamics compared to public spaces.
    Attributes:
    - label (str): Unique label for the house (e.g., "H1", "H2", etc.)
    - capacity (int): Maximum capacity of the house (fixed at 6)
    - infected (int): Number of infected individuals in the house
    """

    def __init__(self, label = "H", capacity = 6):
        """
        Initialize a HouseMembrane instance.

        Parameters:
        - label (str, optional): Base label for the house (will be appended with number)
        - capacity (int, optional): Maximum capacity of the house (default 6)
        """
        super().__init__(label, capacity)
        self.target_occupants = 0
        self.individuals_inside = []
        self.province = None

    def infect_young_house(self):
        """
    Simulate infection spread among young household members.
    Uses 4% infection probability reflecting close household contact
    but lower susceptibility of youth.

    Returns:
    - Newly infected individuals from this infection event
    """
        return InfectionRules.infect_individuals(self.get_young_individuals(), 0.04,
                                          self.get_total_infected(),
                                          len(self.individuals_inside),
                                          ProvinceMembrane.get_province_membrane_by_label(self.province))

    def infect_adult_house(self):
        """
     Simulate infection spread among adult household members.
     Uses 4% infection probability reflecting typical household transmission rates.

     Returns:
     - Newly infected individuals from this infection event
     """
        return InfectionRules.infect_individuals(self.get_adult_individuals(), 0.04,
                                          self.get_total_infected(),
                                          len(self.individuals_inside),
                                          ProvinceMembrane.get_province_membrane_by_label(self.province))

    def infect_elderly_house(self):
        """
        Simulate infection spread among elderly household members.
        Uses 40% infection probability reflecting high vulnerability
        of elderly in close-contact home environments.

        Returns:
        - Newly infected individuals from this infection event
        """
        return InfectionRules.infect_individuals(self.get_elderly_individuals(), 0.4,
                                          self.get_total_infected(),
                                          len(self.individuals_inside),
                                          ProvinceMembrane.get_province_membrane_by_label(self.province))

class Individual:
    """
    Represents an individual in the simulation.

    Attributes:
    - province_origin (str): Origin province of the individual.
    - province_destination (str): Destination province of the individual.
    - number (int): Unique number identifier for the individual.
    - status (str): Health status of the individual ('Infected', 'Incubation', 'Healthy', 'Hospitalization').
    - age_group (str): Age group of the individual.
    - vaccinated (bool): Whether the individual is vaccinated.
    - vaccination_information (int): Information related to vaccination.

    Methods:
    - progress_infection(): Progress the infection status of the individual.
    - start_infection(): Start the infection period for the individual.
    - __repr__(): Return a string representation of the Individual instance.
    """

    def __init__(self, province_origin, province_destination, number, status, age_group,
                 vaccinated=False, hospitalized=False, ICU=False, vaccination_information=0, v1 = 0 , v1_ino = 0, antiv = 1000, antivesp = 0, phag = 5, inf = 0, symptoms = None):
        """
        Initialize an Individual instance.

        Parameters:
        - province_origin (str): Origin province of the individual.
        - province_destination (str): Destination province of the individual.
        - number (int): Unique number identifier for the individual.
        - status (str): Health status of the individual ('Infected', 'Incubation', 'Healthy', 'Hospitalization').
        - age_group (str): Age group of the individual.
        - vaccinated (bool, optional): Whether the individual is vaccinated.
        - vaccination_information (int, optional): Information related to vaccination.
        -symptoms: there are 4 statuses E1, E2, E3 and E4 based on the symptoms status
        """
        self.house = None
        self.incubation_days_left = 0
        self.infection_days_left = 0
        self.vaccination_days_left = 0
        self.province_origin = province_origin
        self.province_destination = province_destination
        self.number = number
        self.age_group = age_group
        self.hospitalization_days_left = 0
        self.immunity_days_left = 0
        # Viral and immune parameters
        self.v1 = v1  # Active viral load
        self.v1_ino = v1_ino  # Initial viral exposure amount
        self.antiv = antiv  # General antiviral capacity
        self.antivesp = antivesp  # Pathogen-specific immune response
        self.phag = phag  # Phagocytosis efficiency
        self.inf = inf  # Symptom intensity level
        self.hospitalized = hospitalized
        self.ICU = ICU

        # Validate status is within allowed values
        if status not in ['Infected', 'Incubation', 'Healthy', 'Recovered']:
            raise ValueError("Invalid status. Status must be 'Infected', 'Incubation', 'Recovered' or 'Healthy'.")
        self.symptoms = symptoms
        self.status = status
        self.vaccinated = vaccinated
        self.vaccination_information = vaccination_information

        if self.vaccinated:
            self.vaccine_effectiveness, self.vaccination_days_left = BehaviorModel.assign_vaccine_effectiveness_with_duration()

    def assign_to_house(self, house):
        """
        Assign this individual to a specific house.

        Parameters:
        - house (HouseMembrane): The house to assign the individual to
        """
        self.house = house


    def __repr__(self):
        base_repr = super().__repr__()
        # Insert house information before the closing parenthesis
        return base_repr[:-1] + f", house={self.house.label if self.house else None})"

    def progress_infection(self):
        """
        Progress the infection status of the individual based on the remaining days in incubation, infection,
        and hospitalization.

        This method should be used the day after new infections occurred.
        """
        if self.incubation_days_left > 0 and self.status == "Incubation":
            self.incubation_days_left -= 1
            if self.incubation_days_left == 0:
                self.start_infection()

        if self.hospitalization_days_left > 0 and (self.hospitalized or self.ICU):
            self.hospitalization_days_left -= 1
            if self.hospitalization_days_left == 0:
                self.status = "Recovered"
                self.infection_days_left = 0
                self.immunity_days_left = 180
                self.hospitalized = False
                self.ICU = False

        if self.infection_days_left > 0 and self.status == "Infected":
            self.infection_days_left -= 1
            if self.infection_days_left == 0:
                self.status = "Recovered"
                self.immunity_days_left = 180

        if self.vaccination_days_left > 0:
            self.vaccination_days_left -= 1
            if self.vaccination_days_left == 0:
                self.vaccinated = False

        if self.status == 'Recovered' and self.immunity_days_left > 0:
            self.immunity_days_left -= 1
            if self.immunity_days_left == 0:
                self.status = 'Healthy'


    def start_infection(self):
        """
        Start the infection period for the individual.
        """
        #self.infection_days_left = 7
        self.status = "Infected"
        if InfectionRules.VIRAL_LOAD:
            self.v1 = InfectionRules.INFECTION_V1 #Add viral load of infected individual

    def recover(self):
        self.status = "Recovered"
        self.immunity_days_left = 180
        if InfectionRules.VIRAL_LOAD:
            self.antivesp = 0
            self.v1 = 0
            self.inf = 0
            self.symptoms = "E1"

    def __repr__(self):
        """
        Generate detailed string representation of this individual.

        Includes different information based on whether viral load
        modeling is enabled in the simulation.

        Returns:
        - str: Complete description of individual's current state
        """
        if InfectionRules.VIRAL_LOAD:
            return (f"Individual({self.province_origin}, {self.province_destination}, {self.number}, {self.status}, "
                f"{self.age_group}, vaccinated={self.vaccinated}, hospitalized={self.hospitalized}, ICUed={self.ICU}, days left={self.hospitalization_days_left} "
                f"vaccination_information={self.vaccination_information}, v1={self.v1}/1000, v1_ino={self.v1_ino}/1000, "
                f"antiv={self.antiv}/1000, antivesp={self.antivesp}/1000, phag={self.phag}, inf={self.inf}, {self.symptoms}), {self.house}")
        else:
            return (f"Individual({self.province_origin}, {self.province_destination}, {self.number}, {self.status}, "
              f"{self.age_group}, vaccinated={self.vaccinated}, hospitalized={self.hospitalized}, ICUed={self.ICU}, days left={self.hospitalization_days_left} "
              f"vaccination_information={self.vaccination_information}, {self.house}")

