import pygame
import sys
from db.database_manager import top_5_puntajes

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
            self.fuente_peq = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 16)
        except:
            self.fuente_titulo = pygame.font.SysFont("Arial", 60)
            self.fuente_menu = pygame.font.SysFont("Arial", 28)
            self.fuente_peq = pygame.font.SysFont("Arial", 16)

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

    def mostrar_ranking(self):
        try:
            puntajes = top_5_puntajes()
            from db.database_manager import leer_csv, PERSONAJES_CSV
            personajes = leer_csv(PERSONAJES_CSV)
        except:
            puntajes = []
            personajes = []

        def nombre_por_id(pid):
            for p in personajes:
                if p["id"] == str(pid):
                    return p["nombre"]
            return "???"

        esperando = True
        reloj = pygame.time.Clock()
        while esperando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    esperando = False

            if self.fondo:
                self.pantalla.blit(self.fondo, (0, 0))
            else:
                self.pantalla.fill((10, 10, 30))

            titulo = self.fuente_titulo.render("TOP 5", True, (0, 200, 255))
            self.pantalla.blit(titulo, titulo.get_rect(center=(self.ancho // 2, 60)))

            if puntajes:
                y = 160
                for i, p in enumerate(puntajes):
                    nombre = nombre_por_id(p.get("personaje_id", 0))
                    pts = p.get("puntos", 0)
                    nivel = p.get("nivel_id", "?")
                    chaqueta = "Si" if p.get("chaqueta_equipada", "False") == "True" else "No"
                    linea = f"{i+1}. {nombre} | {pts} pts | Niv {nivel} | Chaqueta: {chaqueta}"
                    t = self.fuente_peq.render(linea, True, (255, 255, 255))
                    self.pantalla.blit(t, t.get_rect(center=(self.ancho // 2, y)))
                    y += 60
            else:
                vacio = self.fuente_menu.render("Sin puntajes aun", True, (150, 150, 150))
                self.pantalla.blit(vacio, vacio.get_rect(center=(self.ancho // 2, self.alto // 2)))

            inst = self.fuente_peq.render("Presiona cualquier tecla para volver", True, (100, 100, 100))
            self.pantalla.blit(inst, inst.get_rect(center=(self.ancho // 2, self.alto - 40)))
            pygame.display.flip()
            reloj.tick(60)

    def dibujar(self):
        if self.fondo:
            self.pantalla.blit(self.fondo, (0, 0))
        else:
            self.pantalla.fill((10, 10, 30))

        titulo = self.fuente_titulo.render("Jumper Rack", True, (0, 200, 255))
        self.pantalla.blit(titulo, titulo.get_rect(center=(self.ancho // 2, self.alto // 4)))

        for i, op in enumerate(self.opciones):
            color = (0, 255, 150) if i == self.opcion else (200, 200, 200)
            prefijo = "> " if i == self.opcion else "  "
            t = self.fuente_menu.render(prefijo + op, True, color)
            self.pantalla.blit(t, t.get_rect(center=(self.ancho // 2, self.alto // 2 + i * 70)))

        inst = self.fuente_peq.render("W/S mover   Enter elegir", True, (100, 100, 100))
        self.pantalla.blit(inst, inst.get_rect(center=(self.ancho // 2, self.alto - 40)))
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
                        op = self.opciones[self.opcion]
                        if op == "Jugar":
                            pygame.mixer.music.stop()
                            return "jugar"
                        elif op == "Ranking":
                            self.mostrar_ranking()
                        elif op == "Salir":
                            pygame.quit()
                            sys.exit()
            self.dibujar()
            reloj.tick(60)