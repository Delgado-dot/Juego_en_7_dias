import sys
import math
import pygame
from Entidades import Personaje, Trampa
from game.UI.hud import HUD
from game.level import Level, NIVELES
from game.UI.menu import Menu
from game.UI.game_over import GameOver
from game.UI.victoria import Victoria
from config import *

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
    fondos_niveles = [
        pygame.transform.smoothscale(pygame.image.load("assets/images/fondo_nivel1.png").convert(), (ANCHO, ALTO)),
        pygame.transform.smoothscale(pygame.image.load("assets/images/fondo_nivel2.png").convert(), (ANCHO, ALTO)),
        pygame.transform.smoothscale(pygame.image.load("assets/images/fondo_nivel3.png").convert(), (ANCHO, ALTO)),
        pygame.transform.smoothscale(pygame.image.load("assets/images/fondo_nivel4.png").convert(), (ANCHO, ALTO)),
        pygame.transform.smoothscale(pygame.image.load("assets/images/fondo_nivel5.png").convert(), (ANCHO, ALTO)),
    ]
except Exception as e:
    print("Error cargando fondos:", e)
    fondos_niveles = []

try:
    sprite_plataforma = pygame.image.load("assets/images/plataforma.png").convert_alpha()
    sprite_plataforma = pygame.transform.scale(sprite_plataforma, (90, 90))
except:
    sprite_plataforma = None

try:
    sprite_rack = pygame.image.load("assets/images/rack.png").convert_alpha()
    sprite_rack_b = pygame.transform.scale(sprite_rack, (80, 80))
    sprite_rack_med = pygame.transform.scale(sprite_rack, (80, 80))
    sprite_rack_apagado = pygame.image.load("assets/images/rack_apagado.png").convert_alpha()
    sprite_rack_apagado = pygame.transform.scale(sprite_rack_apagado, (80, 80))
except:
    sprite_rack = None
    sprite_rack_b = None
    sprite_rack_med = None
    sprite_rack_apagado = None

try:
    sprite_chaqueta = pygame.image.load("assets/images/chaqueta_item.png").convert_alpha()
    sprite_chaqueta = pygame.transform.scale(sprite_chaqueta, (40, 40))
except:
    sprite_chaqueta = None

try:
    sprite_pared = pygame.image.load("assets/images/pared1.png").convert_alpha()
except:
    sprite_pared = None

try:
    pygame.mixer.music.load(MUSICA_JUEGO)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except:
    pass

tam_jugador = 64
todas_colisiones = []


def crear_nivel(idx):
    global nivel, trampas, tiempo_restante, nivel_completado, punto_cable_actual, todas_colisiones
    nivel = Level(ANCHO, ALTO, idx)
    trampas = []
    for pos in nivel.pos_trampas:
        margen = int(ANCHO * 0.08)
        trampas.append(Trampa(
            x=pos[0], y=pos[1],
            tamano=int(min(ANCHO, ALTO) * 0.035),
            velocidad=max(2, ANCHO // 700),
            min_x=pos[0] - margen,
            max_x=pos[0] + margen
        ))
    todas_colisiones = nivel.plataformas + nivel.paredes
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
        trampas[i].velocidad = max(2, ANCHO // 700)
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
    if fondos_niveles and nivel.numero < len(fondos_niveles):
        pantalla.blit(fondos_niveles[nivel.numero], (0, 0))
    else:
        pantalla.fill((10, 20, 50))


def dibujar_nivel(cam_y):
    for p in nivel.plataformas:
        r = pygame.Rect(p.x, p.y - cam_y, p.w, p.h)
        if -p.h < r.y < ALTO + p.h:
            if sprite_plataforma:
                sp = pygame.transform.scale(sprite_plataforma, (p.w, p.h))
                pantalla.blit(sp, r)
            else:
                pygame.draw.rect(pantalla, GRIS, r)

    for p in nivel.paredes:
        r = pygame.Rect(p.x, p.y - cam_y, p.w, p.h)
        if -p.h < r.y < ALTO + p.h:
            if sprite_pared:
                sp = pygame.transform.scale(sprite_pared, (p.w, p.h))
                pantalla.blit(sp, r)
            else:
                pygame.draw.rect(pantalla, (20, 20, 40), r)

    ax, ay = nivel.punto_a[0], nivel.punto_a[1] - cam_y
    if sprite_rack_b:
        pantalla.blit(sprite_rack_b, (ax - 40, ay - 40))
    else:
        pygame.draw.circle(pantalla, ROJO, (ax, ay), 12)

    bx, by = nivel.punto_b[0], nivel.punto_b[1] - cam_y
    if sprite_rack_apagado:
        pantalla.blit(sprite_rack_apagado, (bx - 40, by - 40))
    else:
        pygame.draw.circle(pantalla, VERDE, (bx, by), 15)

    for cp in nivel.checkpoints:
        cx, cy = cp[0], cp[1] - cam_y
        if sprite_rack_med:
            pantalla.blit(sprite_rack_med, (cx - 30, cy - 30))
        else:
            pygame.draw.circle(pantalla, (0, 200, 255), (cx, cy), 10)

    if nivel.pos_chaqueta:
        jx, jy = nivel.pos_chaqueta[0], nivel.pos_chaqueta[1] - cam_y
        if sprite_chaqueta:
            pantalla.blit(sprite_chaqueta, (jx - 20, jy - 20))
        else:
            pygame.draw.rect(pantalla, (255, 165, 0), (jx - 15, jy - 15, 30, 30))


def dibujar_cable(cam_y):
    ax, ay = punto_cable_actual[0], punto_cable_actual[1] - cam_y

    if jugador.voltear:
        mano_x = jugador.forma.left - 5
    else:
        mano_x = jugador.forma.right + 5
    mano_y = jugador.forma.centery - cam_y - 8

    if jugador.tiene_cable:
        mid_x = (ax + mano_x) // 2
        mid_y = max(ay, mano_y) + 45
        puntos = []
        for i in range(25):
            t = i / 24
            x = int((1-t)**2 * ax + 2*(1-t)*t * mid_x + t**2 * mano_x)
            y = int((1-t)**2 * ay + 2*(1-t)*t * mid_y + t**2 * mano_y)
            puntos.append((x, y))

        pygame.draw.lines(pantalla, (0, 0, 0), False, puntos, 10)
        pygame.draw.lines(pantalla, (25, 25, 25), False, puntos, 7)
        pygame.draw.lines(pantalla, (95, 95, 95), False, puntos, 3)
        pygame.draw.lines(pantalla, (160, 160, 160), False, puntos, 1)

        conector_rect = pygame.Rect(mano_x - 8, mano_y - 5, 16, 10)
        pygame.draw.rect(pantalla, (20, 20, 20), conector_rect, border_radius=3)
        pygame.draw.rect(pantalla, (130, 130, 130), conector_rect, 2, border_radius=3)

        pygame.draw.circle(pantalla, (20, 20, 20), (ax, ay), 8)
        pygame.draw.circle(pantalla, (120, 120, 120), (ax, ay), 4)
    else:
        w = fuente_peq.size("Cable cortado: vuelve al punto C o A")[0]
        texto("Cable cortado: vuelve al punto C o A", fuente_peq, ROJO, (ANCHO // 2 - w // 2, 80))


nivel_idx = 0
nivel = None
trampas = []
todas_colisiones = []
tiempo_restante = 0
nivel_completado = False
game_over = False
victoria_final = False
tiempo_sin_daño = 0
punto_cable_actual = None

crear_nivel(0)

jugador = Personaje(
    nivel.punto_a[0],
    nivel.punto_a[1] - tam_jugador,
    tamano=tam_jugador,
    ancho_hitbox=40,
    alto_hitbox=40
)

sprite_sheet = pygame.image.load("assets/sprites/jugador/idle.png").convert_alpha()
sprite_sheet_run = pygame.image.load("assets/sprites/jugador/run.png").convert_alpha()
sprite_sheet_jump = pygame.image.load("assets/sprites/jugador/jump.png").convert_alpha()

frame_ancho = sprite_sheet.get_width() // 5
frame_alto = sprite_sheet.get_height() // 5
frames = []

for fila in range(5):
    for columna in range(5):
        frame = sprite_sheet.subsurface(pygame.Rect(columna * frame_ancho, fila * frame_alto, frame_ancho, frame_alto))
        frame = pygame.transform.scale(frame, (tam_jugador, tam_jugador))
        frames.append(frame)

frames_run = []
for fila in range(5):
    for columna in range(5):
        frame = sprite_sheet_run.subsurface(pygame.Rect(columna * frame_ancho, fila * frame_alto, frame_ancho, frame_alto))
        frame = pygame.transform.scale(frame, (tam_jugador, tam_jugador))
        frames_run.append(frame)

frames_jump = []
frame_ancho_jump = sprite_sheet_jump.get_width() // 5
frame_alto_jump = sprite_sheet_jump.get_height() // 5
contador = 0

for fila in range(5):
    for columna in range(5):
        if contador >= 23:
            break
        frame = sprite_sheet_jump.subsurface(pygame.Rect(columna * frame_ancho_jump, fila * frame_alto_jump, frame_ancho_jump, frame_alto_jump))
        frame = pygame.transform.scale(frame, (tam_jugador, tam_jugador))
        frames_jump.append(frame)
        contador += 1

frame_idle = 0
frame_run = 0
frame_jump = 0
ultimo_frame = pygame.time.get_ticks()
velocidad_animacion = 80
jugador.imagen = frames[0]
hud = HUD()

while True:
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
        ahora = pygame.time.get_ticks()

        if ahora - ultimo_frame > velocidad_animacion:
            ultimo_frame = ahora
            if not jugador.en_suelo:
                if frame_jump < len(frames_jump) - 1:
                    frame_jump += 1
                jugador.imagen = frames_jump[frame_jump]
            elif jugador.vel_x != 0:
                frame_jump = 0
                frame_run += 1
                if frame_run >= len(frames_run):
                    frame_run = 0
                jugador.imagen = frames_run[frame_run]
            else:
                frame_jump = 0
                frame_idle += 1
                if frame_idle >= len(frames):
                    frame_idle = 0
                jugador.imagen = frames[frame_idle]

        if not game_over and not victoria_final:
            dt = reloj.get_time()
            tiempo_restante -= dt
            if tiempo_restante <= 0:
                tiempo_restante = 0
                game_over = True

            teclas = pygame.key.get_pressed()
            estaba_en_suelo = jugador.en_suelo
            jugador.leer_teclas(teclas)
            jugador.actualizar(todas_colisiones, ANCHO, nivel.alto_total)

            for t in trampas:
                t.mover(todas_colisiones)

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
                dist = math.hypot(jugador.forma.centerx - t.x, jugador.forma.centery - t.y)
                radio_colision = t.tamano * 0.75
                if dist < radio_colision and ahora > tiempo_sin_daño:
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
                    todas_colisiones = nivel.plataformas + nivel.paredes
                    jugador.forma.x = nivel.punto_a[0]
                    jugador.forma.y = nivel.punto_a[1] - tam_jugador
                    jugador.vel_x = 0
                    jugador.vel_y = 0
                    jugador.tiene_cable = True

        dibujar_fondo(cam_y)

        if game_over:
            pygame.display.flip()
            pygame.mixer.music.stop()
            go = GameOver(pantalla, ANCHO, ALTO, jugador.puntaje, nivel_idx + 1, jugador.chaquetas)
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
            vic = Victoria(pantalla, ANCHO, ALTO, jugador.puntaje, nivel_idx + 1, jugador.chaquetas)
            vic.ejecutar()
            jugando = False
        else:
            dibujar_cable(cam_y)
            dibujar_nivel(cam_y)
            for t in trampas:
                t.dibujar(pantalla, cam_x, cam_y)
            jugador.dibujar(pantalla, cam_x, cam_y)
            w = fuente_peq.size("Mover: A/D o Flechas | Saltar: W, Arriba o Espacio")[0]
            texto("Mover: A/D o Flechas | Saltar: W, Arriba o Espacio", fuente_peq, (200, 200, 200), (ANCHO // 2 - w // 2, ALTO - 35))
            hud.draw(pantalla, jugador.vidas, jugador.vidas_max, jugador.chaquetas, tiempo_restante)

        pygame.display.flip()
        reloj.tick(FPS)