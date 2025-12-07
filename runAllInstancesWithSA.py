import os
from simulatedAnnealing import *
import json
import time
from datetime import datetime
import pytz

FOLDER = "instances"

results = []
counter = 0
for file in os.listdir(FOLDER):
    if file.endswith(".json"):
        filepath = os.path.join(FOLDER, file)
        # parse instance and run model
        instanceID = file.split("-")[1].split("_")[0]
        instanceType = file.split("-")[1].split("_")[1]
        instanceValue = file.split("-")[2].split(".")[0]

        with open(filepath, "r") as f:
            instance = json.load(f)
        
        problem = OrderPickingProblem(instance)

        start_time = time.time()
        # print("Starting Iterative Simulated Annealing...\n")
        visited, solution, sa_results = iterative_simulated_annealing(
            problem, 
            T0=100, 
            alpha=0.95, 
            max_iter_per_temp=100,
            stagnation_threshold=20
        )
        end_time = time.time()
        run_time = end_time - start_time
        run_time_ms = int(run_time * 1000)
        # print(f"Total nodes visited: {visited}")
        # print(f"Number of pickers used: {solution[0]}")
        # print(f"Solution is valid: {solution[2]}")

        instance_results = {
            "visited_nodes": visited,
            "runtime": run_time_ms,
            "num_pickers": solution[0],
            "is_valid": solution[2]
        }
        instance_results["id"] = instanceID
        instance_results["type"] = instanceType
        instance_results["param_value"] = instanceValue
        results.append(instance_results)
        print(f"Results for {file}: {instance_results}")
        # time.sleep(2)

        counter += 1
        # if counter == 10:
            # break  # Remove this break to run on all instances

# brussels timezone
brussels_tz = pytz.timezone("Europe/Brussels")
current_time = datetime.now(brussels_tz)
timestamp = current_time.strftime("%Y-%m-%d_%H-%M-%S")
with open(f"simulatedAnnealingResults/results_{timestamp}.json", "w") as out:
    json.dump(results, out, indent=4)

print(f"\nSaved → simulatedAnnealingResults/results_{timestamp}.json")