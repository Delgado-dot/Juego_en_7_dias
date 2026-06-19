import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ventana
ANCHO_VENTANA = 0
ALTO_VENTANA = 0
FPS = 60
TITULO = "Jumper rack"

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (0, 100, 255)
ROJO = (255, 0, 0)
VERDE = (0, 200, 0)
GRIS = (120, 120, 120)
MORADO = (160, 0, 200)
FONDO_OSCURO = (2, 20, 40)

RUTA_SPRITES = os.path.join(BASE_DIR, "assets", "sprites")
RUTA_SONIDOS = os.path.join(BASE_DIR, "assets", "sounds")
RUTA_FUENTES = os.path.join(BASE_DIR, "assets", "fonts")
RUTA_IMAGENES = os.path.join(BASE_DIR, "assets", "images")

SPRITE_JUGADOR = os.path.join(RUTA_SPRITES, "jugador.png")


SPRITE_ENEMIGO = os.path.join(RUTA_SPRITES, "enemigo.png")

SPRITE_FONDO = os.path.join(RUTA_IMAGENES, "Fondo1.png")
SPRITE_PLATAFORMA = os.path.join(RUTA_SPRITES, "plataforma.png")

SPRITE_CORAZON_LLENO = os.path.join(RUTA_IMAGENES, "HUD", "dark blue heart pixel art.png")
SPRITE_CORAZON_VACIO = os.path.join(RUTA_IMAGENES, "HUD", "dark black heart pixel art.png")
SPRITE_CHAQUETA = os.path.join(RUTA_IMAGENES, "HUD", "chaqueta.png")
FUENTE_HUD = os.path.join(RUTA_FUENTES, "PressStart2P-Regular.ttf")

MUSICA_JUEGO = os.path.join(RUTA_SONIDOS, "musica_juego.mp3")
MUSICA_MENU = os.path.join(RUTA_SONIDOS, "musica_menu.mp3")
SONIDO_CABLE_CORTADO = os.path.join(RUTA_SONIDOS, "cable_cortado.mp3")
SONIDO_PERDER_VIDA = os.path.join(RUTA_SONIDOS, "perder_vida.mp3")
SONIDO_GANAR = os.path.join(RUTA_SONIDOS, "sonido_victoria.mp3")
SONIDO_RECOGER_ITEM = os.path.join(RUTA_SONIDOS, "recoger_item.mp3")
sonido_game_over = os.path.join(RUTA_SONIDOS, "musica_gameover.mp3")
VELOCIDAD_JUGADOR = 5
GRAVEDAD = 0.6
FUERZA_SALTO = -18
VIDAS_INICIALES = 3

DURACION_INVENCIBLE = 1500
PUNTOS_POR_CABLE = 100