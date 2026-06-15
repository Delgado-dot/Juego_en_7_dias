import pygame

NIVELES = [
    {
        "tiempo": 120,
        "mapa": [
            "####################",
            "#                  #",
            "#                  #",
            "#    ####          #",
            "#                  #",
            "#          ####    #",
            "#       E          #",
            "#  ####       E    #",
            "#A             R   #",
            "####################"
        ],
    },
    {
        "tiempo": 90,
        "mapa": [
            "####################",
            "#                  #",
            "#              E   #",
            "#  ######          #",
            "#                  #",
            "#    E    ####     #",
            "#                  #",
            "####       E  ###  #",
            "#A             R   #",
            "####################"
        ],
    },
]

class Level:
    def __init__(self, ancho, alto, numero=0):
        self.ancho = ancho
        self.alto = alto
        self.numero = numero
        self.plataformas = []
        self.punto_a = (0, 0)
        self.punto_b = (0, 0)
        self.pos_enemigos = []
        self.tiempo_limite = NIVELES[numero]["tiempo"]
        self._cargar(NIVELES[numero]["mapa"])

    def _cargar(self, mapa):
        filas = len(mapa)
        columnas = len(mapa[0])
        tile_w = self.ancho // columnas
        tile_h = self.alto // filas

        for fila_idx, fila in enumerate(mapa):
            for col_idx, tile in enumerate(fila):
                x = col_idx * tile_w
                y = fila_idx * tile_h
                if tile == "#":
                    self.plataformas.append(pygame.Rect(x, y, tile_w, tile_h))
                elif tile == "A":
                    self.punto_a = (x + tile_w // 2, y + tile_h // 2)
                elif tile == "R":
                    self.punto_b = (x + tile_w // 2, y + tile_h // 2)
                elif tile == "E":
                    self.pos_enemigos.append((x + tile_w // 2, y + tile_h // 2))