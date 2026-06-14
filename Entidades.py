"""
Entidades.py
Archivo de entidades del juego. Aquí viven todas las clases de los objetos
que existen en el mundo:

  - EntidadJuego  → clase base (lo que todas comparten: forma, animación, draw)
  - Personaje     → el jugador (movimiento, salto, gravedad, cable)
  - Enemigo       → el triángulo que patrulla y puede cortar el cable

Para que el juego arranque solo hace falta:
    from Entidades import Personaje, Enemigo
"""

import math
import pygame


# ===========================================================================
# CLASE BASE
# ===========================================================================
class EntidadJuego:
    """
    Clase base para cualquier entidad dibujable del juego
    (jugador, enemigos, sabios). Centraliza lo que todas comparten:

      - tile y hitbox (`forma`)
      - sprite actual (`image`) y orientación (`flip`)
      - el contador de animación por frames (`anim_idx` / `last_anim`)
      - un `draw` básico (las subclases lo sobreescriben cuando
        necesitan efectos extra, como el aura o el parpadeo del jugador,
        o un anclaje distinto del sprite respecto a `forma`).
    """

    def __init__(self, tile):
        self.tile = tile
        self.flip = False

        # estado genérico de animación por frames
        self.anim_idx = 0
        self.last_anim = pygame.time.get_ticks()

        # cada subclase define su propio Rect e imagen inicial,
        # porque el spawn y el tamaño del sprite cambian bastante entre ellas
        self.forma = None
        self.image = None

    def _avanzar_indice(self, total_frames, delay):
        """
        Avanza self.anim_idx si ya pasó 'delay' ms desde el último cambio.
        Devuelve True si avanzó, para que el llamador actualice self.image.
        """
        ahora = pygame.time.get_ticks()
        if ahora - self.last_anim >= delay:
            self.last_anim = ahora
            self.anim_idx = (self.anim_idx + 1) % total_frames
            return True
        return False

    def draw(self, screen, camx=0, camy=0):
        if self.image is None:
            return
        img = pygame.transform.flip(self.image, self.flip, False)
        screen.blit(img, (self.forma.x - camx, self.forma.y - camy))


# ===========================================================================
# PERSONAJE (jugador)
# ===========================================================================
class Personaje(EntidadJuego):
    """
    Jugador controlable. Hereda de EntidadJuego lo visual (forma, draw).
    La parte lógica vive aquí:
      - movimiento horizontal (A/D o flechas)
      - salto (W, flecha arriba o espacio)
      - gravedad y colisión con plataformas
      - cable: lo tiene, lo puede perder, y lo recupera en el punto A
    """

    def __init__(self, x, y, tamano=40):
        super().__init__(tamano)
        # Rect de colisión. Como aún no hay sprite, uso un rect directamente.
        self.forma = pygame.Rect(x, y, tamano, tamano)

        # --- Constantes de movimiento ---
        self.velocidad = 5
        self.gravedad = 0.6
        self.fuerza_salto = -13

        # --- Estado de movimiento ---
        self.vel_x = 0
        self.vel_y = 0
        self.en_suelo = False

        # --- Estado del cable ---
        self.tiene_cable = True
        self.distancia_recuperar_cable = 35  # radio del punto A para recuperarlo

        # --- Estado de partida ---
        self.vidas = 3
        self.vidas_max = 3
        self.puntaje = 0
        self.puntos_por_cable = 100  # cuánto suma reconectar el cable

    # ------------------------------------------------------------------
    # Movimiento
    # ------------------------------------------------------------------
    def leer_input(self, teclas):
        """Lee el teclado y actualiza vel_x / vel_y antes del update."""
        self.vel_x = 0

        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            self.vel_x = -self.velocidad
            self.flip = True
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            self.vel_x = self.velocidad
            self.flip = False

        if (
            teclas[pygame.K_w]
            or teclas[pygame.K_UP]
            or teclas[pygame.K_SPACE]
        ) and self.en_suelo:
            self.vel_y = self.fuerza_salto
            self.en_suelo = False

    def aplicar_gravedad(self):
        self.vel_y += self.gravedad
        self.forma.y += self.vel_y

    def mover_horizontal(self, plataformas):
        self.forma.x += self.vel_x
        for plataforma in plataformas:
            if self.forma.colliderect(plataforma):
                if self.vel_x > 0:
                    self.forma.right = plataforma.left
                elif self.vel_x < 0:
                    self.forma.left = plataforma.right

    def resolver_colision_vertical(self, plataformas):
        """Colisión vertical separada de mover_horizontal para que el jugador
        no se 'atasque' en las esquinas. Marca en_suelo si toca algo arriba."""
        for plataforma in plataformas:
            if self.forma.colliderect(plataforma):
                if self.vel_y > 0:
                    self.forma.bottom = plataforma.top
                    self.vel_y = 0
                    self.en_suelo = True
                elif self.vel_y < 0:
                    self.forma.top = plataforma.bottom
                    self.vel_y = 0

    def limitar_a_pantalla(self, ancho, alto):
        if self.forma.left < 0:
            self.forma.left = 0
        if self.forma.right > ancho:
            self.forma.right = ancho
        if self.forma.top < 0:
            self.forma.top = 0
            self.vel_y = 0
        if self.forma.bottom > alto:
            self.forma.bottom = alto
            self.vel_y = 0
            self.en_suelo = True

    def update(self, plataformas, ancho, alto):
        """Update completo de un frame. Asume que ya llamaron leer_input()."""
        self.en_suelo = False  # se vuelve a poner True si toca suelo

        self.mover_horizontal(plataformas)
        self.aplicar_gravedad()
        self.resolver_colision_vertical(plataformas)
        self.limitar_a_pantalla(ancho, alto)

    # ------------------------------------------------------------------
    # Cable
    # ------------------------------------------------------------------
    def distancia_a_punto(self, punto):
        cx, cy = self.forma.center
        return ((cx - punto[0]) ** 2 + (cy - punto[1]) ** 2) ** 0.5

    def intentar_recuperar_cable(self, punto_a):
        """Si vuelve al punto A, recupera el cable automáticamente.
        No suma puntos (eso pasa al llegar al punto B)."""
        if self.distancia_a_punto(punto_a) < self.distancia_recuperar_cable:
            self.tiene_cable = True

    def cortar_cable(self):
        self.tiene_cable = False

    def perder_vida(self):
        """Lo llama el main cuando el jugador toca al enemigo.
        Devuelve True si todavía le quedan vidas, False si murió."""
        self.vidas -= 1
        self.tiene_cable = False
        return self.vidas > 0

    def reiniciar_posicion(self, x, y):
        """Manda al jugador de vuelta al punto A y le quita el cable."""
        self.forma.x = x
        self.forma.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.tiene_cable = False

    def llego_a_meta(self, punto_b, radio=35):
        """Devuelve True si está sobre el punto B Y todavía tiene cable."""
        if not self.tiene_cable:
            return False
        return self.distancia_a_punto(punto_b) < radio


# ===========================================================================
# ENEMIGO (triángulo que patrulla)
# ===========================================================================
class Enemigo(EntidadJuego):
    """
    Enemigo que se mueve horizontalmente entre min_x y max_x.
    Si el cable del jugador pasa a menos de 'radio_corte' de su posición,
    el método corta_cable() devuelve True para que el main lo corte.
    """

    def __init__(self, x, y, tamano=35, velocidad=3, min_x=180, max_x=560):
        super().__init__(tamano)
        # Trabajamos con (x, y) directamente, no con un Rect,
        # porque el enemigo se dibuja como triángulo.
        self.x = x
        self.y = y

        # --- Estado propio ---
        self.tamano = tamano
        self.velocidad = velocidad
        self.min_x = min_x
        self.max_x = max_x

        # Qué tan cerca del cable tiene que pasar para cortarlo
        self.radio_corte = 25

    # ------------------------------------------------------------------
    # Movimiento
    # ------------------------------------------------------------------
    def update(self):
        self.x += self.velocidad
        if self.x <= self.min_x or self.x >= self.max_x:
            self.velocidad *= -1
            # flip visual según el sentido
            self.flip = self.velocidad < 0

    # ------------------------------------------------------------------
    # Colisión con el cable
    # ------------------------------------------------------------------
    def _distancia_punto_a_segmento(self, px, py, ax, ay, bx, by):
        """Distancia mínima entre el punto (px,py) y el segmento (a)-(b)."""
        dx = bx - ax
        dy = by - ay
        if dx == 0 and dy == 0:
            return math.hypot(px - ax, py - ay)
        t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
        t = max(0.0, min(1.0, t))
        cx = ax + t * dx
        cy = ay + t * dy
        return math.hypot(px - cx, py - cy)

    def corta_cable(self, punto_a, jugador_pos):
        """Devuelve True si el cable queda dentro de radio_corte del enemigo."""
        ax, ay = punto_a
        bx, by = jugador_pos
        d = self._distancia_punto_a_segmento(self.x, self.y, ax, ay, bx, by)
        return d < self.radio_corte

    # ------------------------------------------------------------------
    # Dibujo
    # ------------------------------------------------------------------
    def draw(self, screen, camx=0, camy=0):
        # Triángulo isósceles con la punta hacia arriba
        puntos = [
            (self.x,                self.y - self.tamano),
            (self.x - self.tamano,  self.y + self.tamano),
            (self.x + self.tamano,  self.y + self.tamano),
        ]
        color = (160, 0, 200)  # MORADO
        pygame.draw.polygon(screen, color, puntos)
