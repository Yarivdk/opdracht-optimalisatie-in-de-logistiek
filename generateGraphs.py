import json
import matplotlib.pyplot as plt
import pandas as pd
import os

# ---------------------------
# Generic plotting functions
# ---------------------------

def plot_metric_by_param(df, metric, ylabel, typeResults):
    """Plot a given metric (runtime, iterations, objective) grouped by 'type'."""
    unique_types = df["type"].unique()

    for t in unique_types:
        subset = df[df["type"] == t]

        grouped = subset.groupby("param_value", as_index=False)[metric].mean()

         # Try to sort numerically if possible
        try:
            grouped["param_value_numeric"] = pd.to_numeric(grouped["param_value"])
            grouped = grouped.sort_values("param_value_numeric")
            x = grouped["param_value_numeric"]
        except:
            x = grouped["param_value"]  # keep categorical order

        y = grouped[metric]

        plt.figure(figsize=(8,5))
        plt.plot(x, y, marker="o")
        plt.title(f"{ylabel} vs Parameter Value ({t})")
        plt.xlabel("Parameter value")
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.tight_layout()

        plt.savefig(f"graphs/{typeResults}/{metric}_{t}.png")
        plt.close()


def plot_scatter_runtime_objective(df, typeResults):
    """Scatter plot to detect relationships between runtime and objective."""
    plt.figure(figsize=(8,5))
    plt.scatter(df["num_pickers"], df["runtime"])
    plt.title("Runtime vs Number of Pickers")
    plt.xlabel("Number of Pickers")
    plt.ylabel("Runtime (ms)")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(f"graphs/{typeResults}/runtime_vs_objective.png")
    plt.close()


def bar_chart_metric(df, metric, ylabel, typeResults):
    """Bar chart of averaged metrics grouped by type and param_value."""
    grouped = df.groupby(["type", "param_value"], as_index=False)[metric].mean()

    plt.figure(figsize=(12,5))
    labels = grouped["type"] + " - " + grouped["param_value"].astype(str)
    plt.bar(labels, grouped[metric])

    plt.title(f"Averaged {ylabel} per Type/Value")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel(ylabel)
    plt.tight_layout()

    plt.savefig(f"graphs/{typeResults}/bar_{metric}.png")
    plt.close()


# ---------------------------
# Generate all graphs
# ---------------------------

# ---------------------------
# Load your JSON file
# ---------------------------
for typeResults in ["simulatedAnnealingResults", "hexalyResults"]:
    files = os.listdir(typeResults)
    json_files = [f for f in files if f.startswith("results_") and f.endswith(".json")]
    json_files.sort(reverse=True)  # sort descending to get the latest first
    latest_file = json_files[0]
    with open(f"{typeResults}/{latest_file}", "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # Convert numeric fields
    numeric_columns = ["runtime", "iterations", "num_pickers", "visited_nodes"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    plot_metric_by_param(df, "runtime", "Runtime (ms)", typeResults)
    plot_metric_by_param(df, "num_pickers", "Amount of Pickers", typeResults)
    plot_metric_by_param(df, "visited_nodes", "Visited Nodes", typeResults)

    plot_scatter_runtime_objective(df)

    bar_chart_metric(df, "runtime", "Runtime", typeResults)
    bar_chart_metric(df, "visited_nodes", "Visited Nodes", typeResults)

    print("Graphs generated!")
    break # Remove break to process both result types
