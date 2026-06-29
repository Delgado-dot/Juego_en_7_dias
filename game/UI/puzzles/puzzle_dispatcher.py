"""
PuzzleDispatcher — wrapper que elige un tipo de puzle al azar.

Cada vez que se llega al rack B, se crea una nueva instancia con un puzzle
elegido aleatoriamente de los 3 tipos disponibles. La dificultad (1-5
estrellas) escala con el nivel del juego.
"""

import random

import pygame

from game.UI.puzzles.puzzle_base import dificultad_desde_nivel
from game.UI.puzzles.puzzle_cables import PuzzleCables
from game.UI.puzzles.puzzle_trafico import PuzzleTrafico
from game.UI.puzzles.puzzle_topologia import PuzzleTopologia


class PuzzleDispatcher:
    REGISTRO = {
        "cables":    PuzzleCables,
        "trafico":   PuzzleTrafico,
        "topologia": PuzzleTopologia,
    }

    def __init__(self, pantalla, ancho, alto, fuente_peq, nivel_idx, semilla=None):
        self.dificultad = dificultad_desde_nivel(nivel_idx)

        if semilla is None:
            semilla = pygame.time.get_ticks()

        rng = random.Random(semilla)
        tipo = rng.choice(list(self.REGISTRO.keys()))
        cls = self.REGISTRO[tipo]

        self._instancia = cls(pantalla, ancho, alto, fuente_peq, self.dificultad)

    def ejecutar(self):
        return self._instancia.ejecutar()
