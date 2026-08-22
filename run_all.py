#A code for run the three algorithm together
import subprocess

commands = [
    ["python", "-m", "ga.ga_main"],
    ["python", "-m", "de.de_main"],
    ["python", "-m", "cmaes.cmaes_main"],
]

for command in commands:
    print(f"Starting: {' '.join(command)}")

    with open(f"{command[2].replace('.', '_')}_output.txt", "w") as f:
        result = subprocess.run(command, stdout=f, stderr=subprocess.STDOUT)

    if result.returncode != 0:
        print(f"Process failed with exit code {result.returncode}")
        break

    print(f"Finished: {' '.join(command)}")