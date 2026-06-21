
import pygame
import sys

class InputNombre:
    def __init__(self, pantalla, ancho, alto, puntaje):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.puntaje = puntaje
        self.nombre = ""
        self.max_caracteres = 15

        try:
            self.fuente_titulo = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 40)
            self.fuente_texto = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 24)
            self.fuente_peq = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 16)
        except:
            self.fuente_titulo = pygame.font.SysFont("Arial", 40)
            self.fuente_texto = pygame.font.SysFont("Arial", 24)
            self.fuente_peq = pygame.font.SysFont("Arial", 16)

    def dibujar(self):

    # Fondo
        self.pantalla.fill((10, 10, 30))

    # Overlay oscuro
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.pantalla.blit(overlay, (0, 0))

    # =========================
    # PANEL CENTRAL
    # =========================
        panel_w = 800
        panel_h = 420

        panel_x = self.ancho // 2 - panel_w // 2
        panel_y = self.alto // 2 - panel_h // 2

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((20, 20, 30, 170))

        self.pantalla.blit(panel, (panel_x, panel_y))

        pygame.draw.rect(
            self.pantalla,
            (0, 200, 255),
            (panel_x, panel_y, panel_w, panel_h),
            2,
            border_radius=20
        )

    # =========================
    # TITULO
    # ========================
        sombra = self.fuente_titulo.render(
            "GUARDAR PUNTAJE",
            True,
            (0, 0, 0)
        )

        titulo = self.fuente_titulo.render(
            "GUARDAR PUNTAJE",
            True,
            (0, 220, 255)
        )

        self.pantalla.blit(
            sombra,
            sombra.get_rect(
                center=(self.ancho//2 + 3, panel_y + 70 + 3)
            )
        )

        self.pantalla.blit(
            titulo,
            titulo.get_rect(
                center=(self.ancho//2, panel_y + 70)
            )
        )

    # =========================
    # PUNTAJE
    # ========================
        pts = self.fuente_texto.render(
            f"Puntaje: {self.puntaje}",
            True,
            (255, 255, 255)
        )

        self.pantalla.blit(
            pts,
            pts.get_rect(center=(self.ancho//2, panel_y + 140))
        )

    # =========================
    # TEXTO
    # =========================
        inst = self.fuente_texto.render(
            "Ingresa tu nombre",
            True,
            (200, 200, 200)
        )

        self.pantalla.blit(
            inst,
            inst.get_rect(center=(self.ancho//2, panel_y + 210))
        )

    # =========================
    # CAJA DE TEXTO GLASS
    # ========================
        caja_w = 500
        caja_h = 70

        caja_x = self.ancho // 2 - caja_w // 2
        caja_y = panel_y + 240

        caja = pygame.Surface((caja_w, caja_h), pygame.SRCALPHA)
        caja.fill((40, 40, 55, 180))

        self.pantalla.blit(caja, (caja_x, caja_y))

        pygame.draw.rect(
            self.pantalla,
            (0, 220, 255),
            (caja_x, caja_y, caja_w, caja_h),
            2,
            border_radius=12
        )

    # =========================
    # NOMBRE
    # ========================
        nombre_render = self.fuente_texto.render(
            self.nombre,
            True,
            (255, 255, 255)
        )

        self.pantalla.blit(
            nombre_render,
            nombre_render.get_rect(
                center=(self.ancho//2, caja_y + caja_h//2)
            )
        )

    # =========================
    # CURSOR PARPADEANTE
    # ========================
        if pygame.time.get_ticks() % 1000 < 500:

            cursor_x = (
                self.ancho//2 +
                nombre_render.get_width()//2 +
                8
            )

            pygame.draw.line(
                self.pantalla,
                (255, 255, 255),
                (cursor_x, caja_y + 15),
                (cursor_x, caja_y + 55),
                2
            )

    # =========================
    # CONTADOR
    # =========================
        contador = self.fuente_peq.render(
            f"{len(self.nombre)}/{self.max_caracteres}",
            True,
            (160, 160, 160)
        )

        self.pantalla.blit(
            contador,
            contador.get_rect(
                center=(self.ancho//2, caja_y + 95)
            )
        )

    # =========================
    # INSTRUCCIONES
    # ========================
        ayuda = self.fuente_peq.render(
            "ENTER = Guardar    |    ESC = Omitir",
            True,
            (0, 255, 180)
        )

        self.pantalla.blit(
            ayuda,
            ayuda.get_rect(
                center=(self.ancho//2, panel_y + panel_h - 40)
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
                    if evento.key == pygame.K_RETURN:
                        return self.nombre if self.nombre else "Jugador"
                    elif evento.key == pygame.K_BACKSPACE:
                        self.nombre = self.nombre[:-1]
                    elif evento.key == pygame.K_ESCAPE:
                        return "Jugador"
                    else:
                        if len(self.nombre) < self.max_caracteres and evento.unicode.isprintable():
                            self.nombre += evento.unicode
            self.dibujar()
            reloj.tick(60)