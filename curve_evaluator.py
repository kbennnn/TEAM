import pandas as pd
import numpy as np


class CurveEvaluator:

    def __init__(self, target_csvs):
        """
        Load the 4 target curves for Lombardy.

        target_csvs: dict mapping season label -> csv path, e.g.
            {
                "2022": "incidence_2022-2023.csv",
                "2023": "incidence_2023-2024.csv",
                "2024": "incidence_2024-2025.csv",
                "2025": "incidence_2025-2026.csv",
            }
        """
        self.targets = {
            season: pd.read_csv(path)
            for season, path in target_csvs.items()
        }

    def evaluate(self, simulation_csv):
        """
        Evaluate the simulation against all 4 target curves.

        Returns a dict with:
            - "sum": sum of the 4 MSEs (lower = good overall compromise)
            - "minimax": worst (highest) MSE among the 4, plus which year it came from
            - "maxmax": best (lowest) MSE among the 4, plus which year it came from
        """
        simulation = pd.read_csv(simulation_csv)
        sim_full = simulation["Variation of Infected (%)"].to_numpy()

        scores = {}
        for season, target_df in self.targets.items():
            real = target_df["incidenza"].to_numpy()
            n = min(len(sim_full), len(real))
            sim = sim_full[:n]
            real_n = real[:n]
            scores[season] = self.mse(sim, real_n)

        sum_score = sum(scores.values())

        worst_season = max(scores, key=scores.get)
        worst_score = scores[worst_season]

        best_season = min(scores, key=scores.get)
        best_score = scores[best_season]

        print(f"[minimax] worst score: {worst_score:.4f} (year {worst_season})")
        print(f"[maxmax]  best score:  {best_score:.4f} (year {best_season})")

        return {
            "sum": sum_score,
            "minimax": worst_score,
            "minimax_year": worst_season,
            "maxmax": best_score,
            "maxmax_year": best_season,
            "per_season": scores,
        }

    @staticmethod
    def mse(sim, real):
        return np.mean((sim - real) ** 2)