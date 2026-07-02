import sys
import math
import pygame
from Entidades import *
from game.UI.hud import *
from game.level import Level, NIVELES
from game.UI.menu import *
from game.UI.game_over import *
from game.UI.victoria import *
from game.UI.intro import Introduccion
from game.UI.pause import MenuPausa
from historia import Historia
from transicion_historia import TransicionAHistoria
from game.UI.puzzles.puzzle_dispatcher import PuzzleDispatcher
from config import *

def reproducir_musica_nivel(idx):
    if idx < len(MUSICA_NIVELES):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(MUSICA_NIVELES[idx])
            volumen = menu.panel_config.config.get("vol_musica", 0.5)
            pygame.mixer.music.set_volume(volumen)
            pygame.mixer.music.play(-1)
        except:
            pass

def reproducir_sonido_daño():
    try:
        volumen = menu.panel_config.config.get("vol_efectos", 0.7)
        sonido = pygame.mixer.Sound(SONIDO_MUERTE)
        sonido.set_volume(volumen)
        sonido.play()
    except:
        pass

pygame.init()
pygame.mixer.init()

info = pygame.display.Info()
ANCHO = info.current_w
ALTO = info.current_h

pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
pygame.display.set_caption(TITULO)
fullscreen_actual = True

reloj = pygame.time.Clock()

fuente = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 60)
fuente_peq = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 15)

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

tam_jugador = 64
todas_colisiones = []


def crear_nivel(idx):
    global nivel, trampas, tiempo_restante, nivel_completado, punto_cable_actual, todas_colisiones, sierras_cae, enemigos, proyectiles_enemigos
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
    sierras_cae = []
    for pos in nivel.pos_sierras_cae:
        sierras_cae.append(SierraCae(
            x=pos[0], y=pos[1],
            tamano=int(min(ANCHO, ALTO) * 0.035)
        ))
    enemigos = []
    proyectiles_enemigos = []

    for pos in nivel.pos_enemigos:
        plataforma_encontrada = None
        for p in nivel.plataformas:
            if (
                pos[0] >= p.left and
                pos[0] <= p.right and
                pos[1] <= p.top + 80
            ):
                plataforma_encontrada = p
                break

        if plataforma_encontrada:
            enemigos.append(
                EnemigoPatrulla(
                    pos[0],
                    plataforma_encontrada.top - 40,
                    plataforma_encontrada))
        
    todas_colisiones = nivel.plataformas + nivel.paredes + [dp.obtener_colision() for dp in nivel.plataformas_dinamicas]
    tiempo_restante = nivel.tiempo_limite * 1000
    nivel_completado = False
    punto_cable_actual = nivel.punto_a
    reproducir_musica_nivel(idx)


def reiniciar_nivel():
    global game_over, tiempo_sin_daño, tiempo_restante, nivel_completado, punto_cable_actual
    crear_nivel(nivel_idx)
    jugador.vidas = jugador.vidas_max
    jugador.puntaje = 0
    jugador.tiene_cable = True
    jugador.chaquetas = 0
    jugador.chaqueta_cohete = False
    jugador.modo_cohete = False
    jugador.cohete_tiempo = 0
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
    for pf in nivel.plataformas_fantasma:
        pf.activada = False
        pf.desaparecida = False
        pf.alpha = 255
        pf.tiempo_inicio = 0


def reiniciar_juego():
    global nivel_idx, game_over, victoria_final, punto_cable_actual
    nivel_idx = 0
    crear_nivel(0)
    jugador.vidas = jugador.vidas_max
    jugador.puntaje = 0
    jugador.tiene_cable = True
    jugador.chaquetas = 0
    jugador.chaqueta_cohete = False
    jugador.modo_cohete = False
    jugador.cohete_tiempo = 0
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


def portal_transicion(cerrar=True):
    cam_x, cam_y = camara()
    centro = (
        jugador.forma.centerx - cam_x,
        jugador.forma.centery - cam_y
    )
    radio_max = int((ANCHO**2 + ALTO**2) ** 0.5)
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)

    if cerrar:
        rango = range(radio_max, 0, -15)
    else:
        rango = range(0, radio_max, 15)

    for radio in rango:
        dibujar_fondo(cam_y)
        dibujar_cable(cam_y)
        dibujar_nivel(cam_y)

        for t in trampas:
            t.dibujar(pantalla, cam_x, cam_y)

        for sc in sierras_cae:
            sc.dibujar(pantalla, cam_x, cam_y)

        jugador.dibujar(pantalla, cam_x, cam_y)

        overlay.fill((0, 0, 0, 255))
        pygame.draw.circle(overlay, (0, 0, 0, 0), centro, radio)
        pantalla.blit(overlay, (0, 0))

        pygame.draw.circle(pantalla, (120, 0, 255), centro, radio + 15, 12)
        pygame.draw.circle(pantalla, (200, 120, 255), centro, radio + 5, 6)

        pygame.display.flip()
        reloj.tick(120)


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
    for dp in nivel.plataformas_dinamicas:
        p = dp.obtener_colision()
        r = pygame.Rect(p.x, p.y - cam_y, p.w, p.h)
        if -p.h < r.y < ALTO + p.h:
            if sprite_plataforma:
                sp = pygame.transform.scale(sprite_plataforma, (p.w, p.h))
                pantalla.blit(sp, r)
            else:
                pygame.draw.rect(pantalla, GRIS, r)
    for pf in nivel.plataformas_fantasma:
        if pf.desaparecida:
            continue
        r= pygame.Rect( pf.rect.x,pf.rect.y - cam_y,
                       pf.rect.w, pf.rect.h)
        if sprite_plataforma:
            sp = pygame.transform.scale(sprite_plataforma,(pf.rect.w,pf.rect.h))
            sp.set_alpha(pf.alpha)
            pantalla.blit(sp,r)
        else:
            superficie =pygame.Surface((pf.rect.w, pf.rect.h),pygame.SRCALPHA)
            superficie.fill((180, 180, 180, pf.alpha))
            pantalla.blit(superficie, r)

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
            tiempo = pygame.time.get_ticks()
            pulso = (math.sin(tiempo * 0.004) + 1) / 2
            for radio in range(45, 20, -5):
                alpha = int(40 + pulso * 30)
                glow = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 215, 0, alpha), (radio, radio), radio)
                pantalla.blit(glow, (jx - radio, jy - radio))
            pantalla.blit(sprite_chaqueta, (jx - 20, jy - 20))
        else:
            pygame.draw.rect(pantalla, (255, 165, 0), (jx - 15, jy - 15, 30, 30))


def dibujar_cable(cam_y):
    ax, ay = punto_cable_actual[0], punto_cable_actual[1] - cam_y

    if jugador.voltear:
        mano_x = jugador.forma.left - 2
    else:
        mano_x = jugador.forma.right + 2
    mano_y = jugador.forma.centery - cam_y + 5

    if jugador.tiene_cable:
        mid_x = (ax + mano_x) // 2
        mid_y = max(ay, mano_y) + 35
        puntos = []
        for i in range(25):
            t = i / 24
            x = int((1-t)**2 * ax + 2*(1-t)*t * mid_x + t**2 * mano_x)
            y = int((1-t)**2 * ay + 2*(1-t)*t * mid_y + t**2 * mano_y)
            puntos.append((x, y))

        pygame.draw.lines(pantalla, (0, 0, 0), False, puntos, 8)
        pygame.draw.lines(pantalla, (25, 25, 25), False, puntos, 6)
        pygame.draw.lines(pantalla, (95, 95, 95), False, puntos, 3)
        pygame.draw.lines(pantalla, (160, 160, 160), False, puntos, 1)

        conector_rect = pygame.Rect(mano_x - 4, mano_y - 3, 8, 6)
        pygame.draw.rect(pantalla, (30, 30, 30), conector_rect, border_radius=2)
        pygame.draw.rect(pantalla, (100, 100, 100), conector_rect, 1, border_radius=2)

        pygame.draw.circle(pantalla, (20, 20, 20), (ax, ay), 6)
        pygame.draw.circle(pantalla, (100, 100, 100), (ax, ay), 3)
    else:
        w = fuente_peq.size("Cable cortado: vuelve al punto C o A")[0]
        texto("Cable cortado: vuelve al rack", fuente_peq, ROJO, (ANCHO // 2 - w // 2, 80))
        
def dibujar_dialogo_inicio(cam_y):
    """Panel de instrucciones que aparece sobre el primer rack del nivel 1."""
    if nivel_idx != 0:
        return
    if nivel_completado or game_over:
        return

    # Solo mostrar si el jugador está cerca del rack inicial (punto_a)
    dist = math.hypot(
        jugador.forma.centerx - nivel.punto_a[0],
        jugador.forma.centery - nivel.punto_a[1]
    )
    if dist > 220:
        return

    # Posición del panel: arriba del rack en pantalla
    ax, ay = nivel.punto_a[0], nivel.punto_a[1] - cam_y
    panel_w, panel_h = 360, 110
    panel_x = max(15, min(ax - panel_w // 2, ANCHO - panel_w - 15))
    panel_y = max(15, ay - 150)

    # Superficie con alpha para el fondo
    overlay = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    # Fondo oscuro semi-transparente (alpha 150)
    pygame.draw.rect(overlay, (15, 20, 35, 200), (0, 0, panel_w, panel_h), border_radius=12)
    # Borde cyan brillante
    pygame.draw.rect(overlay, (0, 220, 255, 230), (0, 0, panel_w, panel_h), 2, border_radius=12)

    # Líneas de texto
    titulo = fuente_peq.render("MISIÓN", True, (0, 220, 255))
    linea1 = fuente_peq.render("Llega al rack rojo ", True, (240, 240, 240))
    linea2 = fuente_peq.render("sin perder tu cable.", True, (240, 240, 240))
    linea3 = fuente_peq.render("Evita sierras y trampas.", True, (200, 200, 200))

    overlay.blit(titulo, (15, 12))
    overlay.blit(linea1, (15, 38))
    overlay.blit(linea2, (15, 58))
    overlay.blit(linea3, (15, 82))

    # Flecha apuntando al rack
    if 0 < panel_x + panel_w // 2 < ANCHO:
        flecha_x = panel_x + panel_w // 2
        flecha_y_top = panel_y + panel_h
        flecha_y_bottom = flecha_y_top + 10
        pygame.draw.polygon(
            pantalla,
            (0, 220, 255),
            [(flecha_x - 6, flecha_y_top),
             (flecha_x + 6, flecha_y_top),
             (flecha_x, flecha_y_bottom)]
        )

    pantalla.blit(overlay, (panel_x, panel_y))


nivel_idx = 0
nivel = None
enemigos = []
proyectiles_enemigos = []
trampas = []
sierras_cae = []
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

    pantalla, ANCHO, ALTO, fullscreen_actual = menu.panel_config.aplicar_cambios(
        pantalla, ANCHO, ALTO, fullscreen_actual
    )
    menu.panel_config.actualizar_dimensiones(ANCHO, ALTO)

    TransicionAHistoria(pantalla, ANCHO, ALTO).ejecutar()

    historia = Historia(pantalla, ANCHO, ALTO)
    historia.ejecutar()

    intro = Introduccion(pantalla, ANCHO, ALTO, menu.panel_config.config)
    intro.ejecutar()

    reiniciar_juego()

    portal_transicion(False)

    jugando = True
    while jugando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    cam_x, cam_y = camara()
                    dibujar_fondo(cam_y)
                    dibujar_cable(cam_y)
                    dibujar_nivel(cam_y)
                    for t in trampas:
                        t.dibujar(pantalla, cam_x, cam_y)
                    for sc in sierras_cae:
                        sc.dibujar(pantalla, cam_x, cam_y)
                    jugador.dibujar(pantalla, cam_x, cam_y)
                    hud.draw(pantalla, jugador.vidas, jugador.vidas_max,
                             jugador.chaquetas, tiempo_restante)
                    pygame.display.flip()

                    try:
                        pygame.mixer.music.pause()
                    except:
                        pass

                    pausa = MenuPausa(pantalla, ANCHO, ALTO, menu.panel_config.config)
                    resultado_pausa = pausa.ejecutar()

                    try:
                        pygame.mixer.music.unpause()
                    except:
                        pass

                    if resultado_pausa == "reanudar":
                        ultimo_frame = pygame.time.get_ticks()
                        continue
                    elif resultado_pausa == "reiniciar":
                        reiniciar_nivel()
                        ultimo_frame = pygame.time.get_ticks()
                        continue
                    elif resultado_pausa == "menu":
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
            jugador.activar_cohete(teclas[pygame.K_SPACE])
            if teclas[pygame.K_SPACE]:
                print(f"[COHETE] space pressed | chaq={jugador.chaqueta_cohete} modo={jugador.modo_cohete} vel_y={jugador.vel_y:.2f}")
            estaba_en_suelo = jugador.en_suelo
            jugador.leer_teclas(teclas)

            if nivel.plataformas_dinamicas:
                for dp in nivel.plataformas_dinamicas:
                    dp.actualizar(jugador.forma)
                todas_colisiones = nivel.plataformas + nivel.paredes + [dp.obtener_colision() for dp in nivel.plataformas_dinamicas]

            colisiones = todas_colisiones.copy()

            for pf in nivel.plataformas_fantasma:
                if pf.es_solida():
                    colisiones.append(pf.rect)

            jugador.actualizar(colisiones, ANCHO, nivel.alto_total)

            if jugador.forma.top > nivel.alto_total + 200:
                reproducir_sonido_daño()
                if not jugador.perder_vida():
                    game_over = True
                else:
                    jugador.reiniciar_pos(punto_cable_actual[0], punto_cable_actual[1] - tam_jugador)
                    tiempo_sin_daño = pygame.time.get_ticks() + DURACION_INVENCIBLE

            if jugador.modo_cohete and jugador.chaqueta_cohete:
                if pygame.time.get_ticks() % 2 == 0:
                    jugador.spawn_particula()

            for pf in nivel.plataformas_fantasma:
                if pf.desaparecida:
                    continue

                pie_pf = pygame.Rect(
                    jugador.forma.left,
                    jugador.forma.bottom,
                    jugador.forma.width,
                    2
                )
                if pie_pf.colliderect(pf.rect):
                    pf.pisar()

                pf.actualizar()

            for t in trampas:
                t.mover(todas_colisiones)
                
            for e in enemigos:
                e.actualizar(jugador)
                nuevos = e.intentar_disparar(jugador, ahora)
                proyectiles_enemigos.extend(nuevos)

            for p in proyectiles_enemigos:
                p.actualizar()

            proyectiles_enemigos = [
                p for p in proyectiles_enemigos
                if p.forma.right > 0 and p.forma.left < ANCHO
                and p.forma.bottom > 0 and p.forma.top < nivel.alto_total
            ]

            for p in proyectiles_enemigos:
                if p.forma.colliderect(jugador.forma):
                    if ahora > tiempo_sin_daño:
                        p.activo = False
                        reproducir_sonido_daño()
                        if not jugador.perder_vida():
                            game_over = True
                        else:
                            jugador.reiniciar_pos(
                                punto_cable_actual[0],
                                punto_cable_actual[1] - tam_jugador
                            )
                            tiempo_sin_daño = ahora + DURACION_INVENCIBLE

            proyectiles_enemigos = [p for p in proyectiles_enemigos if p.activo]

            for sc in sierras_cae:
                sc.actualizar(jugador.forma, todas_colisiones)

            for cp in nivel.checkpoints:
                if jugador.distancia(cp) < 30:
                    punto_cable_actual = cp

            if nivel.pos_chaqueta:
                dist_chaq = jugador.distancia(nivel.pos_chaqueta)
                if dist_chaq < 50:
                    print(f"[COHETE] Recogida! dist={dist_chaq:.1f}")
                    jugador.chaquetas += 1
                    jugador.chaqueta_cohete = True
                    jugador.cohete_tiempo = 0
                    nivel.pos_chaqueta = None

            jugador.recuperar_cable(punto_cable_actual)

            for t in trampas:
                if jugador.tiene_cable and t.corta_cable(punto_cable_actual, jugador.forma.center):
                    jugador.cortar_cable()

            for sc in sierras_cae:
                if sc.activa and jugador.tiene_cable and sc.corta_cable(punto_cable_actual, jugador.forma.center):
                    jugador.cortar_cable()

            ahora = pygame.time.get_ticks()
            for t in trampas:
                dist = math.hypot(jugador.forma.centerx - t.x, jugador.forma.centery - t.y)
                radio_colision = t.tamano * 0.75
                if dist < radio_colision and ahora > tiempo_sin_daño:
                    reproducir_sonido_daño()
                    if not jugador.perder_vida():
                        game_over = True
                    else:
                        jugador.reiniciar_pos(punto_cable_actual[0], punto_cable_actual[1] - tam_jugador)
                        tiempo_sin_daño = ahora + DURACION_INVENCIBLE

            for sc in sierras_cae:
                if sc.activa:
                    dist = math.hypot(jugador.forma.centerx - sc.x, jugador.forma.centery - sc.y)
                    radio_colision = sc.tamano * 0.75
                    if dist < radio_colision and ahora > tiempo_sin_daño:
                        reproducir_sonido_daño()
                        if not jugador.perder_vida():
                            game_over = True
                        else:
                            jugador.reiniciar_pos(punto_cable_actual[0], punto_cable_actual[1] - tam_jugador)
                            tiempo_sin_daño = ahora + DURACION_INVENCIBLE
            for e in enemigos:
                if e.forma.colliderect(jugador.forma):
                    if ahora > tiempo_sin_daño:
                        reproducir_sonido_daño()
                        if not jugador.perder_vida():
                            game_over = True
                        else:
                            jugador.reiniciar_pos(
                            punto_cable_actual[0],
                            punto_cable_actual[1] - tam_jugador
                            )
                            tiempo_sin_daño = (
                            ahora + DURACION_INVENCIBLE)

            if not nivel_completado and jugador.llego_meta(nivel.punto_b):
                nivel_completado = True
                jugador.puntaje += jugador.puntos_cable
                siguiente = nivel_idx + 1
                if siguiente >= len(NIVELES):
                    victoria_final = True
                else:
                    try:
                        pygame.mixer.music.pause()
                    except:
                        pass

                    puzzle = PuzzleDispatcher(pantalla, ANCHO, ALTO, fuente_peq, nivel_idx)
                    resultado_puzzle = puzzle.ejecutar()

                    try:
                        pygame.mixer.music.unpause()
                    except:
                        pass

                    if resultado_puzzle == "resuelto":
                        portal_transicion(True)

                        nivel_idx = siguiente
                        crear_nivel(nivel_idx)
                        todas_colisiones = nivel.plataformas + nivel.paredes + [dp.obtener_colision() for dp in nivel.plataformas_dinamicas]
                        jugador.forma.x = nivel.punto_a[0]
                        jugador.forma.y = nivel.punto_a[1] - tam_jugador
                        jugador.vel_x = 0
                        jugador.vel_y = 0
                        jugador.tiene_cable = True

                        portal_transicion(False)
                    elif resultado_puzzle == "salir":
                        pygame.quit()
                        sys.exit()
                    else:
                        nivel_completado = False

        dibujar_fondo(cam_y)

        if game_over:
            pygame.display.flip()
            pygame.mixer.music.stop()
            go = GameOver(pantalla, ANCHO, ALTO, jugador.puntaje, nivel_idx + 1, jugador.chaquetas)
            resultado = go.ejecutar()
            if resultado == "reintentar":
                reiniciar_nivel()
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
            for e in enemigos:
                e.dibujar(pantalla,cam_x,cam_y)
            for p in proyectiles_enemigos:
                p.dibujar(pantalla, cam_x, cam_y)
            for sc in sierras_cae:
                sc.dibujar(pantalla, cam_x, cam_y)
            jugador.dibujar(pantalla, cam_x, cam_y)
            dibujar_dialogo_inicio(cam_y)
            w = fuente_peq.size("Mover: A/D o Flechas | Saltar: W, Arriba o Espacio")[0]
            texto("Mover: A/D o Flechas | Saltar: W, Arriba o Espacio", fuente_peq, (200, 200, 200), (ANCHO // 2 - w // 2, ALTO - 35))
            hud.draw(pantalla, jugador.vidas, jugador.vidas_max, jugador.chaquetas, tiempo_restante)
            hud.draw_cohete_timer(pantalla, jugador)
        pygame.display.flip()
        reloj.tick(FPS)