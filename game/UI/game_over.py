import pygame

def dibujar_game_over(pantalla, fuente, fuente_peq, negro, rojo, ancho, alto, puntaje):
    pantalla.fill((255, 220, 220))
    texto = fuente.render("GAME OVER", True, rojo)
    rect = texto.get_rect(center=(ancho // 2, alto // 2 - 30))
    pantalla.blit(texto, rect)
    puntos = fuente_peq.render(f"Puntaje final: {puntaje}", True, negro)
    rect2 = puntos.get_rect(center=(ancho // 2, alto // 2 + 30))
    pantalla.blit(puntos, rect2)
    reiniciar = fuente_peq.render("Presiona R para reiniciar", True, negro)
    rect3 = reiniciar.get_rect(center=(ancho // 2, alto // 2 + 70))
    pantalla.blit(reiniciar, rect3)