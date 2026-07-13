from simulation import Simulation

def main():

    simulation = Simulation()


    simulation.create_scenario()
    print("Starting the simulation from colab_main")


    simulation.run_simulation(days=10)

if __name__ == "__main__":
    main()