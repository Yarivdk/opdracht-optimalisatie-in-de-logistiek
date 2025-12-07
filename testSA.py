from simulatedAnnealing import *
import json

with open("instances/instance-100_amountItems-100.json", "r") as f:
    instance = json.load(f)

problem = OrderPickingProblem(instance)
    
print("Starting Iterative Simulated Annealing...\n")
visited, solution, results = iterative_simulated_annealing(
    problem, 
    T0=100, 
    alpha=0.95, 
    max_iter_per_temp=100,
    stagnation_threshold=20
)

print(f"\n=== FINAL SOLUTION ===")
print(f"Total nodes visited: {visited}")
print(f"Number of pickers used: {solution[0]}")
print(f"Solution is valid: {solution[2]}")
print(f"\nRoutes:")

for i, picker_routes in enumerate(solution[1]):
    if any(route for route in picker_routes):
        print(f"\nPicker {i+1}:")
        for j, route in enumerate(picker_routes):
            if route:
                time = problem.calculate_route_time(route)
                locations = [problem.product_locations[item] for item in route]
                capacity_ok = len(route) <= problem.capacity
                time_ok = time <= problem.max_time
                status = "✓" if (capacity_ok and time_ok) else "✗"
                print(f"  {status} Round {j+1}: Items {route} at locations {locations}")
                print(f"      Capacity: {len(route)}/{problem.capacity}, Time: {time:.2f}/{problem.max_time}")

# Verify all items collected
all_items_collected = []
for picker_routes in solution[1]:
    for route in picker_routes:
        all_items_collected.extend(route)

print(f"\n--- Verification ---")
print(f"Items to collect: {sorted(problem.items)}")
print(f"Items collected: {sorted(all_items_collected)}")
print(f"All items collected: {set(all_items_collected) == set(problem.items)}")