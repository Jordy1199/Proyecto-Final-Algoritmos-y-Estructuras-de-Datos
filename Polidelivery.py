## =====================================
# POLIDELIVERY - REGISTRO, LOGIN Y ADMIN 
# =====================================
import re
import os
import heapq
from collections import deque

# ---------- VARIABLES GLOBALES ----------
grafo = {}
centros_dict = {}  # Diccionario: codigo -> {nombre, region, subregion}
rutas_list = []    # Lista de rutas: (origen, destino, distancia, costo)
regiones_arbol = {}  # Árbol jerárquico: region -> subregiones -> centros
centros_seleccionados = []

# ---------- CLASES PARA ESTRUCTURAS ----------
class Centro:
    def __init__(self, codigo, nombre, region, subregion):
        self.codigo = codigo
        self.nombre = nombre
        self.region = region
        self.subregion = subregion

    def __str__(self):
        return f"{self.codigo}: {self.nombre} ({self.region}/{self.subregion})"

class Ruta:
    def __init__(self, origen, destino, distancia, costo):
        self.origen = origen
        self.destino = destino
        self.distancia = distancia
        self.costo = costo

    def __str__(self):
        return f"{self.origen} -> {self.destino}: {self.distancia}km, ${self.costo}"

# ---------- VALIDAR CONTRASEÑA ----------
def password_segura(password):
    if len(password) < 6:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    return True

# ---------- REGISTRAR USUARIO ----------
def registrar_usuario():
    print("\n===== REGISTRO DE USUARIO =====")

    nombre = input("Nombre: ").strip()
    apellido = input("Apellido: ").strip()

    while True:
        cedula = input("Cédula: ").strip()
        if cedula.isdigit():
            break
        print("La cédula debe contener solo números")

    while True:
        edad = input("Edad: ").strip()
        if edad.isdigit() and 1 <= int(edad) <= 120:
            break
        print("Edad inválida (1-120)")

    while True:
        correo = input("Correo: ").strip()
        if "@" in correo and "." in correo:
            break
        print("Correo inválido")

    while True:
        password = input("Contraseña: ")
        if password_segura(password):
            break
        else:
            print("La contraseña debe tener al menos 6 caracteres, una mayúscula, una minúscula y un número")

    while True:
        rol = input("Rol (administrador / cliente): ").lower().strip()
        if rol in ["administrador", "cliente"]:
            break
        else:
            print("Rol inválido. Use 'administrador' o 'cliente'")

    with open("usuarios.txt", "a", encoding="utf-8") as archivo:
        archivo.write(f"{nombre};{apellido};{cedula};{edad};{correo};{password};{rol}\n")

    print("Usuario registrado correctamente")

# ---------- CARGAR USUARIOS ----------
def cargar_usuarios():
    usuarios = {}
    try:
        with open("usuarios.txt", "r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if not linea:
                    continue
                partes = linea.split(";")
                if len(partes) != 7:
                    continue
                nombre, apellido, cedula, edad, correo, password, rol = partes
                usuarios[correo] = {
                    "nombre_completo": f"{nombre} {apellido}",
                    "nombre": nombre,
                    "apellido": apellido,
                    "cedula": cedula,
                    "edad": edad,
                    "password": password,
                    "rol": rol
                }
    except FileNotFoundError:
        pass
    return usuarios

# ---------- CARGAR DATOS ----------
def cargar_datos():
    global grafo, centros_dict, rutas_list, regiones_arbol

    # Cargar centros
    try:
        with open("centros.txt", "r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if not linea:
                    continue
                partes = linea.split(";")
                if len(partes) >= 4:
                    codigo, nombre, region, subregion = partes[:4]
                    centros_dict[codigo] = {
                        "nombre": nombre,
                        "region": region,
                        "subregion": subregion
                    }

                    # Construir arbol jerarquico
                    if region not in regiones_arbol:
                        regiones_arbol[region] = {}
                    if subregion not in regiones_arbol[region]:
                        regiones_arbol[region][subregion] = []
                    regiones_arbol[region][subregion].append(codigo)
    except FileNotFoundError:
        print("Archivo centros.txt no encontrado. Se creará uno nuevo.")

    # Inicializar grafo
    for codigo in centros_dict:
        grafo[codigo] = []

    # Cargar rutas
    try:
        with open("rutas.txt", "r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if not linea:
                    continue
                partes = linea.split(";")
                if len(partes) >= 4:
                    origen, destino, distancia, costo = partes[:4]
                    rutas_list.append(Ruta(origen, destino, float(distancia), float(costo)))

                    if origen in grafo and destino in grafo:
                        grafo[origen].append((destino, float(costo)))
                        grafo[destino].append((origen, float(costo)))
    except FileNotFoundError:
        print("Archivo rutas.txt no encontrado. Se creará uno nuevo.")

# ---------- LOGIN ----------
def login():
    usuarios = cargar_usuarios()

    print("\n===== LOGIN =====")
    correo = input("Correo: ").strip()
    password = input("Contraseña: ")

    if correo in usuarios and usuarios[correo]["password"] == password:
        print("Ingreso exitoso")
        return usuarios[correo]["rol"], usuarios[correo]
    else:
        print("Credenciales incorrectas")
        return None, None

# ---------- ALGORITMO DE ORDENAMIENTO (QUICK SORT) ----------
def quicksort(lista, campo, ascendente=True):
    """
    Implementación de Quick Sort para ordenar listas de objetos.
    """
    if len(lista) <= 1:
        return lista

    # Seleccionar pivote (elemento del medio)
    pivot = lista[len(lista) // 2]
    pivot_valor = getattr(pivot, campo)

    # Dividir en sublistas
    left = []
    middle = []
    right = []

    for item in lista:
        item_valor = getattr(item, campo)
        if item_valor < pivot_valor:
            left.append(item)
        elif item_valor > pivot_valor:
            right.append(item)
        else:
            middle.append(item)

    # Ordenar recursivamente y combinar
    if ascendente:
        return quicksort(left, campo, ascendente) + middle + quicksort(right, campo, ascendente)
    else:
        return quicksort(right, campo, ascendente) + middle + quicksort(left, campo, ascendente)

# ---------- ALGORITMO DE BÚSQUEDA (BÚSQUEDA BINARIA) ----------
def busqueda_binaria(lista_ordenada, campo, valor):
    """
    Implementación de Búsqueda Binaria para listas ordenadas.
    Devuelve el índice del elemento encontrado o -1 si no existe.
    """
    izquierda = 0
    derecha = len(lista_ordenada) - 1

    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        medio_valor = getattr(lista_ordenada[medio], campo)

        if medio_valor == valor:
            return medio
        elif medio_valor < valor:
            izquierda = medio + 1
        else:
            derecha = medio - 1

    return -1

def buscar_centros_por_campo(valor_buscar, campo_buscar):
    """
    Función auxiliar para buscar centros usando búsqueda binaria.
    """
    # Primero ordenar la lista
    centros_objetos = []
    for codigo, datos in centros_dict.items():
        centros_objetos.append(Centro(codigo, datos["nombre"], datos["region"], datos["subregion"]))

    # Ordenar por el campo de búsqueda
    centros_ordenados = quicksort(centros_objetos.copy(), campo_buscar)

    # Realizar búsqueda binaria
    indice = busqueda_binaria(centros_ordenados, campo_buscar, valor_buscar)

    if indice != -1:
        return [centros_ordenados[indice]]
    else:
        return []

# ---------- ALGORITMOS DE GRAFOS ----------
def dijkstra(origen, destino=None):
    if origen not in grafo:
        return None

    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[origen] = 0
    predecesores = {nodo: None for nodo in grafo}
    heap = [(0, origen)]

    while heap:
        costo_actual, nodo = heapq.heappop(heap)

        if costo_actual > distancias[nodo]:
            continue

        for vecino, peso in grafo[nodo]:
            nuevo_costo = costo_actual + peso
            if nuevo_costo < distancias[vecino]:
                distancias[vecino] = nuevo_costo
                predecesores[vecino] = nodo
                heapq.heappush(heap, (nuevo_costo, vecino))

    if destino:
        if distancias[destino] == float('inf'):
            return None, float('inf')

        # Reconstruir ruta
        ruta = []
        nodo = destino
        while nodo is not None:
            ruta.append(nodo)
            nodo = predecesores[nodo]
        ruta.reverse()

        return ruta, distancias[destino]

    return distancias, predecesores

def bfs_busqueda_centros(origen, max_distancia):
    if origen not in grafo:
        return []

    visitados = set()
    resultados = []
    cola = deque([(origen, 0)])

    while cola:
        nodo, distancia_actual = cola.popleft()

        if nodo in visitados:
            continue

        visitados.add(nodo)

        if distancia_actual <= max_distancia and nodo != origen:
            resultados.append((nodo, distancia_actual))

        for vecino, peso in grafo[nodo]:
            if vecino not in visitados:
                nueva_distancia = distancia_actual + peso
                if nueva_distancia <= max_distancia:
                    cola.append((vecino, nueva_distancia))

    return resultados

def dfs_exploracion_total(origen):
    if origen not in grafo:
        return []

    visitados = set()
    ruta_completa = []

    def dfs_recursivo(nodo):
        visitados.add(nodo)
        ruta_completa.append(nodo)

        for vecino, _ in grafo[nodo]:
            if vecino not in visitados:
                dfs_recursivo(vecino)

    dfs_recursivo(origen)
    return ruta_completa

# ---------- FUNCIONES DEL ADMINISTRADOR ----------
def agregar_centro_distribucion():
    print("\n" + "="*40)
    print("AGREGAR CENTRO DE DISTRIBUCIÓN")
    print("="*40)

    while True:
        codigo = input("Código del centro (ej: CD001): ").strip().upper()
        if not codigo:
            print("El código no puede estar vacío")
            continue

        if codigo in centros_dict:
            print("Este código ya existe")
            continue

        if len(codigo) < 2:
            print("Código muy corto")
            continue
        break

    nombre = input("Nombre del centro: ").strip()
    while not nombre:
        print("El nombre no puede estar vacío")
        nombre = input("Nombre del centro: ").strip()

    region = input("Región: ").strip()
    while not region:
        print("La región no puede estar vacía")
        region = input("Región: ").strip()

    subregion = input("Subregión: ").strip()
    while not subregion:
        print("La subregión no puede estar vacía")
        subregion = input("Subregión: ").strip()

    # Guardar en archivo
    with open("centros.txt", "a", encoding="utf-8") as archivo:
        archivo.write(f"{codigo};{nombre};{region};{subregion}\n")

    # Actualizar estructuras
    centros_dict[codigo] = {"nombre": nombre, "region": region, "subregion": subregion}

    if region not in regiones_arbol:
        regiones_arbol[region] = {}
    if subregion not in regiones_arbol[region]:
        regiones_arbol[region][subregion] = []
    regiones_arbol[region][subregion].append(codigo)

    grafo[codigo] = []

    print(f"Centro '{nombre}' agregado con código '{codigo}'")

def agregar_ruta_costo():
    print("\n" + "="*40)
    print("AGREGAR NUEVA RUTA")
    print("="*40)

    if len(centros_dict) < 2:
        print("Necesita al menos 2 centros para crear una ruta")
        return

    print("\nCentros disponibles:")
    for i, codigo in enumerate(centros_dict.keys(), 1):
        centro = centros_dict[codigo]
        print(f"  {i:3}. {codigo}: {centro['nombre']}")

    while True:
        origen = input("\nCódigo de origen: ").strip().upper()
        if origen in centros_dict:
            break
        print("Código inválido")

    while True:
        destino = input("Código de destino: ").strip().upper()
        if destino in centros_dict and destino != origen:
            # Verificar si la ruta ya existe
            for ruta in rutas_list:
                if (ruta.origen == origen and ruta.destino == destino) or \
                   (ruta.origen == destino and ruta.destino == origen):
                    print("Esta ruta ya existe")
                    destino = ""
                    break

            if destino:
                break
        elif destino == origen:
            print("Origen y destino no pueden ser iguales")
        else:
            print("Código no válido")

    while True:
        try:
            distancia = float(input("Distancia (km): ").strip())
            if distancia > 0:
                break
            print("La distancia debe ser positiva")
        except ValueError:
            print("Ingrese un número válido")

    while True:
        try:
            costo = float(input("Costo ($): ").strip())
            if costo >= 0:
                break
            print("El costo no puede ser negativo")
        except ValueError:
            print("Ingrese un número válido")

    # Agregar a estructuras
    nueva_ruta = Ruta(origen, destino, distancia, costo)
    rutas_list.append(nueva_ruta)

    grafo[origen].append((destino, costo))
    grafo[destino].append((origen, costo))

    # Guardar en archivo
    with open("rutas.txt", "a", encoding="utf-8") as archivo:
        archivo.write(f"{origen};{destino};{distancia};{costo}\n")

    print(f"Ruta {origen}-{destino} agregada: {distancia}km, ${costo}")

def menu_listar_ordenamiento():
    print("\n" + "="*40)
    print("LISTAR CENTROS CON ORDENAMIENTO")
    print("="*40)

    print("\n¿Qué desea listar?")
    print("1. Centros de distribución")
    print("2. Rutas disponibles")

    opcion = input("Seleccione (1-2): ").strip()

    if opcion == "1":
        print("\nOrdenar por:")
        print("1. Código")
        print("2. Nombre")
        print("3. Región")
        print("4. Subregión")

        campo_opcion = input("Seleccione (1-4): ").strip()

        # Convertir a lista de objetos Centro
        centros_objetos = []
        for codigo, datos in centros_dict.items():
            centros_objetos.append(Centro(codigo, datos["nombre"], datos["region"], datos["subregion"]))

        # Mapear selección de campo
        campos = {1: "codigo", 2: "nombre", 3: "region", 4: "subregion"}
        campo = campos.get(int(campo_opcion), "codigo")

        print("\nOrden:")
        print("1. Ascendente (A-Z, 0-9)")
        print("2. Descendente (Z-A, 9-0)")
        orden_opcion = input("Seleccione (1-2): ").strip()
        ascendente = orden_opcion == "1"

        # Aplicar ordenamiento QUICK SORT
        centros_ordenados = quicksort(centros_objetos.copy(), campo, ascendente)

        print("\n" + "="*80)
        orden_texto = "ASCENDENTE" if ascendente else "DESCENDENTE"
        print(f"CENTROS ORDENADOS POR {campo.upper()} ({orden_texto} - Quick Sort)")
        print("="*80)
        print(f"{'CÓDIGO':<10} {'NOMBRE':<25} {'REGIÓN':<15} {'SUBREGIÓN':<15}")
        print("-"*80)

        for centro in centros_ordenados:
            print(f"{centro.codigo:<10} {centro.nombre:<25} {centro.region:<15} {centro.subregion:<15}")

        print("="*80)
        print(f"Total: {len(centros_ordenados)} centros")

    elif opcion == "2":
        print("\nRUTAS DISPONIBLES:")
        print("="*80)
        print(f"{'ORIGEN':<10} {'DESTINO':<10} {'DISTANCIA (km)':<15} {'COSTO ($)':<10}")
        print("-"*80)

        for ruta in rutas_list:
            print(f"{ruta.origen:<10} {ruta.destino:<10} {ruta.distancia:<15.2f} {ruta.costo:<10.2f}")

        print("="*80)
        print(f"Total: {len(rutas_list)} rutas")

    else:
        print("Opción inválida")

def consultar_centro_especifico():
    print("\n" + "="*40)
    print("CONSULTAR CENTRO ESPECÍFICO")
    print("="*40)

    if not centros_dict:
        print("No hay centros registrados.")
        return

    print("\nBuscar por:")
    print("1. Código")
    print("2. Nombre")
    print("3. Región")
    print("4. Subregión")

    opcion = input("Seleccione (1-4): ").strip()

    campo_map = {"1": "codigo", "2": "nombre", "3": "region", "4": "subregion"}
    campo = campo_map.get(opcion, "codigo")

    valor_buscar = input(f"Ingrese el {campo} a buscar: ").strip()
    if campo == "codigo":
        valor_buscar = valor_buscar.upper()

    # Realizar búsqueda binaria
    resultados = buscar_centros_por_campo(valor_buscar, campo)

    if resultados:
        print("\n" + "="*80)
        print(f"RESULTADOS DE BÚSQUEDA (Búsqueda Binaria)")
        print("="*80)
        print(f"{'CÓDIGO':<10} {'NOMBRE':<25} {'REGIÓN':<15} {'SUBREGIÓN':<15}")
        print("-"*80)

        for centro in resultados:
            print(f"{centro.codigo:<10} {centro.nombre:<25} {centro.region:<15} {centro.subregion:<15}")

        print("="*80)
        print(f"Encontrados: {len(resultados)} centro(s)")
    else:
        print(f"\nNo se encontraron centros con {campo}: '{valor_buscar}'")
def actualizar_centro():
    print("\n" + "="*40)
    print("ACTUALIZAR CENTRO DE DISTRIBUCION")
    print("="*40)
    
    if not centros_dict:
        print("No hay centros registrados")
        return
    
    print("\nCentros disponibles:")
    for i, codigo in enumerate(centros_dict.keys(), 1):
        centro = centros_dict[codigo]
        print(f"  {i:3}. {codigo}: {centro['nombre']}")
    
    codigo = input("\nCodigo del centro a actualizar: ").strip().upper()
    
    if codigo not in centros_dict:
        print("Centro no encontrado")
        return
    
    centro_actual = centros_dict[codigo]
    
    print("\nDatos actuales:")
    print(f"  Nombre: {centro_actual['nombre']}")
    print(f"  Region: {centro_actual['region']}")
    print(f"  Subregion: {centro_actual['subregion']}")
    
    print("\nIngrese nuevos datos (dejar vacio para mantener actual):")
    
    nuevo_nombre = input(f"Nuevo nombre [{centro_actual['nombre']}]: ").strip()
    if nuevo_nombre:
        centro_actual['nombre'] = nuevo_nombre
    
    nueva_region = input(f"Nueva region [{centro_actual['region']}]: ").strip()
    if nueva_region:
        # Actualizar arbol jerarquico
        if nueva_region != centro_actual['region']:
            # Remover de region anterior
            if centro_actual['region'] in regiones_arbol:
                if centro_actual['subregion'] in regiones_arbol[centro_actual['region']]:
                    if codigo in regiones_arbol[centro_actual['region']][centro_actual['subregion']]:
                        regiones_arbol[centro_actual['region']][centro_actual['subregion']].remove(codigo)
            
            # Agregar a nueva region
            if nueva_region not in regiones_arbol:
                regiones_arbol[nueva_region] = {}
            if centro_actual['subregion'] not in regiones_arbol[nueva_region]:
                regiones_arbol[nueva_region][centro_actual['subregion']] = []
            regiones_arbol[nueva_region][centro_actual['subregion']].append(codigo)
        
        centro_actual['region'] = nueva_region
    
    nueva_subregion = input(f"Nueva subregion [{centro_actual['subregion']}]: ").strip()
    if nueva_subregion:
        if nueva_subregion != centro_actual['subregion']:
            # Actualizar arbol jerarquico
            region_actual = centro_actual['region']
            
            # Remover de subregion anterior
            if codigo in regiones_arbol[region_actual][centro_actual['subregion']]:
                regiones_arbol[region_actual][centro_actual['subregion']].remove(codigo)
            
            # Agregar a nueva subregion
            if nueva_subregion not in regiones_arbol[region_actual]:
                regiones_arbol[region_actual][nueva_subregion] = []
            regiones_arbol[region_actual][nueva_subregion].append(codigo)
        
        centro_actual['subregion'] = nueva_subregion
    
    # Guardar cambios en archivo
    with open("centros.txt", "w", encoding="utf-8") as archivo:
        for cod, datos in centros_dict.items():
            archivo.write(f"{cod};{datos['nombre']};{datos['region']};{datos['subregion']}\n")
    
    print("Centro actualizado correctamente")

def eliminar_elemento():
    print("\n" + "="*40)
    print("ELIMINAR ELEMENTOS")
    print("="*40)
    
    print("\nQue desea eliminar?")
    print("1. Centro de distribucion")
    print("2. Ruta")
    
    opcion = input("Seleccione (1-2): ").strip()
    
    if opcion == "1":
        print("\nCentros disponibles:")
        for i, codigo in enumerate(centros_dict.keys(), 1):
            centro = centros_dict[codigo]
            print(f"  {i:3}. {codigo}: {centro['nombre']}")
        
        codigo = input("\nCodigo del centro a eliminar: ").strip().upper()
        
        if codigo not in centros_dict:
            print("Centro no encontrado")
            return
        
        # Confirmar
        confirmar = input(f"Esta seguro de eliminar el centro {codigo}? (s/n): ").strip().lower()
        if confirmar != 's':
            print("Eliminacion cancelada")
            return
        
        # Eliminar rutas asociadas
        rutas_a_eliminar = []
        for ruta in rutas_list:
            if ruta.origen == codigo or ruta.destino == codigo:
                rutas_a_eliminar.append(ruta)
        
        for ruta in rutas_a_eliminar:
            rutas_list.remove(ruta)
        
        # Actualizar archivo de rutas
        with open("rutas.txt", "w", encoding="utf-8") as archivo:
            for ruta in rutas_list:
                archivo.write(f"{ruta.origen};{ruta.destino};{ruta.distancia};{ruta.costo}\n")
        
        # Eliminar del grafo
        if codigo in grafo:
            # Eliminar conexiones de otros nodos
            for vecino, _ in grafo[codigo]:
                grafo[vecino] = [(v, p) for v, p in grafo[vecino] if v != codigo]
            
            del grafo[codigo]
        
        # Eliminar del arbol jerarquico
        datos_centro = centros_dict[codigo]
        if datos_centro['region'] in regiones_arbol:
            if datos_centro['subregion'] in regiones_arbol[datos_centro['region']]:
                if codigo in regiones_arbol[datos_centro['region']][datos_centro['subregion']]:
                    regiones_arbol[datos_centro['region']][datos_centro['subregion']].remove(codigo)
        
        # Eliminar del diccionario
        del centros_dict[codigo]
        
        # Actualizar archivo de centros
        with open("centros.txt", "w", encoding="utf-8") as archivo:
            for cod, datos in centros_dict.items():
                archivo.write(f"{cod};{datos['nombre']};{datos['region']};{datos['subregion']}\n")
        
        print(f"Centro {codigo} eliminado correctamente")
    
    elif opcion == "2":
        if not rutas_list:
            print("No hay rutas registradas")
            return
        
        print("\nRutas disponibles:")
        for i, ruta in enumerate(rutas_list, 1):
            print(f"  {i:3}. {ruta.origen} -> {ruta.destino}: {ruta.distancia}km, ${ruta.costo}")
        
        try:
            indice = int(input("\nNumero de ruta a eliminar: ")) - 1
            if 0 <= indice < len(rutas_list):
                ruta_a_eliminar = rutas_list[indice]
                
                # Confirmar
                confirmar = input(f"Eliminar ruta {ruta_a_eliminar.origen}-{ruta_a_eliminar.destino}? (s/n): ").strip().lower()
                if confirmar != 's':
                    print("Eliminacion cancelada")
                    return
                
                # Eliminar del grafo
                origen = ruta_a_eliminar.origen
                destino = ruta_a_eliminar.destino
                
                if origen in grafo:
                    grafo[origen] = [(v, p) for v, p in grafo[origen] if v != destino]
                if destino in grafo:
                    grafo[destino] = [(v, p) for v, p in grafo[destino] if v != origen]
                
                # Eliminar de la lista
                del rutas_list[indice]
                
                # Actualizar archivo
                with open("rutas.txt", "w", encoding="utf-8") as archivo:
                    for ruta in rutas_list:
                        archivo.write(f"{ruta.origen};{ruta.destino};{ruta.distancia};{ruta.costo}\n")
                
                print("Ruta eliminada correctamente")
            else:
                print("Numero invalido")
        except ValueError:
            print("Ingrese un numero valido")
    
    else:
        print("Opcion invalida")

def guardar_datos():
    print("\n" + "="*40)
    print("GUARDAR DATOS")
    print("="*40)
    
    # Los datos ya se guardan automaticamente en cada operacion
    # Esta funcion es para guardar manualmente
    
    try:
        # Guardar centros
        with open("centros.txt", "w", encoding="utf-8") as archivo:
            for codigo, datos in centros_dict.items():
                archivo.write(f"{codigo};{datos['nombre']};{datos['region']};{datos['subregion']}\n")
        
        # Guardar rutas
        with open("rutas.txt", "w", encoding="utf-8") as archivo:
            for ruta in rutas_list:
                archivo.write(f"{ruta.origen};{ruta.destino};{ruta.distancia};{ruta.costo}\n")
        
        print("Datos guardados correctamente en centros.txt y rutas.txt")
    
    except Exception as e:
        print(f"Error al guardar datos: {e}")
        
#----------- FUNCIONES PARA CLIENTE -----------
def ver_mapa_centros():
    print("\n" + "="*40)
    print("MAPA DE CENTROS CONECTADOS")
    print("="*40)
    
    if not grafo:
        print("No hay centros conectados")
        return
    
    print("\nCentros y sus conexiones:")
    print("="*60)
    
    for centro, conexiones in grafo.items():
        nombre = centros_dict.get(centro, {}).get('nombre', 'Desconocido')
        print(f"\n{centro}: {nombre}")
        print("  Conexiones:")
        
        if conexiones:
            for destino, costo in conexiones:
                nombre_destino = centros_dict.get(destino, {}).get('nombre', 'Desconocido')
                print(f"    -> {destino}: {nombre_destino} (Costo: ${costo})")
        else:
            print("    Sin conexiones")
    
    print("\n" + "="*60)
    print(f"Total de centros: {len(grafo)}")
    print(f"Total de rutas: {len(rutas_list)}")

def consultar_ruta_optima():
    print("\n" + "="*40)
    print("CONSULTAR RUTA OPTIMA")
    print("="*40)
    
    if len(centros_dict) < 2:
        print("Necesita al menos 2 centros")
        return
    
    print("\nCentros disponibles:")
    for i, codigo in enumerate(centros_dict.keys(), 1):
        centro = centros_dict[codigo]
        print(f"  {i:3}. {codigo}: {centro['nombre']}")
    
    while True:
        origen = input("\nCodigo de origen: ").strip().upper()
        if origen in centros_dict:
            break
        print("Centro no encontrado")
    
    while True:
        destino = input("Codigo de destino: ").strip().upper()
        if destino in centros_dict and destino != origen:
            break
        print("Centro no encontrado o igual al origen")
    
    # Usar Dijkstra para encontrar la ruta mas economica
    ruta, costo = dijkstra(origen, destino)
    
    if ruta is None:
        print("No hay ruta disponible entre los centros seleccionados")
        return
    
    print("\n" + "="*60)
    print("RUTA OPTIMA ENCONTRADA")
    print("="*60)
    
    nombre_origen = centros_dict[origen]['nombre']
    nombre_destino = centros_dict[destino]['nombre']
    
    print(f"\nDe: {origen} ({nombre_origen})")
    print(f"A:  {destino} ({nombre_destino})")
    print(f"\nCosto total: ${costo:.2f}")
    
    print("\nRuta detallada:")
    for i, nodo in enumerate(ruta):
        nombre = centros_dict.get(nodo, {}).get('nombre', 'Desconocido')
        print(f"  {i+1:2}. {nodo}: {nombre}")
    
    print("\n" + "="*60)

def guardar_ruta_cliente(usuario_info):
    print("\nGUARDAR RUTA DEL CLIENTE")

    origen = input("Centro de origen: ").strip().upper()
    destino = input("Centro de destino: ").strip().upper()

    if origen not in grafo or destino not in grafo:
        print("Centro no válido")
        return

    ruta, costo = dijkstra(origen, destino)

    if ruta is None:
        print("No existe una ruta disponible")
        return

    nombre_archivo = f"rutas-{usuario_info['nombre'].lower()}-{usuario_info['apellido'].lower()}.txt"

    with open(nombre_archivo, "a", encoding="utf-8") as archivo:
        archivo.write("Ruta guardada:\n")
        archivo.write(" -> ".join(ruta) + "\n")
        archivo.write(f"Costo total: ${costo:.2f}\n")
        archivo.write("-" * 40 + "\n")

    print(f"Ruta guardada correctamente en '{nombre_archivo}'")


def seleccionar_centros_envio():
    global centros_seleccionados
    
    print("\n" + "="*40)
    print("SELECCIONAR CENTROS PARA ENVIO")
    print("="*40)
    
    if len(centros_dict) < 2:
        print("Necesita al menos 2 centros registrados")
        return
    
    while True:
        print("\nCentros disponibles:")
        for i, codigo in enumerate(centros_dict.keys(), 1):
            centro = centros_dict[codigo]
            seleccionado = "X" if codigo in centros_seleccionados else " "
            print(f"  [{seleccionado}] {i:3}. {codigo}: {centro['nombre']}")
        
        print("\nCentros seleccionados actualmente:")
        if centros_seleccionados:
            for i, codigo in enumerate(centros_seleccionados, 1):
                nombre = centros_dict[codigo]['nombre']
                print(f"  {i:2}. {codigo}: {nombre}")
        else:
            print("  (Ninguno)")
        
        print("\nOpciones:")
        print("  [codigo] - Agregar/remover centro")
        print("  ordenar  - Ordenar centros seleccionados")
        print("  limpiar  - Limpiar seleccion")
        print("  listo    - Terminar seleccion")
        
        opcion = input("\nOpcion: ").strip().upper()
        
        if opcion == "LISTO":
            if len(centros_seleccionados) < 2:
                print("Debe seleccionar al menos 2 centros")
                continue
            break
        
        elif opcion == "LIMPIAR":
            centros_seleccionados = []
            print("Seleccion limpiada")
        
        elif opcion == "ORDENAR":
            if len(centros_seleccionados) < 2:
                print("Necesita al menos 2 centros para ordenar")
                continue
            
            print("\nOrdenar por:")
            print("1. Codigo")
            print("2. Nombre")
            print("3. Region")
            
            try:
                campo_opcion = int(input("Seleccione (1-3): "))
                
                # Convertir a objetos Centro
                centros_objs = []
                for codigo in centros_seleccionados:
                    datos = centros_dict[codigo]
                    centros_objs.append(Centro(codigo, datos['nombre'], datos['region'], datos['subregion']))
                
                # Mapear campo
                campos = {1: "codigo", 2: "nombre", 3: "region"}
                campo = campos.get(campo_opcion, "codigo")
                
                # Ordenar con Quick Sort
                centros_ordenados = quicksort(centros_objs, campo, True)
                
                # Actualizar lista
                centros_seleccionados = [centro.codigo for centro in centros_ordenados]
                
                print(f"Centros ordenados por {campo}")
            
            except ValueError:
                print("Opcion invalida")
        
        else:
            # Verificar si es un codigo valido
            if opcion in centros_dict:
                if opcion in centros_seleccionados:
                    centros_seleccionados.remove(opcion)
                    print(f"Centro {opcion} removido de la seleccion")
                else:
                    centros_seleccionados.append(opcion)
                    print(f"Centro {opcion} agregado a la seleccion")
            else:
                print("Codigo no valido")
    
    print(f"\nSeleccion completada: {len(centros_seleccionados)} centros seleccionados")

# ---------- MENÚ ADMINISTRADOR ----------
def menu_admin(usuario_info):
    while True:
        print("\n===== MENÚ ADMINISTRADOR =====")
        print("1. Agregar nuevos centros de distribución")
        print("2. Agregar nuevas rutas con distancias y costos")
        print("3. Listar centros y rutas (con algoritmo de ordenamiento)")
        print("4. Consultar un centro específico (con algoritmo de búsqueda)")
        print("5. Actualizar información de centros")
        print("6. Eliminar centros o rutas")
        print("7. Guardar información en centros.txt")
        print("8. Salir")

        opcion = input("Seleccione una opción: ").strip()

        match opcion:
            case "1":
                agregar_centro_distribucion()
            case "2":
                agregar_ruta_costo()
            case "3":
                menu_listar_ordenamiento()
            case "4":
                consultar_centro_especifico()
            case "5":
                print()
            case "6":
                print()
            case "7":
                print()
            case "8":
                print("Cerrando sesión de administrador...")
                break
            case _:
                print("Opción inválida")

# ---------- MENÚ CLIENTE ----------
def menu_cliente(usuario_info):
    while True:
        print("\n===== MENÚ CLIENTE =====")
        print("1. Ver mapa de centros")
        print("2. Consultar ruta óptima")
        print("3. Seleccionar centros")
        print("4. Guardar ruta")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")

        match opcion:
            case "1":
                print("---Ver mapa de centros---")
                ver_mapa_centros()
            case "2":
                print("---Consultar ruta óptima---")
                consultar_ruta_optima()
            case "3":
                print("---Seleccionar centros---")
                seleccionar_centros_envio()
            case "4":
                print("---Guardar ruta---")
                guardar_ruta_cliente(usuario_info)
            case "5":
                print("Cerrando sesión de cliente...")
                centros_seleccionados.clear()
                break
            case _:
                print("---Opción inválida---")

# ---------- PROGRAMA PRINCIPAL ----------
def principal():
    # Cargar datos al iniciar
    cargar_datos()

    while True:
        print("\n===== POLIDELIVERY =====")
        print("1. Registrar nuevo usuario")
        print("2. Iniciar sesión")
        print("3. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            registrar_usuario()

        elif opcion == "2":
            rol, usuario_info = login()
            if rol == "administrador":
                menu_admin(usuario_info)
            elif rol == "cliente":
                menu_cliente(usuario_info)

        elif opcion == "3":
            print("Saliendo del sistema...")
            break

        else:
            print("Opción inválida")

# ---------- EJECUCIÓN ----------
if __name__ == "__main__":
    # Crear archivos si no existen
    for archivo in ["usuarios.txt", "centros.txt", "rutas.txt"]:
        if not os.path.exists(archivo):
            with open(archivo, "w", encoding="utf-8") as f:
                pass

    principal()
