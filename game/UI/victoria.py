import pygame

def dibujar_ganaste(pantalla, fuente, fuente_peq, negro, verde, ancho, alto, puntaje):
    pantalla.fill((220, 255, 220))
    texto = fuente.render("GANASTE", True, verde)
    rect = texto.get_rect(center=(ancho // 2, alto // 2 - 30))
    pantalla.blit(texto, rect)
    puntos = fuente_peq.render(f"Puntaje final: {puntaje}", True, negro)
    rect2 = puntos.get_rect(center=(ancho // 2, alto // 2 + 30))
    pantalla.blit(puntos, rect2)
    reiniciar = fuente_peq.render("Presiona R para reiniciar", True, negro)
    rect3 = reiniciar.get_rect(center=(ancho // 2, alto // 2 + 70))
    pantalla.blit(reiniciar, rect3)