import random
import math
import copy
import json
from collections import defaultdict

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
        self.categories = instance["categories"]
        self.product_categories = instance["productCategories"]
        self.picker_categories = instance["orderPickerCategories"]
    
    def can_picker_pick_item(self, picker_id, item_id):
        """Check if a picker can pick a specific item based on category constraints"""
        if not self.picker_categories or not self.product_categories:
            # No category constraints
            return True
        
        picker_category = self.picker_categories[picker_id]
        product_category = self.product_categories[item_id]
        
        # If either doesn't have a category assigned, allow
        if picker_category is None or product_category is None:
            return True
        
        return picker_category == product_category
    
    def get_valid_items_for_picker(self, picker_id):
        """Get list of items that a picker can collect"""
        return [item for item in self.items if self.can_picker_pick_item(picker_id, item)]
    
    def get_categories_needed(self):
        """Get set of categories that need to be covered based on items"""
        if not self.product_categories:
            return set()
        
        categories_needed = set()
        for item in self.items:
            cat = self.product_categories[item]
            if cat:
                categories_needed.add(cat)
        return categories_needed
    
    def get_pickers_by_category(self):
        """Group available pickers by their category"""
        pickers_by_cat = defaultdict(list)
        for picker_id in range(self.num_pickers):
            cat = self.picker_categories[picker_id]
            if cat:
                pickers_by_cat[cat].append(picker_id)
        return pickers_by_cat

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
        - Category violations: very high penalty
        - Capacity violations: high penalty
        - Time violations: medium penalty
        """
        items_collected = []
        penalty = 0

        for picker_id, picker_routes in solution.items():
            picker_time = 0
            for route in picker_routes:
                if not route:
                    continue
                
                # Check category constraints
                for item in route:
                    if not self.can_picker_pick_item(picker_id, item):
                        penalty += 2500  # Very high penalty for category violation
                
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


def select_diverse_pickers(problem, num_pickers, max_pickers=None):
    """
    Select the minimal number of pickers required per category
    based on item load. Guarantees feasibility if possible.
    """
    if max_pickers is None:
        max_pickers = problem.num_pickers

    all_available_pickers = list(range(max_pickers))

    if not problem.categories or not problem.picker_categories:
       return all_available_pickers[:num_pickers]
    
    pickers_by_cat = problem.get_pickers_by_category()

    # Count items per category
    items_per_category = defaultdict(int)
    for item in problem.items:
        cat = problem.product_categories[item]
        items_per_category[cat] += 1

    selected = []

    # STEP 1 — ensure every category gets the minimum required number of pickers
    for cat, item_count in items_per_category.items():
        # how many pickers exist for this category?
        available = pickers_by_cat.get(cat, [])
        if not available:
            continue  # no picker available → infeasible instance, nothing to do

        # how many pickers do we need?
        needed = math.ceil(item_count / problem.capacity)

        # clamp to available pickers
        needed = min(needed, len(available))

        # choose needed pickers
        chosen = random.sample(available, needed)
        selected.extend(chosen)

    # STEP 2 — if still fewer than num_pickers, fill up with any pickers
    if len(selected) < num_pickers:
        remaining = [p for p in all_available_pickers if p not in selected]

        needed_extra = num_pickers - len(selected)
        extra = remaining[:needed_extra]
        selected.extend(extra)

    # STEP 3 — if overshoot (rare), trim randomly
    if len(selected) > num_pickers:
        selected = random.sample(selected, num_pickers)

    return selected



def create_initial_solution(problem, num_pickers, selected_pickers=None):
    if selected_pickers is None:
        selected_pickers = select_diverse_pickers(problem, num_pickers)
    
    # Initial empty routes
    picker_assignment = {i: [] for i in selected_pickers}

    # Assign each item exactly once
    for item in problem.items:
        # welke pickers mogen dit item ophalen?
        valid_pickers = [
            picker for picker in selected_pickers
            if problem.can_picker_pick_item(picker, item)
        ]

        # kies random één van de toegestane pickers
        if valid_pickers:
            chosen = random.choice(valid_pickers)
            picker_assignment[chosen].append(item)
        else:
            # GEEN picker kan dit item ophalen → fout in instance?
            # Voor nu gooien we het bij een random picker (zonder crash)
            chosen = random.choice(selected_pickers)
            picker_assignment[chosen].append(item)

    # routes splitsen volgens capaciteit
    solution = {}
    for picker, items in picker_assignment.items():
        routes = []
        for i in range(0, len(items), problem.capacity):
            routes.append(items[i:i+problem.capacity])
        solution[picker] = routes
    
    return solution, selected_pickers


def generate_neighbor(solution, problem, selected_pickers):
    """Generate neighbor solution using various operators respecting category constraints"""
    neighbor = copy.deepcopy(solution)
    
    # Choose operator based on solution structure
    operators = ['swap_items', 'move_item', 'split_route', 'merge_routes', 'reorder_route']
    operator = random.choice(operators)
    
    # Find non-empty pickers
    non_empty = [picker for picker in neighbor if any(route for route in neighbor[picker])]
    
    if not non_empty:
        return neighbor
    
    if operator == 'swap_items' and len(non_empty) >= 2:
        # Swap two items between different pickers (respecting categories)
        attempts = 0
        max_attempts = 10
        
        while attempts < max_attempts:
            idx1, idx2 = random.sample(non_empty, 2)
            routes1 = [r for r in neighbor[idx1] if r]
            routes2 = [r for r in neighbor[idx2] if r]
            
            if routes1 and routes2:
                r1 = random.choice(routes1)
                r2 = random.choice(routes2)
                if r1 and r2:
                    i1 = random.randint(0, len(r1) - 1)
                    i2 = random.randint(0, len(r2) - 1)
                    item1, item2 = r1[i1], r2[i2]
                    
                    # Check if swap respects category constraints
                    if (problem.can_picker_pick_item(idx1, item2) and 
                        problem.can_picker_pick_item(idx2, item1)):
                        r1[i1], r2[i2] = item2, item1
                        break
            
            attempts += 1
    
    elif operator == 'move_item':
        # Move one item from one picker to another (respecting categories)
        idx1 = random.choice(non_empty)
        routes1 = [r for r in neighbor[idx1] if r]
        
        if routes1:
            r1 = random.choice(routes1)
            if r1:
                item_idx = random.randint(0, len(r1) - 1)
                item = r1[item_idx]
                
                # Find pickers that can handle this item
                valid_target_indices = [i for i in selected_pickers
                                       if i != idx1 and 
                                       problem.can_picker_pick_item(i, item)]
                
                if valid_target_indices:
                    idx2 = random.choice(valid_target_indices)
                    r1.pop(item_idx)
                    
                    # Add to existing route or create new one
                    if neighbor[idx2] and neighbor[idx2][0]:
                        neighbor[idx2][0].append(item)
                    else:
                        neighbor[idx2] = [[item]]
                
                # Clean up empty routes
                neighbor[idx1] = [r for r in neighbor[idx1] if r]
    
    elif operator == 'split_route' and non_empty:
        # Split a route into two
        idx = random.choice(non_empty)
        routes = [r for r in neighbor[idx] if r and len(r) > 1]
        
        if routes:
            route = random.choice(routes)
            split_point = random.randint(1, len(route) - 1)
            route1 = route[:split_point]
            route2 = route[split_point:]
            
            # Replace the route with split routes
            route_idx = neighbor[idx].index(route)
            neighbor[idx][route_idx] = route1
            neighbor[idx].insert(route_idx + 1, route2)
    
    elif operator == 'merge_routes' and non_empty:
        # Merge two routes from the same picker
        idx = random.choice(non_empty)
        routes = [r for r in neighbor[idx] if r]
        
        if len(routes) >= 2:
            r1, r2 = random.sample(routes, 2)
            merged = r1 + r2
            
            # Remove old routes and add merged
            neighbor[idx] = [r for r in neighbor[idx] if r not in [r1, r2]]
            neighbor[idx].append(merged)
    
    elif operator == 'reorder_route' and non_empty:
        # Randomly reorder items in a route (for better travel time)
        idx = random.choice(non_empty)
        routes = [r for r in neighbor[idx] if r and len(r) > 1]
        
        if routes:
            route = random.choice(routes)
            random.shuffle(route)
    
    return neighbor


def simulated_annealing_fixed_pickers(problem, num_pickers, selected_pickers, T0=100, alpha=0.95, 
                                      max_iter_per_temp=100, stagnation_threshold=30):
    """
    Run SA for a fixed number of pickers
    Returns the best solution found and whether it's valid
    """
    current_solution, selected_pickers = create_initial_solution(problem, num_pickers, selected_pickers)
    current_penalty, is_valid = problem.evaluate_solution(current_solution, num_pickers)
    
    best_solution = copy.deepcopy(current_solution)
    best_penalty = current_penalty
    best_valid = is_valid
    best_pickers = selected_pickers.copy()
    
    T = T0
    stagnation_counter = 0
    visited_nodes = 0
    
    while stagnation_counter < stagnation_threshold:
        accepted_moves = 0
        for iteration in range(max_iter_per_temp):
            neighbor = generate_neighbor(current_solution, problem, selected_pickers)
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
    
    return best_solution, best_valid, best_penalty, visited_nodes, best_pickers

def iterative_simulated_annealing(problem, logging=False, T0=100, alpha=0.95, max_iter_per_temp=100,
                                  stagnation_threshold=30, max_pickers=None):
    """
    Iteratively try to find valid solution with minimum number of pickers
    Start with 1 picker and increase until valid solution is found
    """
    if max_pickers is None:
        max_pickers = problem.num_pickers
    
    if logging:
        print("=== ITERATIVE SIMULATED ANNEALING (with Categories) ===")
        print(f"Total items to collect: {len(problem.items)}")
        print(f"Capacity per route: {problem.capacity}")
        print(f"Max time per route: {problem.max_time}")
        if problem.categories:
            print(f"Categories: {problem.categories}")
            categories_needed = problem.get_categories_needed()
            print(f"Categories needed for items: {categories_needed}")
            
            # Show picker distribution by category
            pickers_by_cat = problem.get_pickers_by_category()
            print(f"\nPicker distribution by category:")
            for cat in sorted(pickers_by_cat.keys()):
                print(f"  {cat}: {len(pickers_by_cat[cat])} pickers")
        print()
    
    total_visited = 0
    optimization_results = []
    
    # Calculate theoretical minimum pickers needed
    min_pickers_capacity = math.ceil(len(problem.items) / problem.capacity)
    if logging:
        print(f"Theoretical minimum (capacity only): {min_pickers_capacity} pickers\n")
    
    best_solution = None
    best_num_pickers = None
    best_selected_pickers = None
    
    for num_pickers in range(1, max_pickers + 1):
        if problem.categories:
            selected = select_diverse_pickers(problem, num_pickers)
            cats_selected = [problem.picker_categories[p] for p in selected]
        if logging: 
            print(f"--- Trying with {num_pickers} picker{'s' if num_pickers > 1 else ''} ---")
            print(f"    Selected pickers: {selected}")
            print(f"    Categories covered: {set(cats_selected)}")
        
        solution, is_valid, penalty, visited, selected_pickers = simulated_annealing_fixed_pickers(
            problem, num_pickers, selected, T0, alpha, max_iter_per_temp, stagnation_threshold
        )
        
        total_visited += visited
        
        if is_valid:
            if logging:
                print(f"✓ Valid solution found with {num_pickers} picker{'s' if num_pickers > 1 else ''}!")
            best_solution = solution
            best_num_pickers = num_pickers
            best_selected_pickers = selected_pickers
            optimization_results.append(num_pickers)
            best_valid = is_valid
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
        solution, best_valid, _, _, selected_pickers = simulated_annealing_fixed_pickers(
            problem, max_pickers, T0, alpha, max_iter_per_temp, stagnation_threshold
        )
        best_solution = solution
        best_selected_pickers = selected_pickers
    
    result = (best_num_pickers, best_solution, best_valid)
    if best_selected_pickers:
        result = result + (best_selected_pickers,)
    
    return total_visited, result, optimization_results