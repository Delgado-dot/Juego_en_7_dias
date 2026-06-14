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

        self.heart_blue = pygame.transform.scale(self.heart_blue, (88, 88))
        self.heart_black = pygame.transform.scale(self.heart_black, (88, 88))
        self.jacket = pygame.transform.scale(self.jacket, (64, 64))

        self.font = pygame.font.Font(FUENTE_HUD, 32)

    def draw(self, screen, lives, max_lives, jacket_count, start_time):
        for i in range(max_lives):
            if i < lives:
                screen.blit(self.heart_blue, (10 + i * 95, 10))
            else:
                screen.blit(self.heart_black, (10 + i * 95, 10))

        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60

        timer_text = self.font.render(
            f"{minutes:02}:{seconds:02}", True, (0, 0, 0)
        )
        timer_rect = timer_text.get_rect(
            center=(screen.get_width() // 2, 50)
        )
        screen.blit(timer_text, timer_rect)

        screen.blit(self.jacket, (screen.get_width() - 150, 10))
        jacket_text = self.font.render(
            f"x{jacket_count}", True, (0, 0, 0)
        )
        screen.blit(jacket_text, (screen.get_width() - 80, 30))