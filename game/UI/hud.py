import pygame
import math
from config import (
    SPRITE_CORAZON_LLENO, SPRITE_CORAZON_VACIO,
    SPRITE_CHAQUETA, FUENTE_HUD
)

class HUD:
    def __init__(self):
        self.heart_blue = pygame.image.load(SPRITE_CORAZON_LLENO).convert_alpha()
        self.heart_black = pygame.image.load(SPRITE_CORAZON_VACIO).convert_alpha()
        self.jacket = pygame.image.load(SPRITE_CHAQUETA).convert_alpha()

        self.heart_blue = pygame.transform.scale(self.heart_blue, (28, 28))
        self.heart_black = pygame.transform.scale(self.heart_black, (28, 28))
        self.jacket = pygame.transform.scale(self.jacket, (44, 44))

        self.font = pygame.font.Font(FUENTE_HUD, 24)
        self.font_small = pygame.font.Font(FUENTE_HUD, 14)
        self.cohete_icon = pygame.transform.scale(self.jacket, (52, 52))

        # Sonido al activar el cohete (opcional)
        try:
            self.sonido_cohete = pygame.mixer.Sound("assets/sounds/cohete_loop.wav")
            self.sonido_cohete.set_volume(0.4)
        except:
            self.sonido_cohete = None

        self.cohete_loop_activo = False


    def draw_panel(self, screen, rect):
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 130))
        screen.blit(panel, rect.topleft)
        pygame.draw.rect(screen, (0, 240, 255), rect, 2, border_radius=10)

    def draw_cohete_timer(self, screen, jugador):
        """
        Dibuja el cronómetro de la chaqueta cohete en pantalla.
        Muestra el tiempo restante y una barra de progreso.
        Maneja el sonido en loop mientras el cohete está activo.
        """
        # Solo dibujar si tiene la chaqueta Y ya empezó a usarla
        if not jugador.chaqueta_cohete or jugador.cohete_tiempo == 0:
            if self.cohete_loop_activo:
                self._detener_loop_cohete()
            return

        ancho = screen.get_width()
        alto = screen.get_height()

        # Calcular tiempo restante (ms)
        ahora = pygame.time.get_ticks()
        transcurrido = ahora - jugador.cohete_tiempo
        restante_ms = max(0, jugador.duracion_cohete - transcurrido)
        restante_s = restante_ms / 1000.0

        # Fracción restante 0..1
        fraccion = restante_ms / jugador.duracion_cohete

        # Reproducir sonido en loop mientras esté activo
        if self.sonido_cohete:
            if not self.cohete_loop_activo:
                try:
                    self.sonido_cohete.play(-1)
                    self.cohete_loop_activo = True
                except:
                    pass

        # Posición del panel: parte inferior central, sobre el HUD de controles
        panel_w = 360
        panel_h = 70
        panel_x = ancho // 2 - panel_w // 2
        panel_y = alto - 130

        # Panel glass con borde naranja/amarillo (tema fuego)
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        # Color de fondo que cambia a rojo cuando queda poco tiempo
        if restante_s <= 0.8:
            bg_color = (60, 15, 10, 200)
            borde_color = (255, 80, 60)
            barra_color = (255, 80, 60)
        else:
            bg_color = (40, 25, 10, 200)
            borde_color = (255, 180, 60)
            barra_color = (255, 180, 60)

        panel.fill(bg_color)
        screen.blit(panel, (panel_x, panel_y))
        pygame.draw.rect(screen, borde_color, (panel_x, panel_y, panel_w, panel_h),
                         2, border_radius=12)

        # Icono de chaqueta a la izquierda
        screen.blit(self.cohete_icon, (panel_x + 10, panel_y + 9))

        # Texto "COHETE" pequeño arriba a la derecha del icono
        texto_label = self.font_small.render("COHETE", True, (255, 220, 120))
        screen.blit(texto_label, (panel_x + 75, panel_y + 10))

        # Tiempo restante grande (a la derecha del icono)
        texto_tiempo = self.font.render(f"{restante_s:.1f}s", True, (255, 255, 255))
        screen.blit(texto_tiempo, (panel_x + 75, panel_y + 28))

        # Barra de progreso en la parte inferior del panel
        barra_x = panel_x + 75
        barra_y = panel_y + 55
        barra_w = panel_w - 90
        barra_h = 8

        # Fondo de la barra
        pygame.draw.rect(screen, (40, 40, 50), (barra_x, barra_y, barra_w, barra_h),
                         border_radius=4)
        # Borde
        pygame.draw.rect(screen, (120, 120, 130), (barra_x, barra_y, barra_w, barra_h),
                         1, border_radius=4)
        # Relleno (animado: pulsa cuando queda poco)
        ancho_relleno = int(barra_w * fraccion)
        if ancho_relleno > 0:
            if restante_s <= 0.8:
                # Pulso rápido cuando queda poco
                pulso = (math.sin(ahora * 0.02) + 1) / 2
                r = 255
                g = int(80 + pulso * 80)
                b = int(60 + pulso * 40)
                color_relleno = (r, g, b)
            else:
                color_relleno = barra_color

            pygame.draw.rect(screen, color_relleno,
                             (barra_x, barra_y, ancho_relleno, barra_h),
                             border_radius=4)

            # Brillo encima de la barra para que se vea "cargada"
            brillo = pygame.Surface((ancho_relleno, barra_h // 2), pygame.SRCALPHA)
            for x in range(ancho_relleno):
                alpha = int(60 * (1 - abs(x - ancho_relleno / 2) / (ancho_relleno / 2 + 1)))
                brillo.set_at((x, 0), (255, 255, 255, max(0, alpha)))
            screen.blit(brillo, (barra_x, barra_y))

        # Cuando queda muy poco tiempo, hacer parpadear todo el panel
        if restante_s <= 0.8:
            if int(ahora / 100) % 2 == 0:
                flash = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
                flash.fill((255, 100, 80, 50))
                screen.blit(flash, (panel_x, panel_y))

    def _detener_loop_cohete(self):
        """Detiene el sonido en loop del cohete."""
        if self.sonido_cohete and self.cohete_loop_activo:
            try:
                self.sonido_cohete.stop()
            except:
                pass
        self.cohete_loop_activo = False

    def detener_cohete(self):
        """API pública para detener el sonido del cohete (al cambiar de nivel, game over, etc)."""
        self._detener_loop_cohete()   

    def draw(self, screen, lives, max_lives, jacket_count, tiempo_restante):
        ancho = screen.get_width()

        # VIDA
        vida_rect = pygame.Rect(20, 20, 220, 55)
        self.draw_panel(screen, vida_rect)

        texto_vida = self.font_small.render("VIDA", True, (255, 255, 255))
        screen.blit(texto_vida, (35, 24))

        for i in range(max_lives):
             heart = self.heart_blue if i < lives else self.heart_black
             screen.blit(heart, (35 + i * 35, 38))

        # TIEMPO
        segundos = max(0, tiempo_restante // 1000)
        minutes = segundos // 60
        seconds = segundos % 60

        timer_rect = pygame.Rect(ancho // 2 - 80, 20, 160, 55)
        self.draw_panel(screen, timer_rect)

        texto_tiempo = self.font_small.render("TIEMPO", True, (255, 255, 255))
        screen.blit(texto_tiempo, texto_tiempo.get_rect(center=(ancho // 2, 31)))

        color_timer = (255, 60, 60) if segundos <= 10 else (0, 255, 180)
        timer_text = self.font.render(f"{minutes:02}:{seconds:02}", True, color_timer)
        screen.blit(timer_text, timer_text.get_rect(center=(ancho // 2, 57)))

        # CHAQUETA
        jacket_rect = pygame.Rect(ancho - 190, 20, 170, 55)
        self.draw_panel(screen, jacket_rect)

        texto_item = self.font_small.render("CHAQUETA", True, (255, 255, 255))
        screen.blit(texto_item, (ancho - 175, 26))

        screen.blit(self.jacket, (ancho - 175, 40))

        jacket_text = self.font.render(f"x{jacket_count}", True, (255, 255, 255))
        screen.blit(jacket_text, (ancho - 115, 45))