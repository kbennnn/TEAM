from simulation import Simulation

def main():

    simulation = Simulation()


    simulation.create_scenario()
    print("Starting the simulation from colab_main")


    simulation.run_simulation(days=50, GPU_idx=0)

if __name__ == "__main__":
    main()