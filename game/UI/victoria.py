import pygame
import cv2
import sys
from datetime import datetime
from db.database_manager import crear_jugador, crear_personaje, guardar_puntaje
from game.UI.input_nombre import InputNombre
import math
from config import VIDEO_VICTORIA

class Victoria:
    def __init__(self, pantalla, ancho, alto, puntaje, nivel_llegado=1, chaquetas=0):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.puntaje = puntaje
        self.nivel_llegado = nivel_llegado
        self.chaquetas = chaquetas
        self.opcion = 0
        self.opciones = ["Guardar puntaje", "Volver al menú", "Salir"]
        self.video = cv2.VideoCapture(VIDEO_VICTORIA)
        self.ultimo_frame_video = None
        self.video_terminado = False
        self.fade_alpha = 0
        self.fade_activo = False

        try:
            self.fuente_titulo = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 60)
            self.fuente_menu = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 28)
            self.fuente_peq = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 16)
        except:
            self.fuente_titulo = pygame.font.SysFont("Arial", 60)
            self.fuente_menu = pygame.font.SysFont("Arial", 28)
            self.fuente_peq = pygame.font.SysFont("Arial", 16)

        try:
            self.fondo = pygame.image.load("assets/images/victoria_fondo.png")
            self.fondo = pygame.transform.scale(self.fondo, (ancho, alto))
        except:
            self.fondo = None

        try:
            pygame.mixer.music.load("assets/sounds/victoria.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except:
            pass

    def guardar(self):
        inp = InputNombre(self.pantalla, self.ancho, self.alto, self.puntaje)
        nombre = inp.ejecutar()
        jugador_id = crear_jugador(nombre, self.nivel_llegado, self.puntaje)
        personaje_id = crear_personaje(nombre, 3, jugador_id)
        guardar_puntaje(
            puntos=self.puntaje,
            fecha=datetime.now().strftime("%Y-%m-%d %H:%M"),
            personaje_id=personaje_id,
            nivel_id=self.nivel_llegado,
            chaqueta_equipada=self.chaquetas > 0,
            tiempo_juego="00:00"
        )

    def dibujar(self):

    # =========================
    # FONDO + OVERLAY
    # =========================
        if not self.video_terminado:
            ret, frame = self.video.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (self.ancho, self.alto))
                self.ultimo_frame_video = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                self.pantalla.blit(self.ultimo_frame_video, (0, 0))
            else:
                self.video_terminado = True
                self.fade_activo = True
        else:
            if self.ultimo_frame_video:
                self.pantalla.blit(self.ultimo_frame_video, (0, 0))

        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        alpha = 140
        if self.fade_activo:
            alpha = min(140 + self.fade_alpha, 255)
        overlay.fill((0, 0, 0, alpha))
        self.pantalla.blit(overlay, (0, 0))

        tiempo = pygame.time.get_ticks()

    # =========================
    # TITULO CON PULSO
    # ========================
        pulso = (math.sin(tiempo * 0.005) + 1) / 2
        escala = 1 + pulso * 0.06

        color = (
            0,
            200 + int(pulso * 55),
            150
        )

        titulo_base = self.fuente_titulo.render("GANASTE", True, color)

        titulo = pygame.transform.smoothscale(
            titulo_base,
            (
                int(titulo_base.get_width() * escala),
                int(titulo_base.get_height() * escala)
            )
        )

        self.pantalla.blit(
            titulo,
            titulo.get_rect(center=(self.ancho // 2, int(self.alto * 0.22)))
        )

    # =========================
    # PUNTAJE (GLASS CARD)
    # =========================
        panel_w = 420
        panel_h = 120

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((20, 25, 35, 160))

        pygame.draw.rect(
            panel,
            (0, 255, 150, 120),
            (0, 0, panel_w, panel_h),
            2,
            border_radius=20
        )

        self.pantalla.blit(
            panel,
            (
                self.ancho // 2 - panel_w // 2,
                int(self.alto * 0.38)
            )
        )

        pts = self.fuente_menu.render(
            f"Puntaje: {self.puntaje}",
            True,
            (255, 255, 255)
        )

        self.pantalla.blit(
            pts,
            pts.get_rect(center=(self.ancho // 2, int(self.alto * 0.38) + 60))
        )

    # =========================
    # OPCIONES CON GLASS + GLOW
    # =========================
        for i, op in enumerate(self.opciones):

            y = int(self.alto * 0.55) + i * 80

            if i == self.opcion:

                pulso_sel = (math.sin(tiempo * 0.006) + 1) / 2

                glow_alpha = 60 + int(pulso_sel * 90)

                glow = pygame.Surface((420, 75), pygame.SRCALPHA)

                pygame.draw.rect(
                    glow,
                    (0, 255, 150, glow_alpha),
                    (0, 0, 420, 75),
                    border_radius=20
                )

                self.pantalla.blit(
                    glow,
                    (self.ancho // 2 - 210, y - 37)
                )

                texto = self.fuente_menu.render(
                    "> " + op,
                    True,
                    (0, 255, 200)
                )

                escala_t = 1 + pulso_sel * 0.05

                texto = pygame.transform.smoothscale(
                    texto,
                    (
                        int(texto.get_width() * escala_t),
                        int(texto.get_height() * escala_t)
                    )
                )

            else:

                fade = 180 + int(
                    40 * math.sin(tiempo * 0.003 + i)
                )

                texto = self.fuente_menu.render(
                    "  " + op,
                    True,
                    (fade, fade, fade)
                )

            self.pantalla.blit(
                texto,
                texto.get_rect(
                    center=(self.ancho // 2, y)
                )
            )
        

    # =========================
    # INSTRUCCIONES
    # =========================
        inst = self.fuente_peq.render(
            "W/S mover   |   ENTER seleccionar",
            True,
            (150, 150, 150)
        )

        self.pantalla.blit(
            inst,
            inst.get_rect(center=(self.ancho // 2, self.alto - 40))
        )

        pygame.display.flip()

        if self.fade_activo:
            self.fade_alpha += 2
            if self.fade_alpha > 255:
                self.fade_alpha = 255

    def _ease_in_out(self, t):
        return t * t * (3 - 2 * t)

    def _ease_in_cubic(self, t):
        return t * t * t

    def _dibujar_iris(self, progreso, fase_cierre=True):
        cx = self.ancho // 2
        cy = self.alto // 2
        radio_max = int(((cx ** 2) + (cy ** 2)) ** 0.5) + 2
        radio_visible = int(radio_max * (1.0 - progreso))

        vignette = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        vignette.fill((0, 0, 0, 255))
        if radio_visible > 0:
            pygame.draw.circle(vignette, (0, 0, 0, 0), (cx, cy), radio_visible)
        self.pantalla.blit(vignette, (0, 0))

        if radio_visible > 4:
            if fase_cierre:
                for grosor, alpha in [(22, 35), (12, 80), (5, 180), (2, 255)]:
                    borde = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
                    pygame.draw.circle(borde, (255, 210, 0, alpha), (cx, cy), radio_visible, grosor)
                    self.pantalla.blit(borde, (0, 0))
            else:
                for grosor, alpha in [(10, 30), (4, 120), (2, 200)]:
                    borde = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
                    pygame.draw.circle(borde, (0, 255, 150, alpha), (cx, cy), radio_visible, grosor)
                    self.pantalla.blit(borde, (0, 0))

    def transicion_entrada(self, duracion_cierre_ms=1200, duracion_apertura_ms=800):
        reloj = pygame.time.Clock()

        pasos_cierre = duracion_cierre_ms // 16
        for i in range(pasos_cierre + 1):
            t = i / pasos_cierre
            progreso = self._ease_in_cubic(t)
            self.pantalla.fill((0, 0, 0))
            self._dibujar_iris(progreso, fase_cierre=True)
            pygame.display.flip()
            reloj.tick(60)

        pygame.time.delay(180)

        pasos_apertura = duracion_apertura_ms // 16
        for i in range(pasos_apertura + 1):
            t = i / pasos_apertura
            progreso = self._ease_in_out(t)
            self.dibujar()
            self._dibujar_iris(1.0 - progreso, fase_cierre=False)
            pygame.display.flip()
            reloj.tick(60)

    def ejecutar(self):
        reloj = pygame.time.Clock()
        self.transicion_entrada()
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_w, pygame.K_UP):
                        self.opcion = (self.opcion - 1) % len(self.opciones)
                    elif evento.key in (pygame.K_s, pygame.K_DOWN):
                        self.opcion = (self.opcion + 1) % len(self.opciones)
                    elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        op = self.opciones[self.opcion]
                        if op == "Guardar puntaje":
                            self.guardar()
                            return "menu"
                        elif op == "Volver al menú":
                            return "menu"
                        else:
                            pygame.quit()
                            sys.exit()
            self.dibujar()
            reloj.tick(60)