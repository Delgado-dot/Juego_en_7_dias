import pygame
import os
from config import BASE_DIR, MUSICA_INTRO


def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


class Historia:

    ALTURA_CAJA = 220
    DURACION_BOX = 500
    VELOCIDAD_TEXTO = 25
    DURACION_FADE_BOTONES = 400

    def __init__(self, pantalla, ancho, alto):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto

        try:
            self.fuente = pygame.font.Font(
                os.path.join(BASE_DIR, "assets", "fonts", "PressStart2P-Regular.ttf"),
                17
            )
        except:
            self.fuente = pygame.font.SysFont("Arial", 24)

        self.historia = [
            {
                "imagen": "slide_01.png",
                "textos": [
                    "¿Alguna vez te has preguntado qué sucede cuando pierdes tu conexión a internet?",
                    "¿Quién se encarga de solucionar los problemas de conectividad cuando una red\ndeja de funcionar?",
                    "Cuando una página no carga, un archivo no llega a su destino o una empresa\nentera queda incomunicada, existe alguien que trabaja entre las sombras para\nmantener el mundo conectado."
                ]
            },
            {
                "imagen": "slide_02.png",
                "textos": [
                    "Su nombre es Jacked Man.",
                    "Jacked Man es un ser que vive en el internet, viaja de casa en casa sin\n que lo notes a través de la red.",
                    "Protector del internet y héroe anónimo de las redes, Jacked Man combate\nhackers, corrige errores, protege las conexiones y se asegura de que los datos\nlleguen a donde deben llegar. Gracias a él, millones de personas pueden navegar\npor internet ignorando completamente su existencia.",
                    "Porque mientras el mundo continúa con su vida cotidiana, Jacked Man\ntrabaja en silencio."
                ]
            },
            {
                "imagen": "slide_03.png",
                "textos": [
                    "Un día, el internet se fué.",
                    "Pero esta vez, fué diferente...",
                ]
            },
            {
                "imagen": "slide_04.png",
                "textos": [
                    "El mundo entero se enfrentó a una catástrofe global, pues en un instante\n todos perdieron la conección a internet en su totalidad...",
                    "Hospitales, universidades, empresas, incluso los propios\n servidores de internet",
                    "En un instante... todos estaban incomunicados."
                ]
            },
            {
                "imagen": "slide_05.png",
                "textos": [
                    "En cuestión de minutos...",
                    "El caos empezó a apoderarse de las calles al rededor del planeta",
                ]
            },
            {
                "imagen": "slide_06.png",
                "textos": [
                    "Las personas llamaban histéricas a todos los proveedores de \ninternet en busca de una solución.",
                    "El servicio técnico intentaba tranquilizar a cada persona, pero era inútil,\n nadie tenía idea de qué fue lo que sucedió",
                    "Pero mientras los humanos buscaban respuestas...",
                ]
            },
            {
                "imagen": "slide_07.png",
                "textos": [
                    "En algún lugar, más allá de las pantallas...",
                    "Más allá de los routers y los cables...",
                    "Mientras Jacked Man se encontraba realizando su patrullaje normal...",
                    "Una alerta comenzó a sonar.",
                    "La conexión mundial había caído."
                ]
            },
            {
                "imagen": "slide_08.png",
                "textos": [
                    "De pronto Jacked Man fué arrastrado fuera de la red",
                    "Directo hacia la ciudad digital, un lugar caótico, al que va a parar la forma\n etérea de cada usuario que se adentra en la internet",
                    "Justo ahora, éste era el único lugar a donde Jacked Man podía ir a parar ahora\n que la red se encontraba colapsada.",
                    "De pronto Jacked Man se encontraba barado en una ciudad digital ahora desértica, \nal no contar con usuarios que recorran sus calles"
                ]
            },
            {
                "imagen": "slide_09.png",
                "textos": [
                    "Afortunadamente, justo en el corazón de la ciudad digital, se encontraba el rack\ncentral mundial, una enorme estructura que se alza como un rascacielos.",
                    "A trabés de él, fluye el internet, si algo sucede ahí, entonces todo el internet\n se detiene y lo que se encuentre en la red, va a parar a la ciudad,\n era esa la razón por la que él se encontraba en ese lugar",
                    "Si algo salió muy mal, entonces ese debía ser el origen del problema",
                    "A compaña a Jacked Man en su misión de restaurar la conexión a internet",
                    "Recablea el rack, vence a los enemigos que tomaron el control y supera las trampas\n que pusieron por todo el lugar",
                    "Descubre que fué lo que sucedió ahí dentro y salva al mundo de la catástrofe que se avecina",
                    "El tiempo es extremadamente limitado"
                    "Si fallas... se acabó, Jacked Man es la última esperanza de la humanidad",
                    "¿Podrá Jacked Man restaurar la conexión a internet antes de que la sociedad colpse?" 
                ]
            }            
        ]

        self.imagenes = []
        for slide in self.historia:
            img = pygame.image.load(
                os.path.join(BASE_DIR, "assets", "images", "slides", slide["imagen"])
            ).convert()
            self.imagenes.append(img)

        self.skip_img = pygame.image.load(
            os.path.join(BASE_DIR, "assets", "images", "HUD", "skip.png")
        ).convert_alpha()
        self.skip_img = pygame.transform.scale(self.skip_img, (300, 200))

        self.siguiente_img = pygame.image.load(
            os.path.join(BASE_DIR, "assets", "images", "HUD", "siguiente.png")
        ).convert_alpha()
        self.siguiente_img = pygame.transform.scale(self.siguiente_img, (300, 200))

    def _avanzar(self, indice_slide, indice_texto):
        textos = self.historia[indice_slide]["textos"]
        if indice_texto < len(textos) - 1:
            return indice_slide, indice_texto + 1, False
        else:
            siguiente = indice_slide + 1
            if siguiente >= len(self.historia):
                return None, None, None
            return siguiente, 0, False

    def ejecutar(self):
        indice_slide = 0
        indice_texto = 0
        reloj = pygame.time.Clock()

        try:
            pygame.mixer.music.load(MUSICA_INTRO)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

        animando = True
        tiempo_box = pygame.time.get_ticks()
        tiempo_typewriter = None
        texto_listo = False
        alpha_botones = 0
        tiempo_botones = None

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    return

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.stop()
                        return

                    if event.key == pygame.K_RETURN:
                        if animando:
                            animando = False
                            texto_listo = True
                            alpha_botones = 255
                            resultado = self._avanzar(indice_slide, indice_texto)
                            if resultado[0] is None:
                                pygame.mixer.music.stop()
                                return
                            indice_slide = resultado[0]
                            indice_texto = resultado[1]
                        elif not texto_listo:
                            texto_listo = True
                        else:
                            resultado = self._avanzar(indice_slide, indice_texto)
                            if resultado[0] is None:
                                pygame.mixer.music.stop()
                                return
                            indice_slide = resultado[0]
                            indice_texto = resultado[1]

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if animando:
                        animando = False
                        texto_listo = True
                        alpha_botones = 255
                        resultado = self._avanzar(indice_slide, indice_texto)
                        if resultado[0] is None:
                            pygame.mixer.music.stop()
                            return
                        indice_slide = resultado[0]
                        indice_texto = resultado[1]
                    elif alpha_botones >= 255:
                        resultado = self._avanzar(indice_slide, indice_texto)
                        if resultado[0] is None:
                            pygame.mixer.music.stop()
                            return
                        indice_slide = resultado[0]
                        indice_texto = resultado[1]

            ahora = pygame.time.get_ticks()

            imagen_actual = pygame.transform.scale(
                self.imagenes[indice_slide],
                (self.ancho, self.alto)
            )
            self.pantalla.blit(imagen_actual, (0, 0))

            if animando:
                transcurrido_box = ahora - tiempo_box
                t_box = min(1.0, transcurrido_box / self.DURACION_BOX)
                t_box_eased = ease_out_cubic(t_box)

                desplazamiento = int(self.ALTURA_CAJA * (1 - t_box_eased))
                y_caja = self.alto - desplazamiento

                caja_surf = pygame.Surface((self.ancho, self.ALTURA_CAJA), pygame.SRCALPHA)
                caja_surf.fill((0, 0, 0, 180))
                self.pantalla.blit(caja_surf, (0, y_caja))

                if t_box >= 0.8 and tiempo_typewriter is None:
                    tiempo_typewriter = ahora

                texto_actual = self.historia[0]["textos"][0]

                if tiempo_typewriter is not None and not texto_listo:
                    transcurrido_tw = ahora - tiempo_typewriter
                    caracteres = int(transcurrido_tw / self.VELOCIDAD_TEXTO)
                    caracteres = min(caracteres, len(texto_actual))
                    texto_visible = texto_actual[:caracteres]

                    if caracteres >= len(texto_actual):
                        texto_listo = True

                    lineas = texto_visible.split("\n")
                    altura_linea = self.fuente.get_height() + 10
                    altura_total = len(lineas) * altura_linea
                    y_texto = self.alto - (self.ALTURA_CAJA // 2) - (altura_total // 2)

                    for i, linea in enumerate(lineas):
                        render = self.fuente.render(linea, True, (255, 255, 255))
                        rect = render.get_rect(center=(self.ancho // 2, y_texto + i * altura_linea))
                        self.pantalla.blit(render, rect)

                if texto_listo:
                    if tiempo_botones is None:
                        tiempo_botones = ahora

                if tiempo_botones is not None:
                    fade_t = min(1.0, (ahora - tiempo_botones) / self.DURACION_FADE_BOTONES)
                    alpha_botones = int(255 * ease_out_cubic(fade_t))

                if t_box >= 1.0 and texto_listo:
                    animando = False

                if alpha_botones > 0:
                    skip = self.skip_img.copy()
                    skip.set_alpha(alpha_botones)
                    self.pantalla.blit(skip, (20, 20))

                    sig = self.siguiente_img.copy()
                    sig.set_alpha(alpha_botones)
                    self.pantalla.blit(sig, (self.ancho - sig.get_width() - 20, 20))

            else:
                caja_surf = pygame.Surface((self.ancho, self.ALTURA_CAJA), pygame.SRCALPHA)
                caja_surf.fill((0, 0, 0, 180))
                self.pantalla.blit(caja_surf, (0, self.alto - self.ALTURA_CAJA))

                texto_actual = self.historia[indice_slide]["textos"][indice_texto]

                lineas = texto_actual.split("\n")
                altura_linea = self.fuente.get_height() + 10
                altura_total = len(lineas) * altura_linea
                y_texto = self.alto - (self.ALTURA_CAJA // 2) - (altura_total // 2)

                for i, linea in enumerate(lineas):
                    render = self.fuente.render(linea, True, (255, 255, 255))
                    rect = render.get_rect(center=(self.ancho // 2, y_texto + i * altura_linea))
                    self.pantalla.blit(render, rect)

                self.pantalla.blit(self.skip_img, (20, 20))
                self.pantalla.blit(
                    self.siguiente_img,
                    (self.ancho - self.siguiente_img.get_width() - 20, 20)
                )

            pygame.display.flip()
            reloj.tick(60)
