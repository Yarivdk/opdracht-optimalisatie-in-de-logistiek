import os 
import json
import random
from math import ceil

INPUT_FOLDER = "instances"
OUTPUT_FOLDER = "instancesExtended"

# empty folder
for filename in os.listdir(OUTPUT_FOLDER):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")

categories = ["Smartphones", "Laptops", "Tablets", "Desktop Computers", "Monitors", "Keyboards", "Mice", "Headphones", "Earbuds", "Speakers", "Smartwatches", "Fitness Trackers", "Televisions", "Cameras", "Drones", "Printers", "Projectors", "Routers", "Smart Home Devices", "Wearable Tech", "Video Games", "Gaming Consoles", "Board Games", "Toys", "Books", "Magazines", "Office Supplies", "Stationery", "Backpacks", "Luggage", "Handbags", "Wallets", "Shoes", "Clothing", "Jewelry", "Watches", "Sunglasses", "Skincare", "Makeup", "Haircare", "Fragrances", "Health Supplements", "Vitamins", "Medical Devices", "Sports Equipment", "Gym Equipment", "Cycling Gear", "Outdoor Gear", "Camping Equipment", "Garden Tools", "Plants", "Furniture", "Home Decor", "Bedding", "Kitchen Appliances", "Cookware", "Tableware", "Cleaning Supplies", "Laundry Supplies", "Pet Food", "Pet Accessories", "Baby Products", "Diapers", "Strollers", "Car Seats", "Automotive Parts", "Car Accessories", "Motorcycle Gear", "Power Tools", "Hand Tools", "Construction Materials", "Lighting", "Electrical Supplies", "Plumbing Supplies", "Paint & Coatings", "Flooring", "Home Security Products", "Surveillance Cameras", "Batteries", "Chargers", "Cables", "Music Instruments", "Audio Equipment", "Bookshelves", "Storage Solutions", "Rugs", "Mattresses", "Snacks", "Beverages", "Fresh Produce", "Frozen Foods", "Canned Goods", "Wine & Spirits", "Craft Supplies", "Hobby Kits", "3D Printing Supplies", "Lab Equipment"]

for file in os.listdir(INPUT_FOLDER):
    if file.endswith(".json"):
        with open(os.path.join(INPUT_FOLDER, file), "r") as f:
            instance = json.load(f)
        
        # Modify instance: assign picker categories
        amount_items = len(instance["items"])

        if amount_items > 505:
            continue  # skip instances that are too large for category assignment

        amount_categories = min(ceil(amount_items / 10), len(categories))
        selected_categories = random.sample(categories, amount_categories)
        
        categories_pickers = random.choices(selected_categories, k=instance["amountOrderPickers"])
        categories_products = random.choices(selected_categories, k=amount_items)

        instance["orderPickerCategories"] = categories_pickers
        instance["productCategories"] = categories_products
        instance["categories"] = selected_categories

        # Write modified instance to new file
        output_file = os.path.join(OUTPUT_FOLDER, file)
        with open(output_file, "w") as f:
            json.dump(instance, f, indent=4)
        
        print(f"Generated extended instance: {output_file}")