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

categories = ["Technology", "Finance", "Healthcare", "Education", "Sports", "Travel", "Fashion", "Food", "Entertainment", "Real Estate", "Marketing", "Sales", "Human Resources", "Legal", "Operations", "Supply Chain", "Logistics", "Manufacturing", "Energy", "Environment", "Automotive", "Aerospace", "Telecommunications", "Retail", "E-commerce", "Gaming", "Music", "Art", "Photography", "Science", "Biotechnology", "Pharmaceuticals", "Construction", "Architecture", "Interior Design", "Agriculture", "Mining", "Insurance", "Investment", "Banking", "Cryptocurrency", "Machine Learning", "Artificial Intelligence", "Data Science", "Cybersecurity", "Cloud Computing", "DevOps", "Software Engineering", "Mobile Development", "Web Development", "Product Management", "Project Management", "UX Design", "UI Design", "Customer Support", "Public Relations", "Advertising", "Journalism", "Publishing", "Film", "Television", "Theater", "Fitness", "Nutrition", "Wellness", "Psychology", "Sociology", "Politics", "Economics", "History", "Geography", "Philosophy", "Religion", "Parenting", "Pets", "Home Improvement", "Gardening", "Transportation", "Hospitality", "Event Planning", "Nonprofit", "Charity", "Military", "Security", "Astronomy", "Meteorology", "Oceanography", "Chemistry", "Physics", "Mathematics", "Statistics", "Machine Tools", "Drones", "Robotics", "Electronics", "Nanotechnology", "3D Printing", "Virtual Reality", "Augmented Reality"]

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