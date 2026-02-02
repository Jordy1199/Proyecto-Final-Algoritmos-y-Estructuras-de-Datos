## =====================================
# POLIDELIVERY - REGISTRO Y LOGIN
# =====================================

import re


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

    nombre = input("Nombre: ")
    apellido = input("Apellido: ")
    cedula = input("Cédula: ")
    edad = input("Edad: ")
    correo = input("Correo: ")

    while True:
        password = input("Contraseña: ")
        if password_segura(password):
            break
        else:
            print("La contraseña debe tener mayúscula, minúscula y número")

    while True:
        rol = input("Rol (administrador / cliente): ").lower()
        if rol in ["administrador", "cliente"]:
            break
        else:
            print("Rol inválido")

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
                if linea == "":
                    continue

                nombre, apellido, cedula, edad, correo, password, rol = linea.split(";")
                usuarios[correo] = {
                    "password": password,
                    "rol": rol
                }

    except FileNotFoundError:
        pass

    return usuarios


# ---------- LOGIN ----------
def login():
    usuarios = cargar_usuarios()

    print("\n===== LOGIN =====")
    correo = input("Correo: ")
    password = input("Contraseña: ")

    if correo in usuarios and usuarios[correo]["password"] == password:
        print("Ingreso exitoso")
        return usuarios[correo]["rol"]
    else:
        print(" Credenciales incorrectas")
        return None


# ---------- MENÚ ADMINISTRADOR ----------
def menu_admin():
    while True:
        print("\n===== MENÚ ADMINISTRADOR =====")
        print("1. Agregar centros")
        print("2. Listar centros")
        print("3. Actualizar información")
        print("4. Eliminar centros")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")

        match opcion:
            case "1":
                print("---Agregar centros---")
            case "2":
                print("---Listar centros---")
            case "3":
                print("---Actualizar información---")
            case "4":
                print("---Eliminar centros---")
            case "5":
                print("Cerrando sesión de administrador...")
                break
            case _:
                print("Opción inválida")


# ---------- MENÚ CLIENTE ----------
def menu_cliente():
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
    while True:
        print("\n===== POLIDELIVERY =====")
        print("1. Registrar nuevo usuario")
        print("2. Iniciar sesión")
        print("3. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            registrar_usuario()

        elif opcion == "2":
            rol = login()
            if rol == "admin":
                menu_admin()
            elif rol == "cliente":
                menu_cliente()

        elif opcion == "3":
            print("Saliendo del sistema...")
            break

        else:
            print("Opción inválida")


# ---------- EJECUCIÓN ----------
principal()

