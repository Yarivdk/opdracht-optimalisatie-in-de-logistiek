from hexaly.modeler import *
import sys
import json

input_file = sys.argv[1]

with open(input_file, 'r') as f:
    data = json.load(f)

with HexalyModeler() as modeler:
    boxexpress_module = modeler.load_module("boxexpress", "boxexpress.hxm")

    optimizer = modeler.create_optimizer()
    boxexpress_module.run(optimizer, f"inFileName={input_file}")

    # --------------------------------------------------------------------
    # 1) GET SOLUTION + STATISTICS
    # --------------------------------------------------------------------
    usedOrderPickers = boxexpress_module["usedOrderPickers"]


    solution = optimizer.get_solution()
    stats = optimizer.get_statistics()
    status = solution.get_status()

    runtime = stats.get_running_time()
    iterations = stats.get_nb_iterations()
    gap = solution.get_objective_gap(0)
    bound = solution.get_objective_bound(0)


    print("\n=== SOLVER STATISTICS ===")
    print("Runtime (sec):", runtime)
    print("Iterations:", iterations)
    print("Best bound:", bound)
    print("Best gap:", gap)

    # --------------------------------------------------------------------
    # 2) READ OBJECTIVE: usedOrderPickers
    # --------------------------------------------------------------------

    obj_value = 0
    for i in range(len(usedOrderPickers)):
        obj_value += solution.get_value(usedOrderPickers[i])

    print("\nObjective (sum used order pickers):", obj_value)

    # --------------------------------------------------------------------
    # 7) SAVE RESULTS TO JSON
    # --------------------------------------------------------------------
    results = {
        "runtime": runtime,
        "objective_value": obj_value,
        "best_bound": bound,
        "gap": gap
    }

    with open("results.json", "w") as out:
        json.dump(results, out, indent=4)

    print("\nSaved → results.json")
    
