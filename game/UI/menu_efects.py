import pygame
import random
import math


class MenuEffects:

    def __init__(self, ancho, alto):

        self.ancho = ancho
        self.alto = alto

        self.particulas = []

        for _ in range(120):

            self.particulas.append({

                "x": random.randint(0, ancho),
                "y": random.randint(0, alto),

                "vx": random.uniform(-0.2, 0.2),
                "vy": random.uniform(0.2, 0.8),

                "radio": random.randint(1, 3),

                "alpha": random.randint(50, 180)
            })

    # =================================
    # PARTICULAS
    # =================================
    def dibujar_particulas(self, pantalla):

        for p in self.particulas:

            p["x"] += p["vx"]
            p["y"] -= p["vy"]

            if p["y"] < -10:
                p["y"] = self.alto + 10
                p["x"] = random.randint(0, self.ancho)

            if p["x"] < -10:
                p["x"] = self.ancho + 10

            if p["x"] > self.ancho + 10:
                p["x"] = -10

            radio = p["radio"]

            surf = pygame.Surface(
                (radio * 6, radio * 6),
                pygame.SRCALPHA
            )

            pygame.draw.circle(
                surf,
                (120, 220, 255, p["alpha"]),
                (radio * 3, radio * 3),
                radio + 1
            )

            pygame.draw.circle(
                surf,
                (255, 255, 255, p["alpha"]),
                (radio * 3, radio * 3),
                radio
            )

            pantalla.blit(
                surf,
                (p["x"], p["y"])
            )

    # =================================
    # PULSO
    # =================================
    def obtener_pulso(self, velocidad=0.005):

        tiempo = pygame.time.get_ticks()

        return (math.sin(tiempo * velocidad) + 1) / 2

    # =================================
    # TEXTO CON PULSO
    # =================================
    def render_texto_pulso(
        self,
        fuente,
        texto,
        color,
        escala_base=1,
        intensidad=0.08
    ):

        pulso = self.obtener_pulso()

        escala = escala_base + pulso * intensidad

        render = fuente.render(
            texto,
            True,
            color
        )

        return pygame.transform.smoothscale(
            render,
            (
                int(render.get_width() * escala),
                int(render.get_height() * escala)
            )
        )

    # =================================
    # PANEL GLASS
    # =================================
    def dibujar_panel_glass(
        self,
        pantalla,
        x,
        y,
        ancho,
        alto,
        alpha=120
    ):

        panel = pygame.Surface(
            (ancho, alto),
            pygame.SRCALPHA
        )

        panel.fill((20, 25, 35, alpha))

        pantalla.blit(panel, (x, y))

        pygame.draw.rect(
            pantalla,
            (120, 180, 255),
            (x, y, ancho, alto),
            2,
            border_radius=20
        )

    # =================================
    # BOTON SELECCIONADO
    # =================================
    def dibujar_glow_boton(
        self,
        pantalla,
        x,
        y,
        ancho,
        alto
    ):

        pulso = self.obtener_pulso(0.006)

        alpha = 60 + int(pulso * 80)

        glow = pygame.Surface(
            (ancho + 40, alto + 20),
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            glow,
            (0, 220, 255, alpha),
            (0, 0, ancho + 40, alto + 20),
            border_radius=20
        )

        pantalla.blit(
            glow,
            (x - 20, y - 10)
        )

        pygame.draw.rect(
            pantalla,
            (0, 220, 255),
            (x, y, ancho, alto),
            2,
            border_radius=15
        )