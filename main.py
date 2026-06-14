"""
main.py
Punto de entrada del juego. Aquí solo va:
  - detección de resolución del monitor + escalado del juego
  - instanciar Personaje, Enemigo, plataformas
  - bucle principal: eventos, update de cada entidad, dibujado
  - HUD (vidas + puntaje) y pantalla de Game Over

La lógica de cada cosa vive en su propio archivo:
  - Entidades.py  → EntidadJuego, Personaje, Enemigo
"""

import sys
import pygame
from Entidades import Personaje, Enemigo

# ---------------------------------------------------------------------------
# Resolución lógica del juego (fija, no cambia)
# ---------------------------------------------------------------------------


BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (0, 100, 255)
ROJO = (255, 0, 0)
VERDE = (0, 200, 0)
GRIS = (120, 120, 120)
NARANJA = (255, 140, 0)
Fondo_oscuro = (20, 20, 25)

# ---------------------------------------------------------------------------
# Inicialización de pygame
# ---------------------------------------------------------------------------
pygame.init()

# Detección de resolución del monitor actual
info = pygame.display.Info()
ANCHO = info.current_w
ALTO = info.current_h

# Creamos la ventana del tamaño del monitor
pantalla = pygame.display.set_mode(
    (ANCHO, ALTO),
    pygame.FULLSCREEN
)
pygame.display.set_caption("Cuadrado con Cable y Enemigo")

# Superficie lógica: el juego se dibuja aquí a 800x500 y luego se escala al monitor


clock = pygame.time.Clock()


FUENTE = pygame.font.SysFont("Arial", 60)
FUENTE_PEQ = pygame.font.SysFont("Arial", 25)
FUENTE_HUD = pygame.font.SysFont("Arial", 22)

# ---------------------------------------------------------------------------
# Nivel: puntos A/B y plataformas
# ---------------------------------------------------------------------------
PUNTO_A = (int(ANCHO * 0.10), int(ALTO * 0.84))
PUNTO_B = (int(ANCHO * 0.90), int(ALTO * 0.24))

PLATAFORMAS = [
    pygame.Rect(0, int(ALTO * 0.92), ANCHO, int(ALTO * 0.08)),

    pygame.Rect(
        int(ANCHO * 0.20),
        int(ALTO * 0.74),
        int(ANCHO * 0.20),
        int(ALTO * 0.04)
    ),

    pygame.Rect(
        int(ANCHO * 0.50),
        int(ALTO * 0.58),
        int(ANCHO * 0.20),
        int(ALTO * 0.04)
    ),

    pygame.Rect(
        int(ANCHO * 0.76),
        int(ALTO * 0.40),
        int(ANCHO * 0.16),
        int(ALTO * 0.04)
    ),
]

# ---------------------------------------------------------------------------
# Entidades
# ---------------------------------------------------------------------------
tam_jugador = int(min(ANCHO, ALTO) * 0.05)

jugador = Personaje(
    PUNTO_A[0],
    PUNTO_A[1] - tam_jugador,
    tamano=tam_jugador
)

enemigo = Enemigo(
    x=int(ANCHO * 0.31),
    y=int(ALTO * 0.66),
    tamano=int(min(ANCHO, ALTO) * 0.04),
    velocidad=max(3, ANCHO // 500),
    min_x=int(ANCHO * 0.22),
    max_x=int(ANCHO * 0.70)
)

ganaste = False
game_over = False

# Para que el enemigo no mate al jugador infinitamente en el mismo toque
tiempo_invulnerable = 0  # ms en los que el jugador no puede morir
duracion_invencible = 1500  # 1.5 segundos


# ---------------------------------------------------------------------------
# Helpers de dibujo (trabajan sobre pantalla, no sobre pantalla)
# ---------------------------------------------------------------------------
def dibujar_texto(texto, fuente, color, pos):
    img = fuente.render(texto, True, color)
    pantalla.blit(img, pos)


def dibujar_nivel():
    for plataforma in PLATAFORMAS:
        pygame.draw.rect(pantalla, GRIS, plataforma)

    pygame.draw.circle(pantalla, ROJO, PUNTO_A, 12)
    dibujar_texto("A", FUENTE_PEQ, NEGRO, (PUNTO_A[0] - 8, PUNTO_A[1] - 40))

    pygame.draw.circle(pantalla, VERDE, PUNTO_B, 15)
    dibujar_texto("B", FUENTE_PEQ, NEGRO, (PUNTO_B[0] - 8, PUNTO_B[1] - 40))


def dibujar_cable():
    if jugador.tiene_cable:
        pygame.draw.line(pantalla, AZUL, PUNTO_A, jugador.forma.center, 5)
    else:
        dibujar_texto(
            "Cable cortado: vuelve al punto A",
            FUENTE_PEQ,
            ROJO,
            (20, 55),
        )


def dibujar_hud():
    # Vidas: dibujamos N corazones en la esquina superior derecha
    texto_vidas = FUENTE_HUD.render(f"Vidas: {jugador.vidas}", True, NEGRO)
    pantalla.blit(texto_vidas, (ANCHO - texto_vidas.get_width() - 20, 20))

    # Puntaje
    texto_puntos = FUENTE_HUD.render(f"Puntos: {jugador.puntaje}", True, NEGRO)
    pantalla.blit(texto_puntos, (20, 470))


def dibujar_game_over():
    pantalla.fill((255, 220, 220))
    texto = FUENTE.render("GAME OVER", True, ROJO)
    rect = texto.get_rect(center=(ANCHO // 2, ALTO // 2 - 30))
    pantalla.blit(texto, rect)

    puntos = FUENTE_PEQ.render(f"Puntaje final: {jugador.puntaje}", True, NEGRO)
    rect2 = puntos.get_rect(center=(ANCHO // 2, ALTO // 2 + 30))
    pantalla.blit(puntos, rect2)

    reiniciar = FUENTE_PEQ.render("Presiona R para reiniciar", True, NEGRO)
    rect3 = reiniciar.get_rect(center=(ANCHO // 2, ALTO // 2 + 70))
    pantalla.blit(reiniciar, rect3)


def dibujar_ganaste():
    pantalla.fill((220, 255, 220))
    texto = FUENTE.render("¡GANASTE!", True, VERDE)
    rect = texto.get_rect(center=(ANCHO // 2, ALTO // 2 - 30))
    pantalla.blit(texto, rect)

    puntos = FUENTE_PEQ.render(f"Puntaje final: {jugador.puntaje}", True, NEGRO)
    rect2 = puntos.get_rect(center=(ANCHO // 2, ALTO // 2 + 30))
    pantalla.blit(puntos, rect2)

    reiniciar = FUENTE_PEQ.render("Presiona R para reiniciar", True, NEGRO)
    rect3 = reiniciar.get_rect(center=(ANCHO // 2, ALTO // 2 + 70))
    pantalla.blit(reiniciar, rect3)


def reiniciar_partida():
    """Resetea al jugador, enemigo y estado de la partida."""
    global ganaste, game_over, tiempo_invulnerable
    jugador.vidas = jugador.vidas_max
    jugador.puntaje = 0
    jugador.tiene_cable = True
    jugador.forma.x = PUNTO_A[0]
    jugador.forma.y = PUNTO_A[1] - 40
    jugador.vel_x = 0
    jugador.vel_y = 0
    enemigo.x = 250
    enemigo.velocidad = 3
    ganaste = False
    game_over = False
    tiempo_invulnerable = 0


# ---------------------------------------------------------------------------
# Bucle principal
# ---------------------------------------------------------------------------
while True:
    # --- Eventos ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if evento.key == pygame.K_r and (ganaste or game_over):
                reiniciar_partida()

    if not ganaste and not game_over:
        # --- Update de entidades ---
        teclas = pygame.key.get_pressed()
        jugador.leer_input(teclas)
        jugador.update(PLATAFORMAS, ANCHO, ALTO)
        enemigo.update()

        # --- Cable: recuperar y cortar ---
        jugador.intentar_recuperar_cable(PUNTO_A)
        if jugador.tiene_cable and enemigo.corta_cable(PUNTO_A, jugador.forma.center):
            jugador.cortar_cable()

        # --- Colisión con el enemigo (quitar vida) ---
        # Usamos un rect del tamaño del triángulo centrado en (enemigo.x, enemigo.y)
        hitbox_enemigo = pygame.Rect(
            enemigo.x - enemigo.tamano,
            enemigo.y - enemigo.tamano,
            enemigo.tamano * 2,
            enemigo.tamano * 2,
        )
        ahora = pygame.time.get_ticks()
        if jugador.forma.colliderect(hitbox_enemigo) and ahora > tiempo_invulnerable:
            if not jugador.perder_vida():
                game_over = True
            else:
                # Lo mandamos de vuelta al punto A y le damos un ratito de invulnerabilidad
                jugador.reiniciar_posicion(PUNTO_A[0], PUNTO_A[1] - 40)
                tiempo_invulnerable = ahora + duracion_invencible

        # --- Victoria: +100 puntos al conectar el cable en el punto B ---
        if jugador.llego_a_meta(PUNTO_B):
            if not ganaste:
                jugador.puntaje += jugador.puntos_por_cable
            ganaste = True

    # --- Dibujado ---
    # 1) Pintamos la superficie lógica del juego (800x500)
    pantalla.fill(BLANCO)

    if game_over:
        dibujar_game_over()
    elif ganaste:
        dibujar_ganaste()
    else:
        dibujar_cable()
        dibujar_nivel()
        enemigo.draw(pantalla)
        pygame.draw.rect(pantalla, NEGRO, jugador.forma)
        dibujar_texto(
            "Mover: A/D o Flechas | Saltar: W, Arriba o Espacio",
            FUENTE_PEQ,
            NEGRO,
            (20, 20),
        )
        dibujar_hud()

    # 2) Escalamos al monitor con una sola operación y la pegamos centrada
 # fondo detrás del juego (barras negras)
    

    pygame.display.flip()
    clock.tick(60)
