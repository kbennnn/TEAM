import pandas as pd
import matplotlib.pyplot as plt

# ==========================
# Input files (season -> csv path)
# ==========================
files = {
    "2022-2023": "incidence_2022-2023.csv",
    "2023-2024": "incidence_2023-2024.csv",
    "2024-2025": "incidence_2024-2025.csv",
    "2025-2026": "incidence_2025-2026.csv",
}

# ==========================
# Generate one graph per file
# ==========================
for season, path in files.items():
    ili = pd.read_csv(path)

    # Sequential x-axis: 1, 2, 3, ...
    x = range(1, len(ili) + 1)

    plt.figure(figsize=(12, 5))

    plt.plot(
        x,
        ili["incidenza"],
        marker='o',
        linewidth=2
    )

    plt.title(f"ILI Incidence {season}")
    plt.xlabel("Week number")
    plt.ylabel("Incidence per 100 inhabitants")
    plt.xticks(x)
    plt.grid(True)

    plt.tight_layout()

    filename = f"ILI_Incidence_{season}.png"
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved {filename}")