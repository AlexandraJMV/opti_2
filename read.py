from os import listdir as dir
from os.path import join 

def leer_archivo(arch):
    aux = True
    cap_cost = False
    dem     = False
    
    
    
    capacity = []
    costos_fijos = []
    
    demandas = []
    costo = []
    
    with open(arch, 'r') as file:
        for linea in file:
            
            if 'capacity' in linea:
                linea = linea.replace('capacity', '-1')
                
            
            numeros = [float(n) for n in linea.strip().split()]  # Convertir a lista de números
            
                        # Número de centros, numero de clientes
            if aux:                
                params = [int(i) for i in numeros]   
                aux = False         # No hay que leer más parámetros 
                cap_cost = True     # Ahora se deben leer las capacidades y costos fijos     
            
            elif cap_cost:
                if "." not in linea:
                    cap_cost = False
                    demandas.append(numeros[0])
                else:
                    capacity.append(numeros[0])
                    costos_fijos.append(numeros[1])
            elif "." not in linea:
                demandas.append(numeros[0])
            else:
                if len(costo) == 0 :
                    costo.append(numeros)
                elif len(costo[-1]) < params[0]:
                    for num in numeros:
                        costo[-1].append(num)
                else:
                    costo.append(numeros)
                    
    return params, capacity, costos_fijos, demandas, costo

def read_options(path):
    """
    Lee el nombre y dimensiones de todas las intancias disponibles en directorio
    
    Args:
        path (str) : Nombre del directorio donde están las instancias
        
    """
    
    options = []
    
    for option in dir(path):
        file_path = join(path, option)        # Se une el path del directorio con el nombre de la instancia a leer
        name = option.strip('.txt')           # Se extrae el nombre de la instancia

        # Leer primera línea (dimension del problema, Cliente / Facilidades)
        with open(file_path, 'r') as file : 
            dims = [int(item) for item in file.readline().strip().split()]
            
        options.append( [name, dims])
        
    return options

def read_instance(file_path):
    
    # Se extare información de la instancia
    (params,                                 # Numero de Centros / Clientes 
    capacity,                               # Capacidad de los Centros
    costos_fijos,                           # Costo de abrir cada Centro
    demandas,                               # Demanda de cada cliente
    costo) = leer_archivo(file_path)        # Costo de transporte entre cada centro/cliente 
    
    data = {
        "params": params,
        "capacity": capacity,
        "costos_fijos": costos_fijos,
        "demandas": demandas,
        "costo": costo,
        "initial_capacity" : capacity.copy(),
        "initial_demand": demandas.copy()
    }
    
    return data