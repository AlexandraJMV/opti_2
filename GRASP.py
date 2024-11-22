import random
from read import read_instance
from scipy.sparse import dok_matrix
ENE = 5

# Done?
def complete_solution(solution, data):
    """
    Verifica que todas las demandas de los clientes han sido satisfechos.

    Args:
        solution (dok_matrix): Solución actual
        data (dict): Datos de la instancia

    Returns:
        bool: True si se satisface la demanda, False en caso de que no. 
    """
    
    total_assigned = {client: 0 for client in range(data["params"][1])}  # Diccionario con total asignado por cliente 
    
    for (facility, client), proportion in solution.items():               # Suma iterativa de las proporciones asignadas a cada cliente 
        total_assigned[client] += proportion

    return all(
        total_assigned[client] >= data["initial_demand"][client]   # Verifica que el total asignado sea mayor o igual a la demanda de cada cliente
        for client in range(data["params"][1])               # para todos los clientes.
    )

# Done?
def all_candidates(data, solution):
    """
    Builds a list of candidates for assignment based on remaining capacities, client demands, and the current partial solution.

    Args:
        data (dict): Instance data (capacity, demands, costs, etc.)
        solution (dok_matrix): Current partial solution matrix

    Returns:
        list: List of feasible candidates (facility, client) based on current solution state
    """
    candidates = []
    
    # Iterate over all facilities
    for facility in range(data["params"][0]):
        if data["capacity"][facility] > 0:  # Only consider facilities with remaining capacity
            # Iterate over all clients
            for client in range(data["params"][1]):
                if data["demandas"][client] > 0:  # Only consider clients with remaining demand
                    # Check if the client hasn't been fully satisfied yet
                    if solution[facility, client] < 1.0:  # Client not fully satisfied
                        # Check if assigning this client to the facility doesn't exceed capacity
                        current_demand_satisfied = solution[:, client].sum()
                        remaining_capacity = data["capacity"][facility] - current_demand_satisfied
                        
                        if remaining_capacity > 0:  # The facility can still accommodate more of the client's demand
                            candidates.append((facility, client))
    
    return candidates

# Falta expandir
def construct_candidates(data, solution):
    """
    Dada la data y la solución parcial, construye una lista de candidatos para agregar a la solución parcial.
    El procedimiento es:
        1. Crear lista de todos los candidatos posibles
        2. Evaluar cada candidato con una función greedy
        3. Formar lista de candidatos con los mejores N candidatos luego de la evaluación 

    Args:
        data (_type_): Datos que representan la instancia del probelma
    """
    
    all_can = all_candidates(data, solution)
    
    return all_can

# DONE?
def select_candidate(candidate_list, seed):
    """
    Selecciona un candidato aleatorio de la lista.

    Args:
        candidate_list (list): Lista de candidatos posibles
        seed (int): Semilla aleatoria para reproducibilidad

    Returns:
        tuple: Candidato seleccionado (facility, client)
    """
    
    
    if not candidate_list:
        return None
    return random.choice(candidate_list)

def add_candidate(solution, candidate, data):
    """
    Assigns a total demand of a client to a facility, not a proportion.
    
    Args:
        solution (dok_matrix): Current partial solution matrix
        candidate (tuple): Selected candidate (facility, client)
        data (dict): Instance data (e.g., capacities, demands, etc.)
    
    Returns:
        dok_matrix: Updated solution matrix
    """
    facility, client = candidate
    demand = data["demandas"][client]  # Total demand of the client
    capacity = data["capacity"][facility]  # Capacity of the facility

    # Assign as much demand as possible to the facility
    total_assigned_demand = min(demand, capacity)

    # Update the solution by assigning the total demand to the facility
    solution[facility, client] += total_assigned_demand

    # Update the remaining demand and capacity
    data["demandas"][client] -= total_assigned_demand
    data["capacity"][facility] -= total_assigned_demand

    return solution

def evaluate_cost(solution, data):
    """
    Calculates the total cost of the solution.

    Args:
        solution (dok_matrix): Current solution
        data (dict): Instance data

    Returns:
        float: Total cost
    """
    total_cost = 0
    facilities_used = set(i for i, _ in solution.keys() if solution[i, _] > 0)

    # Fixed cost of opening facilities
    total_cost += sum(data["costos_fijos"][facility] for facility in facilities_used)

    # Transportation cost
    for (facility, client), proportion in solution.items():
        if proportion > 0:  # If there's a non-zero assignment
            total_cost += proportion * data["costo"][client][facility]

    return total_cost

def greedy_randomized_construction(seed, data):
    """
    Construye una solución aleatoria usando una estrategia greedy
    Itera hasta formar una solución completa (todas las demandas satisfechas)

    Args:
        seed (int): Seed para la generación de números aleatorios
        data (list):Datos de la instancia
    """
    
    instance_dim = data["params"]                               # Extraer parámetros de la instancia (centros, clientes)
    
    solution = dok_matrix( (instance_dim[0], instance_dim[1]),  # Generar matriz solución
                            dtype= float)
    cost = None                                                 # Costo de la solución 

    while not complete_solution(solution, data):
        
        candidate_list = construct_candidates(data, solution)           # Construír lista de candidatos para la solución 
        
        selection = select_candidate(candidate_list, seed)    # Selección aleatoria de un candidato usando evaluación greedy 
        
        solution = add_candidate(solution, selection, data)         # Agregar candidato a la solución
        cost = evaluate_cost(solution, data)                        # Evaluar costo de la solución resultante 
        
    return solution, cost

def SAS(solution, data):
    """
    Reassigns a portion of a client's demand from one facility to another to reduce cost
    or improve resource utilization while respecting capacity and demand constraints.

    Args:
        solution (dok_matrix): Current solution matrix (centers x clients), where values represent 
                               the amount of demand satisfied by each facility.
        data (dict): Instance data, including capacities, demands, costs, etc.

    Returns:
        dok_matrix: Updated solution matrix after performing a single assignment swap.
    """
    best_solution = solution.copy()  # Copy current solution as the baseline
    best_cost = evaluate_cost(best_solution, data)  # Initial cost of the current solution
    improved = False 
    # Iterate over all assignments in the solution
    for (current_facility, client), assigned_demand in solution.items():
        if assigned_demand <= 0:  # Skip if no demand is currently assigned
            continue

        # Iterate over all alternative facilities (to swap with)
        for alternative_facility in range(data["params"][0]):
            if alternative_facility == current_facility:
                continue  # Skip the current facility

            # Calculate the potential new demand for both facilities
            # Tentatively swap the entire demand between the current and alternative facility
            tentative_solution = best_solution.copy()
            tentative_solution[current_facility, client] -= assigned_demand
            tentative_solution[alternative_facility, client] += assigned_demand

            # Check if this reassignment respects the capacity constraints
            # Ensure that no facility exceeds its original capacity after reassignment
            facility_demand_current = tentative_solution[current_facility, :].sum()  # Total demand in the current facility
            facility_demand_alternative = tentative_solution[alternative_facility, :].sum()  # Total demand in the alternative facility

            if facility_demand_current <= data["initial_capacity"][current_facility] and facility_demand_alternative <= data["initial_capacity"][alternative_facility]:
                # If the solution is feasible, evaluate the cost
                tentative_cost = evaluate_cost(tentative_solution, data)

                # If this reassignment reduces the cost, update the best solution
                if tentative_cost < best_cost:
                    best_solution = tentative_solution
                    best_cost = tentative_cost
                    improved = True

    return best_solution, improved
def facility_opening_closing(solution, data):
    """
    Evaluates whether to open or close a facility to improve the overall solution.
    If closing a facility results in lower cost, it will close the facility and reassign its demand.
    If opening a facility results in lower cost, it will open the facility and reassign demand.
    
    Args:
        solution (dok_matrix): Current solution matrix (centers x clients), where values represent 
                               the amount of demand satisfied by each facility.
        data (dict): Instance data, including capacities, demands, costs, etc.
    
    Returns:
        dok_matrix: Updated solution matrix after performing the facility opening/closing operation.
        bool: True if the solution was improved, False otherwise.
    """
    improved = False
    best_solution = solution.copy()  # Copy current solution as the baseline
    best_cost = evaluate_cost(best_solution, data)  # Initial cost of the current solution
    
    # First, attempt to close facilities that are not serving any clients.
    for facility in range(data["params"][0]):
        # If the facility is currently serving any clients, skip it.
        if solution[facility, :].sum() == 0:
            continue
        
        # Tentatively close the facility by removing all assignments.
        tentative_solution = solution.copy()
        tentative_solution[facility, :] = 0  # Remove all assignments from this facility

        # Reassign demand to other facilities based on the cost and available capacity.
        for client in range(data["params"][1]):
            demand_to_assign = data["demandas"][client] - tentative_solution[:, client].sum()
            
            if demand_to_assign > 0:
                # Find the facility with the lowest cost to serve this client
                min_cost = float('inf')
                best_facility = -1
                for alt_facility in range(data["params"][0]):
                    if alt_facility != facility and tentative_solution[alt_facility, client] < data["initial_capacity"][alt_facility]:
                        cost = data["costo"][client][alt_facility]
                        if cost < min_cost:
                            min_cost = cost
                            best_facility = alt_facility
                
                # Assign demand to the best facility
                if best_facility != -1:
                    tentative_solution[best_facility, client] += demand_to_assign
                    data["demandas"][client] -= demand_to_assign

        # Evaluate if the cost after closure is lower
        tentative_cost = evaluate_cost(tentative_solution, data)
        if tentative_cost < best_cost:
            best_solution = tentative_solution
            best_cost = tentative_cost
            improved = True
    
    # Now, attempt to open closed facilities to improve the solution.
    for facility in range(data["params"][0]):
        # If the facility is already serving clients, skip it.
        if solution[facility, :].sum() > 0:
            continue

        # Tentatively open the facility and reassign demand to it.
        tentative_solution = best_solution.copy()

        for client in range(data["params"][1]):
            demand_to_assign = data["demandas"][client] - tentative_solution[:, client].sum()

            if demand_to_assign > 0:
                # Assign demand to the newly opened facility
                cost = data["costo"][client][facility]
                if cost < float('inf'):
                    tentative_solution[facility, client] += demand_to_assign
                    data["demandas"][client] -= demand_to_assign

        # Evaluate if the cost after opening the facility is lower
        tentative_cost = evaluate_cost(tentative_solution, data)
        if tentative_cost < best_cost:
            best_solution = tentative_solution
            best_cost = tentative_cost
            improved = True

    return best_solution, improved

def find_improvement(solution, data, iter, N):
    improved = False
    
    
    # Dado un número de SAS, hacer FOC
    if iter % N == 0:               
        new, improved =  facility_opening_closing(solution, data)
    new, improved = SAS(solution, data)
    
    if improved:    return new, improved
    else:           return solution, improved

#Done?
def Local_Search(solution, data):
    """
    Mejora la solución iterativamente

    Args:
        solution (dok_matrix): Solución inicial
        data (dict): Datos de la instancia

    Returns:
        dok_matrix: Solución mejorada, en caso de que se hayan logrado mejoras
    """
    improved = True
    i = 1
    while improved:
        new_solution, improved = find_improvement(solution, data, i, N = ENE)
        print("i : ", i)
        if improved:
            solution = new_solution
        else:
            improved = False
            
        i += 1
    return solution, evaluate_cost(solution, data)

#Done?
def Update_Solution(current, best):
    """
    Actualiza la mejor solución encontrada hasta el momento-

    Args:
        current (tuple): Solución actual (solution, cost)
        best (tuple): Mejor solución hasta el momento (solution, cost)

    Returns:
        tuple: Mejor solución entre ambas
    """
    
    print(current)
    print(best)
    if best is None or current[1] < best[1]:
        return current
    return best

from copy import deepcopy

def GRASP(iterations, seed, instance_name):
    
    data = read_instance(instance_name)  # Leer datos de entrada 
    best_Solution = None                 # Almacenamiento de la mejor solución
    
    for _ in range(iterations):          # Iteraciones del algoritmo
        dat = deepcopy(data)
        
        solution, cost = greedy_randomized_construction(seed, dat)         # Se construye una solución
        
        print("generated sol cost", cost)
        
        solution, cost = Local_Search(solution.copy(), dat)                             # Local Search para refinar la solución
        
        best_Solution = Update_Solution((solution, cost), best_Solution)    # Actualizar la mejor solución   

        print("completed?", complete_solution(solution, dat))
        print()
        print("-"*100)
        
    return best_Solution
        
    