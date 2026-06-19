import csv
import os
from datetime import datetime

DATA_DIR = "db"

JUGADORES_CSV = os.path.join(DATA_DIR, "jugador.csv")
PERSONAJES_CSV = os.path.join(DATA_DIR, "personaje.csv")
PUNTAJES_CSV = os.path.join(DATA_DIR, "puntaje.csv")
NIVELES_CSV = os.path.join(DATA_DIR, "niveles.csv")
OBJETOS_CSV = os.path.join(DATA_DIR, "objetos.csv")

ENCABEZADOS = {
    JUGADORES_CSV: ["id", "nombre", "nivel", "puntos_totales"],
    PERSONAJES_CSV: ["id", "nombre", "vida", "jugador_id"],
    PUNTAJES_CSV: ["id", "puntos", "fecha", "personaje_id", "nivel_id", "chaqueta_equipada", "tiempo_juego"],
    NIVELES_CSV: ["id", "nombre_nivel", "dificultad", "descripcion"],
    OBJETOS_CSV: ["id", "nombre_objeto", "tipo", "descripcion", "personaje_id"],
}

def inicializar():
    os.makedirs(DATA_DIR, exist_ok=True)
    for ruta, encabezado in ENCABEZADOS.items():
        if not os.path.exists(ruta):
            with open(ruta, "w", newline="", encoding="utf-8") as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(encabezado)

def leer_csv(ruta):
    with open(ruta, "r", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        return list(lector)

def nuevo_id(ruta):
    with open(ruta, "r", encoding="utf-8") as archivo:
        lector = csv.reader(archivo)
        filas = list(lector)
    return len(filas)

def agregar_fila(ruta, fila):
    with open(ruta, "a", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(fila)

def existe_id(ruta, id_buscar):
    datos = leer_csv(ruta)
    for fila in datos:
        if fila["id"] == str(id_buscar):
            return True
    return False

def crear_jugador(nombre, nivel=1, puntos_totales=0):
    id_nuevo = nuevo_id(JUGADORES_CSV)
    agregar_fila(JUGADORES_CSV, [id_nuevo, nombre, nivel, puntos_totales])
    return id_nuevo

def obtener_jugadores():
    return leer_csv(JUGADORES_CSV)

def crear_personaje(nombre, vida, jugador_id):
    if not existe_id(JUGADORES_CSV, jugador_id):
        print("Error: el jugador_id no existe")
        return None
    id_nuevo = nuevo_id(PERSONAJES_CSV)
    agregar_fila(PERSONAJES_CSV, [id_nuevo, nombre, vida, jugador_id])
    return id_nuevo

def obtener_personajes():
    return leer_csv(PERSONAJES_CSV)

def crear_nivel_db(nombre_nivel, dificultad, descripcion):
    id_nuevo = nuevo_id(NIVELES_CSV)
    agregar_fila(NIVELES_CSV, [id_nuevo, nombre_nivel, dificultad, descripcion])
    return id_nuevo

def obtener_niveles():
    return leer_csv(NIVELES_CSV)

def crear_objeto(nombre_objeto, tipo, descripcion, personaje_id):
    if not existe_id(PERSONAJES_CSV, personaje_id):
        print("Error: el personaje_id no existe")
        return None
    id_nuevo = nuevo_id(OBJETOS_CSV)
    agregar_fila(OBJETOS_CSV, [id_nuevo, nombre_objeto, tipo, descripcion, personaje_id])
    return id_nuevo

def obtener_objetos():
    return leer_csv(OBJETOS_CSV)

def guardar_puntaje(puntos, fecha, personaje_id, nivel_id, chaqueta_equipada, tiempo_juego):
    if not existe_id(PERSONAJES_CSV, personaje_id):
        print("Error: el personaje_id no existe")
        return None
    id_nuevo = nuevo_id(PUNTAJES_CSV)
    agregar_fila(PUNTAJES_CSV, [id_nuevo, puntos, fecha, personaje_id, nivel_id, chaqueta_equipada, tiempo_juego])
    return id_nuevo

def obtener_puntajes():
    return leer_csv(PUNTAJES_CSV)

def top_5_puntajes():
    puntajes = obtener_puntajes()
    puntajes.sort(key=lambda x: int(x["puntos"]), reverse=True)
    return puntajes[:5]

inicializar()