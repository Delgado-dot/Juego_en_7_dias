import pygame
from config import *

tamaño_mapa = 60

NIVELES = [
    {
    "tiempo": 120,
    "fondo": SPRITE_FONDO_1,
    "mapa": [
        "####################",
        "#        R         #",
        "#   #####   #####  #",
        "#                  #",
        "#        #####     #",
        "#               C  #",
        "# #####        ### #",
        "#             E    #",
        "#       E          #",
        "#   #####          #",
        "#            ####  #",
        "#                  #",
        "#      J           #",
        "# #######          #",
        "#          E       #",
        "#A                 #",
        "####################"
    ]
},
{
    "tiempo": 150,
    "fondo": sprite_fondo_2,
    "mapa": [
        "####################",
        "#        R         #",
        "# #####     #####  #",
        "#                  #",
        "#      #######     #",
        "#  C               #",
        "# ####        #### #",
        "#                  #",
        "#          E       #",
        "#   #####          #",
        "#            ##### #",
        "#                  #",
        "#      J           #",
        "# #######          #",
        "#        E         #",
        "# #####            #",
        "#                  #",
        "#A                 #",
        "####################"
    ]
},
{
    "tiempo": 90,
    "fondo": sprite_fondo_3,
    "mapa": [
        "####################",
        "#        R         #",
        "#      #####       #",
        "#   #####    ##### #",
        "#      #####       #",
        "# #####      ##### #",
        "#      #####       #",
        "# #####      ##### #",
        "#      #####       #",
        "#          J       #",
        "# #####      ##### #",
        "#      #####       #",
        "# #####      ##### #",
        "#      #####       #",
        "#A                 #",
        "####################"
    ]
}

]

class Level:
    def __init__(self, ancho, alto, numero=0):
        self.ancho = ancho
        self.alto = alto
        self.numero = numero
        self.plataformas = []
        self.punto_a = (0, 0)
        self.punto_b = (0, 0)
        self.pos_trampas = []
        self.checkpoints = []
        self.ruta_fondo = NIVELES[numero]["fondo"]
        self.pos_chaqueta = None
        self.pos_chaqueta_original = None
        self.tiempo_limite = NIVELES[numero]["tiempo"]
        self.mapa_data = NIVELES[numero]["mapa"]
        self.filas = len(self.mapa_data)
        self.columnas = len(self.mapa_data[0])
        self.tile_w = ancho // self.columnas
        self.tile_h = tamaño_mapa
        self.alto_total = self.filas * self.tile_h
        self._cargar()

    def _cargar(self):
        for fila_idx, fila in enumerate(self.mapa_data):
            for col_idx, tile in enumerate(fila):
                x = col_idx * self.tile_w
                y = fila_idx * self.tile_h
                if tile == "#":
                    self.plataformas.append(pygame.Rect(x, y, self.tile_w, self.tile_h))
                elif tile == "A":
                    self.punto_a = (x + self.tile_w // 2, y + self.tile_h // 2)
                elif tile == "R":
                    self.punto_b = (x + self.tile_w // 2, y + self.tile_h // 2)
                elif tile == "E":
                    self.pos_trampas.append((x + self.tile_w // 2, y + self.tile_h // 2))
                elif tile == "C":
                    self.checkpoints.append((x + self.tile_w // 2, y + self.tile_h // 2))
                elif tile == "J":
                    self.pos_chaqueta = (x + self.tile_w // 2, y + self.tile_h // 2)
                    self.pos_chaqueta_original = self.pos_chaqueta