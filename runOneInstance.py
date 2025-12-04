from model import run_model
import json
import sys
from datetime import datetime
INSTANCE_FILE = sys.argv[1]

results = []

# parse instance and run model
instanceID = INSTANCE_FILE.split("-")[1].split("_")[0]
instanceType = INSTANCE_FILE.split("-")[1].split("_")[1]
instanceValue = INSTANCE_FILE.split("-")[2].split(".")[0]

instance_results = run_model(input_file=INSTANCE_FILE, timeLimit=60)
instance_results["id"] = instanceID
instance_results["type"] = instanceType
instance_results["param_value"] = instanceValue
results.append(instance_results)
print(f"Results for {INSTANCE_FILE}: {instance_results}")

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

with open(f"results/results_individual_instance_{timestamp}.json", "w") as out:
    json.dump(results, out, indent=4)

print(f"\nSaved → results/results_individual_instance_{timestamp}.json")