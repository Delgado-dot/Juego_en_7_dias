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
            self.fuente_titulo = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 58)
            self.fuente_menu = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 22)
            self.fuente_peq = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 14)
        except:
            self.fuente_titulo = pygame.font.SysFont("Arial", 58)
            self.fuente_menu = pygame.font.SysFont("Arial", 22)
            self.fuente_peq = pygame.font.SysFont("Arial", 14)

        try:
            self.fondo = pygame.image.load("assets/images/game_over_fondo.png").convert()
            self.fondo = pygame.transform.scale(self.fondo, (ancho, alto))
        except:
            self.fondo = None

        try:
            pygame.mixer.music.load("assets/sounds/game_over.mp3")
            pygame.mixer.music.set_volume(0.45)
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

    def dibujar_panel(self, rect, color_borde=(255, 60, 80)):
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 155))
        self.pantalla.blit(panel, rect.topleft)

        pygame.draw.rect(
            self.pantalla,
            color_borde,
            rect,
            3,
            border_radius=18
        )

    def dibujar_texto_centrado(self, texto, fuente, color, y):
        render = fuente.render(texto, True, color)
        rect = render.get_rect(center=(self.ancho // 2, y))
        self.pantalla.blit(render, rect)

    def dibujar(self):
        if self.fondo:
            self.pantalla.blit(self.fondo, (0, 0))
        else:
            self.pantalla.fill((15, 0, 10))

        # Oscurecer fondo
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 135))
        self.pantalla.blit(overlay, (0, 0))

        # Panel principal
        panel_rect = pygame.Rect(
            self.ancho // 2 - 360,
            70,
            720,
            560
        )
        self.dibujar_panel(panel_rect)

        # Título
        self.dibujar_texto_centrado("GAME OVER", self.fuente_titulo, (255, 55, 80), 135)

        # Línea decorativa
        pygame.draw.line(
            self.pantalla,
            (0, 240, 255),
            (self.ancho // 2 - 230, 180),
            (self.ancho // 2 + 230, 180),
            3
        )

        # Datos
        puntaje_font = pygame.font.Font(
    "assets/fonts/PressStart2P-Regular.ttf",
    30
        )

        self.dibujar_texto_centrado(
            f"PUNTAJE FINAL: {self.puntaje}",
            puntaje_font,
            (255, 255, 255),
            230
        )
        
        self.dibujar_texto_centrado(
            f"NIVEL ALCANZADO: {self.nivel_llegado}",
              self.fuente_peq,
                (0, 255, 180),
                  270
                  )
        
        self.dibujar_texto_centrado(
            f"CHAQUETAS: {self.chaquetas}", 
            self.fuente_peq, 
            (0, 220, 255), 
            300
            )

        # Opciones tipo botones
        inicio_y = 365
        for i, op in enumerate(self.opciones):
            seleccionado = i == self.opcion

            btn_rect = pygame.Rect(
                self.ancho // 2 - 260,
                inicio_y + i * 58,
                520,
                42
            )

            color_borde = (0, 255, 180) if seleccionado else (90, 90, 90)
            color_texto = (0, 255, 180) if seleccionado else (220, 220, 220)

            btn_surface = pygame.Surface((btn_rect.width, btn_rect.height), pygame.SRCALPHA)
            btn_surface.fill((0, 0, 0, 100))
            self.pantalla.blit(btn_surface, btn_rect.topleft)

            pygame.draw.rect(
                self.pantalla,
                color_borde,
                btn_rect,
                2,
                border_radius=12
            )

            prefijo = "► " if seleccionado else "  "
            texto = self.fuente_peq.render(prefijo + op, True, color_texto)
            self.pantalla.blit(texto, texto.get_rect(center=btn_rect.center))

        inst = self.fuente_peq.render(
            "W/S o Flechas: mover    ENTER: elegir",
            True,
            (160, 160, 160)
        )
        self.pantalla.blit(inst, inst.get_rect(center=(self.ancho // 2, self.alto - 35)))

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