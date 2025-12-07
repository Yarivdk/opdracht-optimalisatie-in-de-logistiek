import os
import json
import random

INSTANCES_PER_CONFIGURATION = 5

# krijg een warning bij instance size van 150 (teveel operands)
ITEMS_SET = range(5, 800, 25)
# CAPACITY_SET = [3, 5, 8, 10, 13, 15]
SCALES = ["short", "medium", "long"]

default_values = {
    "capacity": 10,
    "maxTimePerRound": 60,
    "amount_items": 8,
    "scale": "short",
}

OUTPUT_FOLDER = "instances"

# Travel-time ranges
TRAVEL_TIME_RANGES = {
    "short": (1, 10),
    "medium": (10, 20),
    "long": (20, 30)
}

# empty the folder first
for filename in os.listdir(OUTPUT_FOLDER):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")

counter = 1
for amountItems in ITEMS_SET:
    for instance_number in range(INSTANCES_PER_CONFIGURATION):
        jsonFile = os.path.join(OUTPUT_FOLDER, f"instance-{counter}_amountItems-{amountItems}.json")

        # Generate items
        items = list(range(amountItems))
        productLocations = list(range(amountItems))
        random.shuffle(productLocations)

        # Generate travel time matrix
        travel_time_min, travel_time_max = TRAVEL_TIME_RANGES[default_values["scale"]]
        travelTimeMatrix = []
        for i in range(amountItems+1):
            row = []
            for j in range(amountItems+1):
                if i == j:
                    row.append(999)
                else:
                    travel_time = random.randint(travel_time_min, travel_time_max)
                    row.append(travel_time)
            travelTimeMatrix.append(row)
        
        # Build dictionary to write to JSON
        data = {
            "amountOrderPickers": amountItems,
            "capacity": default_values["capacity"],
            "maxTimePerRound": default_values["maxTimePerRound"],
            "amountWarehouses": amountItems,
            "productLocations": productLocations,
            "travelTimeMatrix": travelTimeMatrix,
            "items": items,
            "maxRoundsPerOrderPicker": amountItems
        }

        # Write to JSON file
        with open(jsonFile, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"Generated instance: {jsonFile}")
        counter += 1

for scale in SCALES:
    for instance_number in range(INSTANCES_PER_CONFIGURATION):
        jsonFile = os.path.join(OUTPUT_FOLDER, f"instance-{counter}_travelTimes-{scale}.json")

        # Generate items
        items = list(range(default_values["amount_items"]))
        productLocations = list(range(default_values["amount_items"]))
        random.shuffle(productLocations)
        # Generate travel time matrix
        travel_time_min, travel_time_max = TRAVEL_TIME_RANGES[scale]
        travelTimeMatrix = []
        for i in range(default_values["amount_items"]+1):
            row = []
            for j in range(default_values["amount_items"]+1):
                if i == j:
                    row.append(999)
                else:
                    travel_time = random.randint(travel_time_min, travel_time_max)
                    row.append(travel_time)
            travelTimeMatrix.append(row)
        
        # Build dictionary to write to JSON
        data = {
            "amountOrderPickers": default_values["amount_items"],
            "capacity": default_values["capacity"],
            "maxTimePerRound": default_values["maxTimePerRound"],
            "amountWarehouses": default_values["amount_items"],
            "productLocations": productLocations,
            "travelTimeMatrix": travelTimeMatrix,
            "items": items,
            "maxRoundsPerOrderPicker": default_values["amount_items"]
        }

        # Write to JSON file
        with open(jsonFile, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"Generated instance: {jsonFile}")
        counter += 1