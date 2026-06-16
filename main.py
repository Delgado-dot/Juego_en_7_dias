import sys
import pygame
from Entidades import Personaje, Trampa
from game.UI.hud import HUD
from game.level import Level, NIVELES
from game.UI.menu import Menu
from game.UI.game_over import GameOver
from game.UI.victoria import Victoria
from config import (
    FPS, TITULO, NEGRO, AZUL, ROJO,
    VERDE, GRIS, DURACION_INVENCIBLE,
    MUSICA_JUEGO, SPRITE_FONDO
)

pygame.init()
pygame.mixer.init()

info = pygame.display.Info()
ANCHO = info.current_w
ALTO = info.current_h

pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
pygame.display.set_caption(TITULO)

reloj = pygame.time.Clock()

fuente = pygame.font.SysFont("Arial", 60)
fuente_peq = pygame.font.SysFont("Arial", 25)

try:
    fondo_juego = pygame.image.load(SPRITE_FONDO).convert()
    fondo_juego = pygame.transform.scale(fondo_juego, (ANCHO, ALTO))
except:
    fondo_juego = None

try:
    pygame.mixer.music.load(MUSICA_JUEGO)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except:
    pass

tam_jugador = int(min(ANCHO, ALTO) * 0.03)


def crear_nivel(idx):
    global nivel, trampas, tiempo_restante, nivel_completado, punto_cable_actual
    nivel = Level(ANCHO, ALTO, idx)
    trampas = []
    for pos in nivel.pos_trampas:
        trampas.append(Trampa(
            x=pos[0], y=pos[1],
            tamano=int(min(ANCHO, ALTO) * 0.04),
            velocidad=max(3, ANCHO // 500),
            min_x=pos[0] - int(ANCHO * 0.20),
            max_x=pos[0] + int(ANCHO * 0.20)
        ))
    tiempo_restante = nivel.tiempo_limite * 1000
    nivel_completado = False
    punto_cable_actual = nivel.punto_a


def reiniciar_nivel():
    global game_over, tiempo_sin_daño, tiempo_restante, nivel_completado, punto_cable_actual
    jugador.vidas = jugador.vidas_max
    jugador.puntaje = 0
    jugador.tiene_cable = True
    jugador.chaquetas = 0
    jugador.forma.x = nivel.punto_a[0]
    jugador.forma.y = nivel.punto_a[1] - tam_jugador
    jugador.vel_x = 0
    jugador.vel_y = 0
    for i, pos in enumerate(nivel.pos_trampas):
        trampas[i].x = pos[0]
        trampas[i].y = pos[1]
        trampas[i].velocidad = max(3, ANCHO // 500)
    game_over = False
    tiempo_sin_daño = 0
    tiempo_restante = nivel.tiempo_limite * 1000
    nivel_completado = False
    punto_cable_actual = nivel.punto_a
    nivel.pos_chaqueta = nivel.pos_chaqueta_original


def reiniciar_juego():
    global nivel_idx, game_over, victoria_final, punto_cable_actual
    nivel_idx = 0
    crear_nivel(0)
    jugador.vidas = jugador.vidas_max
    jugador.puntaje = 0
    jugador.tiene_cable = True
    jugador.chaquetas = 0
    jugador.forma.x = nivel.punto_a[0]
    jugador.forma.y = nivel.punto_a[1] - tam_jugador
    jugador.vel_x = 0
    jugador.vel_y = 0
    game_over = False
    victoria_final = False
    punto_cable_actual = nivel.punto_a


def camara():
    cam_y = jugador.forma.centery - ALTO // 2
    cam_y = max(0, min(cam_y, nivel.alto_total - ALTO))
    return 0, cam_y


def texto(msg, fnt, color, pos):
    img = fnt.render(msg, True, color)
    pantalla.blit(img, pos)


def dibujar_fondo(cam_y):
    if fondo_juego:
        pantalla.blit(fondo_juego, (0, 0))
    else:
        pantalla.fill((255, 255, 255))


def dibujar_nivel(cam_y):
    for p in nivel.plataformas:
        r = pygame.Rect(p.x, p.y - cam_y, p.w, p.h)
        if -p.h < r.y < ALTO + p.h:
            pygame.draw.rect(pantalla, GRIS, r)

    ax, ay = nivel.punto_a[0], nivel.punto_a[1] - cam_y
    pygame.draw.circle(pantalla, ROJO, (ax, ay), 12)
    texto("A", fuente_peq, NEGRO, (ax - 8, ay - 40))

    bx, by = nivel.punto_b[0], nivel.punto_b[1] - cam_y
    pygame.draw.circle(pantalla, VERDE, (bx, by), 15)
    texto("B", fuente_peq, NEGRO, (bx - 8, by - 40))

    for cp in nivel.checkpoints:
        cx, cy = cp[0], cp[1] - cam_y
        pygame.draw.circle(pantalla, (0, 200, 255), (cx, cy), 10)
        texto("C", fuente_peq, NEGRO, (cx - 8, cy - 30))

    if nivel.pos_chaqueta:
        jx, jy = nivel.pos_chaqueta[0], nivel.pos_chaqueta[1] - cam_y
        pygame.draw.rect(pantalla, (255, 165, 0), (jx - 15, jy - 15, 30, 30))
        texto("J", fuente_peq, NEGRO, (jx - 8, jy - 10))


def dibujar_cable(cam_y):
    ax, ay = punto_cable_actual[0], punto_cable_actual[1] - cam_y
    jx, jy = jugador.forma.centerx, jugador.forma.centery - cam_y
    if jugador.tiene_cable:
        pygame.draw.line(pantalla, NEGRO, (ax, ay), (jx, jy), 5)
    else:
        w = fuente_peq.size("Cable cortado: vuelve al punto C o A")[0]
        texto("Cable cortado: vuelve al punto C o A", fuente_peq, ROJO, (ANCHO // 2 - w // 2, 80))


nivel_idx = 0
nivel = None
trampas = []
tiempo_restante = 0
nivel_completado = False
game_over = False
victoria_final = False
tiempo_sin_daño = 0
punto_cable_actual = None

crear_nivel(0)
jugador = Personaje(nivel.punto_a[0], nivel.punto_a[1] - tam_jugador, tamano=tam_jugador)
hud = HUD()

while True:
    try:
        pygame.mixer.music.load(MUSICA_JUEGO)
        pygame.mixer.music.play(-1)
    except:
        pass

    menu = Menu(pantalla, ANCHO, ALTO)
    resultado = menu.ejecutar()
    if resultado == "salir":
        pygame.quit()
        sys.exit()

    try:
        pygame.mixer.music.load(MUSICA_JUEGO)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except:
        pass

    reiniciar_juego()

    jugando = True
    while jugando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    jugando = False

        cam_x, cam_y = camara()

        if not game_over and not victoria_final:
            dt = reloj.get_time()
            tiempo_restante -= dt
            if tiempo_restante <= 0:
                tiempo_restante = 0
                game_over = True

            teclas = pygame.key.get_pressed()
            jugador.leer_teclas(teclas)
            jugador.actualizar(nivel.plataformas, ANCHO, nivel.alto_total)

            for t in trampas:
                t.mover(nivel.plataformas)

            for cp in nivel.checkpoints:
                if jugador.distancia(cp) < 30:
                    punto_cable_actual = cp

            if nivel.pos_chaqueta:
                if jugador.distancia(nivel.pos_chaqueta) < 30:
                    jugador.chaquetas += 1
                    nivel.pos_chaqueta = None

            jugador.recuperar_cable(punto_cable_actual)

            for t in trampas:
                if jugador.tiene_cable and t.corta_cable(punto_cable_actual, jugador.forma.center):
                    jugador.cortar_cable()

            ahora = pygame.time.get_ticks()
            for t in trampas:
                hitbox = pygame.Rect(
                    t.x - t.tamano, int(t.y) - t.tamano,
                    t.tamano * 2, t.tamano * 2
                )
                if jugador.forma.colliderect(hitbox) and ahora > tiempo_sin_daño:
                    if not jugador.perder_vida():
                        game_over = True
                    else:
                        jugador.reiniciar_pos(punto_cable_actual[0], punto_cable_actual[1] - tam_jugador)
                        tiempo_sin_daño = ahora + DURACION_INVENCIBLE

            if not nivel_completado and jugador.llego_meta(nivel.punto_b):
                nivel_completado = True
                jugador.puntaje += jugador.puntos_cable
                siguiente = nivel_idx + 1
                if siguiente >= len(NIVELES):
                    victoria_final = True
                else:
                    nivel_idx = siguiente
                    crear_nivel(nivel_idx)
                    jugador.forma.x = nivel.punto_a[0]
                    jugador.forma.y = nivel.punto_a[1] - tam_jugador
                    jugador.vel_x = 0
                    jugador.vel_y = 0
                    jugador.tiene_cable = True

        dibujar_fondo(cam_y)

        if game_over:
            pygame.display.flip()
            pygame.mixer.music.stop()
            go = GameOver(pantalla, ANCHO, ALTO, jugador.puntaje)
            resultado = go.ejecutar()
            if resultado == "reintentar":
                reiniciar_nivel()
                try:
                    pygame.mixer.music.load(MUSICA_JUEGO)
                    pygame.mixer.music.play(-1)
                except:
                    pass
            elif resultado == "menu":
                jugando = False
        elif victoria_final:
            pygame.display.flip()
            pygame.mixer.music.stop()
            vic = Victoria(pantalla, ANCHO, ALTO, jugador.puntaje)
            vic.ejecutar()
            jugando = False
        else:
            dibujar_cable(cam_y)
            dibujar_nivel(cam_y)
            for t in trampas:
                t.dibujar(pantalla, cam_x, cam_y)
            jr = pygame.Rect(jugador.forma.x, jugador.forma.y - cam_y, jugador.forma.w, jugador.forma.h)
            pygame.draw.rect(pantalla, NEGRO, jr)
            w = fuente_peq.size("Mover: A/D o Flechas | Saltar: W, Arriba o Espacio")[0]
            texto("Mover: A/D o Flechas | Saltar: W, Arriba o Espacio", fuente_peq, (200, 200, 200), (ANCHO // 2 - w // 2, ALTO - 35))
            hud.draw(pantalla, jugador.vidas, jugador.vidas_max, jugador.chaquetas, tiempo_restante)

        pygame.display.flip()
        reloj.tick(FPS)