import pygame
import sys

class Victoria:
    def __init__(self, pantalla, ancho, alto, puntaje):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.puntaje = puntaje
        self.opcion = 0
        self.opciones = ["Volver al menú", "Salir"]

        try:
            self.fuente_titulo = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 60)
            self.fuente_menu = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 28)
            self.fuente_pequeña = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 16)
        except:
            self.fuente_titulo = pygame.font.SysFont("Arial", 60)
            self.fuente_menu = pygame.font.SysFont("Arial", 28)
            self.fuente_pequeña = pygame.font.SysFont("Arial", 16)

        try:
            self.fondo = pygame.image.load("assets/images/victoria_fondo.png")
            self.fondo = pygame.transform.scale(self.fondo, (ancho, alto))
        except:
            self.fondo = None

    def dibujar(self):
        if self.fondo:
            self.pantalla.blit(self.fondo, (0, 0))
        else:
            self.pantalla.fill((0, 20, 0))

        titulo = self.fuente_titulo.render("GANASTE", True, (0, 255, 150))
        rect = titulo.get_rect(center=(self.ancho // 2, self.alto // 4))
        self.pantalla.blit(titulo, rect)

        puntos = self.fuente_menu.render(f"Puntaje: {self.puntaje}", True, (255, 255, 255))
        rect2 = puntos.get_rect(center=(self.ancho // 2, self.alto // 3 + 20))
        self.pantalla.blit(puntos, rect2)

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
                        if self.opciones[self.opcion] == "Volver al menú":
                            return "menu"
                        else:
                            pygame.quit()
                            sys.exit()
            self.dibujar()
            reloj.tick(60)