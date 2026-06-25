import pygame
import math
from game.UI.menu_efects import MenuEffects


class MenuPausa:

    def __init__(self, pantalla, ancho, alto, config=None):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.config = config or {}
        self.opcion = 0
        self.opciones = ["Reanudar", "Reiniciar nivel", "Salir al menu"]
        self.effects = MenuEffects(ancho, alto)

        try:
            self.fuente_titulo = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 52)
            self.fuente_menu = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 24)
            self.fuente_peq = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 14)
        except:
            self.fuente_titulo = pygame.font.SysFont("Arial", 52)
            self.fuente_menu = pygame.font.SysFont("Arial", 24)
            self.fuente_peq = pygame.font.SysFont("Arial", 14)

        self.fondo_congelado = pantalla.copy()
        self.tiempo_inicio = pygame.time.get_ticks()
        self.duracion_entrada = 350

        try:
            self.sonido_pausa = pygame.mixer.Sound("assets/sounds/pause.wav")
        except:
            self.sonido_pausa = None

    def _progreso_entrada(self):
        transcurrido = pygame.time.get_ticks() - self.tiempo_inicio
        return min(1.0, transcurrido / self.duracion_entrada)

    def dibujar(self):
        self.pantalla.blit(self.fondo_congelado, (0, 0))

        progreso = self._progreso_entrada()
        eased = 1 - (1 - progreso) ** 3

        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(160 * eased)))
        self.pantalla.blit(overlay, (0, 0))

        if self.config.get("particulas", True):
            self.effects.dibujar_particulas(self.pantalla)

        panel_w = int(900 * (0.7 + 0.3 * eased))
        panel_h = int(440 * (0.7 + 0.3 * eased))
        panel_x = self.ancho // 2 - panel_w // 2
        panel_y = self.alto // 2 - panel_h // 2

        self.effects.dibujar_panel_glass(self.pantalla, panel_x, panel_y, panel_w, panel_h)

        titulo = self.effects.render_texto_pulso(
            self.fuente_titulo, "PAUSA", (120, 230, 255), 1, 0.05
        )
        alpha_titulo = int(255 * eased)
        titulo.set_alpha(alpha_titulo)
        self.pantalla.blit(titulo, titulo.get_rect(center=(self.ancho // 2, panel_y + 70)))

        linea_y = panel_y + 115
        ancho_linea = int(360 * eased)
        linea_x = self.ancho // 2 - ancho_linea // 2
        for i in range(3):
            color = (0, 220, 255, max(40, 220 - i * 80))
            pygame.draw.line(
                self.pantalla, color,
                (linea_x, linea_y + i), (linea_x + ancho_linea, linea_y + i), 1
            )

        for i, op in enumerate(self.opciones):
            y = panel_y + 180 + i * 65
            btn_x = self.ancho // 2 - 200
            btn_y = y - 25
            btn_w = 400
            btn_h = 50

            if i == self.opcion:
                self.effects.dibujar_glow_boton(self.pantalla, btn_x, btn_y, btn_w, btn_h)
                texto = self.effects.render_texto_pulso(
                    self.fuente_menu, op, (255, 255, 255), 1, 0.05
                )
            else:
                texto = self.fuente_menu.render(op, True, (200, 200, 200))

            texto.set_alpha(int(255 * eased))
            self.pantalla.blit(texto, texto.get_rect(center=(self.ancho // 2, y)))

        instrucciones = self.fuente_peq.render(
            "W/S - Navegar   |   ENTER - Seleccionar   |   ESC - Reanudar", True, (180, 180, 180)
        )
        instrucciones.set_alpha(int(255 * eased))
        self.pantalla.blit(
            instrucciones, instrucciones.get_rect(center=(self.ancho // 2, panel_y + panel_h - 35))
        )

        pygame.display.flip()

    def ejecutar(self):
        if self.sonido_pausa:
            try:
                volumen = self.config.get("vol_efectos", 0.7) if hasattr(self, 'config') else 0.7
                self.sonido_pausa.set_volume(volumen)
                self.sonido_pausa.play()
            except:
                pass

        reloj = pygame.time.Clock()
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()

                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        return "reanudar"

                    if evento.key in (pygame.K_w, pygame.K_UP):
                        self.opcion = (self.opcion - 1) % len(self.opciones)
                    elif evento.key in (pygame.K_s, pygame.K_DOWN):
                        self.opcion = (self.opcion + 1) % len(self.opciones)
                    elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.opcion == 0:
                            return "reanudar"
                        elif self.opcion == 1:
                            return "reiniciar"
                        elif self.opcion == 2:
                            return "menu"

            self.dibujar()
            reloj.tick(60)
