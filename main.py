import sys
import pygame
from Entidades import Personaje, Enemigo
from game.UI.hud import HUD
from game.level import Level
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

nivel = Level(ANCHO, ALTO, 0)

tam_jugador = int(min(ANCHO, ALTO) * 0.05)

jugador = Personaje(nivel.punto_a[0], nivel.punto_a[1] - tam_jugador, tamano=tam_jugador)

enemigos = []
for pos in nivel.pos_enemigos:
    enemigos.append(Enemigo(
        x=pos[0],
        y=pos[1],
        tamano=int(min(ANCHO, ALTO) * 0.04),
        velocidad=max(3, ANCHO // 500),
        min_x=pos[0] - int(ANCHO * 0.20),
        max_x=pos[0] + int(ANCHO * 0.20)
    ))

hud = HUD()
inicio_tiempo = pygame.time.get_ticks()
tiempo_restante = nivel.tiempo_limite * 1000
ganaste = False
game_over = False
tiempo_invulnerable = 0


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


def reiniciar_partida():
    global ganaste, game_over, tiempo_invulnerable, inicio_tiempo, tiempo_restante
    jugador.vidas = jugador.vidas_max
    jugador.puntaje = 0
    jugador.tiene_cable = True
    jugador.forma.x = nivel.punto_a[0]
    jugador.forma.y = nivel.punto_a[1] - 40
    jugador.vel_x = 0
    jugador.vel_y = 0
    for i, pos in enumerate(nivel.pos_enemigos):
        enemigos[i].x = pos[0]
        enemigos[i].velocidad = max(3, ANCHO // 500)
    ganaste = False
    game_over = False
    tiempo_invulnerable = 0
    inicio_tiempo = pygame.time.get_ticks()
    tiempo_restante = nivel.tiempo_limite * 1000


while True:
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
                    jugador.reiniciar_posicion(nivel.punto_a[0], nivel.punto_a[1] - 40)
                    tiempo_invulnerable = ahora + DURACION_INVENCIBLE

        if jugador.llego_a_meta(nivel.punto_b):
            if not ganaste:
                jugador.puntaje += jugador.puntos_por_cable
            ganaste = True

    pantalla.fill(BLANCO)

    if game_over:
        from game.UI.game_over import dibujar_game_over
        dibujar_game_over(pantalla, FUENTE, FUENTE_PEQ, NEGRO, ROJO, ANCHO, ALTO, jugador.puntaje)
    elif ganaste:
        from game.UI.victoria import dibujar_ganaste
        dibujar_ganaste(pantalla, FUENTE, FUENTE_PEQ, NEGRO, VERDE, ANCHO, ALTO, jugador.puntaje)
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