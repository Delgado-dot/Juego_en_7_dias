
import pygame
import sys
from datetime import datetime
from db.database_manager import crear_jugador, crear_personaje, guardar_puntaje
from game.UI.input_nombre import InputNombre

class GameOver:
    def __init__(self, pantalla, ancho, alto, puntaje, nivel_llegado=1, chaquetas=0):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.puntaje = puntaje
        self.nivel_llegado = nivel_llegado
        self.chaquetas = chaquetas
        self.opcion = 0
        self.opciones = ["Guardar y reintentar", "Reintentar", "Volver al menú", "Salir"]

        try:
            self.fuente_titulo = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 60)
            self.fuente_menu = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 28)
            self.fuente_peq = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 16)
        except:
            self.fuente_titulo = pygame.font.SysFont("Arial", 60)
            self.fuente_menu = pygame.font.SysFont("Arial", 28)
            self.fuente_peq = pygame.font.SysFont("Arial", 16)

        try:
            self.fondo = pygame.image.load("assets/images/game_over_fondo.png")
            self.fondo = pygame.transform.scale(self.fondo, (ancho, alto))
        except:
            self.fondo = None

        try:
            pygame.mixer.music.load("assets/sounds/game_over.mp3")
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

        if self.fondo:
            self.pantalla.blit(self.fondo, (0, 0))

            sombra_fondo = pygame.Surface(
                (self.ancho, self.alto)
            )
            sombra_fondo.set_alpha(170)
            sombra_fondo.fill((0, 0, 0))

            self.pantalla.blit(
                sombra_fondo,
                (0, 0)
            )
        else:
            self.pantalla.fill((15, 0, 0))

        tiempo = pygame.time.get_ticks()

# =========================
# TITULO
# =========================

        brillo = int(
            30 * abs(
                __import__("math").sin(
                    tiempo * 0.004
                )
            )
        )

        sombra = self.fuente_titulo.render(
        "GAME OVER",
        True,
        (0, 0, 0)
        )

        titulo = self.fuente_titulo.render(
            "GAME OVER",
            True,
            (
            min(255, 220 + brillo),
            50,
            50
            )
        )

        self.pantalla.blit(
            sombra,
            sombra.get_rect(
                center=(
                    self.ancho // 2 + 4,
                    self.alto // 5 + 4
                )
            )
        )

        self.pantalla.blit(
            titulo,
            titulo.get_rect(
                center=(
                    self.ancho // 2,
                    self.alto // 5
                )
            )
        )

# =========================
# PANEL CENTRAL
# =========================
        panel_ancho = 820
        panel_alto = 440

        x = self.ancho // 2 - panel_ancho // 2
        y = self.alto // 2 - panel_alto // 2 + 80

        # PANEL (oscuro)
        panel = pygame.Surface((panel_ancho, panel_alto))
        panel.set_alpha(190)
        panel.fill((12, 12, 12))

        self.pantalla.blit(panel, (x, y))

        # BORDE PRINCIPAL (rojo elegante)
        pygame.draw.rect(
            self.pantalla,
            (220, 60, 60),
            (x, y, panel_ancho, panel_alto),
            3,
            border_radius=18
        )

    # BORDE INTERNO (detalle pro)
        pygame.draw.rect(
            self.pantalla,
            (80, 0, 0),
            (x + 6, y + 6, panel_ancho - 12, panel_alto - 12),
            1,
            border_radius=14
        )
# =========================
# PUNTAJE
# =========================

        texto_pts = self.fuente_menu.render(
            f"PUNTAJE FINAL: {self.puntaje}",
            True,
            (255, 220, 100)
        )

        self.pantalla.blit(
            texto_pts,
            texto_pts.get_rect(
                center=(
                    self.ancho // 2,
                    self.alto // 2 - 80
                )
            )
        )

# =========================
# NIVEL
# =========================

        texto_nivel = self.fuente_peq.render(
            f"Nivel alcanzado: {self.nivel_llegado}",
            True,
            (220, 220, 220)
        )

        self.pantalla.blit(
            texto_nivel,
            texto_nivel.get_rect(
                center=(
                    self.ancho // 2,
                    self.alto // 2 - 35
                )
            )
        )

# =========================
# OPCIONES
# =========================

        for i, op in enumerate(self.opciones):

            y = self.alto // 2 + 40 + i * 60

            if i == self.opcion:

                pygame.draw.rect(
                    self.pantalla,
                    (255, 80, 80),
                    (
                        self.ancho // 2 - 250,
                        y - 25,
                        500,
                        50
                    ),
                    2,
                    border_radius=10
                )

                texto = self.fuente_menu.render(
                    op,
                    True,
                    (255, 120, 120)
                )

            else:

                texto = self.fuente_menu.render(
                    op,
                    True,
                    (200, 200, 200)
                )

            self.pantalla.blit(
                    texto,
                    texto.get_rect(
                        center=(
                            self.ancho // 2,
                            y
                        )
                    )
                )

# =========================
# MENSAJE INFERIOR
# =========================

        mensaje = self.fuente_peq.render(
            "W/S o Flechas - ENTER para seleccionar",
            True,
            (150, 150, 150)
        )

        self.pantalla.blit(
            mensaje,
            mensaje.get_rect(
                center=(
                    self.ancho // 2,
                    self.alto - 35
                )
            )
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
                        if op == "Guardar y reintentar":
                            self.guardar()
                            return "reintentar"
                        elif op == "Reintentar":
                            return "reintentar"
                        elif op == "Volver al menú":
                            return "menu"
                        else:
                            pygame.quit()
                            sys.exit()
            self.dibujar()
            reloj.tick(60)