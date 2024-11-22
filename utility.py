


def display(instances):
    """
        Muestra las instancias disponibles para su ejecución. 

        Args:
            instances (list): Lista de instancias disponibles
            
    """
    
    # Mostar lista de instancias disponibles con su respectiva dimensión 
    print("Seleccione :")
    for idx, (name, dimension) in enumerate(instances):
        print(f"{idx + 1}: {name} (Dimension: {dimension})")
    
    # Extraer selección 
    while True:
        try:
            choice = int(input("Ingrese el número de su elección: ")) - 1
            if 0 <= choice < len(instances):
                selected_item = instances[choice]
                print(f"Ha seleccionado: {selected_item[0]} (Dim: {selected_item[1]})")
                return selected_item
            else:
                print("Inválido.")
        except ValueError:
            print("Inválido.")

def get_iter():
    """Receives the maximum number of iterations for the algorithm from user input."""
    while True:
        try:
            max_iter = int(input("Introduce el número máximo de iteraciones: "))
            if max_iter > 0:
                return max_iter
            else:
                print("Por favor, ingresa un número positivo.")
        except ValueError:
            print("Entrada inválida. Por favor, ingresa un número entero.")