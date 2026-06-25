import pygame
import os
from config import BASE_DIR


class Historia:

    def __init__(self, pantalla, ancho, alto):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto

        try:
            self.fuente = pygame.font.Font(
                os.path.join(BASE_DIR, "assets", "fonts", "PressStart2P-Regular.ttf"),
                24
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
                    "Protector del internet y héroe anónimo de las redes, Jacked Man combate\nhackers, corrige errores, protege las conexiones y se asegura de que los datos\nlleguen a donde deben llegar. Gracias a él, millones de personas pueden navegar\npor internet ignorando completamente su existencia.",
                    "Porque mientras el mundo continúa con su vida cotidiana, Jacked Man\ntrabaja en silencio."
                ]
            },
            {
                "imagen": "slide_03.png",
                "textos": [
                    "Un día, la red de una importante empresa colapsó por completo.",
                    "Nadie podía navegar por internet.",
                    "Los archivos dejaron de compartirse.",
                    "Los sistemas dejaron de responder.",
                    "Y la comunicación con una sucursal remota se perdió por completo.",
                    "El caos no tardó en apoderarse de la oficina."
                ]
            },
            {
                "imagen": "slide_04.png",
                "textos": [
                    "El jefe llamó de inmediato al proveedor de internet, exigiendo una\nsolución. Le aseguraron que el problema sería atendido lo antes posible.",
                    "Pero mientras los humanos buscaban respuestas..."
                ]
            },
            {
                "imagen": "slide_05.png",
                "textos": [
                    "En algún lugar, más allá de las pantallas...",
                    "Más allá de los routers y los cables...",
                    "Una alarma comenzó a sonar.",
                    "Una conexión había caído."
                ]
            },
            {
                "imagen": "slide_06.png",
                "textos": [
                    "Sin perder un segundo, Jacked Man se dirigió al origen del problema: el rack\nprincipal de la empresa."
                ]
            },
            {
                "imagen": "slide_07.png",
                "textos": [
                    "Adéntrate en el complejo mundo de las redes a través de los ojos\nde Jacked Man. Explora la loca infraestructura digital del rack, restablece la\nconectividad y salva el día.",
                    "¿Podrá Jacked Man recablear el rack y restaurar la conexión a internet?"
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

    def ejecutar(self):
        indice_slide = 0
        indice_texto = 0
        reloj = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return

                    if event.key == pygame.K_RETURN:
                        textos_actuales = self.historia[indice_slide]["textos"]

                        if indice_texto < len(textos_actuales) - 1:
                            indice_texto += 1
                        else:
                            indice_slide += 1
                            indice_texto = 0

                            if indice_slide >= len(self.historia):
                                return

            imagen_actual = pygame.transform.scale(
                self.imagenes[indice_slide],
                (self.ancho, self.alto)
            )
            self.pantalla.blit(imagen_actual, (0, 0))

            ALTURA_CAJA = 220

            caja = pygame.Surface((self.ancho, ALTURA_CAJA))
            caja.set_alpha(180)
            caja.fill((0, 0, 0))
            self.pantalla.blit(caja, (0, self.alto - ALTURA_CAJA))

            texto_actual = self.historia[indice_slide]["textos"][indice_texto]
            lineas = texto_actual.split("\n")

            altura_linea = self.fuente.get_height() + 10
            altura_total = len(lineas) * altura_linea
            y_inicial = self.alto - (ALTURA_CAJA // 2) - (altura_total // 2)

            for i, linea in enumerate(lineas):
                texto_surface = self.fuente.render(linea, True, (255, 255, 255))
                texto_rect = texto_surface.get_rect(
                    center=(self.ancho // 2, y_inicial + i * altura_linea)
                )
                self.pantalla.blit(texto_surface, texto_rect)

            self.pantalla.blit(self.skip_img, (20, 20))
            self.pantalla.blit(
                self.siguiente_img,
                (self.ancho - self.siguiente_img.get_width() - 20, 20)
            )

            pygame.display.flip()
            reloj.tick(60)
