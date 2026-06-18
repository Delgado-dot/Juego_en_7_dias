import pygame
import sys
from datetime import datetime
from db.database_manager import crear_jugador, crear_personaje, guardar_puntaje
from game.UI.input_nombre import InputNombre

class GameOver:
    def __init__(self, pantalla, ancho, alto, puntaje, nivel_llegado=1, chaquetas=0):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.puntaje = puntaje
        self.nivel_llegado = nivel_llegado
        self.chaquetas = chaquetas
        self.opcion = 0
        self.opciones = ["Guardar y reintentar", "Reintentar", "Volver al menú", "Salir"]

        try:
            self.fuente_titulo = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 60)
            self.fuente_menu = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 28)
            self.fuente_peq = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 16)
        except:
            self.fuente_titulo = pygame.font.SysFont("Arial", 60)
            self.fuente_menu = pygame.font.SysFont("Arial", 28)
            self.fuente_peq = pygame.font.SysFont("Arial", 16)

        try:
            self.fondo = pygame.image.load("assets/images/game_over_fondo.png")
            self.fondo = pygame.transform.scale(self.fondo, (ancho, alto))
        except:
            self.fondo = None

        try:
            pygame.mixer.music.load("assets/sounds/game_over.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except:
            pass

    def guardar(self):
        inp = InputNombre(self.pantalla, self.ancho, self.alto, self.puntaje)
        nombre = inp.ejecutar()
        jugador_id = crear_jugador(nombre, self.nivel_llegado, self.puntaje)
        personaje_id = crear_personaje(nombre, 3, jugador_id)
        guardar_puntaje(
            puntos=self.puntaje,
            fecha=datetime.now().strftime("%Y-%m-%d %H:%M"),
            personaje_id=personaje_id,
            nivel_id=self.nivel_llegado,
            chaqueta_equipada=self.chaquetas > 0,
            tiempo_juego="00:00"
        )

    def dibujar(self):
        if self.fondo:
            self.pantalla.blit(self.fondo, (0, 0))
        else:
            self.pantalla.fill((20, 0, 0))

        titulo = self.fuente_titulo.render("GAME OVER", True, (255, 50, 50))
        self.pantalla.blit(titulo, titulo.get_rect(center=(self.ancho // 2, self.alto // 4)))

        pts = self.fuente_menu.render(f"Puntaje: {self.puntaje}", True, (255, 255, 255))
        self.pantalla.blit(pts, pts.get_rect(center=(self.ancho // 2, self.alto // 3 + 20)))

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
                        if op == "Guardar y reintentar":
                            self.guardar()
                            return "reintentar"
                        elif op == "Reintentar":
                            return "reintentar"
                        elif op == "Volver al menú":
                            return "menu"
                        else:
                            pygame.quit()
                            sys.exit()
            self.dibujar()
            reloj.tick(60)