import os
import json
import random
import shuffle


ITEMS_SET = [10, 20, 50, 100, 200]
WAREHOUSES_SET = [5, 10, 20, 40]
CAPACITY_SET = [3, 5, 8, 10, 13, 15]
SCALES = ["short", "medium", "long"]

default_vaules = {
    "amountOrderPickers": 10,
    "capacity": 5,
    "maxTimePerRound": 60,
    "amount_items": 50,
    "amount_warehouses": 10,
    "capacity": 5,
    "scale": "medium",
}

OUTPUT_FOLDER = "instance"

# Travel-time ranges
TRAVEL_TIME_RANGES = {
    "short": (5, 10),
    "medium": (10, 40),
    "long": (40, 200)
}

