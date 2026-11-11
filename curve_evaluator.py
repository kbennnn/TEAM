import pandas as pd
import numpy as np


class CurveEvaluator:

    def __init__(self, target_csvs):
        """
        Load the 4 target curves for Lombardy.

        target_csvs: dict mapping season label -> csv path, e.g.
            {
                "2022": "incidence_strain_2022-2023.csv",
                "2023": "incidence_strain_2023-2024.csv",
                "2024": "incidence_strain_2024-2025.csv",
                "2025": "incidence_strain_2025-2026.csv",
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
            real = target_df["totale_perc"].to_numpy()
            n = min(len(sim_full), len(real))
            sim = sim_full[:n]
            real_n = real[:n]
            scores[season] = self.weighted_mse(sim, real_n)

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
    def weighted_mse(sim, real):
        """
        Calculate the balanced epidemic fitness (Weighted MSE + Off-Season Penalty + Peak Penalty).
        This replaces the simple MSE to avoid flat or zero curves.
        """
        sim = np.array(sim)
        real = np.array(real)
        n = len(sim)
        
        # 1. Weighted MSE
        weights = np.ones(n)
        
        # Off-season weights 50% more
        off_season_end_idx = min(8, n)
        off_season_start_idx = min(34, n)
        
        weights[:off_season_end_idx] = 1.5
        weights[off_season_start_idx:] = 1.5
        
        # Peak-season weights 100% more
        peak_start_idx = min(14, n)
        peak_end_idx = min(26, n)
        if peak_start_idx < peak_end_idx:
            weights[peak_start_idx:peak_end_idx] = 2.0
            
        weighted_mse = np.sum(weights * ((sim - real) ** 2)) / np.sum(weights)
        
        # 2. Background Noise Penalty (Off-Season)
        off_season_indices = list(range(0, off_season_end_idx)) + list(range(off_season_start_idx, n))
        if len(off_season_indices) > 0:
            off_season_mean = np.mean(sim[off_season_indices])
        else:
            off_season_mean = 0.0
            
        penalty_baseline = 2.0 * (off_season_mean ** 2)  # Adds approx. 0.0 - 0.35
        
        # 3. Peak Height Penalty - Proportional to the real target peak
        max_sim = np.max(sim) if len(sim) > 0 else 0.0
        max_real = np.max(real) if len(real) > 0 else 0.0
        
        penalty_peak = 1.0 * ((max_sim - max_real) ** 2)  # Adds approx. 0.0 - 0.50
        
        # Balanced total score - maintains the same numerical range as standard MSE
        return weighted_mse + penalty_baseline + penalty_peak