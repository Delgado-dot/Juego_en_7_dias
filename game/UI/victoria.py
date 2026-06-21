import pygame
import sys
from datetime import datetime
from db.database_manager import crear_jugador, crear_personaje, guardar_puntaje
from game.UI.input_nombre import InputNombre
import math

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
        if self.fondo:
            self.pantalla.blit(self.fondo, (0, 0))
        else:
            self.pantalla.fill((0, 20, 0))

        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
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
            titulo.get_rect(center=(self.ancho // 2, self.alto // 4))
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
                self.alto // 3 - 10
            )
        )

        pts = self.fuente_menu.render(
            f"Puntaje: {self.puntaje}",
            True,
            (255, 255, 255)
        )

        self.pantalla.blit(
            pts,
            pts.get_rect(center=(self.ancho // 2, self.alto // 3 + 50))
        )

    # =========================
    # OPCIONES CON GLASS + GLOW
    # =========================
        for i, op in enumerate(self.opciones):

            y = self.alto // 2 + i * 75

            if i == self.opcion:

                pulso_sel = (math.sin(tiempo * 0.006) + 1) / 2

                glow_alpha = 60 + int(pulso_sel * 90)

                glow = pygame.Surface((420, 70), pygame.SRCALPHA)

                pygame.draw.rect(
                    glow,
                    (0, 255, 150, glow_alpha),
                    (0, 0, 420, 70),
                    border_radius=20
                )

                self.pantalla.blit(
                    glow,
                    (self.ancho // 2 - 210, y - 35)
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

    def ejecutar(self):
        reloj = pygame.time.Clock()
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