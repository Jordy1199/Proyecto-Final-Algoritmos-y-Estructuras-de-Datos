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
    Modificado para ordenar in-place cuando sea posible.
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

# ---------- ALGORITMO DE BÚSQUEDA (BÚSQUEDA BINARIA MEJORADA) ----------
def busqueda_binaria_mejorada(lista_ordenada, campo, valor):
    """
    Implementación de Búsqueda Binaria mejorada que encuentra TODAS las coincidencias.
    Devuelve una lista con todos los elementos que coinciden.
    """
    if not lista_ordenada:
        return []
    
    # Primero encontrar la PRIMERA ocurrencia
    izquierda = 0
    derecha = len(lista_ordenada) - 1
    primera_ocurrencia = -1
    
    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        medio_valor = getattr(lista_ordenada[medio], campo)
        
        if medio_valor == valor:
            primera_ocurrencia = medio
            derecha = medio - 1  # Buscar hacia atrás para la primera ocurrencia
        elif medio_valor < valor:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    
    # Si no se encontró ninguna ocurrencia
    if primera_ocurrencia == -1:
        return []
    
    # Recoger todas las ocurrencias consecutivas
    resultados = []
    i = primera_ocurrencia
    while i < len(lista_ordenada) and getattr(lista_ordenada[i], campo) == valor:
        resultados.append(lista_ordenada[i])
        i += 1
    
    return resultados

def buscar_centros_por_campo(valor_buscar, campo_buscar):
    """
    Función auxiliar para buscar centros usando búsqueda binaria mejorada.
    """
    # Convertir a lista de objetos Centro
    centros_objetos = []
    for codigo, datos in centros_dict.items():
        centros_objetos.append(Centro(codigo, datos["nombre"], datos["region"], datos["subregion"]))

    # Ordenar por el campo de búsqueda
    centros_ordenados = quicksort(centros_objetos, campo_buscar)

    # Realizar búsqueda binaria mejorada
    return busqueda_binaria_mejorada(centros_ordenados, campo_buscar, valor_buscar)

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

# ---------- FUNCIONES SEGURAS PARA GUARDAR ----------
def guardar_centros():
    """Función segura para guardar centros"""
    try:
        with open("centros.txt", "w", encoding="utf-8") as archivo:
            for codigo, datos in centros_dict.items():
                archivo.write(f"{codigo};{datos['nombre']};{datos['region']};{datos['subregion']}\n")
        return True
    except Exception as e:
        print(f"Error al guardar centros: {e}")
        return False

def guardar_rutas():
    """Función segura para guardar rutas"""
    try:
        with open("rutas.txt", "w", encoding="utf-8") as archivo:
            for ruta in rutas_list:
                archivo.write(f"{ruta.origen};{ruta.destino};{ruta.distancia};{ruta.costo}\n")
        return True
    except Exception as e:
        print(f"Error al guardar rutas: {e}")
        return False

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
        centros_ordenados = quicksort(centros_objetos, campo, ascendente)

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

    # Realizar búsqueda binaria mejorada
    resultados = buscar_centros_por_campo(valor_buscar, campo)

    if resultados:
        print("\n" + "="*80)
        print(f"RESULTADOS DE BÚSQUEDA (Búsqueda Binaria Mejorada)")
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
    print("ACTUALIZAR CENTRO DE DISTRIBUCIÓN")
    print("="*40)
    
    if not centros_dict:
        print("No hay centros registrados")
        return
    
    print("\nCentros disponibles:")
    for i, codigo in enumerate(centros_dict.keys(), 1):
        centro = centros_dict[codigo]
        print(f"  {i:3}. {codigo}: {centro['nombre']}")
    
    codigo = input("\nCódigo del centro a actualizar: ").strip().upper()
    
    if codigo not in centros_dict:
        print("Centro no encontrado")
        return
    
    centro_actual = centros_dict[codigo]
    
    print("\nDatos actuales:")
    print(f"  Nombre: {centro_actual['nombre']}")
    print(f"  Región: {centro_actual['region']}")
    print(f"  Subregión: {centro_actual['subregion']}")
    
    print("\nIngrese nuevos datos (dejar vacío para mantener actual):")
    
    nuevo_nombre = input(f"Nuevo nombre [{centro_actual['nombre']}]: ").strip()
    if nuevo_nombre:
        centro_actual['nombre'] = nuevo_nombre
    
    nueva_region = input(f"Nueva región [{centro_actual['region']}]: ").strip()
    if nueva_region:
        # Actualizar árbol jerárquico
        if nueva_region != centro_actual['region']:
            # Remover de región anterior
            if centro_actual['region'] in regiones_arbol:
                if centro_actual['subregion'] in regiones_arbol[centro_actual['region']]:
                    if codigo in regiones_arbol[centro_actual['region']][centro_actual['subregion']]:
                        regiones_arbol[centro_actual['region']][centro_actual['subregion']].remove(codigo)
                        # Limpiar subregiones vacías
                        if not regiones_arbol[centro_actual['region']][centro_actual['subregion']]:
                            del regiones_arbol[centro_actual['region']][centro_actual['subregion']]
                        # Limpiar regiones vacías
                        if not regiones_arbol[centro_actual['region']]:
                            del regiones_arbol[centro_actual['region']]
            
            # Agregar a nueva región
            if nueva_region not in regiones_arbol:
                regiones_arbol[nueva_region] = {}
            if centro_actual['subregion'] not in regiones_arbol[nueva_region]:
                regiones_arbol[nueva_region][centro_actual['subregion']] = []
            regiones_arbol[nueva_region][centro_actual['subregion']].append(codigo)
        
        centro_actual['region'] = nueva_region
    
    nueva_subregion = input(f"Nueva subregión [{centro_actual['subregion']}]: ").strip()
    if nueva_subregion:
        region_actual = centro_actual['region']
        
        if nueva_subregion != centro_actual['subregion']:
            # Actualizar árbol jerárquico
            # Remover de subregión anterior
            if region_actual in regiones_arbol:
                if centro_actual['subregion'] in regiones_arbol[region_actual]:
                    if codigo in regiones_arbol[region_actual][centro_actual['subregion']]:
                        regiones_arbol[region_actual][centro_actual['subregion']].remove(codigo)
                        # Limpiar subregiones vacías
                        if not regiones_arbol[region_actual][centro_actual['subregion']]:
                            del regiones_arbol[region_actual][centro_actual['subregion']]
            
            # Agregar a nueva subregión
            if nueva_subregion not in regiones_arbol[region_actual]:
                regiones_arbol[region_actual][nueva_subregion] = []
            regiones_arbol[region_actual][nueva_subregion].append(codigo)
        
        centro_actual['subregion'] = nueva_subregion
    
    # Guardar cambios en archivo
    if guardar_centros():
        print("Centro actualizado correctamente")
    else:
        print("Error al guardar los cambios")

def eliminar_elemento():
    print("\n" + "="*40)
    print("ELIMINAR ELEMENTOS")
    print("="*40)
    
    print("\n¿Qué desea eliminar?")
    print("1. Centro de distribución")
    print("2. Ruta")
    
    opcion = input("Seleccione (1-2): ").strip()
    
    if opcion == "1":
        if not centros_dict:
            print("No hay centros registrados")
            return
            
        print("\nCentros disponibles:")
        for i, codigo in enumerate(centros_dict.keys(), 1):
            centro = centros_dict[codigo]
            print(f"  {i:3}. {codigo}: {centro['nombre']}")
        
        codigo = input("\nCódigo del centro a eliminar: ").strip().upper()
        
        if codigo not in centros_dict:
            print("Centro no encontrado")
            return
        
        # Confirmar
        confirmar = input(f"¿Está seguro de eliminar el centro {codigo}? (s/n): ").strip().lower()
        if confirmar != 's':
            print("Eliminación cancelada")
            return
        
        # Eliminar rutas asociadas del grafo y lista
        rutas_a_eliminar = []
        for ruta in rutas_list:
            if ruta.origen == codigo or ruta.destino == codigo:
                rutas_a_eliminar.append(ruta)
                # Eliminar del grafo también
                if ruta.origen in grafo:
                    grafo[ruta.origen] = [(v, p) for v, p in grafo[ruta.origen] if v != ruta.destino]
                if ruta.destino in grafo:
                    grafo[ruta.destino] = [(v, p) for v, p in grafo[ruta.destino] if v != ruta.origen]
        
        # Eliminar de la lista
        for ruta in rutas_a_eliminar:
            rutas_list.remove(ruta)
        
        # Eliminar del grafo
        if codigo in grafo:
            # Eliminar conexiones de otros nodos hacia este centro
            for vecino, _ in grafo[codigo]:
                if vecino in grafo:
                    grafo[vecino] = [(v, p) for v, p in grafo[vecino] if v != codigo]
            del grafo[codigo]
        
        # Eliminar del árbol jerárquico
        datos_centro = centros_dict[codigo]
        if datos_centro['region'] in regiones_arbol:
            if datos_centro['subregion'] in regiones_arbol[datos_centro['region']]:
                if codigo in regiones_arbol[datos_centro['region']][datos_centro['subregion']]:
                    regiones_arbol[datos_centro['region']][datos_centro['subregion']].remove(codigo)
                    # Limpiar si la subregión queda vacía
                    if not regiones_arbol[datos_centro['region']][datos_centro['subregion']]:
                        del regiones_arbol[datos_centro['region']][datos_centro['subregion']]
                    # Limpiar si la región queda vacía
                    if not regiones_arbol[datos_centro['region']]:
                        del regiones_arbol[datos_centro['region']]
        
        # Eliminar del diccionario
        del centros_dict[codigo]
        
        # Actualizar archivos
        guardar_centros()
        guardar_rutas()
        
        print(f"Centro {codigo} eliminado correctamente")
    
    elif opcion == "2":
        if not rutas_list:
            print("No hay rutas registradas")
            return
        
        print("\nRutas disponibles:")
        for i, ruta in enumerate(rutas_list, 1):
            print(f"  {i:3}. {ruta.origen} -> {ruta.destino}: {ruta.distancia}km, ${ruta.costo}")
        
        try:
            indice = int(input("\nNúmero de ruta a eliminar: ")) - 1
            if 0 <= indice < len(rutas_list):
                ruta_a_eliminar = rutas_list[indice]
                
                # Confirmar
                confirmar = input(f"¿Eliminar ruta {ruta_a_eliminar.origen}-{ruta_a_eliminar.destino}? (s/n): ").strip().lower()
                if confirmar != 's':
                    print("Eliminación cancelada")
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
                guardar_rutas()
                
                print("Ruta eliminada correctamente")
            else:
                print("Número inválido")
        except ValueError:
            print("Ingrese un número válido")
    
    else:
        print("Opción inválida")

def guardar_datos():
    print("\n" + "="*40)
    print("GUARDAR DATOS")
    print("="*40)
    
    # Guardar centros
    centros_ok = guardar_centros()
    
    # Guardar rutas
    rutas_ok = guardar_rutas()
    
    if centros_ok and rutas_ok:
        print("Datos guardados correctamente en centros.txt y rutas.txt")
    else:
        print("Hubo problemas al guardar algunos datos")

# ---------- FUNCIONES PARA CLIENTE -----------
def ver_mapa_centros():
    print("\n" + "="*40)
    print("MAPA DE CENTROS CONECTADOS")
    print("="*40)
    
    if not grafo:
        print("No hay centros conectados")
        return
    
    print("\nCentros y sus conexiones:")
    print("="*60)
    
    total_conexiones = 0
    for centro, conexiones in grafo.items():
        nombre = centros_dict.get(centro, {}).get('nombre', 'Desconocido')
        print(f"\n{centro}: {nombre}")
        print("  Conexiones:")
        
        if conexiones:
            for destino, costo in conexiones:
                nombre_destino = centros_dict.get(destino, {}).get('nombre', 'Desconocido')
                print(f"    -> {destino}: {nombre_destino} (Costo: ${costo:.2f})")
                total_conexiones += 1
        else:
            print("    Sin conexiones")
    
    print("\n" + "="*60)
    print(f"Total de centros: {len(grafo)}")
    print(f"Total de conexiones: {total_conexiones // 2}")  # Dividir por 2 porque cada ruta se cuenta dos veces
    print(f"Total de rutas únicas: {len(rutas_list)}")

def consultar_ruta_optima():
    print("\n" + "="*40)
    print("CONSULTAR RUTA ÓPTIMA")
    print("="*40)
    
    if len(centros_dict) < 2:
        print("Necesita al menos 2 centros")
        return
    
    print("\nCentros disponibles:")
    for i, codigo in enumerate(centros_dict.keys(), 1):
        centro = centros_dict[codigo]
        print(f"  {i:3}. {codigo}: {centro['nombre']}")
    
    while True:
        origen = input("\nCódigo de origen: ").strip().upper()
        if origen in centros_dict:
            break
        print("Centro no encontrado")
    
    while True:
        destino = input("Código de destino: ").strip().upper()
        if destino in centros_dict and destino != origen:
            break
        print("Centro no encontrado o igual al origen")
    
    # Usar Dijkstra para encontrar la ruta más económica
    ruta, costo = dijkstra(origen, destino)
    
    if ruta is None:
        print("No hay ruta disponible entre los centros seleccionados")
        return
    
    print("\n" + "="*60)
    print("RUTA ÓPTIMA ENCONTRADA")
    print("="*60)
    
    nombre_origen = centros_dict[origen]['nombre']
    nombre_destino = centros_dict[destino]['nombre']
    
    print(f"\nDe: {origen} ({nombre_origen})")
    print(f"A:  {destino} ({nombre_destino})")
    print(f"\nCosto total: ${costo:.2f}")
    
    print("\nRuta detallada:")
    for i, nodo in enumerate(ruta):
        nombre = centros_dict.get(nodo, {}).get('nombre', 'Desconocido')
        if i > 0:
            # Encontrar el costo entre nodos consecutivos
            costo_segmento = 0
            for vecino, peso in grafo[ruta[i-1]]:
                if vecino == nodo:
                    costo_segmento = peso
                    break
            print(f"  {i:2}. {nodo}: {nombre} (Costo del segmento: ${costo_segmento:.2f})")
        else:
            print(f"  {i+1:2}. {nodo}: {nombre}")
    
    print("\n" + "="*60)

def seleccionar_centros_envio():
    global centros_seleccionados
    
    print("\n" + "="*40)
    print("SELECCIONAR CENTROS PARA ENVÍO")
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
        print("  [código] - Agregar/remover centro")
        print("  ordenar  - Ordenar centros seleccionados")
        print("  limpiar  - Limpiar selección")
        print("  listo    - Terminar selección")
        
        opcion = input("\nOpción: ").strip().upper()
        
        if opcion == "LISTO":
            if len(centros_seleccionados) < 2:
                print("Debe seleccionar al menos 2 centros")
                continue
            break
        
        elif opcion == "LIMPIAR":
            centros_seleccionados = []
            print("Selección limpiada")
        
        elif opcion == "ORDENAR":
            if len(centros_seleccionados) < 2:
                print("Necesita al menos 2 centros para ordenar")
                continue
            
            print("\nOrdenar por:")
            print("1. Código")
            print("2. Nombre")
            print("3. Región")
            
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
                print("Opción inválida")
        
        else:
            # Verificar si es un código válido
            if opcion in centros_dict:
                if opcion in centros_seleccionados:
                    centros_seleccionados.remove(opcion)
                    print(f"Centro {opcion} removido de la selección")
                else:
                    centros_seleccionados.append(opcion)
                    print(f"Centro {opcion} agregado a la selección")
            else:
                print("Código no válido")
    
    print(f"\nSelección completada: {len(centros_seleccionados)} centros seleccionados")


def explorar_centros_jerarquicos():
    print("\nCENTROS ORGANIZADOS POR REGIÓN Y SUBREGIÓN\n")

    if not regiones_arbol:
        print("No hay centros registrados")
        return

    for region, subregiones in regiones_arbol.items():
        print(f"Región: {region}")
        for subregion, centros in subregiones.items():
            print(f"  Subregión: {subregion}")
            for codigo in centros:
                nombre = centros_dict[codigo]['nombre']
                print(f"    - {codigo}: {nombre}")

def listar_centros_seleccionados_y_costo():
    print("\nCENTROS SELECCIONADOS Y COSTO TOTAL\n")

    if len(centros_seleccionados) < 2:
        print("Debe haber al menos 2 centros seleccionados")
        return

    costo_total = 0
    ruta_completa = []

    print("Ruta seleccionada:")
    for i in range(len(centros_seleccionados) - 1):
        origen = centros_seleccionados[i]
        destino = centros_seleccionados[i + 1]
        ruta, costo = dijkstra(origen, destino)
        
        if ruta is None:
            print(f"No hay ruta disponible entre {origen} y {destino}")
            return
        
        if i == 0:
            ruta_completa.extend(ruta)
        else:
            # Evitar duplicar el nodo de conexión
            ruta_completa.extend(ruta[1:])
        
        costo_total += costo
    
    print(" -> ".join(centros_seleccionados))
    print(f"\nCosto total estimado: ${costo_total:.2f}")
    
    print("\nRuta detallada completa:")
    for i, codigo in enumerate(ruta_completa):
        nombre = centros_dict.get(codigo, {}).get('nombre', 'Desconocido')
        print(f"  {i+1:2}. {codigo}: {nombre}")

def eliminar_centros_seleccionados():
    global centros_seleccionados

    if not centros_seleccionados:
        print("No hay centros seleccionados")
        return

    print("\nCentros seleccionados:")
    for i, codigo in enumerate(centros_seleccionados, 1):
        nombre = centros_dict[codigo]['nombre']
        print(f"{i}. {codigo}: {nombre}")

    codigo = input("\nIngrese código a eliminar (o 'todos'): ").strip().upper()

    if codigo == "TODOS":
        centros_seleccionados.clear()
        print("Selección eliminada")
    elif codigo in centros_seleccionados:
        centros_seleccionados.remove(codigo)
        print(f"Centro {codigo} eliminado de la selección")
    else:
        print("Código no válido")

def guardar_seleccion_cliente(usuario_info):
    if len(centros_seleccionados) < 2:
        print("Debe seleccionar al menos 2 centros")
        return

    nombre_archivo = f"seleccion-{usuario_info['nombre'].lower()}-{usuario_info['apellido'].lower()}.txt"

    try:
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            archivo.write("="*60 + "\n")
            archivo.write(f"  SELECCIÓN DE CENTROS PARA ENVÍO\n")
            archivo.write("="*60 + "\n\n")
            archivo.write(f"Cliente: {usuario_info['nombre']} {usuario_info['apellido']}\n")
            archivo.write(f"Cédula: {usuario_info['cedula']}\n")
            archivo.write(f"Fecha: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            archivo.write("Centros seleccionados:\n")
            archivo.write("-"*60 + "\n")
            
            for i, codigo in enumerate(centros_seleccionados, 1):
                nombre = centros_dict[codigo]['nombre']
                region = centros_dict[codigo]['region']
                subregion = centros_dict[codigo]['subregion']
                archivo.write(f"{i:2}. {codigo}: {nombre}\n")
                archivo.write(f"     Región: {region} - Subregión: {subregion}\n")
            
            archivo.write("\n" + "="*60 + "\n")
        
        print(f"Selección guardada en {nombre_archivo}")
    except Exception as e:
        print(f"Error al guardar la selección: {e}")


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
        print("7. Guardar información de centros y rutas")
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
                actualizar_centro()
            case "6":
                eliminar_elemento()
            case "7":
                guardar_datos()
            case "8":
                print("Cerrando sesión de administrador...")
                break
            case _:
                print("Opción inválida")

# ---------- MENÚ CLIENTE ----------
def menu_cliente(usuario_info):
    while True:
        print("\n===== MENÚ CLIENTE =====")
        print("1. Ver mapa de centros conectados")
        print("2. Consultar ruta óptima entre dos centros")
        print("3. Explorar centros organizados jerárquicamente")
        print("4. Seleccionar centros para un envío (mínimo dos)")
        print("5. Listar centros seleccionados y costo total")
        print("6. Actualizar selección de centros")
        print("7. Eliminar centros seleccionados")
        print("8. Guardar selección en archivo personal")
        print("9. Salir")

        opcion = input("Seleccione una opción: ").strip()

        match opcion:
            case "1":
                print("--- Ver Mapa de Centros ---")
                ver_mapa_centros()
            case "2":
                print("--- Consultar ruta óptima ---")
                consultar_ruta_optima()
            case "3":
                print("--- Explorar centros organizados jerárquicamente ---")
                explorar_centros_jerarquicos()
            case "4":
                print("--- Seleccionar centros ---")
                seleccionar_centros_envio()
            case "5":
                print("--- Listar centros seleccionados / Precio Total ---")
                listar_centros_seleccionados_y_costo()
            case "6":
                print("--- Actualizar selección de centros ---")
                seleccionar_centros_envio()
            case "7":
                print("--- Eliminar centros seleccionados ---")
                eliminar_centros_seleccionados()
            case "8":
                print("--- Guardar ruta ---")
                guardar_seleccion_cliente(usuario_info)
            case "9":
                print("Cerrando sesión de cliente...")
                break
            case _:
                print("--- Opción inválida ---")

# ---------- PROGRAMA PRINCIPAL ----------
def principal():
    # Cargar datos al iniciar
    cargar_datos()

    while True:
        print("\n===== POLIDELIVERY =====")
        print("1. Registrar nuevo usuario")
        print("2. Iniciar sesión")
        print("3. Salir")

        opcion = input("Seleccione una opción: ").strip()

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
            try:
                with open(archivo, "w", encoding="utf-8") as f:
                    pass
                print(f"Archivo {archivo} creado.")
            except Exception as e:
                print(f"Error al crear {archivo}: {e}")

    principal()
