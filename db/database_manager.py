import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join("db", "videojuego.db")

PERSONAJES_CSV = "compat"


def _conexion():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def inicializar():
    conn = _conexion()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jugador (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            nivel INTEGER DEFAULT 1,
            puntos_totales INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personaje (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            vida INTEGER DEFAULT 100,
            jugador_id INTEGER NOT NULL,
            FOREIGN KEY (jugador_id) REFERENCES jugador(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS niveles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_nivel TEXT NOT NULL,
            dificultad INTEGER DEFAULT 1,
            descripcion TEXT DEFAULT ''
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS objetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_objeto TEXT NOT NULL,
            tipo TEXT NOT NULL,
            descripcion TEXT DEFAULT '',
            personaje_id INTEGER NOT NULL,
            FOREIGN KEY (personaje_id) REFERENCES personaje(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS puntaje (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            puntos INTEGER DEFAULT 0,
            fecha TEXT NOT NULL,
            personaje_id INTEGER NOT NULL,
            nivel_id INTEGER DEFAULT 1,
            chaqueta_equipada INTEGER DEFAULT 0,
            tiempo_juego TEXT DEFAULT '00:00',
            FOREIGN KEY (personaje_id) REFERENCES personaje(id)
        )
    """)
    conn.commit()
    conn.close()


def crear_jugador(nombre, nivel=1, puntos_totales=0):
    conn = _conexion()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO jugador (nombre, nivel, puntos_totales) VALUES (?, ?, ?)",
        (nombre, nivel, puntos_totales)
    )
    id_nuevo = cursor.lastrowid
    conn.commit()
    conn.close()
    return id_nuevo


def obtener_jugadores():
    conn = _conexion()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, nivel, puntos_totales FROM jugador ORDER BY id")
    datos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return datos


def crear_personaje(nombre, vida, jugador_id):
    conn = _conexion()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO personaje (nombre, vida, jugador_id) VALUES (?, ?, ?)",
        (nombre, vida, jugador_id)
    )
    id_nuevo = cursor.lastrowid
    conn.commit()
    conn.close()
    return id_nuevo


def obtener_personajes():
    conn = _conexion()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, vida, jugador_id FROM personaje ORDER BY id")
    datos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return datos


def crear_nivel_db(nombre_nivel, dificultad, descripcion):
    conn = _conexion()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO niveles (nombre_nivel, dificultad, descripcion) VALUES (?, ?, ?)",
        (nombre_nivel, dificultad, descripcion)
    )
    id_nuevo = cursor.lastrowid
    conn.commit()
    conn.close()
    return id_nuevo


def obtener_niveles():
    conn = _conexion()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre_nivel, dificultad, descripcion FROM niveles ORDER BY id")
    datos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return datos


def crear_objeto(nombre_objeto, tipo, descripcion, personaje_id):
    conn = _conexion()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO objetos (nombre_objeto, tipo, descripcion, personaje_id) VALUES (?, ?, ?, ?)",
        (nombre_objeto, tipo, descripcion, personaje_id)
    )
    id_nuevo = cursor.lastrowid
    conn.commit()
    conn.close()
    return id_nuevo


def obtener_objetos():
    conn = _conexion()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre_objeto, tipo, descripcion, personaje_id FROM objetos ORDER BY id")
    datos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return datos


def guardar_puntaje(puntos, fecha, personaje_id, nivel_id, chaqueta_equipada, tiempo_juego):
    conn = _conexion()
    cursor = conn.cursor()
    if fecha is None:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
        """INSERT INTO puntaje (puntos, fecha, personaje_id, nivel_id, chaqueta_equipada, tiempo_juego)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (puntos, fecha, personaje_id, nivel_id, chaqueta_equipada, tiempo_juego)
    )
    id_nuevo = cursor.lastrowid
    conn.commit()
    conn.close()
    return id_nuevo


def obtener_puntajes():
    conn = _conexion()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, puntos, fecha, personaje_id, nivel_id, chaqueta_equipada, tiempo_juego FROM puntaje ORDER BY id")
    datos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return datos


def top_5_puntajes():
    conn = _conexion()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, puntos, fecha, personaje_id, nivel_id, chaqueta_equipada, tiempo_juego FROM puntaje ORDER BY puntos DESC LIMIT 5")
    datos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return datos


def leer_csv(ruta):
    return obtener_personajes()


def buscar_jugador_por_nombre(nombre):
    conn = _conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, nivel, puntos_totales FROM jugador WHERE LOWER(nombre) = LOWER(?) LIMIT 1", (nombre,))
    jugador = cursor.fetchone()
    conn.close()
    return jugador


def iniciar_jugador(nombre):
    jugador = buscar_jugador_por_nombre(nombre)
    if jugador:
        print("Jugador encontrado:", jugador)
        return jugador
    id_jugador = crear_jugador(nombre, 1, 0)
    id_personaje = crear_personaje("Explorador", 100, id_jugador)
    print("Jugador nuevo creado")
    print("ID jugador:", id_jugador)
    print("ID personaje:", id_personaje)
    return obtener_jugador_por_id(id_jugador)


def obtener_jugador_por_id(id_jugador):
    conn = _conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, nivel, puntos_totales FROM jugador WHERE id = ?", (id_jugador,))
    jugador = cursor.fetchone()
    conn.close()
    return jugador


inicializar()
