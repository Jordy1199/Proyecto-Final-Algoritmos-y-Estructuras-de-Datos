## =====================================
# POLIDELIVERY - REGISTRO, LOGIN Y ADMIN (Funciones 1-3)
# =====================================

import re
import os

# ---------- VARIABLES GLOBALES ----------
grafo = {}
centros_dict = {}  # Diccionario: codigo -> {nombre, region, subregion}
rutas_list = []    # Lista de rutas: (origen, destino, distancia, costo)
regiones_arbol = {}  # Árbol jerárquico: region -> subregiones -> centros

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
    
    print("✅ Usuario registrado correctamente")

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

# ---------- ALGORITMO DE ORDENAMIENTO ----------
def ordenamiento_burbuja(lista, campo):
    n = len(lista)
    for i in range(n-1):
        for j in range(0, n-i-1):
            if getattr(lista[j], campo) > getattr(lista[j+1], campo):
                lista[j], lista[j+1] = lista[j+1], lista[j]
    return lista

# ---------- ALGORITMO DE BÚSQUEDA ----------
def busqueda_secuencial(lista, campo, valor):
    resultados = []
    for item in lista:
        if getattr(item, campo) == valor:
            resultados.append(item)
    return resultados

# ---------- FUNCIONES 1, 2 y 3 DEL ADMINISTRADOR ----------
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
        
        campo_opcion = input("Seleccione (1-3): ").strip()
        
        # Convertir a lista de objetos Centro
        centros_objetos = []
        for codigo, datos in centros_dict.items():
            centros_objetos.append(Centro(codigo, datos["nombre"], datos["region"], datos["subregion"]))
        
        # Mapear selección de campo
        campos = {1: "codigo", 2: "nombre", 3: "region"}
        campo = campos.get(int(campo_opcion), "codigo")
        
        # Aplicar ordenamiento
        centros_ordenados = ordenamiento_burbuja(centros_objetos.copy(), campo)
        
        print("\n" + "="*80)
        print(f"CENTROS ORDENADOS POR {campo.upper()} (Ordenamiento Burbuja)")
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
                print()
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
def menu_cliente(usuario_info):  # Mantenido exactamente como en tu segundo código
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
            case "2":
                print("---Consultar ruta óptima---")
            case "3":
                print("---Seleccionar centros---")
            case "4":
                print("---Guardar ruta---")
            case "5":
                print("Cerrando sesión de cliente...")
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