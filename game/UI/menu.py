import pygame
import sys
import cv2
from db.database_manager import top_5_puntajes, leer_csv, PERSONAJES_CSV
from game.UI.menu_efects import MenuEffects


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
        self.effects = MenuEffects(ancho, alto)

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
            MENU_X = int(ancho * 0.70)
            self.titulo_img = pygame.image.load("assets/images/HUD/Titulomenu.png").convert_alpha()
            self.titulo_img = pygame.transform.scale(self.titulo_img, (600, 350))
            self.btn_jugar = pygame.image.load("assets/images/HUD/boton_jugar.png").convert_alpha()
            self.btn_jugar = pygame.transform.scale(self.btn_jugar, (500, 220))
            self.btn_ranking = pygame.image.load("assets/images/HUD/boton_ranking.png").convert_alpha()
            self.btn_ranking = pygame.transform.scale(self.btn_ranking, (425, 220))
            self.btn_salir = pygame.image.load("assets/images/HUD/boton_salir.png").convert_alpha()
            self.btn_salir = pygame.transform.scale(self.btn_salir, (450, 220))
            self.rect_jugar = self.btn_jugar.get_rect(center=(MENU_X , 450))
            self.rect_ranking = self.btn_ranking.get_rect(center=(MENU_X, 550))
            self.rect_salir = self.btn_salir.get_rect(center=(MENU_X, 640))
        except Exception as e:
            print(f"Error cargando botones: {e}")
            self.titulo_img = None

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

            overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.pantalla.blit(overlay, (0, 0))

            self.effects.dibujar_particulas(self.pantalla)

            titulo = self.effects.render_texto_pulso(
                self.fuente_titulo, "TOP 5", (120, 230, 255), 1, 0.08
            )
            self.pantalla.blit(titulo, titulo.get_rect(center=(self.ancho // 2, 70)))

            panel_w, panel_h = 900, 520
            panel_x = self.ancho // 2 - panel_w // 2
            panel_y = 120
            self.effects.dibujar_panel_glass(self.pantalla, panel_x, panel_y, panel_w, panel_h)

            if puntajes:
                y = panel_y + 60
                colores = [(255, 215, 0), (180, 180, 180), (205, 127, 50)]
                for i, p in enumerate(puntajes):
                    nombre = nombre_por_id(p.get("personaje_id", 0))
                    pts = p.get("puntos", 0)
                    color = colores[i] if i < 3 else (220, 220, 220)
                    linea = f"{i+1}. {nombre}   |   {pts} pts"
                    render = self.fuente_menu.render(linea, True, color)
                    self.pantalla.blit(render, render.get_rect(center=(self.ancho // 2, y)))
                    pygame.draw.line(self.pantalla, (60, 60, 60),
                        (panel_x + 80, y + 25), (panel_x + panel_w - 80, y + 25), 1)
                    y += 90
            else:
                vacio = self.fuente_menu.render("Sin puntajes aun", True, (150, 150, 150))
                self.pantalla.blit(vacio, vacio.get_rect(center=(self.ancho // 2, self.alto // 2)))

            inst = self.fuente_peq.render("Presiona cualquier tecla para volver", True, (180, 180, 180))
            self.pantalla.blit(inst, inst.get_rect(center=(self.ancho // 2, self.alto - 40)))
            pygame.display.flip()
            reloj.tick(60)

    def dibujar(self):
        if self.frames_video:
            self.avanzar_video()
        else:
            self.pantalla.fill((10, 10, 30))

        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.pantalla.blit(overlay, (0, 0))

        self.effects.dibujar_particulas(self.pantalla)

        if self.titulo_img:
            x = int(self.ancho * 0.70) - self.titulo_img.get_width() // 2
            self.pantalla.blit(self.titulo_img, (x, 50))

            botones = [
                (self.btn_jugar, self.rect_jugar),
                (self.btn_ranking, self.rect_ranking),
                (self.btn_salir, self.rect_salir)
            ]

            for i, (btn, rect) in enumerate(botones):
                if i == self.opcion:

                    pulso = self.effects.obtener_pulso()
                    escala = 1 + pulso * 0.05
                    nuevo_w = int(rect.width * escala)
                    nuevo_h = int(rect.height * escala)
                    btn_animado = pygame.transform.smoothscale(
                        btn,
                        (nuevo_w, nuevo_h))

                    nuevo_rect = btn_animado.get_rect(
                         center=rect.center)

                    self.pantalla.blit(
                        btn_animado,
                        nuevo_rect.topleft)
                else:

                    self.pantalla.blit(
                        btn,
                        rect.topleft)
        else:
            titulo = self.effects.render_texto_pulso(
                self.fuente_titulo, "Cable Runner", (120, 230, 255)
            )
            self.pantalla.blit(titulo, titulo.get_rect(center=(self.ancho // 2, self.alto // 4)))

            panel_w, panel_h = 620, 340
            panel_x = self.ancho // 2 - panel_w // 2
            panel_y = self.alto // 2 - 120
            self.effects.dibujar_panel_glass(self.pantalla, panel_x, panel_y, panel_w, panel_h)

            for i, op in enumerate(self.opciones):
                y = self.alto // 2 + i * 75
                if i == self.opcion:
                    self.effects.dibujar_glow_boton(
                        self.pantalla, self.ancho // 2 - 190, y - 25, 380, 50
                    )
                    texto = self.effects.render_texto_pulso(
                        self.fuente_menu, op, (255, 255, 255), 1, 0.06
                    )
                else:
                    texto = self.fuente_menu.render(op, True, (200, 200, 200))
                self.pantalla.blit(texto, texto.get_rect(center=(self.ancho // 2, y)))

        controles = self.fuente_peq.render("W/S o Flechas  |  ENTER", True, (180, 180, 180))
        self.pantalla.blit(controles, controles.get_rect(center=(self.ancho // 2, self.alto - 40)))
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