import pygame
from config import *
from Entidades import *

tamaño_mapa = 70


NIVEL_DINAMICO_DESDE = 1


class PlataformaDinamica:

    ANCHO_MIN = 20
    VELOCIDAD_ENCOGER = 2
    VELOCIDAD_CRECER = 1

    def __init__(self, rect, vel_x=0, vel_y=0, rango_x=0, rango_y=0, encoger=False):
        self.rect_original = rect.copy()
        self.rect = rect.copy()

        self.vel_x = vel_x
        self.vel_y = vel_y
        self.rango_x = rango_x
        self.rango_y = rango_y
        self.encoger = encoger

        self._origen_x = float(rect.x)
        self._origen_y = float(rect.y)
        self._pos_x = float(rect.x)
        self._pos_y = float(rect.y)

        self._ancho_actual = float(rect.w)
        self._ancho_objetivo = float(rect.w)

    def actualizar(self, jugador_rect):

        if self.rango_x:
            self._pos_x += self.vel_x
            despl_x = self._pos_x - self._origen_x
            if abs(despl_x) >= self.rango_x:
                self.vel_x *= -1
            self.rect.x = int(self._pos_x)

        if self.rango_y:
            self._pos_y += self.vel_y
            despl_y = self._pos_y - self._origen_y
            if abs(despl_y) >= self.rango_y:
                self.vel_y *= -1
            self.rect.y = int(self._pos_y)

        if self.encoger:
            jugador_encima = (
                jugador_rect is not None
                and jugador_rect.bottom >= self.rect.top
                and jugador_rect.bottom <= self.rect.top + 12
                and jugador_rect.right > self.rect.left
                and jugador_rect.left < self.rect.right
            )

            if jugador_encima:
                self._ancho_actual = max(
                    self.ANCHO_MIN,
                    self._ancho_actual - self.VELOCIDAD_ENCOGER
                )
            else:
                self._ancho_actual = min(
                    float(self.rect_original.w),
                    self._ancho_actual + self.VELOCIDAD_CRECER
                )

            centro_x = self.rect.x + self.rect_original.w // 2
            self.rect.w = int(self._ancho_actual)
            self.rect.x = centro_x - self.rect.w // 2

    def obtener_colision(self):
        return self.rect


NIVELES = [

{
    "tiempo": 25,
    "mapa": [
        "####################",
        "$     VR           $",
        "$      # V         $",
        "$                  $",
        "$     #       #    $",
        "$        M         $",
        "$        ##  ##    $",
        "$     #            $",
        "$                  $",
        "$       #          $",
        "$      E           $",
        "$                  $",
        "$    #             $",
        "$                  $",
        "$A                 $",
        "##  EEEEEEEEEEEEEEE#"
    ]
},
{
    "tiempo": 60,
    "mapa": [
        "####################",
        "$        R      V  $",
        "$      #####       $",
        "$        V    E    $",
        "$   ####           $",
        "$      V      C    $",
        "$        #### #    $",
        "$  V               $",
        "$     #   #   E    $",
        "$                ##$",
        "$    ####    E     $",
        "$     E          ##$",
        "$      J   %%%%%   $",
        "$ # % #            $",
        "$   V      %###    $",
        "$A     E           $",
        "####################"
    ]
},

{
    "tiempo": 60,
    "mapa": [
          "####################",
        "$             R    $",
        "$          %####   $",
        "$          V       $",
        "$     %#%##        $",
        "$           E      $",
        "$ V  ####       V  $",
        "$          C       $",
        "$        E         $",
        "$        ##€#      $",
        "$                  $",
        "$    %%%#V    V    $",
        "$               J  $",
        "$           %#%    $",
        "$   ####      E    $",
        "$A                 $",
        "####################"
    ]
},

{
    "tiempo": 60,
    "mapa": [
        "####################",
        "$             R    $",
        "$          #####   $",
        "$          V       $",
        "$      ####        $",
        "$                  $",
        "$   ####           $",
        "$                  $",
        "$        E         $",
        "$        ####      $",
        "$                  $",
        "$    %%%#    V     $",
        "$       J          $",
        "$                  $",
        "$   ####      E    $",
        "$A                 $",
        "####################"
    ]
},

{
    "tiempo": 60,
    "mapa": [
        "####################",
        "$      R           $",
        "$   ##%##          $",
        "$             %#%% $",
        "$    E             $",
        "$       #%%%       $",
        "$    ####          $",
        "$  V           E   $",
        "$  E             E $",
        "$       ####       $",
        "$          V    V  $",
        "$  ##%%            $",
        "$         #J%      $",
        "$                  $",
        "$  V %%%#    E   # $",
        "$A                 $",
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
        self.pos_enemigos = []
        self.checkpoints = []
        self.plataformas_fantasma = []
        self.plataformas_dinamicas = []
        self.pos_sierras_cae = []
        self.paredes = []
        self.pos_checkpoints_o = []
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
        print("enemigos cargados:",self.pos_enemigos)
        if numero >= NIVEL_DINAMICO_DESDE:
            self._generar_dinamicas()

    def _cargar(self):
        for fila_idx, fila in enumerate(self.mapa_data):
            for col_idx, tile in enumerate(fila):
                x = col_idx * self.tile_w
                y = fila_idx * self.tile_h

                if tile == "#":
                    self.plataformas.append(
                        pygame.Rect(x, y, self.tile_w, self.tile_h)
                    )

                elif tile == "A":
                    self.punto_a = (
                        x + self.tile_w // 2,
                        y + self.tile_h // 2
                    )

                elif tile == "R":
                    self.punto_b = (
                        x + self.tile_w // 2,
                        y + self.tile_h // 2
                    )

                elif tile == "E":
                    self.pos_trampas.append(
                        (x + self.tile_w // 2, y + self.tile_h // 2)
                    )

                elif tile == "C":
                    self.checkpoints.append(
                        (x + self.tile_w // 2, y + self.tile_h // 2)
                    )

                elif tile == "J":
                    self.pos_chaqueta = (
                        x + self.tile_w // 2,
                        y + self.tile_h // 2
                    )
                    self.pos_chaqueta_original = self.pos_chaqueta

                elif tile == "$":
                    self.paredes.append(
                        pygame.Rect(x, y, self.tile_w, self.tile_h)
                    )
                elif tile == "%":
                    self.plataformas_fantasma.append(
                        PlataformaFantasma(pygame.Rect(x,y,self.tile_w,self.tile_h )))
                elif tile == "V":
                    self.pos_sierras_cae.append(
                        (x + self.tile_w // 2, y + self.tile_h // 2)
                    )
                elif tile == "M":
                    self.pos_enemigos.append(
                        (
                            x + self.tile_w // 2,
                            y + self.tile_h // 2))

    def _generar_dinamicas(self):
        import random
        rng = random.Random(self.numero * 7 + 13)

        internas = [
            p for p in self.plataformas
            if p.x > self.tile_w and p.right < self.ancho - self.tile_w
            and p.y > self.tile_h and p.bottom < self.alto_total - self.tile_h
        ]

        porcentaje = min(0.3 + (self.numero - NIVEL_DINAMICO_DESDE) * 0.15, 0.75)
        n_afectadas = max(2, int(len(internas) * porcentaje))
        seleccionadas = rng.sample(internas, min(n_afectadas, len(internas)))

        vel_base = 1.5 + (self.numero - NIVEL_DINAMICO_DESDE) * 0.5

        for i, p in enumerate(seleccionadas):
            tipo = i % 3

            if tipo == 0:
                dp = PlataformaDinamica(
                    p.copy(),
                    vel_x=vel_base * rng.choice([-1, 1]),
                    rango_x=int(self.tile_w * 2.5),
                    encoger=False
                )
            elif tipo == 1:
                dp = PlataformaDinamica(
                    p.copy(),
                    vel_y=vel_base * 0.6 * rng.choice([-1, 1]),
                    rango_y=int(self.tile_h * 1.5),
                    encoger=True
                )
            else:
                dp = PlataformaDinamica(
                    p.copy(),
                    vel_x=vel_base * rng.choice([-1, 1]),
                    rango_x=int(self.tile_w * 2),
                    encoger=True
                )

            self.plataformas.remove(p)
            self.plataformas_dinamicas.append(dp)