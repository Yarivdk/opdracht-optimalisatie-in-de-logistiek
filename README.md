# Order Picking Optimization in Logistics

This project implements and compares two optimization approaches for solving the **Order Picking Problem** in warehouse logistics: **Hexaly Optimizer** (commercial solver) and **Simulated Annealing** (metaheuristic algorithm).

## Problem Description

The Order Picking Problem involves optimizing the assignment of items to order pickers in a warehouse setting with the following constraints:

- **Order Pickers**: Fixed number of available order pickers
- **Capacity**: Maximum number of items per route
- **Time Limit**: Maximum time per round for each picker
- **Warehouses**: Multiple warehouse locations with travel time matrix
- **Items**: List of items to be collected, each at a specific warehouse location
- **Routes**: Each picker can make multiple rounds (routes)

**Objective**: Minimize the number of order pickers needed while ensuring all items are collected within capacity and time constraints.

## Project Structure

```
├── hexaly/                          # Hexaly Optimizer implementation
│   ├── boxexpress.hxm              # Hexaly Modeler model definition
│   ├── model.py                    # Python wrapper for Hexaly model
│   ├── runOneInstance.py           # Run single instance
│   ├── runAllInstances.py          # Batch processing
│   ├── instanceGenerator.py        # Generate test instances
│   ├── generateGraphs.py           # Visualization of results
│   ├── instances/                  # Test instances (JSON)
│   ├── results/                    # Solver output results
│   └── graphs/                     # Generated performance graphs
│
├── simulatedAnnealing/             # Simulated Annealing implementation
│   ├── simulatedAnnealing.py       # SA algorithm implementation
│   ├── runOneInstance.py           # Run single instance
│   ├── runAllInstances.py          # Batch processing
│   ├── instanceGenerator.py        # Generate test instances
│   ├── generateGraphs.py           # Visualization of results
│   ├── *Extended.py                # Extended problem variant files
│   ├── instances/                  # Test instances (JSON)
│   ├── results/                    # Algorithm output results
│   └── graphs/                     # Generated performance graphs
│
├── .github/workflows/              # GitHub Actions CI/CD pipelines
│   ├── runOneInstance.yml         # Run single instance workflow
│   ├── runAllInstances.yml        # Batch run workflow
│   ├── generateInstances.yml      # Instance generation workflow
│   └── generateGraphs.yml         # Graph generation workflow
│
└── requirements.txt               # Python dependencies
```

## Installation

### Prerequisites

- Python 3.11+
- [Hexaly Optimizer](https://www.hexaly.com/) (for Hexaly approach)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd opdracht-optimalisatie-in-de-logistiek
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. For Hexaly approach, install Hexaly Optimizer:
```bash
pip install hexaly -i https://pip.hexaly.com
```

4. Set up Hexaly license (required for Hexaly approach):
   - Create a `hexaly.license` file in the `hexaly/` directory
   - Or set the `HEXALY_LICENSE` environment variable

## Usage

### Running Single Instance

#### Hexaly Approach
```bash
cd hexaly
python runOneInstance.py instances/instance-1_amountItems-5.json
```

#### Simulated Annealing Approach
```bash
cd simulatedAnnealing
python runOneInstance.py instances/instance-1_amountItems-5.json
```

### Running All Instances (Batch Mode)

```bash
# Hexaly
cd hexaly
python runAllInstances.py

# Simulated Annealing
cd simulatedAnnealing
python runAllInstances.py
```

### Generating Test Instances

```bash
# Hexaly instances
cd hexaly
python instanceGenerator.py

# Simulated Annealing instances
cd simulatedAnnealing
python instanceGenerator.py
```

### Generating Performance Graphs

```bash
# Hexaly results
cd hexaly
python generateGraphs.py

# Simulated Annealing results
cd simulatedAnnealing
python generateGraphs.py
```

## Instance Format

Instances are stored as JSON files with the following structure:

```json
{
    "amountOrderPickers": 10,
    "capacity": 5,
    "maxTimePerRound": 60,
    "amountWarehouses": 10,
    "productLocations": [5, 7, 2, 9, 1, 3, 4, 8, 6, 0],
    "travelTimeMatrix": [[999, 3, 5, ...], ...],
    "items": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    "maxRoundsPerOrderPicker": 10
}
```

**Key Fields**:
- `amountOrderPickers`: Number of available pickers
- `capacity`: Maximum items per route
- `maxTimePerRound`: Time limit per picker per round
- `amountWarehouses`: Number of warehouse locations (including depot)
- `productLocations`: Maps item IDs to warehouse locations
- `travelTimeMatrix`: Symmetric travel time matrix (depot is last index -1)
- `items`: List of item IDs to collect
- `maxRoundsPerOrderPicker`: Maximum routes per picker

## Solution Output

Both solvers output results in JSON format:

```json
{
    "runtime": 1234,              // Execution time (ms or seconds)
    "visited_nodes": 5678,        // Nodes/iterations visited
    "num_pickers": 3,             // Number of pickers used (objective)
    "is_valid": true,             // Whether solution is feasible
    "best_bound": 2.8,            // Best known lower bound (if available)
    "gap": 0.05                   // Optimality gap (if available)
}
```

## Algorithms

### Hexaly Optimizer

The Hexaly implementation uses the **LocalSolver/Hexaly Modeler** language to define:
- Decision variables for routes per picker
- Constraints for item coverage, capacity, and time limits
- Objective to minimize active order pickers

The model leverages Hexaly's hybrid optimization engine combining local search, constraint programming, and mathematical programming.

### Simulated Annealing

The Simulated Annealing implementation features:
- **Iterative approach**: Starts with minimum pickers and increases until feasible
- **Temperature schedule**: Geometric cooling with α=0.95, T₀=100
- **Neighborhood operators**:
  - `swap_items`: Swap items between pickers
  - `move_item`: Move item from one picker to another
  - `split_route`: Split a route into two
  - `merge_routes`: Combine two routes
  - `reorder_route`: Reorder items in a route
- **Penalty-based evaluation**: Handles infeasible solutions during search
- **Stagnation detection**: Stops early if no improvement

## GitHub Actions Workflows

The project includes automated workflows:

- **Run One Instance**: Test a specific instance with chosen solver
- **Run All Instances**: Batch process all instances
- **Generate Instances**: Create new test instances
- **Generate Graphs**: Produce performance visualizations

Workflows support both Hexaly and Simulated Annealing approaches, with options for standard and extended problem variants.

## Performance Comparison

Results are compared across multiple dimensions:
- **Runtime**: Execution time to find solutions
- **Solution Quality**: Number of pickers used (lower is better)
- **Feasibility**: Percentage of valid solutions found
- **Scalability**: Performance on different instance sizes

Use `generateGraphs.py` to visualize comparative performance across parameter variations (item count, capacity, travel times).

## Instance Parameters

The instance generators create diverse test cases by varying:
- **Item count**: 5 to 125 items (in steps of 5)
- **Travel time scales**: short (1-10), medium (10-20), long (20-30)
- Each configuration is repeated 5 times with different random seeds

## Dependencies

Key Python packages:
- `pandas`: Data manipulation and analysis
- `matplotlib`: Visualization and plotting
- `numpy`: Numerical operations
- `pytz`: Timezone handling for timestamps
- `hexaly`: Commercial optimization solver (optional)
