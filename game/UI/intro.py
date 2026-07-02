import pygame
import sys
import math
from game.UI.menu_efects import MenuEffects
from config import MUSICA_INTRO


class Introduccion:

    PANTALLAS = [
        {
            "titulo": "RACK JACKED MAN",
            "subtitulo": "Conecta los racks. Sobrevive al cable.",
            "secciones": [
                {
                    "encabezado": "OBJETIVO",
                    "color": (0, 255, 180),
                    "lineas": [
                        "Eres un tecnico de redes en peligro.",
                        "Tu cable de datos esta conectado al rack inicial.",
                        "Llega al rack rojo sin perder la conexion.",
                    ],
                },
                {
                    "encabezado": "CONTROLES",
                    "color": (0, 220, 255),
                    "lineas": [
                        "A / D o Flechas : mover",
                        "W / Arriba / Espacio : saltar",
                        "Esc : pausar y volver al menu",
                    ],
                },
            ],
        },
        {
            "titulo": "CONSEJOS",
            "subtitulo": "Lo que debes saber para llegar lejos.",
            "secciones": [
                {
                    "encabezado": "CABLE",
                    "color": (255, 200, 60),
                    "lineas": [
                        "Si una sierra o trampa corta el cable,",
                        "vuelve a un rack o checkpoint  para recuperarlo.",
                        "Sin cable, no puedes llegar al siguiente rack.",
                    ],
                },
                {
                    "encabezado": "POWER-UP",
                    "color": (255, 165, 0),
                    "lineas": [
                        "La chaqueta cohete  te da un impulso vertical.",
                        "Manten ESPACIO para volar mientras dure el efecto.",
                        "Usala para alcanzar plataformas altas.",
                    ],
                },
            ],
        },
        {
            "titulo": "PELIGROS",
            "subtitulo": "Evitalos o perderas una vida.",
            "secciones": [
                {
                    "encabezado": "ENEMIGOS Y TRAMPAS",
                    "color": (255, 80, 80),
                    "lineas": [
                        "Sierras moviles y sierras que caen del techo.",
                        "Ambas cortan cables danan al jugador.",
                        "Cronometra bien tus saltos para superarlas.",
                        "Evita los drones que pueden dispararte"
                    ],
                },
                {
                    "encabezado": "PLATAFORMAS",
                    "color": (180, 130, 255),
                    "lineas": [
                        "Plataformas fantasma: desaparecen al pisarlas.",
                        "Plataformas dinamicas: se mueven o encogen.",
                        "Confia en el ritmo, no te detengas.",
                    ],
                },
            ],
        },
    ]

    def __init__(self, pantalla, ancho, alto, config=None):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.config = config or {}
        self.pantalla_idx = 0
        self.alpha = 0
        self.fase = "fade_in"
        self.tiempo_inicio = pygame.time.get_ticks()
        self.effects = MenuEffects(ancho, alto)

        try:
            self.fuente_titulo = pygame.font.Font(
                "assets/fonts/PressStart2P-Regular.ttf", 56
            )
            self.fuente_subtitulo = pygame.font.Font(
                "assets/fonts/PressStart2P-Regular.ttf", 16
            )
            self.fuente_encabezado = pygame.font.Font(
                "assets/fonts/PressStart2P-Regular.ttf", 22
            )
            self.fuente_linea = pygame.font.Font(
                "assets/fonts/PressStart2P-Regular.ttf", 13
            )
            self.fuente_peq = pygame.font.Font(
                "assets/fonts/PressStart2P-Regular.ttf", 12
            )
        except:
            self.fuente_titulo = pygame.font.SysFont("Arial", 56, bold=True)
            self.fuente_subtitulo = pygame.font.SysFont("Arial", 16)
            self.fuente_encabezado = pygame.font.SysFont("Arial", 22, bold=True)
            self.fuente_linea = pygame.font.SysFont("Arial", 13)
            self.fuente_peq = pygame.font.SysFont("Arial", 12)

        self.duracion_fade = 400
        self.duracion_estatico = 3500
        self.terminado = False

    def _ease_out(self, t):
        return 1 - (1 - t) ** 2

    def _ease_in(self, t):
        return t * t

    def _dibujar_panel(self, x, y, w, h, alpha_mult=1.0):
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        alpha_base = int(180 * alpha_mult)
        panel.fill((10, 15, 25, alpha_base))
        self.pantalla.blit(panel, (x, y))

        for grosor, alpha in [(8, int(25 * alpha_mult)), (3, int(120 * alpha_mult)), (2, int(220 * alpha_mult))]:
            borde = pygame.Surface((w + grosor * 2, h + grosor * 2), pygame.SRCALPHA)
            pygame.draw.rect(
                borde,
                (0, 220, 255, alpha),
                (grosor, grosor, w, h),
                grosor,
                border_radius=18,
            )
            self.pantalla.blit(borde, (x - grosor, y - grosor))

    def _dibujar_texto_con_alpha(self, texto, fuente, color, pos, alpha):
        render = fuente.render(texto, True, color)
        render.set_alpha(alpha)
        self.pantalla.blit(render, pos)

    def _dibujar_pagina(self, datos, alpha_mult):
        titulo_y = 80
        pulso = (math.sin(pygame.time.get_ticks() * 0.003) + 1) / 2
        escala = 1.0 + pulso * 0.04
        titulo_render = self.fuente_titulo.render(datos["titulo"], True, (120, 230, 255))
        tw, th = titulo_render.get_size()
        titulo_scaled = pygame.transform.smoothscale(
            titulo_render, (int(tw * escala), int(th * escala))
        )
        titulo_scaled.set_alpha(int(255 * alpha_mult))
        self.pantalla.blit(
            titulo_scaled, titulo_scaled.get_rect(center=(self.ancho // 2, titulo_y))
        )

        sub_y = 145
        self._dibujar_texto_con_alpha(
            datos["subtitulo"],
            self.fuente_subtitulo,
            (200, 200, 200),
            self.fuente_subtitulo.render(datos["subtitulo"], True, (200, 200, 200))
            .get_rect(center=(self.ancho // 2, sub_y)),
            int(220 * alpha_mult),
        )

        linea_y = 175
        ancho_linea = int(500 * alpha_mult)
        pygame.draw.line(
            self.pantalla,
            (0, 220, 255),
            (self.ancho // 2 - ancho_linea // 2, linea_y),
            (self.ancho // 2 + ancho_linea // 2, linea_y),
            2,
        )

        panel_w = 720
        panel_h = 240
        panel_total_h = panel_h * len(datos["secciones"]) + 30 * (len(datos["secciones"]) - 1)
        panel_y_inicio = (self.alto - panel_total_h) // 2 + 52

        for i, seccion in enumerate(datos["secciones"]):
            panel_y = panel_y_inicio + i * (panel_h + 30)
            panel_x = self.ancho // 2 - panel_w // 2
            self._dibujar_panel(panel_x, panel_y, panel_w, panel_h, alpha_mult)

            barra_x = panel_x + 18
            barra_y = panel_y + 22
            barra_h = 32
            pygame.draw.rect(
                self.pantalla,
                seccion["color"],
                (barra_x, barra_y, 5, barra_h),
                border_radius=3,
            )

            encab_x = barra_x + 18
            encab_y = panel_y + 22
            self._dibujar_texto_con_alpha(
                seccion["encabezado"],
                self.fuente_encabezado,
                seccion["color"],
                (encab_x, encab_y),
                int(255 * alpha_mult),
            )

            contenido_y = encab_y + 50
            for j, linea in enumerate(seccion["lineas"]):
                pygame.draw.circle(
                    self.pantalla,
                    seccion["color"],
                    (encab_x + 8, contenido_y + 8 + j * 36),
                    3,
                )
                self._dibujar_texto_con_alpha(
                    linea,
                    self.fuente_linea,
                    (230, 230, 230),
                    (encab_x + 12, contenido_y + j * 35),
                    int(230 * alpha_mult),
                )

    def _dibujar_indicador_paginas(self, alpha_mult):
        cantidad = len(self.PANTALLAS)
        espacio = 30
        total_w = espacio * (cantidad - 1)
        inicio_x = self.ancho // 2 - total_w // 2
        y = self.alto - 70

        for i in range(cantidad):
            cx = inicio_x + i * espacio
            if i == self.pantalla_idx:
                pygame.draw.circle(self.pantalla, (0, 255, 200), (cx, y), 8)
                pygame.draw.circle(self.pantalla, (255, 255, 255), (cx, y), 4)
            else:
                pygame.draw.circle(self.pantalla, (80, 80, 100), (cx, y), 5)

    def _dibujar_hint_inferior(self, alpha_mult, completo=False):
        if completo:
            msg = "Presiona ENTER para jugar"
            color = (0, 255, 180)
        else:
            msg = "ENTER: siguiente  |  ESC: saltar"
            color = (180, 180, 180)

        render = self.fuente_peq.render(msg, True, color)
        render.set_alpha(int(220 * alpha_mult))
        self.pantalla.blit(
            render, render.get_rect(center=(self.ancho // 2, self.alto - 35))
        )

    def dibujar(self):
        fondo = pygame.Surface((self.ancho, self.alto))
        fondo.fill((5, 8, 18))
        self.pantalla.blit(fondo, (0, 0))

        if self.config.get("particulas", True):
            self.effects.dibujar_particulas(self.pantalla)

        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.pantalla.blit(overlay, (0, 0))

        if self.fase == "fade_in":
            t = min(1.0, (pygame.time.get_ticks() - self.tiempo_inicio) / self.duracion_fade)
            alpha_mult = self._ease_out(t)
            if t >= 1.0:
                self.fase = "mostrar"
                self.tiempo_inicio = pygame.time.get_ticks()
        elif self.fase == "mostrar":
            alpha_mult = 1.0
            transcurrido = pygame.time.get_ticks() - self.tiempo_inicio
            if transcurrido > self.duracion_estatico:
                self.fase = "fade_out"
                self.tiempo_inicio = pygame.time.get_ticks()
        else:
            t = min(1.0, (pygame.time.get_ticks() - self.tiempo_inicio) / self.duracion_fade)
            alpha_mult = 1.0 - self._ease_in(t)
            if t >= 1.0:
                self.pantalla_idx += 1
                if self.pantalla_idx >= len(self.PANTALLAS):
                    self.terminado = True
                    return
                self.fase = "fade_in"
                self.tiempo_inicio = pygame.time.get_ticks()

        datos = self.PANTALLAS[self.pantalla_idx]
        es_ultima = self.pantalla_idx == len(self.PANTALLAS) - 1

        self._dibujar_pagina(datos, alpha_mult)
        self._dibujar_indicador_paginas(alpha_mult)
        self._dibujar_hint_inferior(alpha_mult, completo=es_ultima and self.fase != "fade_out")

        pygame.display.flip()

    def ejecutar(self):
        try:
            pygame.mixer.music.load(MUSICA_INTRO)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

        reloj = pygame.time.Clock()
        while not self.terminado:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_d, pygame.K_RIGHT):
                        if self.fase == "fade_out":
                            continue
                        if self.pantalla_idx == len(self.PANTALLAS) - 1:
                            pygame.mixer.music.stop()
                            self.terminado = True
                            break
                        self.fase = "fade_out"
                        self.tiempo_inicio = pygame.time.get_ticks()
                    elif evento.key == pygame.K_ESCAPE:
                        pygame.mixer.music.stop()
                        self.terminado = True
                        break

            self.dibujar()
            reloj.tick(60)
