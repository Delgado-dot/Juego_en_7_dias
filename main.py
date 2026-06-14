import pygame
import sys
from game.UI.hud import HUD

pantalla_ancho = 1920
pantalla_alto = 1080    
FPS = 60

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((pantalla_ancho, pantalla_alto))
    pygame.display.set_caption("-----")
    reloj = pygame.time.Clock()
    hud = HUD()
    inicio_tiempo = pygame.time.get_ticks()
    
    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
        
        pantalla.fill((30, 30, 30))
        hud.draw(pantalla, 3, 0, inicio_tiempo)
        pygame.display.flip()
        reloj.tick(FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()