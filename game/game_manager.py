import pygame
class GameManager:
    def __init__(self):
        self.vidas = None
        self.puntaje = 0
        self.nivel_actual = 1
        self.estado = "menu"
        
    def cambiar_estado(self, nuevo_estado):
        self.estado = nuevo_estado
        
    def perder_vida(self):
        if self.vidas is not None:
            self.vidas -= 1
            if self.vidas <= 0:
                self.cambiar_estado("game_over")
    
    def sumar_puntaje(self, cantidad_ganada):
        self.puntaje += cantidad_ganada
    
    def reiniciar(self):
        self.puntaje = 0
        self.nivel_actual = 1
        self.estado = "jugando"