import sys
import pandas as pd
import json
from math import ceil

excelFile = sys.argv[1]
jsonFile = sys.argv[2]

# Read Excel sheets
sheet_general = pd.read_excel(excelFile, sheet_name=0, header=None)
sheet_productLocations = pd.read_excel(excelFile, sheet_name=1)
sheet_travelTimeMatrix = pd.read_excel(excelFile, sheet_name=2, header=None)
sheet_orderList = pd.read_excel(excelFile, sheet_name=3)

# Extract parameters
params = dict(zip(sheet_general[0], sheet_general[1]))
amountOrderPickers = int(params.get('amountOrderPickers'))
capacity = int(params.get('capacity'))
maxTimePerRound = int(params.get('maxTimePerRound'))
amountOrders = int(params.get('amountOrders'))
amountWarehouses = int(params.get('amountWarehouses'))

# Normalize column names
sheet_productLocations.columns = [col.lower() for col in sheet_productLocations.columns]
sheet_orderList.columns = [col.lower() for col in sheet_orderList.columns]

# Extract item lists
locationList = sheet_productLocations["location"].tolist()
productList = sheet_productLocations["product"].tolist()

productLocationsCollection = []
for i in range(len(productList)):
    productLocationsCollection.append(productList[i])

# Extract travel time matrix
travelTimeMatrix = sheet_travelTimeMatrix.values.tolist()

# Extract order list details
orderIDs = sheet_orderList["order"].tolist()
orderProducts = sheet_orderList["products"].tolist()

ordersProductsCollection = []

for i in range(len(orderIDs)):
    products = [int(p) for p in orderProducts[i].split(',')]
    ordersProductsCollection.append(products)

items = []
for order in ordersProductsCollection:
    for item in order:
        items.append(item)

maxRoundsPerOrderPicker = len(items)

# Build dictionary to write to JSON
data = {
    "amountOrderPickers": amountOrderPickers,
    "capacity": capacity,
    "maxTimePerRound": maxTimePerRound,
    "amountOrders": amountOrders,
    "amountWarehouses": amountWarehouses,
    "productLocations": productLocationsCollection,
    "travelTimeMatrix": travelTimeMatrix,
    "items": items,
    "maxRoundsPerOrderPicker": maxRoundsPerOrderPicker
}

# Write to JSON file
with open(jsonFile, 'w') as f:
    json.dump(data, f, indent=4)

print(f"Data written to {jsonFile}")
