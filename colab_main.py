from simulation import Simulation
from parameters import Parameters
from infection_rules import InfectionRules
from curve_evaluator import CurveEvaluator

CF = [0.0, 0.0001, 0.001, 0.01, 0.1, 1]

def main(caution):

    params = Parameters()
    #params.init_infection_per_province = random.randint(1,100)
    params.apply() # use PARAMETER_BOUNDS for handle random changes

    simulation = Simulation()

    simulation.create_scenario()
    InfectionRules.update_caution_factor(caution)
    print("Starting the simulation from colab_main")

    weekly_csv = simulation.run_simulation(days=100, GPU_idx=0)

    evaluator = CurveEvaluator("lombardy/incidenza_ILI_2025-2026.csv")

    score = evaluator.evaluate(weekly_csv)

    print("Score of the curve: ", score)

if __name__ == "__main__":
    for caution in CF:
        main(caution)
