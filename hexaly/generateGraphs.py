import json
import matplotlib.pyplot as plt
import pandas as pd
import os
import re
from datetime import datetime
import numpy as np
# ---------------------------
# Generic plotting functions
# ---------------------------

def sort_param_values(grouped):
    """Sort parameter values with special handling for travelTimes."""
    # Check if this looks like travelTimes data
    if grouped['param_value'].astype(str).isin(['short', 'medium', 'long']).any():
        # Define custom order for travel times
        order = ['short', 'medium', 'long']
        grouped['sort_key'] = grouped['param_value'].apply(lambda x: order.index(x) if x in order else 999)
        grouped = grouped.sort_values('sort_key').drop('sort_key', axis=1)
    else:
        # Try numeric sort
        try:
            grouped['param_value_numeric'] = pd.to_numeric(grouped['param_value'])
            grouped = grouped.sort_values('param_value_numeric').drop('param_value_numeric', axis=1)
        except:
            # Fall back to alphabetic sort
            grouped = grouped.sort_values('param_value')
    
    return grouped

def plot_metric_by_param(df, metric, ylabel):
    """Plot a given metric (runtime, visited nodes, objective) grouped by 'type'."""
    unique_types = df["type"].unique()

    for t in unique_types:
        subset = df[df["type"] == t]

        grouped = subset.groupby("param_value", as_index=False)[metric].mean()
        grouped = sort_param_values(grouped)

        x = grouped["param_value"]
        y = grouped[metric]

        plt.figure(figsize=(8,5))
        plt.plot(x, y, marker="o")
        plt.title(f"{ylabel} vs Parameter Value ({t})")
        plt.xlabel("Parameter value")
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.tight_layout()

        plt.savefig(f"graphs/{metric}_{t}.png")
        plt.close()


def plot_scatter_runtime_objective(df):
    """Scatter plot to detect relationships between runtime and objective."""
    plt.figure(figsize=(8,5))
    plt.scatter(df["objective_value"], df["runtime"])
    plt.title("Runtime vs Number of Pickers")
    plt.xlabel("Number of Pickers")
    plt.ylabel("Runtime (s)")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(f"graphs/runtime_vs_objective.png")
    plt.close()

def extract_datetime(filename: str) -> datetime | None:
    """
    Extracts a datetime object from a filename like:
    'results_2025-12-07_12-26-37.json'
    """
    match = re.search(r"(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})", filename)
    if not match:
        return None

    date_part, time_part = match.groups()
    timestamp = f"{date_part} {time_part.replace('-', ':')}"
    return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

def pie_chart_valid(df):
    """Pie chart showing the proportion of valid vs invalid solutions."""
    df['is_valid'] = ~np.isinf(df['gap'])
    valid_counts = df['is_valid'].value_counts()

    plt.figure(figsize=(6,6))
    plt.pie(valid_counts, labels=valid_counts.index, autopct='%1.1f%%', startangle=140)
    plt.title("Proportion of Valid vs Invalid Solutions")
    plt.tight_layout()

    plt.savefig("graphs/valid_solutions_pie_chart.png")
    plt.close()

    print("Pie chart of valid vs invalid solutions saved.")

# ---------------------------
# Generate all graphs
# ---------------------------


files = os.listdir("results")
json_files = [f for f in files if f.startswith("results_") and f.endswith(".json")]
latest_file = None
latest_dt = None

for f in json_files:
    dt = extract_datetime(f)
    print(f, dt)
    if dt is None:
        # skip files without a recognizable timestamp
        continue
    if latest_dt is None or dt > latest_dt:
        latest_dt = dt
        latest_file = f



print(f"Processing file: {latest_file}")
with open(f"results/{latest_file}", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Convert numeric fields
numeric_columns = ["runtime", "objective_value", "iterations"]
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

plot_metric_by_param(df, "runtime", "Runtime (s)")
plot_metric_by_param(df, "objective_value", "Amount of Pickers")
plot_metric_by_param(df, "iterations", "Visited Nodes")

plot_scatter_runtime_objective(df)

pie_chart_valid(df)

print("Graphs generated!")
