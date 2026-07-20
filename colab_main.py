from simulation import Simulation
from curve_evaluator import CurveEvaluator

def main():

    simulation = Simulation()


    simulation.create_scenario()
    print("Starting the simulation from colab_main")


    weekly_csv = simulation.run_simulation(days=50, GPU_idx=0)

    evaluator = CurveEvaluator("lombardy/incidenza_ILI_2025-2026.csv")

    score = evaluator.evaluate(weekly_csv)

    print("Score of the curve: ", score)

if __name__ == "__main__":
    main()
