import sqlite3
import os
from datetime import date

DB_NAME = os.path.join(os.path.dirname(__file__), "videojuego.db")

# =========================
# CONEXIÓN
# =========================
def conectar():
    return sqlite3.connect(DB_NAME)

# ACTIVA FOREIGN KEYS
def init_db():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    conn.close()

# =========================
# PERSONAJE
# =========================
def crear_personaje(nombre, vida, ataque, defensa):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO personaje (nombre, vida, ataque, defensa)
        VALUES (?, ?, ?, ?)
    """, (nombre, vida, ataque, defensa))

    conn.commit()
    conn.close()


def obtener_personajes():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM personaje")
    datos = cursor.fetchall()

    conn.close()
    return datos

# =========================
# PUNTAJE
# =========================
def guardar_puntaje(puntos, personaje_id):
    conn = conectar()
    cursor = conn.cursor()

    hoy = date.today().isoformat()

    cursor.execute("""
        INSERT INTO puntaje (puntos, fecha, personaje_id)
        VALUES (?, ?, ?)
    """, (puntos, hoy, personaje_id))

    conn.commit()
    conn.close()


def ranking_del_dia():
    conn = conectar()
    cursor = conn.cursor()

    hoy = date.today().isoformat()

    cursor.execute("""
        SELECT p.nombre, pt.puntos, pt.fecha
        FROM personaje p
        JOIN puntaje pt ON p.id = pt.personaje_id
        WHERE pt.fecha = ?
        ORDER BY pt.puntos DESC
    """, (hoy,))

    datos = cursor.fetchall()

    conn.close()
    return datos

# =========================
# OPCIONAL (BORRAR / LIMPIAR)
# =========================
def limpiar_puntajes():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM puntaje")

    conn.commit()
    conn.close()