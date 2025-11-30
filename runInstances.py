import os
from model import run_model
import json

FOLDER = "instances"

results = []
for file in os.listdir(FOLDER):
    if file.endswith(".json"):
        filepath = os.path.join(FOLDER, file)
        # parse instance and run model
        instanceID = file.split("-")[1].split("_")[0]
        instanceType = file.split("-")[1].split("_")[1]
        instanceValue = file.split("-")[2].split(".")[0]

        instance_results = run_model(input_file=filepath, timeLimit=60)
        instance_results["id"] = instanceID
        instance_results["type"] = instanceType
        instance_results["param_value"] = int(instanceValue)
        results.append(instance_results)
        print(f"Results for {file}: {instance_results}")
        break # Remove this break to run on all instances


with open("results.json", "w") as out:
    json.dump(results, out, indent=4)

print("\nSaved → results.json")