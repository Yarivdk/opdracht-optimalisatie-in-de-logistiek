def get_parameter_vals():
    parameter_vals = {
        "T0": [5, 10, 25, 50, 100], # initial temperature
        "alpha": [0.85, 0.90, 0.95, 0.99], # cooling rate
        "stagnation_treshold": [1, 2, 3], # Max iterations with too few or no accepted moves
        "max_iter": [10, 25, 50, 100] # max iterations per temperature level
    }

    default_vals = {
        "T0": 25,
        "alpha": 0.95,
        "stagnation_treshold": 2,
        "max_iter": 50
    }

    parameter_names = {
        "T0": "initialTemperature",
        "alpha": "coolingRate",
        "stagnation_treshold": "stagnationTreshold",
        "max_iter": "maxIterations"
    }

    return parameter_vals, default_vals, parameter_names