import pygame
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

heart_blue = pygame.image.load(
    os.path.join(
        BASE_DIR,
        "assets",
        "images",
        "HUD",
        "dark blue heart pixel art.png"
    )
).convert_alpha()

heart_black = pygame.image.load(
    os.path.join(
        BASE_DIR,
        "assets",
        "images",
        "HUD",
        "dark black heart pixel art.png"
    )
).convert_alpha()

jacket = pygame.image.load(
    os.path.join(
        BASE_DIR,
        "assets",
        "images",
        "HUD",
        "chaqueta.png"
    )
).convert_alpha()

heart_blue = pygame.transform.scale(heart_blue, (88, 88))
heart_black = pygame.transform.scale(heart_black, (88, 88))
jacket = pygame.transform.scale(jacket, (64, 64))

font = pygame.font.Font(
    os.path.join(
        BASE_DIR,
        "assets",
        "fonts",
        "PressStart2P-Regular.ttf"
    ),
    52
)

def draw_hud(screen, lives, max_lives, jacket_count, start_time):
    for i in range(max_lives):
        if i < lives:
            screen.blit(heart_blue, (10 + i * 65, 10))
        else:
            screen.blit(heart_black, (10 + i * 65, 10))

    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000

    minutes = elapsed_time // 60
    seconds = elapsed_time % 60

    timer_text = font.render(
        f"{minutes:02}:{seconds:02}",
        True,
        (255, 255, 255)
    )

    timer_rect = timer_text.get_rect(
        center=(screen.get_width() // 2, 50)
    )

    screen.blit(timer_text, timer_rect)

    screen.blit(jacket, (1680, 30))

    jacket_text = font.render(
        f"x{jacket_count}",
        True,
        (255, 255, 255)
    )

    screen.blit(jacket_text, (1760, 30))