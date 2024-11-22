Representación de los datos en el programa:

data leída = params, capacity, costos_fijos, demandas, costo

params  = Numero de centros, numero de clientes 
capacity = capacidad de cada centro
costos_fijos = costo de abrir cada centro
demandas    = demanda de cada cliente
costo      = costo de transporte desde cliente i a centro j

solución:
        La solución es una matriz de asignaciones binaria (SSCFLP), o una matriz de proporciones (MSCFLP)

        Estas patrices serán almacenadas de forma sparce: Usando el formato DOK y CSR

Representación de la solución:
Matriz usaría mucha memoria, ademas si las soluciones son sparce habrá problemas


dimensiones = CENTROS X CLIENTES 


TAREAS:


TODO: 
Dar opcion para seed = None

implementar evaluación greedy de los candidatos para acortar la lista de candidatos
