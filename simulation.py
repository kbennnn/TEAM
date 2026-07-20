import csv
import math
import os
import random
import time

import pandas as pd
import matplotlib.pyplot as plt

from infection_rules import InfectionRules, phag_eating, handle_infection, handle_symptoms
from membrane import (
    ProvinceMembrane,
    SchoolMembrane,
    WorkPlaceMembrane,
    LeisureCenterMembrane,
    CommonAreaMembrane,
    Individual,
    HospitalMembrane,
    ICUMembrane,
    Membrane,
)
from movement_rules import MovementRules
from datetime import datetime

class Simulation:
    """
    The Simulation class represents a simulation scenario with provinces, places, and individuals.

    Attributes:
    - PROVINCES (list): List of province labels.
    - TOTAL_POPULATION (int): Total population for the simulation.
    - VACCINE_COVERAGE (float): Base vaccine coverage for the simulation.
    - INIT_INFECTIONS_PER_PROVINCE (int): Number of initial infections.
    - YOUNG_PERCENTAGE (float): Percentage of young population.
    - ELDERLY_PERCENTAGE (float): Percentage of elderly population.
    - GET_HOME_18 (float): Probability of students getting home at 18.
    - GET_HOME_19 (float): Probability of students getting home at 19.
    - CERTAINTY_PROBABILITY (float): Certainty probability for certain events.
    - SCHOOL_CAPACITY (int): Maximum capacity of schools.
    - WORKPLACE_CAPACITY (int): Maximum capacity of workplaces.

    Methods:
    - create_scenario(): Creates a simulation scenario with provinces, places, and individuals.
    - run_simulation(days=7, hours_per_day=24): Runs the simulation for a specified number of days and hours per day.
    - get_to_school(): Moves students from common area to school.
    - school_infections(): Simulates infections in schools.
    - common_area_infections(): Simulates infections in common areas.
    - leave_school(probability, students_home): Moves students from school to common area based on probability.
    - get_back_home_students(students_to_move): Moves students back to their homes based on a list of students to move.
    - students_to_destination_prov(): Moves students from one province to another based on movement rules.
    - get_infected_individuals(): Returns a list of currently infected individuals.
    - track_infections(): Tracks daily infections and updates the list of currently infected individuals.

    """
    @classmethod
    def update_total_population(cls, new_value: int):
        cls.TOTAL_POPULATION = new_value
    @classmethod
    def update_initial_infection_per_province(cls, new_value: int):
        cls.INIT_INFECTIONS_PER_PROVINCE = new_value
    @classmethod
    def update_vaccine_coverage(cls, new_value: float):
        cls.VACCINE_COVERAGE = new_value
    @classmethod
    def update_quarantine_enabled(cls, new_value: bool):
        cls.QUARANTINE_ENABLED = new_value
    @classmethod
    def update_quarantine_duration(cls, new_value: int):
        cls.QUARANTINE_DURATION = new_value
    @classmethod
    def update_quarantine_start_day(cls, new_value: int):
        cls.QUARANTINE_START_DAY = new_value
    @classmethod
    def update_provinces(cls, new_provinces):
        cls.PROVINCES = new_provinces.copy()  # Make a copy to avoid reference issues

    # Class constants and default parameters
    PROVINCES = Membrane.PROVINCES
    TOTAL_POPULATION = 25000
    VACCINE_COVERAGE = 0.2 #MODIFICATO
    INIT_INFECTIONS_PER_PROVINCE = 83 #MODIFICATO
    YOUNG_PERCENTAGE = 0.2  # Population aged 0-20 years #MODIFICATO
    ELDERLY_PERCENTAGE = 0.3  # Population aged 60+ years #MODIFICATO
    ADULT_PERCENTAGE = 1 - YOUNG_PERCENTAGE - ELDERLY_PERCENTAGE  # Population aged 21-59 years
    GET_HOME_18 = 0.2  # Probability of students returning home at 18:00
    GET_HOME_19 = 0.48  # Probability of students returning home at 19:00
    CERTAINTY_PROBABILITY = 1.0  # Probability representing certainty (100%)
    GET_HOME_ONE_HOUR = 0.4  # Probability of returning home after one hour
    GET_HOME_TWO_HOURS = 0.24  # Probability of returning home after two hours
    QUARANTINE_ENABLED = False  # Whether quarantine policy is active
    QUARANTINE_DURATION = 14  # Number of days quarantine lasts once active
    QUARANTINE_START_DAY = 7  # Days until quarantine policy begins
    MOVEMENT_RESTRICTION_ENABLED = False  # Whether movement restrictions are active
    MOVEMENT_RESTRICTION_DURATION = 14  # Number of days movement restrictions last
    MOVEMENT_RESTRICTION_START_DAY = 7  # Days until movement restrictions begin
    DEATH_REDUCTION_FACTOR = 6  # Factor by which death probability is reduced
    SAME_PROVINCE_PERCENTAGE = 0.8  # Probability of staying in home province



    def __init__(self):
        """
        Initialize a Simulation object.

        Attributes:
        - provinces (list): List to store ProvinceMembrane instances representing provinces in the simulation.
        - currently_infected (list): List containing currently infected individuals.
        - daily_infected (list): List with infected individuals to be updated first every day.
        - prevalence (List): List with daily number of all infected in the simulation.
        - new_daily_cases (list): List to store the count of new daily infection cases.

        """

        self.on_day_completed = None  # Callback for GUI updates
        self.provinces = []
        self.currently_infected = set()
        self.yesterday_infected = 0
        self.new_daily_cases = []
        self.prevalence = []
        self.deaths = []

    # SIMULATION
    def create_scenario(self):
        """
        Initialize the simulation environment with provinces, locations, and population.

        This method:
        1. Creates province objects
        2. Populates provinces with various location types (schools, workplaces, etc.)
        3. Creates and distributes individuals with demographic attributes
        4. Seeds initial infections in each province

        Returns:
            List of initialized Province objects
        """
        num_provinces = len(self.PROVINCES)
        total_population = self.TOTAL_POPULATION

        def get_destination_province(origin_province):
            """
            Determine an individual's destination province based on mobility patterns.

            Args:
                origin_province: The individual's home province

            Returns:
                String identifier of destination province (may be same as origin)
            """
            if random.random() < self.SAME_PROVINCE_PERCENTAGE:  # 80% chance of staying
                return origin_province
            else:
                # For the 20% case, choose a different province
                other_provinces = [p for p in self.PROVINCES if p != origin_province]
                return random.choice(other_provinces)

        # Create provinces
        for province_label in self.PROVINCES:
            province = ProvinceMembrane(label=province_label)
            province.initialize_houses(self.TOTAL_POPULATION)

            # Calculate capacity parameters based on realistic ratios
            SCHOOL_CAPACITY = 300  # Students per school
            WORK_CAPACITY = 200  # Workers per workplace
            ICU_CAPACITY = 1  # Patients per ICU unit (individualized care)
            HOSPITAL_CAPACITY = 150  # Patients per hospital
            LEISURE_CAPACITY = 200  # People per leisure center

            # Calculate number of each location type needed
            # Multiplier 1.6 provides buffer capacity for demographic variation
            NUMBER_OF_SCHOOLS = math.floor(max(1, self.TOTAL_POPULATION * self.YOUNG_PERCENTAGE / Membrane.NUM_OF_PROV / SCHOOL_CAPACITY) * 1.6)
            NUMBER_OF_WORKS = math.floor(max(1, self.TOTAL_POPULATION * self.ADULT_PERCENTAGE / Membrane.NUM_OF_PROV / WORK_CAPACITY) * 1.6)
            NUMBER_OF_ICUS = math.floor(max(1, self.TOTAL_POPULATION / Membrane.NUM_OF_PROV / ICU_CAPACITY / 500))
            NUMBER_OF_HOSPITAL = math.floor(max(1, self.TOTAL_POPULATION / Membrane.NUM_OF_PROV / HOSPITAL_CAPACITY / 20))
            NUMBER_OF_LEISURE = math.floor(max(1, self.TOTAL_POPULATION / Membrane.NUM_OF_PROV / LEISURE_CAPACITY) * 1.6)

            # Create schools, hospitals, leisure centres, and common areas
            for _ in range(NUMBER_OF_SCHOOLS):
                school = SchoolMembrane(capacity=SCHOOL_CAPACITY)
                province.add_place(school)
            for _ in range(NUMBER_OF_WORKS):
                workplace = WorkPlaceMembrane(capacity=WORK_CAPACITY)
                province.add_place(workplace)
            if InfectionRules.ICU_PRESENCE:
                for _ in range(NUMBER_OF_ICUS):
                    ICU = ICUMembrane(capacity=ICU_CAPACITY)
                    province.add_place(ICU)
            for _ in range(NUMBER_OF_HOSPITAL):
                hospital = HospitalMembrane(capacity=HOSPITAL_CAPACITY)
                province.add_place(hospital)
            for _ in range(NUMBER_OF_LEISURE):
                leisure_center = LeisureCenterMembrane(capacity=LEISURE_CAPACITY)
                province.add_place(leisure_center)

            # Add common area with capacity for 50% of province population
            common_area = CommonAreaMembrane(
                capacity=math.floor(self.TOTAL_POPULATION / (len(self.PROVINCES) * 0.5))
            )
            province.add_place(common_area)
            self.provinces.append(province)

        def assign_to_house(individual, province):

            """
            Assign an individual to a house within a province.

            Prioritizes filling houses that already have occupants before using empty ones.

            Args:
                individual: The Individual object to assign
                province: The Province object containing houses

            Returns:
                bool: True if assignment successful, False otherwise
            """

            available_houses = [h for h in province.houses
                                if len(h.individuals_inside) < h.target_occupants]

            if not available_houses:
                print(f"No available houses in province {province.label}")
                return False

            # Choose house with fewest occupants first
            chosen_house = min(available_houses,
                               key=lambda h: len(h.individuals_inside)) #start filling from the empty ones first
            chosen_house.add_individual(individual)
            individual.assign_to_house(chosen_house)
            return True

        # Distribute individuals across provinces with correct age distribution
        young_population = int(self.YOUNG_PERCENTAGE * total_population)
        elderly_population = int(self.ELDERLY_PERCENTAGE * total_population)

        # Assign age groups to individuals
        # Create young individuals (0-20 years)
        for i in range(young_population):
            province_index = i % num_provinces
            province = self.provinces[province_index]
            destination = get_destination_province(province.label)
            if InfectionRules.VIRAL_LOAD:
                individual = Individual(province_origin=province.label, province_destination=destination,
                                        number=i, status="Healthy", age_group="young", v1=0, v1_ino=0, antiv=1000, antivesp=0,
                                        phag=5, inf=0, symptoms = "E1")
            else:
                individual = Individual(province_origin=province.label, province_destination=destination,
                                        number=i, status="Healthy", age_group="young")
            assign_to_house(individual, province)

        # Create elderly individuals (60+ years)
        for i in range(young_population, young_population + elderly_population):
            province_index = i % num_provinces
            province = self.provinces[province_index]
            destination = get_destination_province(province.label)
            if InfectionRules.VIRAL_LOAD:
                individual = Individual(province_origin=province.label, province_destination=destination,
                                        number=i, status="Healthy", age_group="elderly", v1=0, v1_ino=0, antiv=1000,
                                        antivesp=0, phag=5, inf=0, symptoms = "E1")
            else:
                individual = Individual(province_origin=province.label, province_destination=destination,
                                        number=i, status="Healthy", age_group="elderly")
            assign_to_house(individual, province)

        # Create adult individuals (21-59 years)
        for i in range(young_population + elderly_population, total_population):
            province_index = i % num_provinces
            province = self.provinces[province_index]
            destination = get_destination_province(province.label)

            if InfectionRules.VIRAL_LOAD:
                individual = Individual(province_origin=province.label, province_destination=destination,
                                    number=i, status="Healthy", age_group="adult", v1=0, v1_ino=0, antiv=1000, antivesp=0,
                                    phag=5,  inf=0, symptoms = "E1")
            else:
                individual = Individual(province_origin=province.label, province_destination=destination,
                                        number=i, status="Healthy", age_group="adult")
            assign_to_house(individual, province)

        # Introduce initial infections
        for province in self.provinces:
            infected_individuals = set()
            available_individuals = set()

            for houses in province.houses: # Get all the individuals from houses
                for individual in houses.individuals_inside:
                    available_individuals.add(individual)

            for _ in range(self.INIT_INFECTIONS_PER_PROVINCE):
                available_individuals_list = list(available_individuals)
                if available_individuals:
                    individual = random.choice(available_individuals_list)
                    individual.start_infection()
                    infected_individuals.add(individual)
                    available_individuals.remove(individual)

    def run_simulation(self, days=7, hours_per_day=24):
        """
        Execute the complete simulation for the specified duration.

        This method:
        1. Sets up data collection and reporting infrastructure
        2. Runs the day/hour nested loop to simulate time progression
        3. For each time step, executes movement, infection, and intervention logic
        4. Tracks and reports key metrics
        5. Creates visualization outputs

        Args:
            days (int): Number of days to simulate
            hours_per_day (int): Number of hours per simulated day
        """

        # Create a unique timestamp for this simulation run
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Set up output directory and CSV file
        directory = "simulations"
        os.makedirs(directory, exist_ok=True)
        # Create filename with descriptive parameters
        csv_filename = (
            f"{directory}/simulation_{self.TOTAL_POPULATION}_{len(self.PROVINCES)}_{days}___"
            f"{current_datetime}.csv"
        )
        # Initialize the CSV file with headers
        with open(csv_filename, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)

            csv_writer.writerow(["Day", "Variation of Infected", "Prevalence", "Deaths", "Seconds", "classS", "classE", "classI", "classT3", "classT4", "classR"])

            # Temporary tracking lists for daily activities
            students_home_18 = []  # Students who go home at 18:00
            elderly_outside = []   # Elderly people out of their homes
            workers = []           # Working adults


            # Main simulation loop - days
            for day in range(1, days + 1):
                print("--- Day:", day, "---")
                start_time = time.time()

                # Check if today is a quarantine day
                if (self.QUARANTINE_ENABLED and self.QUARANTINE_START_DAY <= 0 <= self.QUARANTINE_DURATION):
                    print("Lockdown day")
                # Update infection progression for all individuals (except day 1)
                if day != 1:
                    for p in self.provinces:
                        if InfectionRules.VIRAL_LOAD:
                            p.reduce_all_hospital_day()  # Reduce hospitalization counters
                            p.reduce_all_vaccine_day()   # Update vaccine effectiveness
                        else:
                            p.trigger_infection_progress()  # Simple state progression
                else:
                    # First day initialization and reporting
                    print("prudence parameter of", InfectionRules.PRUDENCE_PARAMETER,
                          " i have a factor of * ", (1 - InfectionRules.PRUDENCE_PARAMETER)**2)
                    self.currently_infected = self.get_infected_individuals()
                    self.yesterday_infected = len(self.currently_infected)

                # Update quarantine timing counters
                self.QUARANTINE_START_DAY -= 1
                if self.QUARANTINE_START_DAY <= 0:
                    self.QUARANTINE_DURATION -= 1

                # Main simulation loop - hours within day
                for hour in range(1, hours_per_day + 1):

                    # ADDED: updates cache every hour
                    for p in self.provinces:
                        p.update_cache()

                    # Handle quarantine activation (first hour of first quarantine day)
                    if (self.QUARANTINE_ENABLED and self.QUARANTINE_START_DAY <= 0 <= self.QUARANTINE_DURATION):
                     # First time entering quarantine - move everyone home
                        if self.QUARANTINE_START_DAY == 0 and hour == 1:
                            print("people in houses before lockdown: ", len(self.get_house_individuals()))
                            self.get_back_home_elderly(elderly_outside)
                            self.get_back_home_workers(self.leave_workplace())
                            self.get_back_home_students(self.leave_school(1))
                            print("first day of lockdown, everyone should be home")
                            print("number of people in houses: ", len(self.get_house_individuals()))
                    # Normal activity patterns - weekday (Mon-Fri)
                    elif 1 <= day % 7 <= 5:         #weekday
                        # Daily routine management by hour
                        if hour == 1:
                            all_home1 = self.leave_leisure_all(self.CERTAINTY_PROBABILITY, self.CERTAINTY_PROBABILITY, 0)
                            self.get_back_home_all(all_home1)
                        if hour == 6:
                            self.workers_to_destination_prov()  # Adults to common areas
                        if hour == 7:
                            self.students_to_destination_prov()
                            self.get_to_workplace()  # workers to workplaces
                        if hour == 8:
                            self.workplace_infections()  # infections in workplaces
                            self.get_to_school()  # Students to schools
                            elderly_outside.extend(self.elderly_to_destination_prov())
                        if 9 <= hour < 17:
                            self.trigger_vaccination_progress(self.VACCINE_COVERAGE)
                            self.workplace_infections()  # infections in workplaces
                            self.school_infections()  # Infections in schools
                            elderly_outside.extend(self.elderly_to_destination_prov())
                            self.get_to_leisure_elderly(0.04)
                            self.get_back_home_elderly(elderly_outside)
                        if hour == 17:
                            self.leave_leisure_elderly(self.CERTAINTY_PROBABILITY)
                            students_home_18 = self.leave_school(self.GET_HOME_18)
                            students_home_19 = self.leave_school(self.GET_HOME_19)
                            students_home_20 = self.leave_school(self.CERTAINTY_PROBABILITY)
                            workers = self.leave_workplace()
                            elderly_outside.extend(self.elderly_to_destination_prov())
                            self.get_back_home_elderly(elderly_outside)
                        if hour == 18:
                            self.get_back_home_students(students_home_18)
                            elderly_outside.extend(self.elderly_to_destination_prov())
                            self.get_back_home_elderly(elderly_outside)
                        if hour == 19:
                            self.get_back_home_all(self.get_all_individuals())
                        if hour == 21:
                            self.get_to_leisure_all(0.15, 0.08, 0)
                        if hour == 22:
                            all_home22 = self.leave_leisure_all(0.25, 0.25, 0)
                            self.get_back_home_all(all_home22)
                        if hour == 23:
                            all_home23 = self.leave_leisure_all(0.4, 0.4, 0)
                            self.get_back_home_all(all_home23)
                        if hour == 24:
                            all_home24 = self.leave_leisure_all(self.CERTAINTY_PROBABILITY, self.CERTAINTY_PROBABILITY, 0)
                            self.get_back_home_all(all_home24)
                    else: # Weekend activity patterns (Sat-Sun)
                        if hour == 1:
                            all_home1 = self.leave_leisure_all(0.15, 0.15, 0)
                            self.get_back_home_all(all_home1)
                        if hour == 2:
                            all_home2 = self.leave_leisure_all(0.2, 0.2, 0)
                            self.get_back_home_all(all_home2)
                        if hour == 3:
                            all_home3 = self.leave_leisure_all(0.3, 0.3, 0)
                            self.get_back_home_all(all_home3)
                        if hour == 4:
                            all_home4 = self.leave_leisure_all(self.CERTAINTY_PROBABILITY, self.CERTAINTY_PROBABILITY, 0)
                            self.get_back_home_all(all_home4)
                        if hour == 8:
                            self.get_to_common_all(0.17, 0.36, 0.18)
                        if hour == 9:
                            self.get_to_leisure_all(0.15, 0.08, 0.08)
                        if hour == 11:
                            all_home11 = self.leave_leisure_all(0.4, 0.4, 0.4)
                            self.get_back_home_all(all_home11)
                        if hour == 12:
                            all_home12 = self.leave_leisure_all(self.CERTAINTY_PROBABILITY, self.CERTAINTY_PROBABILITY, self.CERTAINTY_PROBABILITY)
                            self.get_back_home_all(all_home12)
                            self.leave_common_all()
                        if hour == 15:
                            self.get_to_common_all(0.2, 0.4, 0.15)
                        if hour == 16:
                            self.get_to_leisure_all(0.1, 0.17, 0.04)
                        if hour == 17:
                            all_home17 = self.leave_leisure_all(0.15, 0.15, 0.1)
                            self.get_back_home_all(all_home17)
                        if hour == 18:
                            all_home18 = self.leave_leisure_all(0.25, 0.25, self.CERTAINTY_PROBABILITY)
                            self.get_back_home_all(all_home18)
                        if hour == 19:
                            all_home19 = self.leave_leisure_all(self.CERTAINTY_PROBABILITY, self.CERTAINTY_PROBABILITY, 0)
                            self.get_back_home_all(all_home19)
                            self.leave_common_all()
                        if hour == 22:
                            self.get_to_leisure_all(0.33, 0.1, 0)
                        if hour == 23:
                            all_home23 = self.leave_leisure_all(0.05, 0.05, 0)
                            self.get_back_home_all(all_home23)
                        if hour == 24:
                            all_home24 = self.leave_leisure_all(0.1, 0.1, 0)
                            self.get_back_home_all(all_home24)


                    # Hourly processes that happen regardless of day type or quarantine
                    self.discharge_from_hospital()  # Process hospital discharges (includes ICUs)
                    self.check_for_hospitalization()  # Check if any infected need hospitalization
                    self.house_infections(day, hour)  # Process household transmission

                    if InfectionRules.ICU_PRESENCE:
                        self.check_for_ICU()  # Check if any hospitalized need ICU

                    self.common_area_infections(day, hour)  # Process transmission in common areas
                    self.leisure_infections(day, hour)  # Process transmission in leisure venues
                    self.check_for_death(self.currently_infected)  # Check for mortality events

                    for p in self.provinces: #Update the status of all individuals
                        p.update_all_status()
                    self.currently_infected = self.get_infected_individuals()

                    if InfectionRules.VIRAL_LOAD:
                        # The order of rules is managed by the priority value of the rule. Keep attention!
                        phag_eating(self.get_v1_ino_individuals()) # phag eat armless v1_ino
                        handle_infection(self.currently_infected, InfectionRules.V1_GROWTH_PROB, InfectionRules.ANTIV_KILL_PROB) #function for virus management in individuals
                        handle_symptoms(self.currently_infected) #function for symptoms management in individuals

                # End of day processing
                # --- DAILY ICU MONITORING ---
                if InfectionRules.ICU_PRESENCE:
                    # Calculate aggregate capacity across all provinces
                    total_icu_cap = sum(icu.capacity for p in self.provinces for icu in p.ICUs)
                    total_icu_occ = sum(len(icu.individuals_inside) for p in self.provinces for icu in p.ICUs)

                    if total_icu_cap > 0:
                        occupancy_rate = total_icu_occ / total_icu_cap
                        if occupancy_rate >= 0.9:
                            alert_msg = f"!!! ALERT - Day {day}: ICU capacity at {occupancy_rate*100:.1f}%. Action required!"
                            print(alert_msg) # Terminal output

                            # Trigger GUI notification
                            if self.on_day_completed:
                                # We pass "ALERT" as the first argument to bypass standard formatting
                                self.on_day_completed("ALERT", alert_msg, "", "", "")



                self.track_infections()
                if self.new_daily_cases[day - 1] == 0:
                    print("No new infections.")

                # Existing end-of-day processing follows:
                #self.track_infections()

                # Calculate and report timing information
                end_time = time.time()
                elapsed_time = end_time - start_time
                elapsed_time = round(elapsed_time, 2)

                # Report daily statistics
                print("Variation of Infected:", self.new_daily_cases[day - 1])
                print("Prevalence:", self.prevalence[day - 1])
                print("Deaths:", len(self.deaths))
                print("Seconds:", elapsed_time)

                # Calculate SEJIRS model class populations
                class_S = 0  # Susceptible
                class_E = 0  # Exposed
                class_I = 0  # Infected
                class_J3 = 0  # Hospitalized
                class_J4 = 0  # ICU
                class_R = 0  # Recovered
                individuals = self.get_all_individuals()
                for individual in individuals:
                    if individual.status == "Healthy":
                        class_S += 1
                    elif individual.status == "Incubation":
                        class_E += 1
                    elif individual.status == "Infected" and individual.symptoms == "E3":
                        class_J3 += 1
                    elif individual.status == "Infected" and individual.symptoms == "E4":
                        class_J4 += 1
                    elif individual.status == "Infected":
                        class_I += 1
                    elif individual.status == "Recovered":
                        class_R += 1
                print("SEJIRS class: ", class_S, class_E, class_I, class_J3, class_J4, class_R)
                # Write daily data to CSV
                csv_writer.writerow(
                    [day, self.new_daily_cases[day - 1],
                     self.prevalence[day - 1], len(self.deaths), elapsed_time, class_S, class_E, class_I, class_J3, class_J4, class_R]
                )

                # At the end of each day, notify GUI if callback exists
                if self.on_day_completed:
                    self.on_day_completed(
                        day,
                        self.new_daily_cases[day - 1],
                        self.prevalence[day - 1],
                        len(self.deaths),
                        elapsed_time
                    )


        # Post-simulation reporting and visualization
        print("Simulation results saved to:", csv_filename)
        # Generate visualization graphs from simulation data
        data = pd.read_csv(csv_filename)

        # Create weekly aggregated CSV
        weekly_data = data.iloc[:len(data) - len(data) % 7].copy()
        weekly_data["Week"] = (
            weekly_data["Day"] // 7
        )

        weekly_data = weekly_data.groupby("Week").agg({
            "Variation of Infected": "sum",
            "Prevalence": "mean",
            "Deaths": "last",
            "Seconds": "sum",
            "classS": "mean",
            "classE": "mean",
            "classI": "mean",
            "classT3": "mean",
            "classT4": "mean",
            "classR": "mean"
        }).reset_index()

        weekly_data["Week"] = weekly_data["Week"] + 1

        weekly_csv_filename = csv_filename.replace(
            ".csv",
            "_weekly.csv"
        )

        weekly_data.to_csv(
            weekly_csv_filename,
            index=False
        )
        print("Weekly results saved to:", weekly_csv_filename)


        output_dir = os.path.join(os.path.dirname(csv_filename), "graphs")
        os.makedirs(output_dir, exist_ok=True)  # Creates folder if does not exist

        # Calculate percentages for better comparability
        data["Prevalence (%)"] = (data["Prevalence"] / self.TOTAL_POPULATION) * 100
        data["Variation of Infected (%)"] = (data["Variation of Infected"] / self.TOTAL_POPULATION) * 100
        data["Deaths (%)"] = (data["Deaths"] / self.TOTAL_POPULATION) * 100


        # Line plots
        def create_line_chart(x, y, title, x_label, y_label, base_filename, color):
            simulation_name = os.path.splitext(os.path.basename(csv_filename))[0]  # File name without extension
            filename = f"{base_filename}_{simulation_name}.png"  # Graph name
            output_file = os.path.join(output_dir, filename)  # Full file path
            plt.figure(figsize=(10, 6))
            plt.plot(x, y, color=color, linewidth=2)  # Specify the color
            plt.title(title, fontsize=16)
            plt.xlabel(x_label, fontsize=14)
            plt.ylabel(y_label, fontsize=14)
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.xticks(fontsize=12, rotation=45)
            plt.yticks(fontsize=12)
            plt.tight_layout()
            plt.savefig(output_file)
            plt.close()

        # Line Chart 1: Day vs Prevalence
        create_line_chart(
            x=data["Day"],
            y=data["Prevalence (%)"],
            title="Prevalence Over Days (%)",
            x_label="Days",
            y_label="Prevalence (%)",
            base_filename="prevalence_line_chart",
            color="red"
        )

        # Line Chart 2: Day vs Variation of Infected
        create_line_chart(
            x=data["Day"],
            y=data["Variation of Infected (%)"],
            title="Variation of Infected Over Days (%)",
            x_label="Days",
            y_label="Variation of Infected (%)",
            base_filename="variation_of_infected_line_chart",
            color="blue"
        )

        # Line Chart 3: Day vs Deaths
        create_line_chart(
            x=data["Day"],
            y=data["Deaths (%)"],
            title="Deaths Over Days (%)",
            x_label="Days",
            y_label="Deaths (%)",
            base_filename="deaths_line_chart",
            color="green"
        )


    def students_to_destination_prov(self):
        """
        Move students between provinces based on movement rules.

        Returns:
            int: Total number of students that moved between provinces
        """
        total_move_count = 0
        for origin_province in self.provinces:
            for destination_province in self.provinces:
                if origin_province.label != destination_province.label:
                    total_move_count += MovementRules.move_students_between_provinces(origin_province.label, destination_province.label)
        return total_move_count

    def workers_to_destination_prov(self):
        """
        Move workers between provinces based on movement rules.

        Note: Unlike students, this method doesn't return a count of moved workers.
        """
        for origin_province in self.provinces:
            for destination_province in self.provinces:
                if origin_province.label != destination_province.label:
                    MovementRules.move_workers_between_provinces(origin_province.label, destination_province.label)

    def elderly_to_destination_prov(self):
        """
        Move elderly from one province to another based on movement rules.

        Returns:
        - list: List of return hours for the moved elderly individuals.
        """
        return_hours = []
        for origin_province in self.provinces:
            for destination_province in self.provinces:
                #if origin_province.label != destination_province.label: # Commented condition - all provinces considered
                return_hours.extend(MovementRules.move_elderly_between_provinces(origin_province.label, destination_province.label))
        return return_hours


    # ENTER PLACE MEMBRANES
    def get_to_school(self):
        """
        Move students from houses and common areas to schools with 100% probability.
        """
        for province in self.provinces:
            for place in province.common_areas + province.houses:
                students = place.get_young_individuals()
                for student in students:
                    if self.can_move(student, base_probability=1):
                        for school in province.schools:
                            if self.move_individual(student, place, school):
                                break


    def get_to_leisure_elderly(self, prob_of_moving):
        """
        Move elderly individuals from houses and common areas to leisure centers.

        Args:
            prob_of_moving (float): Probability (0-1) of an elderly individual going to a leisure center
        """
        for province in self.provinces:
            for place in province.common_areas + province.houses:
                elderly = place.get_elderly_individuals()
                for elder in elderly:
                    if self.can_move(elder, prob_of_moving):
                        for leisure_center in province.leisure_centers:
                            if self.move_individual(elder, place, leisure_center):
                                break


    def get_to_workplace(self):
        """
        Move workers from houses and common areas to workplaces with 100% probability.
        """
        for province in self.provinces:
            for place in province.common_areas + province.houses:
                workers = place.get_adult_individuals()
                for worker in workers:
                    if self.can_move(worker, base_probability=1):
                        for workplace in province.workplaces:
                            if self.move_individual(worker, place, workplace):
                                break

    # LEAVE PLACE MEMBRANES
    def leave_school(self, probability):
        """
        Move students from schools to the common area based on a specified probability.

        Parameters:
        - probability (float): Probability of students moving to the common area (0-1).

        Returns:
        - list: List of students who go home at a certain hour.
        """
        students_home = []
        for province in self.provinces:
            for school in province.schools:
                for student in school.individuals_inside.copy():
                    if random.uniform(0, 1) < probability:
                        school.remove_individual(student)
                        # Add to local common area
                        common_area = province.common_areas[0]
                        common_area.add_individual(student)
                        students_home.append(student)
        return students_home

    def leave_workplace(self):
        """
        Move workers from workplaces to the common area.

        Returns:
        - list: List of workers who leave their workplaces.
        """
        workers_home = []
        for province in self.provinces:
            for workplace in province.workplaces:
                for worker in workplace.individuals_inside.copy():
                    workplace.remove_individual(worker)
                    # Add to local common area
                    common_area = province.common_areas[0]
                    common_area.add_individual(worker)
                    workers_home.append(worker)
        return workers_home

    def leave_leisure_all(self, prob_young, prob_adult, prob_elderly):
        """
        Move individuals of all age groups from leisure centers to common areas.

        Args:
            prob_young (float): Probability (0-1) of young individuals leaving
            prob_adult (float): Probability (0-1) of adult individuals leaving
            prob_elderly (float): Probability (0-1) of elderly individuals leaving

        Returns:
            list: Individuals who left leisure centers
        """
        individual_home = []
        for province in self.provinces:
            for leisure_center in province.leisure_centers:
                individuals = leisure_center.get_all_individuals()
                for individual in individuals:
                    probability = 0
                    if individual.age_group == "young":
                        probability = prob_young
                    elif individual.age_group == "adult":
                        probability = prob_adult
                    elif individual.age_group == "elderly":
                        probability = prob_elderly
                    if random.uniform(0, 1) < probability:
                        leisure_center.remove_individual(individual)
                        common_area = province.common_areas[0]
                        common_area.add_individual(individual)
                        individual_home.append(individual)
        return individual_home

    def get_to_leisure_all(self, prob_young, prob_adult, prob_elderly):
        """
    Move individuals of all age groups from houses and common areas to leisure centers.

    Args:
        prob_young (float): Probability (0-1) of young individuals going to leisure centers
        prob_adult (float): Probability (0-1) of adult individuals going to leisure centers
        prob_elderly (float): Probability (0-1) of elderly individuals going to leisure centers
    """
        for province in self.provinces:
            for place in province.common_areas + province.houses:
                individuals = place.get_all_individuals()
                for individual in individuals:
                    probability = 0
                    if individual.age_group == "young":
                        probability = prob_young
                    elif individual.age_group == "adult":
                        probability = prob_adult
                    elif individual.age_group == "elderly":
                        probability = prob_elderly
                    if self.can_move(individual, probability):
                        for leisure_center in province.leisure_centers:
                            if self.move_individual(individual, place, leisure_center):
                                break

    def get_to_common_all(self, prob_young, prob_adult, prob_elderly):
        """
        Move individuals from houses to common areas based on age-specific probabilities.

        Args:
            prob_young (float): Probability (0-1) of young individuals going to common areas
            prob_adult (float): Probability (0-1) of adult individuals going to common areas
            prob_elderly (float): Probability (0-1) of elderly individuals going to common areas
        """
        for province in self.provinces:
            for house in province.houses:
                individuals = house.get_all_individuals()
                for individual in individuals:
                    probability = 0
                    if individual.age_group == "young":
                        probability = prob_young
                    elif individual.age_group == "adult":
                        probability = prob_adult
                    elif individual.age_group == "elderly":
                        probability = prob_elderly
                    if self.can_move(individual, probability):
                        for common_area in province.common_areas:
                            if self.move_individual(individual, house, common_area):
                                break

    def leave_common_all(self):
        """
        Collect all individuals in common areas and send them back home.

        Returns:
            list: Individuals who were in common areas
        """
        individual_home = []
        for province in self.provinces:
            for common_area in province.common_areas:
                individuals = common_area.get_all_individuals()
                for individual in individuals:
                    individual_home.append(individual)
        self.get_back_home_workers(individual_home)


    def leave_leisure_elderly(self, probability):
        """
        Move elders from leisure centers to the common area.

        Returns:
        - list: List of workers who leave leisure centers.
        """
        elderly_home = []
        for province in self.provinces:
            for leisure_center in province.leisure_centers:
                elderly = leisure_center.get_elderly_individuals()
                for elder in elderly:
                    if random.uniform(0, 1) < probability:
                        leisure_center.remove_individual(elder)
                        common_area = province.common_areas[0]
                        common_area.add_individual(elder)
                        elderly_home.append(elder)
        return elderly_home

    def get_back_home_all(self, individuals_to_move):
        """
    Move specified individuals back to their homes across all provinces.

    Args:
        individuals_to_move (list): Individuals to move back home
    """
        for province in self.provinces:
            province: ProvinceMembrane
            MovementRules.get_home_students(province, individuals_to_move)


    def get_back_home_students(self, students_to_move):
        """
        Move students back to their own province of origin.

        Parameters:
        - students_to_move (list): List of students to move back to their own province of origin.
        """
        for province in self.provinces:
            province: ProvinceMembrane
            MovementRules.get_home_students(province, students_to_move)

    def get_back_home_workers(self, workers):
        """
        Move workers back to their own province of origin.

        Parameters:
        - workers (list): List of workers to move back to their own province of origin.
        """
        for province in self.provinces:
            province: ProvinceMembrane
            # Using get_home_students for workers as well
            MovementRules.get_home_students(province, workers)

    def get_back_home_elderly(self, elderly_outside):
        """
        Move elderly individuals back home after a certain number of hours outside.

        Parameters:
        - elderly_outside (list): List of tuples with (individual_number, hours_left) for elderly individuals outside.

        """
        individuals_to_move = []

        # Process the list of tuples
        index = 0
        while index < len(elderly_outside):
            individual_number, hours_left = elderly_outside[index]
            if hours_left == 1:
                # Find the Individual object based on individual_number
                individual_to_move = None
                for province in self.provinces:
                    for individual in province.common_areas[0].individuals_inside:
                        if individual.number == individual_number:
                            individual_to_move = individual
                            break
                    if individual_to_move:
                        break

                if individual_to_move:
                    # If hours_left is 1, append the Individual to the list
                    individuals_to_move.append(individual_to_move)

                    # Remove the tuple from the list
                    del elderly_outside[index]
                    continue

            # Decrease the remaining tuples second argument by one
            elderly_outside[index] = (individual_number, hours_left - 1)
            index += 1

        # Move the elderly individuals back home
        for province in self.provinces:
            province: ProvinceMembrane
            MovementRules.get_home_students(province, individuals_to_move)


    def get_house_individuals(self):
        """
        Get a list of all individuals in the house.

        Returns:
        - list: List of all Individual instances.

        """
        individuals_list = []

        for province in self.provinces:
            for place in province.houses:
                for individual in place.individuals_inside:
                    if individual not in individuals_list:
                        individuals_list.append(individual)
        return individuals_list

    def get_infected_individuals(self):
        """
        Get a list of all infected individuals from all places across all provinces.
        Individuals are considered infected if their status is "Infected" or viral load > 0.

        Returns:
            list: All infected individuals
        """
        infected_list = []
        for province in self.provinces:
            for place in province.schools + province.common_areas + province.workplaces + province.leisure_centers + province.hospitals + province.ICUs + province.houses:
                for individual in place.individuals_inside:
                    if (individual.status == "Infected" or individual.v1 > 0) and individual not in infected_list:
                        infected_list.append(individual)
        return infected_list

    def get_v1_ino_individuals(self):
        """
        Get a list of individuals with v1_ino.

        Returns:
        - list: List of Individual instances with v1_ino.

        """
        v1_ino_list = []

        for province in self.provinces:
            for place in province.schools + province.common_areas + province.workplaces + province.leisure_centers + province.hospitals + province.ICUs + province.houses:
                for individual in place.individuals_inside:
                    if individual.v1_ino > 0 and individual not in v1_ino_list:
                        v1_ino_list.append(individual)
        return v1_ino_list

    def get_all_individuals(self):
        """
        Get a list of all individuals in the simulation across all provinces and places.
        Ensures each individual is only included once in the list.

        Returns:
            list: All individuals in the simulation
        """
        all_list = []
        for province in self.provinces:
            for place in province.schools + province.common_areas + province.workplaces + province.leisure_centers + province.hospitals + province.ICUs + province.houses:
                for individual in place.individuals_inside:
                    if individual not in all_list:
                        all_list.append(individual)
        return all_list

    def school_infections(self):
        """
        Simulate infections in schools.

        """
        for province in self.provinces:
            for school in province.schools:
                school.infect_young_school()

    def common_area_infections(self, day, hour):
        """
        Simulate infections in common areas.

        """
        if (7 < hour < 22) or ((1 <= day % 7 <= 5) and (5 < hour < 8)):
            for province in self.provinces:
                for common_area in province.common_areas:
                    common_area.infect_young_ca()
                    common_area.infect_adult_ca()
                    common_area.infect_elderly_ca()

    def workplace_infections(self):
        """
        Simulate infections in workplaces.

        """
        for province in self.provinces:
            for workplace in province.workplaces:
                workplace.infect_adult_workplace()

    def house_infections(self, day, hour): #OLD house infection
        """
        Simulate infections in houses.
        """
        if ((1 <= day % 7 <= 5) and (8 <= hour <= 18)) or (1 <= hour <= 6) or (hour % 2 == 1): #weekday and between 8 and 19, or night, or odd hour
            return
        else:
            number_of_infected = 0
            for province in self.provinces:
                for house in province.houses:
                    number_of_infected += house.infect_young_house()
                    number_of_infected += house.infect_adult_house()
                    number_of_infected += house.infect_elderly_house()


    def leisure_infections(self, day, hour):
        """
        Simulate infections in leisure centers

        """
        if 1 <= day % 7 <= 5:
            if 1 <= hour <= 8:
                return
        else:
            if (4 <= hour <= 8) or (19 <= hour <= 21):
                return

        for province in self.provinces:
            for leisure_center in province.leisure_centers:
                if 1 <= day % 7 <= 5:
                    #settimana
                    if 9 <= hour <= 21:
                        leisure_center.infect_elderly_lc()
                    if 21 <= hour <= 24:
                        leisure_center.infect_young_lc(hour)
                        leisure_center.infect_adult_lc(hour)
                else:
                    #weekend
                    if 9 <= hour <= 16:
                        leisure_center.infect_elderly_lc()
                    if (1 <= hour <= 3) or (9 <= hour <= 11) or (16 <= hour <= 18) or (22 <= hour <= 24):
                        leisure_center.infect_young_lc(hour)
                        leisure_center.infect_adult_lc(hour)

    # TRACKING METHODS
    def track_infections(self):
        """
        Track daily infections and update the list of currently infected individuals.

        """
        self.new_daily_cases.append(len(set(self.currently_infected)) - self.yesterday_infected)
        self.prevalence.append(len(self.currently_infected))
        self.yesterday_infected = len(self.currently_infected)

    # HOSPITALIZATION
    def check_for_hospitalization(self):
        """
        Check for hospitalization based on the capacity of hospitals.

        """
        for province in self.provinces:
            for place in province.workplaces + province.schools + province.common_areas + province.leisure_centers + province.houses:
                for individual in place.individuals_inside:
                    available_hospital = next((hospital for hospital in province.hospitals if len(hospital.individuals_inside) < hospital.capacity), None)
                    if available_hospital:
                        place.check_hospitalization(individual, available_hospital)

    def check_for_ICU(self):
        """
        Check for hospitalization based on the capacity of hospitals.

        """
        for province in self.provinces:
            for place in province.workplaces + province.schools + province.common_areas + province.leisure_centers + province.hospitals + province.houses:
                for individual in place.individuals_inside:
                    available_ICU = next((ICU for ICU in province.ICUs if len(ICU.individuals_inside) < ICU.capacity), None)
                    if available_ICU:
                        place.check_ICU(individual, available_ICU)



    def discharge_from_hospital(self):
        """
        Discharge individuals from hospitals and ICUs who have recovered.

        """
        for province in self.provinces:
            for hospital in province.hospitals + province.ICUs:
                for individual in hospital.individuals_inside.copy():
                    if individual.status == "Recovered":
                        hospital.remove_individual(individual)
                        MovementRules.get_home_from_hospital(individual)

    # VACCINATION RELATED METHODS
    def trigger_vaccination_progress(self, vaccination_coverage):
        """
        Trigger vaccination progress in the simulation.

        Parameters:
        - vaccination_coverage (float): Maximum vaccination coverage for the simulation.

        """
        total_vaccinated_fraction = sum(province.total_vaccinated() for province in self.provinces)

        remaining_vaccination_coverage = vaccination_coverage - total_vaccinated_fraction
        if remaining_vaccination_coverage <= 0:
            return

        for province in self.provinces:
            remaining_vaccination_coverage = vaccination_coverage - total_vaccinated_fraction

            if remaining_vaccination_coverage <= 0:
                break

            fraction_to_vaccinate = min(remaining_vaccination_coverage, 1.0)
            province.vaccinate_population(fraction_to_vaccinate) #errore qui
            total_vaccinated_fraction += fraction_to_vaccinate

    def check_for_death(self, individuals):
        for individual in individuals:
            if InfectionRules.VIRAL_LOAD:
                if individual.symptoms == "E3":
                    death_probability = 0.0001 # Is 0.0005 in paper and Is 0.00025 in rules.xml
                elif individual.symptoms == "E4":
                    if InfectionRules.ICU_PRESENCE:
                        if individual.ICU:
                            death_probability = 0.0006 # Is 0.003 in paper and Is 0.002 in rules.xml
                        else:
                            death_probability = 0.0012 # Is 0.006 in paper and Is 0.004 in rules.xml
                    else:
                        death_probability = 0.0012 # Is 0.006 in paper and Is 0.004 in rules.xml
                else:
                    death_probability = 0
            else:
                death_probability = 0.001 # Was 0.005 in MVT

            death_probability = death_probability / self.DEATH_REDUCTION_FACTOR
            if individual.status == "Infected" and random.uniform(0, 1) < death_probability:
                individual.status = "Deceased"
                self.deaths.append(individual)

    #helper methods for optimization
    def can_move(self, individual, base_probability):
        if hasattr(individual, "symptoms"):
            if individual.symptoms in ["E3", "E4"]:
                return False
            if individual.symptoms == "E2":
                base_probability *= (1 - InfectionRules.PRUDENCE_PARAMETER)**2
        return base_probability >= random.random()

    def move_individual(self, individual, origin, destination):
        if len(destination.individuals_inside) < destination.capacity:
            origin.remove_individual(individual)
            destination.add_individual(individual)
            return True
        return False

