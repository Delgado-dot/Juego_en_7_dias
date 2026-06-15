import sys
import pygame
from Entidades import Personaje, Enemigo
from game.UI.hud import HUD
from game.level import Level, NIVELES
from game.UI.menu import Menu
from game.UI.game_over import GameOver
from game.UI.victoria import Victoria
from config import (
    FPS, TITULO, BLANCO, NEGRO, AZUL, ROJO,
    VERDE, GRIS, DURACION_INVENCIBLE
)

pygame.init()

info = pygame.display.Info()
ANCHO = info.current_w
ALTO = info.current_h

pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
pygame.display.set_caption(TITULO)

clock = pygame.time.Clock()

FUENTE = pygame.font.SysFont("Arial", 60)
FUENTE_PEQ = pygame.font.SysFont("Arial", 25)

tam_jugador = int(min(ANCHO, ALTO) * 0.03)


def crear_nivel(idx):
    global nivel, enemigos, tiempo_restante, nivel_completado
    nivel = Level(ANCHO, ALTO, idx)
    enemigos = []
    for pos in nivel.pos_enemigos:
        enemigos.append(Enemigo(
            x=pos[0], y=pos[1],
            tamano=int(min(ANCHO, ALTO) * 0.04),
            velocidad=max(3, ANCHO // 500),
            min_x=pos[0] - int(ANCHO * 0.20),
            max_x=pos[0] + int(ANCHO * 0.20)
        ))
    tiempo_restante = nivel.tiempo_limite * 1000
    nivel_completado = False


def reiniciar_nivel():
    global game_over, tiempo_invulnerable, tiempo_restante, nivel_completado
    jugador.vidas = jugador.vidas_max
    jugador.puntaje = 0
    jugador.tiene_cable = True
    jugador.forma.x = nivel.punto_a[0]
    jugador.forma.y = nivel.punto_a[1] - tam_jugador
    jugador.vel_x = 0
    jugador.vel_y = 0
    for i, pos in enumerate(nivel.pos_enemigos):
        enemigos[i].x = pos[0]
        enemigos[i].velocidad = max(3, ANCHO // 500)
    game_over = False
    tiempo_invulnerable = 0
    tiempo_restante = nivel.tiempo_limite * 1000
    nivel_completado = False


def reiniciar_juego_completo():
    global nivel_actual_idx, game_over, victoria_final
    nivel_actual_idx = 0
    crear_nivel(0)
    jugador.vidas = jugador.vidas_max
    jugador.puntaje = 0
    jugador.tiene_cable = True
    jugador.forma.x = nivel.punto_a[0]
    jugador.forma.y = nivel.punto_a[1] - tam_jugador
    jugador.vel_x = 0
    jugador.vel_y = 0
    game_over = False
    victoria_final = False


def dibujar_texto(texto, fuente, color, pos):
    img = fuente.render(texto, True, color)
    pantalla.blit(img, pos)


def dibujar_nivel():
    for plataforma in nivel.plataformas:
        pygame.draw.rect(pantalla, GRIS, plataforma)
    pygame.draw.circle(pantalla, ROJO, nivel.punto_a, 12)
    dibujar_texto("A", FUENTE_PEQ, NEGRO, (nivel.punto_a[0] - 8, nivel.punto_a[1] - 40))
    pygame.draw.circle(pantalla, VERDE, nivel.punto_b, 15)
    dibujar_texto("B", FUENTE_PEQ, NEGRO, (nivel.punto_b[0] - 8, nivel.punto_b[1] - 40))


def dibujar_cable():
    if jugador.tiene_cable:
        pygame.draw.line(pantalla, AZUL, nivel.punto_a, jugador.forma.center, 5)
    else:
        ancho_cable = FUENTE_PEQ.size("Cable cortado: vuelve al punto A")[0]
        dibujar_texto("Cable cortado: vuelve al punto A", FUENTE_PEQ, ROJO, (ANCHO // 2 - ancho_cable // 2, 80))


nivel_actual_idx = 0
nivel = None
enemigos = []
tiempo_restante = 0
nivel_completado = False
game_over = False
victoria_final = False
tiempo_invulnerable = 0

crear_nivel(0)
jugador = Personaje(nivel.punto_a[0], nivel.punto_a[1] - tam_jugador, tamano=tam_jugador)
hud = HUD()

while True:
    menu = Menu(pantalla, ANCHO, ALTO)
    resultado_menu = menu.ejecutar()
    if resultado_menu == "salir":
        pygame.quit()
        sys.exit()

    reiniciar_juego_completo()

    jugando = True
    while jugando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    jugando = False

        if not game_over and not victoria_final:
            dt = clock.get_time()
            tiempo_restante -= dt

            if tiempo_restante <= 0:
                tiempo_restante = 0
                game_over = True

            teclas = pygame.key.get_pressed()
            jugador.leer_input(teclas)
            jugador.update(nivel.plataformas, ANCHO, ALTO)

            for enemigo in enemigos:
                enemigo.update()

            jugador.intentar_recuperar_cable(nivel.punto_a)
            for enemigo in enemigos:
                if jugador.tiene_cable and enemigo.corta_cable(nivel.punto_a, jugador.forma.center):
                    jugador.cortar_cable()

            ahora = pygame.time.get_ticks()
            for enemigo in enemigos:
                hitbox_enemigo = pygame.Rect(
                    enemigo.x - enemigo.tamano,
                    enemigo.y - enemigo.tamano,
                    enemigo.tamano * 2,
                    enemigo.tamano * 2,
                )
                if jugador.forma.colliderect(hitbox_enemigo) and ahora > tiempo_invulnerable:
                    if not jugador.perder_vida():
                        game_over = True
                    else:
                        jugador.reiniciar_posicion(nivel.punto_a[0], nivel.punto_a[1] - tam_jugador)
                        tiempo_invulnerable = ahora + DURACION_INVENCIBLE

            if not nivel_completado and jugador.llego_a_meta(nivel.punto_b):
                nivel_completado = True
                jugador.puntaje += jugador.puntos_por_cable
                siguiente = nivel_actual_idx + 1
                if siguiente >= len(NIVELES):
                    victoria_final = True
                else:
                    nivel_actual_idx = siguiente
                    crear_nivel(nivel_actual_idx)
                    jugador.forma.x = nivel.punto_a[0]
                    jugador.forma.y = nivel.punto_a[1] - tam_jugador
                    jugador.vel_x = 0
                    jugador.vel_y = 0
                    jugador.tiene_cable = True

        pantalla.fill(BLANCO)

        if game_over:
            pygame.display.flip()
            go = GameOver(pantalla, ANCHO, ALTO, jugador.puntaje)
            resultado = go.ejecutar()
            if resultado == "reintentar":
                reiniciar_nivel()
            elif resultado == "menu":
                jugando = False
        elif victoria_final:
            pygame.display.flip()
            vic = Victoria(pantalla, ANCHO, ALTO, jugador.puntaje)
            resultado = vic.ejecutar()
            jugando = False
        else:
            dibujar_cable()
            dibujar_nivel()
            for enemigo in enemigos:
                enemigo.draw(pantalla)
            pygame.draw.rect(pantalla, NEGRO, jugador.forma)
            ancho_texto = FUENTE_PEQ.size("Mover: A/D o Flechas | Saltar: W, Arriba o Espacio")[0]
            dibujar_texto("Mover: A/D o Flechas | Saltar: W, Arriba o Espacio", FUENTE_PEQ, BLANCO, (ANCHO // 2 - ancho_texto // 2, ALTO - 35))
            hud.draw(pantalla, jugador.vidas, jugador.vidas_max, 0, tiempo_restante)

        pygame.display.flip()
        clock.tick(FPS)