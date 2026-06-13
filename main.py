import pygame
import sys

pantalla_ancho = 800
pantalla_alto = 600
FPS = 60

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((pantalla_ancho, pantalla_alto))
    pygame.display.set_caption( "-----")
    reloj = pygame.time.Clock()
    
    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
        
        pantalla.fill((30,30,30))
        pygame.display.flip()
        reloj.tick(FPS)
        
    pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main()