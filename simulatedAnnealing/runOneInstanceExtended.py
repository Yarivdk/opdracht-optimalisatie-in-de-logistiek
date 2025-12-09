from simulatedAnnealingExtended import *
import json
import sys
from datetime import datetime
import pytz
import time

INSTANCE_FILE = sys.argv[1]

results = []

# parse instance and run model
instanceID = INSTANCE_FILE.split("-")[1].split("_")[0]
instanceType = INSTANCE_FILE.split("-")[1].split("_")[1]
instanceValue = INSTANCE_FILE.split("-")[2].split(".")[0]

with open(INSTANCE_FILE, "r") as f:
    instance = json.load(f)

problem = OrderPickingProblem(instance)

start_time = time.time()
# print("Starting Iterative Simulated Annealing...\n")
visited, solution, sa_results = iterative_simulated_annealing(
    problem,
    logging=True, 
    T0=100, 
    alpha=0.95, 
    max_iter_per_temp=100,
    stagnation_threshold=20
)
end_time = time.time()
run_time = end_time - start_time
run_time_ms = int(run_time * 1000)
print(f"Total nodes visited: {visited}")
print(f"Number of pickers used: {solution[0]}")
print(f"Solution is valid: {solution[2]}")

print(f"\nRoutes:")

for picker, picker_routes in solution[1].items():
    if any(route for route in picker_routes):
        print(f"\nPicker {picker} ({problem.picker_categories[picker]}):")
        for j, route in enumerate(picker_routes):
            if route:
                time = problem.calculate_route_time(route)
                locations = [problem.product_locations[item] for item in route]
                capacity_ok = len(route) <= problem.capacity
                time_ok = time <= problem.max_time
                status = "✓" if (capacity_ok and time_ok) else "✗"
                print(f"  {status} Round {j+1}: Items {route} at locations {locations}")
                print(f"      Capacity: {len(route)}/{problem.capacity}, Time: {time:.2f}/{problem.max_time}")

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
print(f"Results for {INSTANCE_FILE}: {instance_results}")


brussels_tz = pytz.timezone("Europe/Brussels")
current_time = datetime.now(brussels_tz)
timestamp = current_time.strftime("%Y-%m-%d_%H-%M-%S")

with open(f"results/results_individual_instance_{timestamp}.json", "w") as out:
    json.dump(results, out, indent=4)

print(f"\nSaved → results/results_individual_instance_{timestamp}.json")