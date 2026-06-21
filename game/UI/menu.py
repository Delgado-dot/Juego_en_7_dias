import pygame
import sys
import cv2
from db.database_manager import top_5_puntajes, leer_csv, PERSONAJES_CSV


class Menu:
    def __init__(self, pantalla, ancho, alto):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.opcion = 0
        self.opciones = ["Jugar", "Ranking", "Salir"]
        self.frames_video = []
        self.frame_actual = 0
        self.direccion_video = 1
        self.titulo_img = None

        try:
            self.fuente_titulo = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 60)
            self.fuente_menu = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 28)
            self.fuente_peq = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 16)
        except:
            self.fuente_titulo = pygame.font.SysFont("Arial", 60)
            self.fuente_menu = pygame.font.SysFont("Arial", 28)
            self.fuente_peq = pygame.font.SysFont("Arial", 16)

        pygame.mixer.music.stop()
        try:
            pygame.mixer.music.load("assets/sounds/musica_menu.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except:
            pass

        pantalla.fill((10, 10, 30))
        cargando = self.fuente_peq.render("Cargando...", True, (0, 200, 255))
        pantalla.blit(cargando, cargando.get_rect(center=(ancho // 2, alto // 2)))
        pygame.display.flip()

        try:
            self.titulo_img = pygame.image.load("assets/images/HUD/Titulomenu.png").convert_alpha()
            self.titulo_img = pygame.transform.scale(self.titulo_img, (600, 300))
            self.btn_jugar = pygame.image.load("assets/images/HUD/boton_jugar.png").convert_alpha()
            self.btn_jugar = pygame.transform.scale(self.btn_jugar, (450, 100))
            self.btn_ranking = pygame.image.load("assets/images/HUD/boton_ranking.png").convert_alpha()
            self.btn_ranking = pygame.transform.scale(self.btn_ranking, (450, 100))
            self.btn_salir = pygame.image.load("assets/images/HUD/boton_salir.png").convert_alpha()
            self.btn_salir = pygame.transform.scale(self.btn_salir, (450, 100))
            self.rect_jugar = self.btn_jugar.get_rect(center=(ancho // 2, 450))
            self.rect_ranking = self.btn_ranking.get_rect(center=(ancho // 2, 550))
            self.rect_salir = self.btn_salir.get_rect(center=(ancho // 2, 650))
        except Exception as e:
            print(f"Error cargando botones: {e}")

        try:
            video = cv2.VideoCapture("assets/images/HUD/menu_fondo.mp4")
            contador = 0
            while True:
                ret, frame = video.read()
                if not ret or contador > 300:
                    break
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (ancho, alto))
                superficie = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                self.frames_video.append(superficie)
                contador += 1
            video.release()
        except Exception as e:
            print(f"Error cargando video: {e}")

    def avanzar_video(self):
        if not self.frames_video:
            return
        self.pantalla.blit(self.frames_video[self.frame_actual], (0, 0))
        self.frame_actual += self.direccion_video
        if self.frame_actual >= len(self.frames_video) - 1:
            self.direccion_video = -1
        elif self.frame_actual <= 0:
            self.direccion_video = 1

    def mostrar_ranking(self):
        try:
            puntajes = top_5_puntajes()
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

            if self.frames_video:
                self.avanzar_video()
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
        if self.frames_video:
            self.avanzar_video()
        else:
            self.pantalla.fill((10, 10, 30))

        if self.titulo_img:
            x = (self.ancho - self.titulo_img.get_width()) // 2
            self.pantalla.blit(self.titulo_img, (x, 50))
            self.pantalla.blit(self.btn_jugar, self.rect_jugar.topleft)
            self.pantalla.blit(self.btn_ranking, self.rect_ranking.topleft)
            self.pantalla.blit(self.btn_salir, self.rect_salir.topleft)
            color_borde = (255, 0, 128) if self.opcion == 2 else (0, 255, 240)
            rects = [self.rect_jugar, self.rect_ranking, self.rect_salir]
            pygame.draw.rect(self.pantalla, color_borde, rects[self.opcion], 4, border_radius=10)
        else:
            titulo = self.fuente_titulo.render("Cable Runner", True, (0, 200, 255))
            self.pantalla.blit(titulo, titulo.get_rect(center=(self.ancho // 2, self.alto // 4)))
            for i, op in enumerate(self.opciones):
                color = (0, 255, 150) if i == self.opcion else (200, 200, 200)
                prefijo = "> " if i == self.opcion else "  "
                t = self.fuente_menu.render(prefijo + op, True, color)
                self.pantalla.blit(t, t.get_rect(center=(self.ancho // 2, self.alto // 2 + i * 70)))

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