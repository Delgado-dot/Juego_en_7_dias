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
        self.pantalla.fill((10, 10, 30))

        titulo = self.fuente_titulo.render("GUARDAR PUNTAJE", True, (0, 200, 255))
        self.pantalla.blit(titulo, titulo.get_rect(center=(self.ancho // 2, 100)))

        pts = self.fuente_texto.render(f"Puntaje: {self.puntaje}", True, (255, 255, 255))
        self.pantalla.blit(pts, pts.get_rect(center=(self.ancho // 2, 200)))

        inst = self.fuente_texto.render("Ingresa tu nombre:", True, (200, 200, 200))
        self.pantalla.blit(inst, inst.get_rect(center=(self.ancho // 2, 280)))

        caja_w, caja_h = 400, 60
        caja_x = self.ancho // 2 - caja_w // 2
        caja_y = 320
        pygame.draw.rect(self.pantalla, (40, 40, 60), (caja_x, caja_y, caja_w, caja_h))
        pygame.draw.rect(self.pantalla, (0, 200, 255), (caja_x, caja_y, caja_w, caja_h), 2)

        nombre_render = self.fuente_texto.render(self.nombre, True, (255, 255, 255))
        self.pantalla.blit(nombre_render, nombre_render.get_rect(center=(self.ancho // 2, caja_y + 30)))

        if pygame.time.get_ticks() % 1000 < 500:
            cursor_x = self.ancho // 2 + nombre_render.get_width() // 2 + 5
            pygame.draw.line(self.pantalla, (255, 255, 255), (cursor_x, caja_y + 10), (cursor_x, caja_y + 50), 2)

        cont = self.fuente_peq.render(f"{len(self.nombre)}/{self.max_caracteres}", True, (100, 100, 100))
        self.pantalla.blit(cont, cont.get_rect(center=(self.ancho // 2, caja_y + 80)))

        inst2 = self.fuente_peq.render("Enter para confirmar", True, (0, 200, 100))
        self.pantalla.blit(inst2, inst2.get_rect(center=(self.ancho // 2, self.alto - 40)))

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