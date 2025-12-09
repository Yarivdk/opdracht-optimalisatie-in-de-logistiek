import random
import math
import copy
import json

class OrderPickingProblem:
    def __init__(self, instance):
        self.num_pickers = instance["amountOrderPickers"]
        self.capacity = instance["capacity"]
        self.max_time = instance["maxTimePerRound"]
        self.num_warehouses = instance["amountWarehouses"]
        self.product_locations = instance["productLocations"]
        self.travel_times = instance["travelTimeMatrix"]
        self.items = instance["items"]
        self.max_rounds = instance["maxRoundsPerOrderPicker"]
        
    def calculate_route_time(self, route):
        """Calculate total time for a route including depot returns"""
        if not route:
            return 0
        
        time = 0
        # Start from depot (-1) to first location
        time += self.travel_times[-1][self.product_locations[route[0]]]
        
        # Travel between locations
        for i in range(len(route) - 1):
            loc1 = self.product_locations[route[i]]
            loc2 = self.product_locations[route[i + 1]]
            time += self.travel_times[loc1][loc2]
        
        # Return to depot
        time += self.travel_times[self.product_locations[route[-1]]][-1]
        
        return time
    
    def evaluate_solution(self, solution, num_pickers):
        """
        Evaluate a solution for a fixed number of pickers
        solution = list of routes for exactly num_pickers pickers
        Returns: (penalty, is_valid)
        
        Penalty components:
        - Missing items: very high penalty
        - Duplicate items: high penalty
        - Capacity violations: high penalty
        - Time violations: medium penalty
        """
        items_collected = []
        penalty = 0
        
        for picker_routes in solution:
            picker_time = 0
            for route in picker_routes:
                if not route:
                    continue
                
                # Penalize capacity constraint violations
                if len(route) > self.capacity:
                    capacity_violation = len(route) - self.capacity
                    penalty += capacity_violation * 1000
                
                # Penalize time constraint violations
                route_time = self.calculate_route_time(route)
                picker_time += route_time 
                
                items_collected.extend(route)
                
            if picker_time > self.max_time:
                    time_violation = picker_time - self.max_time
                    penalty += time_violation * 50
        
        # Penalize missing items
        missing_items = len(self.items) - len(set(items_collected))
        if missing_items > 0:
            penalty += missing_items * 2000
        
        # Penalize duplicate items
        duplicate_items = len(items_collected) - len(set(items_collected))
        if duplicate_items > 0:
            penalty += duplicate_items * 1500
        
        # Check if solution is valid
        is_valid = (penalty == 0)
        
        return penalty, is_valid


def create_initial_solution(problem, num_pickers):
    """Create initial solution for exactly num_pickers pickers"""
    items = problem.items.copy()
    random.shuffle(items)
    
    # Distribute items evenly across pickers
    solution = [[] for _ in range(num_pickers)]
    items_per_picker = len(items) // num_pickers
    extra_items = len(items) % num_pickers
    
    item_idx = 0
    for picker_idx in range(num_pickers):
        # Determine how many items this picker should get
        picker_items_count = items_per_picker + (1 if picker_idx < extra_items else 0)
        picker_items = items[item_idx:item_idx + picker_items_count]
        item_idx += picker_items_count
        
        # Split into routes respecting capacity
        picker_routes = []
        for i in range(0, len(picker_items), problem.capacity):
            route = picker_items[i:i + problem.capacity]
            picker_routes.append(route)
        
        solution[picker_idx] = picker_routes
    
    return solution


def generate_neighbor(solution, problem, num_pickers):
    """Generate neighbor solution using various operators"""
    neighbor = copy.deepcopy(solution)
    
    # Choose operator based on solution structure
    operators = ['swap_items', 'move_item', 'split_route', 'merge_routes', 'reorder_route']
    operator = random.choice(operators)
    
    # Find non-empty pickers
    non_empty = [i for i, picker in enumerate(neighbor) if any(route for route in picker)]
    
    if not non_empty:
        return neighbor
    
    if operator == 'swap_items' and len(non_empty) >= 2:
        # Swap two items between different pickers
        p1, p2 = random.sample(non_empty, 2)
        routes1 = [r for r in neighbor[p1] if r]
        routes2 = [r for r in neighbor[p2] if r]
        
        if routes1 and routes2:
            r1 = random.choice(routes1)
            r2 = random.choice(routes2)
            if r1 and r2:
                i1 = random.randint(0, len(r1) - 1)
                i2 = random.randint(0, len(r2) - 1)
                r1[i1], r2[i2] = r2[i2], r1[i1]
    
    elif operator == 'move_item':
        # Move one item from one picker to another
        p1 = random.choice(non_empty)
        routes1 = [r for r in neighbor[p1] if r]
        
        if routes1:
            r1 = random.choice(routes1)
            if r1:
                item = r1.pop(random.randint(0, len(r1) - 1))
                
                # Choose a different picker
                other_pickers = [i for i in range(num_pickers) if i != p1]
                if other_pickers:
                    p2 = random.choice(other_pickers)
                    
                    # Add to existing route or create new one
                    if neighbor[p2] and neighbor[p2][0]:
                        neighbor[p2][0].append(item)
                    else:
                        neighbor[p2] = [[item]]
                
                # Clean up empty routes
                neighbor[p1] = [r for r in neighbor[p1] if r]
    
    elif operator == 'split_route' and non_empty:
        # Split a route into two
        p = random.choice(non_empty)
        routes = [r for r in neighbor[p] if r and len(r) > 1]
        
        if routes:
            route = random.choice(routes)
            split_point = random.randint(1, len(route) - 1)
            route1 = route[:split_point]
            route2 = route[split_point:]
            
            # Replace the route with split routes
            route_idx = neighbor[p].index(route)
            neighbor[p][route_idx] = route1
            neighbor[p].insert(route_idx + 1, route2)
    
    elif operator == 'merge_routes' and non_empty:
        # Merge two routes from the same picker
        p = random.choice(non_empty)
        routes = [r for r in neighbor[p] if r]
        
        if len(routes) >= 2:
            r1, r2 = random.sample(routes, 2)
            merged = r1 + r2
            
            # Remove old routes and add merged
            neighbor[p] = [r for r in neighbor[p] if r not in [r1, r2]]
            neighbor[p].append(merged)
    
    elif operator == 'reorder_route' and non_empty:
        # Randomly reorder items in a route (for better travel time)
        p = random.choice(non_empty)
        routes = [r for r in neighbor[p] if r and len(r) > 1]
        
        if routes:
            route = random.choice(routes)
            random.shuffle(route)
    
    return neighbor


def simulated_annealing_fixed_pickers(problem, num_pickers, T0=100, alpha=0.95, 
                                      max_iter_per_temp=100, stagnation_threshold=30):
    """
    Run SA for a fixed number of pickers
    Returns the best solution found and whether it's valid
    """
    current_solution = create_initial_solution(problem, num_pickers)
    current_penalty, is_valid = problem.evaluate_solution(current_solution, num_pickers)
    
    best_solution = copy.deepcopy(current_solution)
    best_penalty = current_penalty
    best_valid = is_valid
    
    T = T0
    stagnation_counter = 0
    visited_nodes = 0
    
    while stagnation_counter < stagnation_threshold:
        accepted_moves = 0
        for iteration in range(max_iter_per_temp):
            neighbor = generate_neighbor(current_solution, problem, num_pickers)
            neighbor_penalty, neighbor_valid = problem.evaluate_solution(neighbor, num_pickers)
            visited_nodes += 1
            
            # Calculate delta
            delta = neighbor_penalty - current_penalty
            
            # Accept or reject
            if delta < 0 or random.random() < math.exp(-delta / T):
                current_solution = neighbor
                current_penalty = neighbor_penalty
                accepted_moves += 1
                
                # Update best
                if neighbor_penalty < best_penalty:
                    best_solution = copy.deepcopy(neighbor)
                    best_penalty = neighbor_penalty
                    best_valid = neighbor_valid
        
        # Check stagnation
        if accepted_moves < max_iter_per_temp * 0.01:
            stagnation_counter += 1
        else:
            stagnation_counter = 0
        
        T *= alpha
        
        if T < 0.01:
            break
    
    return best_solution, best_valid, best_penalty, visited_nodes


def iterative_simulated_annealing(problem, logging=False, T0=100, alpha=0.95, max_iter_per_temp=100,
                                  stagnation_threshold=30, max_pickers=None):
    """
    Iteratively try to find valid solution with minimum number of pickers
    Start with 1 picker and increase until valid solution is found
    """
    if max_pickers is None:
        max_pickers = problem.num_pickers
    
    if logging:
        print("=== ITERATIVE SIMULATED ANNEALING ===")
        print(f"Total items to collect: {len(problem.items)}")
        print(f"Capacity per route: {problem.capacity}")
        print(f"Max time per route: {problem.max_time}")
        print()
    
    total_visited = 0
    optimization_results = []
    
    # Calculate theoretical minimum pickers needed
    min_pickers_capacity = math.ceil(len(problem.items) / problem.capacity)
    if logging:
        print(f"Theoretical minimum (capacity only): {min_pickers_capacity} pickers\n")
    
    best_solution = None
    best_num_pickers = None
    
    for num_pickers in range(1, max_pickers + 1):
        if logging:
            print(f"--- Trying with {num_pickers} picker{'s' if num_pickers > 1 else ''} ---")
        
        solution, is_valid, penalty, visited = simulated_annealing_fixed_pickers(
            problem, num_pickers, T0, alpha, max_iter_per_temp, stagnation_threshold
        )
        
        total_visited += visited
        
        if is_valid:
            if logging:
                print(f"✓ Valid solution found with {num_pickers} picker{'s' if num_pickers > 1 else ''}!")
            best_solution = solution
            best_num_pickers = num_pickers
            best_valid = is_valid
            optimization_results.append(num_pickers)
            break
        else:
            if logging:
                print(f"✗ No valid solution found (penalty: {penalty:.0f})")
            optimization_results.append(float('inf'))
    
    if best_solution is None:
        if logging:
            print(f"\n⚠ Could not find valid solution with up to {max_pickers} pickers")
        # Return best attempt
        best_num_pickers = max_pickers
        best_solution, best_valid, _, _ = simulated_annealing_fixed_pickers(
            problem, max_pickers, T0, alpha, max_iter_per_temp, stagnation_threshold
        )
    
    return total_visited, (best_num_pickers, best_solution, best_valid), optimization_results
    
    