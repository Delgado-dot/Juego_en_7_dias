import pygame
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

    def draw_panel(self, screen, rect):
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 130))
        screen.blit(panel, rect.topleft)
        pygame.draw.rect(screen, (0, 240, 255), rect, 2, border_radius=10)

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