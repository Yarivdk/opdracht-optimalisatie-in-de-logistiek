import json
import matplotlib.pyplot as plt
import pandas as pd

import json
import matplotlib.pyplot as plt
import pandas as pd

# ---------------------------
# Load your JSON file
# ---------------------------
with open("results.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Convert numeric fields
numeric_columns = ["runtime", "iterations", "objective_value"]
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ---------------------------
# Generic plotting functions
# ---------------------------

def plot_metric_by_param(df, metric, ylabel):
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

        plt.savefig(f"graphs/{metric}_{t}.png")
        plt.close()


def plot_scatter_runtime_objective(df):
    """Scatter plot to detect relationships between runtime and objective."""
    plt.figure(figsize=(8,5))
    plt.scatter(df["objective_value"], df["runtime"])
    plt.title("Runtime vs Objective Value")
    plt.xlabel("Objective value")
    plt.ylabel("Runtime (s)")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig("graphs/runtime_vs_objective.png")
    plt.close()


def bar_chart_metric(df, metric, ylabel):
    """Bar chart of averaged metrics grouped by type and param_value."""
    grouped = df.groupby(["type", "param_value"], as_index=False)[metric].mean()

    plt.figure(figsize=(12,5))
    labels = grouped["type"] + " - " + grouped["param_value"].astype(str)
    plt.bar(labels, grouped[metric])

    plt.title(f"Averaged {ylabel} per Type/Value")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel(ylabel)
    plt.tight_layout()

    plt.savefig(f"graphs/bar_{metric}.png")
    plt.close()

# ---------------------------
# Generate all graphs
# ---------------------------

plot_metric_by_param(df, "runtime", "Runtime (s)")
plot_metric_by_param(df, "objective_value", "Objective Value")
plot_metric_by_param(df, "iterations", "Iterations")

plot_scatter_runtime_objective(df)

bar_chart_metric(df, "runtime", "Runtime")
bar_chart_metric(df, "objective_value", "Objective Value")

print("Graphs generated!")
