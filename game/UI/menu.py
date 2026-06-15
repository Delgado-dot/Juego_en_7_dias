import pygame
import sys

class Menu:
    def __init__(self, pantalla, ancho, alto):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.opcion = 0
        self.opciones = ["Jugar", "Ranking", "Salir"]
        
        try:
            self.fuente_titulo = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 60)
            self.fuente_menu = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 28)
            self.fuente_pequeña = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 16)
        except:
            self.fuente_titulo = pygame.font.SysFont("Arial", 60)
            self.fuente_menu = pygame.font.SysFont("Arial", 28)
            self.fuente_pequeña = pygame.font.SysFont("Arial", 16)
        
        try:
            self.fondo = pygame.image.load("assets/images/menu_fondo.png")
            self.fondo = pygame.transform.scale(self.fondo, (ancho, alto))
        except:
            self.fondo = None
        
        try:
            pygame.mixer.music.load("assets/sounds/musica_menu.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except:
            pass

    def dibujar(self):
        if self.fondo:
            self.pantalla.blit(self.fondo, (0, 0))
        else:
            self.pantalla.fill((10, 10, 30))

        titulo = self.fuente_titulo.render("Cable Runner", True, (0, 200, 255))
        rect = titulo.get_rect(center=(self.ancho // 2, self.alto // 4))
        self.pantalla.blit(titulo, rect)

        for i, opcion in enumerate(self.opciones):
            color = (0, 255, 150) if i == self.opcion else (200, 200, 200)
            prefijo = "> " if i == self.opcion else "  "
            texto = self.fuente_menu.render(prefijo + opcion, True, color)
            rect = texto.get_rect(center=(self.ancho // 2, self.alto // 2 + i * 70))
            self.pantalla.blit(texto, rect)

        instruccion = self.fuente_pequeña.render("W/S mover   Enter elegir", True, (100, 100, 100))
        rect = instruccion.get_rect(center=(self.ancho // 2, self.alto - 40))
        self.pantalla.blit(instruccion, rect)

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
                        opcion = self.opciones[self.opcion]
                        if opcion == "Jugar":
                            pygame.mixer.music.stop()
                            return "jugar"
                        elif opcion == "Ranking":
                            return "ranking"
                        elif opcion == "Salir":
                            return "salir"
            self.dibujar()
            reloj.tick(60)