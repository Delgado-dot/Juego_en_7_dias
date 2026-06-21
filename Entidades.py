import math
import pygame


class EntidadJuego:
    def __init__(self, tamano):
        self.tamano = tamano
        self.voltear = False
        self.indice_anim = 0
        self.ultimo_anim = pygame.time.get_ticks()
        self.forma = None
        self.imagen = None

    def avanzar_anim(self, total_fotogramas, retraso):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_anim >= retraso:
            self.ultimo_anim = ahora
            self.indice_anim = (self.indice_anim + 1) % total_fotogramas
            return True
        return False

    def dibujar(self, pantalla, cam_x=0, cam_y=0):
        if self.imagen is None:
            return

        img = pygame.transform.flip(self.imagen, self.voltear, False)
        OFFSET_Y = -27

        pantalla.blit(
            img,
            (
                self.forma.x - cam_x,
                self.forma.y - cam_y - OFFSET_Y
            )
        )


class Personaje(EntidadJuego):
    AJUSTE_PIES = 40
    ESCALA_VISUAL = 1.4

    @property
    def hitbox_pies(self):
        return pygame.Rect(
            self.forma.left,
            self.forma.bottom - self.alto_pies,
            self.forma.width,
            self.alto_pies
        )

    @property
    def hitbox_cabeza(self):
        return pygame.Rect(
            self.forma.left,
            self.forma.top,
            self.forma.width,
            self.alto_pies
        )

    def comprobar_suelo(self, plataformas):
        self.en_suelo = False

        pie = pygame.Rect(
            self.forma.left,
            self.forma.bottom,
            self.forma.width,
            2
        )

        for p in plataformas:
            if pie.colliderect(p):
                self.en_suelo = True
                break

    def __init__(self, x, y, tamano=40, ancho_hitbox=None, alto_hitbox=None, alto_pies=16):
        super().__init__(tamano)

        hb_w = ancho_hitbox if ancho_hitbox is not None else tamano
        hb_h = alto_hitbox if alto_hitbox is not None else tamano

        self.forma = pygame.Rect(x, y, hb_w, hb_h)
        self.alto_pies = alto_pies

        self.velocidad = 5
        self.gravedad = 0.6
        self.fuerza_salto = -18
        self.vel_x = 0
        self.vel_y = 0
        self.en_suelo = False
        self.tiene_cable = True
        self.radio_cable = 50
        self.vidas = 3
        self.vidas_max = 3
        self.puntaje = 0
        self.puntos_cable = 100
        self.chaquetas = 0

    def leer_teclas(self, teclas):
        self.vel_x = 0

        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            self.vel_x = -self.velocidad
            self.voltear = True

        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            self.vel_x = self.velocidad
            self.voltear = False

        if (teclas[pygame.K_w] or teclas[pygame.K_UP] or teclas[pygame.K_SPACE]) and self.en_suelo:
            self.vel_y = self.fuerza_salto
            self.en_suelo = False

    def aplicar_gravedad(self):
        if self.chaquetas > 0 and self.vel_y > 0:
            gravedad_real = self.gravedad * 0.3
        else:
            gravedad_real = self.gravedad

        self.vel_y += gravedad_real
        self.forma.y += int(self.vel_y)

    def mover_x(self, plataformas):
        self.forma.x += self.vel_x

        for p in plataformas:
            if self.forma.colliderect(p):
                if self.vel_x > 0:
                    self.forma.right = p.left
                elif self.vel_x < 0:
                    self.forma.left = p.right

    def colision_y(self, plataformas):
        if self.vel_y >= 0:
            pies = self.hitbox_pies

            for p in plataformas:
                if pies.colliderect(p):
                    self.forma.bottom = p.top
                    self.vel_y = 0
                    self.en_suelo = True
        else:
            cabeza = self.hitbox_cabeza

            for p in plataformas:
                if cabeza.colliderect(p):
                    self.forma.top = p.bottom
                    self.vel_y = 0

    def limitar_x(self, ancho):
        if self.forma.left < 0:
            self.forma.left = 0

        if self.forma.right > ancho:
            self.forma.right = ancho

    def actualizar(self, plataformas, ancho, alto_total):
        self.comprobar_suelo(plataformas)
        self.mover_x(plataformas)
        self.aplicar_gravedad()
        self.colision_y(plataformas)
        self.limitar_x(ancho)

        if self.forma.bottom > alto_total:
            self.forma.bottom = alto_total
            self.vel_y = 0
            self.en_suelo = True

    def distancia(self, punto):
        cx, cy = self.forma.center
        return ((cx - punto[0]) ** 2 + (cy - punto[1]) ** 2) ** 0.5

    def recuperar_cable(self, punto):
        if self.distancia(punto) < self.radio_cable:
            self.tiene_cable = True

    def cortar_cable(self):
        self.tiene_cable = False

    def perder_vida(self):
        self.vidas -= 1
        self.tiene_cable = False

        if self.chaquetas > 0:
            self.chaquetas -= 1

        return self.vidas > 0

    def reiniciar_pos(self, x, y):
        self.forma.x = x
        self.forma.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.tiene_cable = False

    def llego_meta(self, punto_b, radio=35):
        if not self.tiene_cable:
            return False

        return self.distancia(punto_b) < radio

    def dibujar(self, pantalla, cam_x=0, cam_y=0):
        if self.imagen is None:
            return

        img = pygame.transform.flip(self.imagen, self.voltear, False)

        nuevo_ancho = int(self.tamano * self.ESCALA_VISUAL)
        nuevo_alto = int(self.tamano * self.ESCALA_VISUAL)

        img = pygame.transform.scale(img, (nuevo_ancho, nuevo_alto))

        x = self.forma.centerx - nuevo_ancho // 2 - cam_x
        y = self.forma.bottom - nuevo_alto + self.AJUSTE_PIES - cam_y

        sombra_ancho = int(nuevo_ancho * 0.65)
        sombra_alto = 8

        sombra = pygame.Surface((sombra_ancho, sombra_alto), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra, (0, 0, 0, 120), sombra.get_rect())

        pantalla.blit(
            sombra,
            (
                self.forma.centerx - sombra_ancho // 2 - cam_x,
                self.forma.bottom - cam_y - 3
            )
        )

        pantalla.blit(img, (x, y))


class Trampa(EntidadJuego):
    def __init__(self, x, y, tamano=35, velocidad=3, min_x=0, max_x=100):
        super().__init__(tamano)

        self.x = float(x)
        self.y = float(y)
        self.velocidad = velocidad
        self.min_x = min_x
        self.max_x = max_x
        self.radio_corte = 25
        self.angulo = 0
        self.imagen_original = None

        try:
            self.imagen = pygame.image.load(
                "assets/images/sierracutre.png"
            ).convert_alpha()

            self.imagen = pygame.transform.scale(
                self.imagen,
                (tamano * 2, tamano * 2)
            )

            self.imagen_original = self.imagen

        except:
            self.imagen = None
            self.imagen_original = None

    def mover(self, plataformas):
        self.x += self.velocidad

        if self.x <= self.min_x or self.x >= self.max_x:
            self.velocidad *= -1
            self.voltear = self.velocidad < 0

        hitbox = pygame.Rect(
            self.x - self.tamano,
            int(self.y) - self.tamano,
            self.tamano * 2,
            self.tamano * 2
        )

        for p in plataformas:
            if hitbox.colliderect(p):
                if self.velocidad > 0:
                    self.x = p.left - self.tamano
                else:
                    self.x = p.right + self.tamano

                self.velocidad *= -1

    def corta_cable(self, origen, pos_jugador):
        ax, ay = origen
        bx, by = pos_jugador
        dx = bx - ax
        dy = by - ay

        if dx == 0 and dy == 0:
            return math.hypot(self.x - ax, self.y - ay) < self.radio_corte

        t = ((self.x - ax) * dx + (self.y - ay) * dy) / (dx * dx + dy * dy)
        t = max(0.0, min(1.0, t))

        cx = ax + t * dx
        cy = ay + t * dy

        return math.hypot(self.x - cx, self.y - cy) < self.radio_corte

    def dibujar(self, pantalla, cam_x=0, cam_y=0):
        if self.imagen_original is None:
            return

        self.angulo = (self.angulo + 8) % 360

        imagen_rotada = pygame.transform.rotate(
            self.imagen_original,
            self.angulo
        )

        rect = imagen_rotada.get_rect(
            center=(self.x - cam_x, self.y - cam_y)
        )

        pantalla.blit(imagen_rotada, rect.topleft)