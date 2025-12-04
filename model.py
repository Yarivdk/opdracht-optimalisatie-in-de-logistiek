from hexaly.modeler import *
from hexaly.optimizer import *
import sys
import json

def run_model(input_file=None, timeLimit=60):
    TIMESTAMPS_PER_SOLUTION = []
    with open(input_file, 'r') as f:
        data = json.load(f)

    def my_callback(opt, cb_type):
        stats = opt.statistics
        obj = opt.model.objectives[0]
        # e.g. log whenever objective improved
        # print(f"EIGEN OUTPUT: [{stats.running_time} sec, {stats.nb_iterations} itr] obj = {obj.value}, status = {opt.solution.status}")
        results = {
            "time": stats.running_time,
            "iterations": stats.nb_iterations,
            "objective_value": obj.value,
            "status": opt.solution.status.value
        }
        TIMESTAMPS_PER_SOLUTION.append(results)


    with HexalyModeler() as modeler:
        boxexpress_module = modeler.load_module("boxexpress", "boxexpress.hxm")

        optimizer = modeler.create_optimizer()
        # optimizer.param.iteration_between_ticks = 100
        optimizer.add_callback(HxCallbackType.TIME_TICKED, my_callback)
        boxexpress_module.run(optimizer, f"inFileName={input_file}", f"lsTimeLimit={timeLimit}")
        # print("CHECK:",TIMESTAMPS_PER_SOLUTION)
        sorted_timestamps_per_solution = sorted(TIMESTAMPS_PER_SOLUTION, key=lambda x: x["iterations"])

        # --------------------------------------------------------------------
        # 1) GET SOLUTION + STATISTICS
        # --------------------------------------------------------------------
        usedOrderPickers = boxexpress_module["usedOrderPickers"]
        solution = optimizer.get_solution()

        obj_value = 0
        for i in range(len(usedOrderPickers)):
            obj_value += solution.get_value(usedOrderPickers[i])

        runtime = None
        iterations = None
        for result in sorted_timestamps_per_solution:
            if result["status"] == 1:  # infeasible
                continue
            elif result["objective_value"] == obj_value:
                runtime = result["time"]
                iterations = result["iterations"]
                break

        gap = solution.get_objective_gap(0)
        bound = solution.get_objective_bound(0)

        # --------------------------------------------------------------------
        # 7) SAVE RESULTS TO JSON
        # --------------------------------------------------------------------
        results = {
            "runtime": runtime,
            "iterations": iterations,
            "objective_value": obj_value,
            "best_bound": bound,
            "gap": gap
        }

        optimizer.delete()

        return results
    