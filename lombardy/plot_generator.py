import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


#---------PLOT STOCHASTICITY OF SEJIRS CLASSES (SUBPLOTS)-------

# 1. Insert the names of your 3 CSV files
csv_files = [
    "csv/PP 0,9 SPP 0.8 - 400 days/simulation_25000_12_400___20260323_131809.csv",
    "csv/PP 0,9 SPP 0.8 - 400 days/simulation_25000_12_400___20260323_160341.csv",
    "csv/PP 0,9 SPP 0.8 - 400 days/simulation_25000_12_400___20260323_184948.csv",
    "csv/PP 0,9 SPP 0.8 - 400 days/simulation_25000_12_400___20260417_083148.csv",
    "csv/PP 0,9 SPP 0.8 - 400 days/simulation_25000_12_400___20260417_110948.csv",
    "csv/PP 0,9 SPP 0.8 - 400 days/simulation_25000_12_400___20260417_134420.csv"
]

# Total population for percentage calculation (adjust if your simulation changes)
total_population = 25000

# Read data from the 3 files
dfs = [pd.read_csv(file) for file in csv_files]
days = dfs[0]["Day"] # Use the days from the first simulation

# Define the columns to analyze and their colors
columns = ["classS", "classE", "classI", "classT3", "classT4", "classR"]
labels = ["S", "E", "I", "J1", "J2", "R"]
colors = ["blue", "orange", "green", "red", "purple", "brown"]

# 2. Create a SINGLE image containing a 2x3 grid (2 rows, 3 columns)
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()  # Flatten the grid into a list for easier iteration

# 3. Draw each class in its dedicated subplot
for idx, (col, label, color) in enumerate(zip(columns, labels, colors)):
    ax = axes[idx] # Select the current subplot

    # Extract the data and convert it directly to percentage: (value / total) * 100
    class_data = np.array([(df[col].values / total_population) * 100 for df in dfs])
    mean_data = class_data.mean(axis=0) # Calculate the mean of the percentages

    # Draw the 3 individual simulations (thin and semi-transparent lines)
    for i, sim_data in enumerate(class_data):
        sim_label = "Individual Runs" if i == 0 else ""
        ax.plot(days, sim_data, color=color, alpha=0.3, linewidth=1, label=sim_label)

    # Draw the mean line (thick and opaque line)
    ax.plot(days, mean_data, color=color, alpha=1.0, linewidth=2.5, label="Mean")

    # Configure the individual subplot
    ax.set_title(f"Class {label}", fontsize=18)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=14, loc="best")

    # Add axes labels (Y label only on the left column, X label only on the bottom row)
    if idx % 3 == 0:
        ax.set_ylabel("Population (%)", fontsize=16)
    if idx >= 3:
        ax.set_xlabel("Days", fontsize=16)

# 4. Final configurations for the entire image
plt.suptitle("Cardinality of the SEJIRS model classes over days (%)", fontsize=22)
plt.tight_layout() # Optimize spacing to avoid overlapping text

# 5. Save the generated image
output_dir = "graphs"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "sejirs_cardinality.png")
plt.savefig(output_path, dpi=300)

print(f"Chart successfully saved in: {output_path}")
plt.show()




#---------PLOT STOCHASTICITY OF PREVALENCE AND DEATHS IN A SINGLE CHART (PP & SPP)-------


def plot_stochastic_single_chart(base_dir, sub_dirs, labels, metric, title, output_filename, total_population=25000):
    # Create a single large figure
    plt.figure(figsize=(12, 8))
    
    # Define a color palette for the different parameters
    colors = ["blue", "orange", "green", "red", "purple"]

    for idx, (sub_dir, label) in enumerate(zip(sub_dirs, labels)):
        folder_path = os.path.join(base_dir, sub_dir)
        color = colors[idx % len(colors)] # Assign a specific color to this parameter
        
        # Automatically find all CSV files
        try:
            csv_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
        except FileNotFoundError:
            print(f"Warning: Folder '{folder_path}' not found. Skipping...")
            continue
            
        if len(csv_files) == 0:
            print(f"Warning: No CSV files found in {folder_path}. Skipping...")
            continue

        # Read data from the files
        dfs = [pd.read_csv(f) for f in csv_files]
        
        # --- FIX FOR INHOMOGENEOUS SHAPE ---
        min_len = min(len(df) for df in dfs)
        days = dfs[0]["Day"].values[:min_len]

        # Extract the requested metric, slice to min_len, and convert to percentage
        class_data = np.array([(df[metric].values[:min_len] / total_population) * 100 for df in dfs])
        
        # Calculate Mean
        mean_data = class_data.mean(axis=0)

        # Draw the individual simulations (Thin and semi-transparent)
        for sim_data in class_data:
            # We don't add a label here to avoid cluttering the legend
            plt.plot(days, sim_data, color=color, alpha=0.2, linewidth=1)

        # Draw the mean line on top (Thick and fully opaque)
        plt.plot(days, mean_data, color=color, alpha=1.0, linewidth=2.5, label=f"{label} (Mean)")

    # Configure the chart
    plt.title(title, fontsize=27)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(fontsize=21, loc="best")
    plt.xlabel("Days", fontsize=22)
    ylabel = "Susceptible (%)" if metric == "classS" else f"{metric} (%)"
    if metric == "classR": ylabel = "Recovered (%)"
    plt.ylabel(ylabel, fontsize=22)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.tight_layout()

    # Save the generated image right next to the script
    script_directory = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_directory, "graphs")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    plt.savefig(output_path, dpi=300)
    plt.close() # Close the figure to free up memory

    print(f"Chart successfully saved in: {output_path}")

# ==========================================
# Get the exact absolute path of this python script
# ==========================================
script_dir = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# 1. EXECUTE FOR PP (Overlapped in a single chart)
# ==========================================
sub_dirs_pp = [
    "csv/PP 0,25 SPP 0.8",
    "csv/PP 0,5 SPP 0.8",
    "csv/PP 0,75 SPP 0.8",
    "csv/PP 0,9 SPP 0.8",
    "csv/PP 1 SPP 0.8"
]
labels_pp = ["PP = 0.25", "PP = 0.5", "PP = 0.75", "PP = 0.9", "PP = 1"]

# Plot Prevalence for PP
plot_stochastic_single_chart(script_dir, sub_dirs_pp, labels_pp, "Prevalence", "Prevalence over days (%) at varying PP", "PP_prevalence_combined.png")
# Plot Deaths for PP
plot_stochastic_single_chart(script_dir, sub_dirs_pp, labels_pp, "Deaths", "Deaths over days (%) at varying PP", "PP_deaths_combined.png")
# Plot R for PP
plot_stochastic_single_chart(script_dir, sub_dirs_pp, labels_pp, "classR", "Recovered over days (%) at varying PP", "PP_R_combined.png")
# Plot S for PP
plot_stochastic_single_chart(script_dir, sub_dirs_pp, labels_pp, "classS", "Susceptible over days (%) at varying PP", "PP_S_combined.png")

# ==========================================
# 2. EXECUTE FOR SPP (Overlapped in a single chart)
# ==========================================
sub_dirs_spp = [
    "csv/PP 0,9 SPP 0",
    "csv/PP 0,9 SPP 0.5",
    "csv/PP 0,9 SPP 0.8",
    "csv/PP 0,9 SPP 1"
]
labels_spp = ["SPP = 0", "SPP = 0.5", "SPP = 0.8", "SPP = 1"]

# Plot Prevalence for SPP
plot_stochastic_single_chart(script_dir, sub_dirs_spp, labels_spp, "Prevalence", "Prevalence over days (%) at varying SPP", "SPP_prevalence_combined.png")
# Plot Deaths for SPP
plot_stochastic_single_chart(script_dir, sub_dirs_spp, labels_spp, "Deaths", "Deaths over days (%) at varying SPP", "SPP_deaths_combined.png")
# Plot R for SPP
plot_stochastic_single_chart(script_dir, sub_dirs_spp, labels_spp, "classR", "Recovered over days (%) at varying SPP", "SPP_R_combined.png")
# Plot S for PP
plot_stochastic_single_chart(script_dir, sub_dirs_spp, labels_spp, "classS", "Susceptible over days (%) at varying SPP", "SPP_S_combined.png")


#---------PLOT STOCHASTICITY OF LOCKDOWNS (SINGLE CHART WITH PADDING)-------

def plot_lockdown_single_chart(base_dir, sub_dirs, labels, metric, title, output_filename, total_population=25000):
    # Create a single large figure
    plt.figure(figsize=(12, 8))
    
    # Define a color palette: Blue (Base), Orange (60-day), Green (3 20-day)
    colors = ["blue", "orange", "green"]

    # First pass: read all data to find the global maximum length (e.g., 800 days)
    all_dfs = []
    global_max_len = 0
    master_days = None
    
    for sub_dir in sub_dirs:
        folder_path = os.path.join(base_dir, sub_dir)
        try:
            csv_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
            dfs = [pd.read_csv(f) for f in csv_files]
            all_dfs.append(dfs)
            for df in dfs:
                if len(df) > global_max_len:
                    global_max_len = len(df)
                    master_days = df["Day"].values
        except FileNotFoundError:
            print(f"Warning: Folder '{folder_path}' not found. Skipping...")
            all_dfs.append([])

    # Second pass: Plotting with intelligent Padding (Zero or Edge)
    for idx, (dfs, label) in enumerate(zip(all_dfs, labels)):
        if not dfs:
            continue
            
        color = colors[idx % len(colors)]
        class_data = []

        # Process each simulation and pad if it's shorter than the maximum length
        for df in dfs:
            val = (df[metric].values / total_population) * 100
            if len(val) < global_max_len:
                if metric == "Deaths":
                    # For cumulative metrics (Deaths), we carry forward the last recorded value
                    val = np.pad(val, (0, global_max_len - len(val)), mode='edge')
                else:
                    # For active metrics (Prevalence), we pad with 0s
                    val = np.pad(val, (0, global_max_len - len(val)), constant_values=np.nan)
            class_data.append(val)
            
        class_data = np.array(class_data)
        
        # Calculate Mean
        mean_data = np.nanmean(class_data, axis=0)

        # Draw the individual simulations (Thin and semi-transparent)
        for sim_data in class_data:
            plt.plot(master_days, sim_data, color=color, alpha=0.2, linewidth=1)

        # Draw the mean line on top (Thick and fully opaque)
        plt.plot(master_days, mean_data, color=color, alpha=1.0, linewidth=2.5, label=f"{label} (Mean)")

    # Add the horizontal dashed lines for lockdown periods at the bottom
    ax = plt.gca()
    ymin, ymax = ax.get_ylim()

    y_pos_green = ymin + 0.04 * (ymax - ymin)
    y_pos_orange = ymin + 0.05 * (ymax - ymin)

    ax.hlines(y=y_pos_green, xmin=50, xmax=70, color='green', linestyle='--', linewidth=2)
    ax.hlines(y=y_pos_green, xmin=90, xmax=110, color='green', linestyle='--', linewidth=2)
    ax.hlines(y=y_pos_green, xmin=130, xmax=150, color='green', linestyle='--', linewidth=2)

    ax.hlines(y=y_pos_orange, xmin=50, xmax=110, color='orange', linestyle='--', linewidth=2)

    # Configure the chart
    plt.title(title, fontsize=27)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(fontsize=21, loc="best")
    plt.xlabel("Days", fontsize=22)
    ylabel = "Susceptible (%)" if metric == "classS" else f"{metric} (%)"
    if metric == "classR": ylabel = "Recovered (%)"
    plt.ylabel(ylabel, fontsize=22)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.tight_layout()

    # Save the generated image
    script_directory = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_directory, "graphs")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Chart successfully saved in: {output_path}")

# ==========================================
# Get the exact absolute path of this python script
# ==========================================
script_dir = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# 3. EXECUTE FOR LOCKDOWNS
# ==========================================
# Check if these exact folder names match your directories
sub_dirs_lockdowns = [
    "csv/no lockdown - 800 days", 
    "csv/60 day lockdown - 800 days", 
    "csv/3 20 day lockdown - 800 days"
]
labels_lockdowns = ["No lockdown", "60 day lockdown", "3 20 day lockdown"]

# Plot Prevalence for Lockdowns
plot_lockdown_single_chart(script_dir, sub_dirs_lockdowns, labels_lockdowns, "Prevalence", "Prevalence over days (%) at varying lockdowns", "Lockdown_prevalence_combined.png")
# Plot Deaths for Lockdowns
plot_lockdown_single_chart(script_dir, sub_dirs_lockdowns, labels_lockdowns, "Deaths", "Deaths over days (%) at varying lockdowns", "Lockdown_deaths_combined.png")
# Plot Recovered for Lockdowns
plot_lockdown_single_chart(script_dir, sub_dirs_lockdowns, labels_lockdowns, "classR", "Recovered over days (%) at varying lockdowns", "Lockdown_R_combined.png")
# Plot Recovered for Lockdowns
plot_lockdown_single_chart(script_dir, sub_dirs_lockdowns, labels_lockdowns, "classS", "Susceptible over days (%) at varying lockdowns", "Lockdown_S_combined.png")
