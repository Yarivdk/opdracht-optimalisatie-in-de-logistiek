import json
import matplotlib.pyplot as plt
import pandas as pd
import os
import re
from datetime import datetime

# ---------------------------
# Generic plotting functions
# ---------------------------

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

def load_latest_result(directory, model_name):
    """Load the latest results JSON file from a directory and tag it with a model name."""
    files = os.listdir(directory)
    json_files = [f for f in files if f.startswith("results_") and f.endswith(".json")
                  and "individual_instance" not in f]

    latest_file = None
    latest_dt = None

    for f in json_files:
        dt = extract_datetime(f)
        if dt and (latest_dt is None or dt > latest_dt):
            latest_dt = dt
            latest_file = f

    print(f"Loading latest {model_name} file: {latest_file}")
    with open(f"{directory}/{latest_file}", "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df["model"] = model_name
    return df

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

        plt.savefig(f"graphsExtended/{metric}_{t}.png")
        plt.close()
    
        print(f"Plot of {ylabel} vs Parameter Value for type '{t}' saved.")

def plot_scatter_runtime_objective(df):
    """Scatter plot to detect relationships between runtime and objective."""
    plt.figure(figsize=(8,5))
    plt.scatter(df["num_pickers"], df["runtime"])
    plt.title("Runtime vs Number of Pickers")
    plt.xlabel("Number of Pickers")
    plt.ylabel("Runtime (s)")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(f"graphsExtended/runtime_vs_objective.png")
    plt.close()

    print("Scatter plot of Runtime vs Number of Pickers saved.")

def pie_chart_valid(df):
    """Pie chart showing the proportion of valid vs invalid solutions."""
    valid_counts = df['is_valid'].value_counts()

    plt.figure(figsize=(6,6))
    plt.pie(valid_counts, labels=valid_counts.index, autopct='%1.1f%%', startangle=140)
    plt.title("Proportion of Valid vs Invalid Solutions")
    plt.tight_layout()

    plt.savefig("graphsExtended/valid_solutions_pie_chart.png")
    plt.close()

    print("Pie chart of valid vs invalid solutions saved.")


def plot_comparison_scatter(df_original, df_extended, metric, ylabel):
    """Create line charts comparing original vs extended results using means."""
    unique_types = set(df_original["type"].unique()) | set(df_extended["type"].unique())
    
    for t in unique_types:
        plt.figure(figsize=(10, 6))
        
        # Filter data for this type
        subset_original = df_original[df_original["type"] == t]
        subset_extended = df_extended[df_extended["type"] == t]
        
        # Plot means as line charts
        if not subset_original.empty:
            grouped_original = subset_original.groupby("param_value", as_index=False)[metric].mean()
            grouped_original = sort_param_values(grouped_original)
            
            # For travel times, we need to handle categorical x-axis
            if grouped_original['param_value'].astype(str).isin(['short', 'medium', 'long']).any():
                order_map = {'short': 0, 'medium': 1, 'long': 2}
                x_vals = grouped_original['param_value'].map(order_map)
                plt.plot(x_vals, grouped_original[metric], 
                        label="Original", marker='o', linewidth=2)
            else:
                x_vals = pd.to_numeric(grouped_original['param_value'])
                plt.plot(x_vals, grouped_original[metric], 
                        label="Original", marker='o', linewidth=2)
        
        if not subset_extended.empty:
            grouped_extended = subset_extended.groupby("param_value", as_index=False)[metric].mean()
            grouped_extended = sort_param_values(grouped_extended)
            
            # For travel times, we need to handle categorical x-axis
            if grouped_extended['param_value'].astype(str).isin(['short', 'medium', 'long']).any():
                order_map = {'short': 0, 'medium': 1, 'long': 2}
                x_vals = grouped_extended['param_value'].map(order_map)
                plt.plot(x_vals, grouped_extended[metric], 
                        label="Extended", marker='s', linewidth=2)
                # Set custom x-tick labels
                plt.xticks([0, 1, 2], ['short', 'medium', 'long'])
            else:
                x_vals = pd.to_numeric(grouped_extended['param_value'])
                plt.plot(x_vals, grouped_extended[metric], 
                        label="Extended", marker='s', linewidth=2)
        
        plt.title(f"{ylabel} Comparison: Original vs Extended ({t})")
        plt.xlabel("Parameter value")
        plt.ylabel(ylabel)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(f"graphsExtended/comparison_{metric}_{t}.png")
        plt.close()
        
        print(f"Comparison line chart for {ylabel} ({t}) saved.")

# ---------------------------
# Generate all graphs
# ---------------------------

df_original = load_latest_result("results", "Simulated Annealing")
df_extended = load_latest_result("resultsExtended", "Simulated Annealing Extended")

numeric_columns = ["runtime", "visited_nodes", "num_pickers"]
for df in [df_original, df_extended]:
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # Convert runtime from milliseconds to seconds
    df["runtime"] = df["runtime"] / 1000

df = pd.concat([df_original, df_extended], ignore_index=True)

# Generate extended-only plots
plot_metric_by_param(df_extended, "runtime", "Runtime (s)")
plot_metric_by_param(df_extended, "num_pickers", "Amount of Pickers")
plot_metric_by_param(df_extended, "visited_nodes", "Visited Nodes")

plot_scatter_runtime_objective(df_extended)

pie_chart_valid(df_extended)

# Generate comparison scatter plots
print("\nGenerating comparison plots...")
plot_comparison_scatter(df_original, df_extended, "runtime", "Runtime (s)")
plot_comparison_scatter(df_original, df_extended, "num_pickers", "Amount of Pickers")
plot_comparison_scatter(df_original, df_extended, "visited_nodes", "Visited Nodes")

print("\nAll graphs generated!")