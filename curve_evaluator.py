import pandas as pd
import numpy as np


class CurveEvaluator:

    def __init__(self, target_csv):
        """Load the targer curve for the lombardy"""
        self.target = pd.read_csv(target_csv)

    def evaluate(self, simulation_csv):
        """evalulate the simulation with a score"""
        simulation = pd.read_csv(simulation_csv)

        sim = simulation["Variation of Infected"].to_numpy()
        real = self.target["incidenza"].to_numpy()

        n = min(len(sim), len(real))

        sim = sim[:n]
        real = real[:n]

        return self.mse(sim, real)

    @staticmethod
    def mse(sim, real):
        return np.mean((sim - real) ** 2)