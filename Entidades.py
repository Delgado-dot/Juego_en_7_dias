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
        OFFSET_Y = -27
    
        if self.imagen is None:
        
            rect_temporal = pygame.Rect(self.forma.x - cam_x, self.forma.y - cam_y - OFFSET_Y, self.tamano, self.tamano)
            pygame.draw.rect(pantalla, (255, 0, 0), rect_temporal)
            return

        img = pygame.transform.flip(self.imagen, self.voltear, False)
        pantalla.blit(
            img,
            (
                self.forma.x - cam_x,
                self.forma.y - cam_y - OFFSET_Y
                ) )

class Personaje(EntidadJuego):
    AJUSTE_PIES = 40
    ESCALA_VISUAL = 1.4

    def obtener_hitbox_pies(self):
        return pygame.Rect(
            self.forma.left,
            self.forma.bottom - self.alto_pies,
            self.forma.width,
            self.alto_pies
        )

    def obtener_hitbox_cabeza(self):
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
        self.chaqueta_cohete = False
        self.modo_cohete = False
        self.energia_cohete = 0
        self.max_energia_cohete = 100
        self.cohete_tiempo = 0
        self.duracion_cohete = 1500
        self.particulas = []
        self.generar_particulas = False

    def spawn_particula(self):
        x = self.forma.centerx + (5 if not self.voltear else -5)
        y = self.forma.centery

        self.particulas.append([
            x, y,
            (255, 200, 50),  # color
            5,               # tamaño
            -self.vel_x * 0.3,
            1.5              # velocidad fade
        ])
    def actualizar_particulas(self, pantalla, cam_x, cam_y):
        for p in self.particulas[:]:
            p[0] += p[4]
            p[3] -= 0.1  # se encoge

            pygame.draw.circle(
                pantalla,
                p[2],
                (int(p[0] - cam_x), int(p[1] - cam_y)),
                max(1, int(p[3]))
            )

            if p[3] <= 0:
                self.particulas.remove(p)
    def leer_teclas(self, teclas):
        self.vel_x = 0

        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            self.vel_x = -self.velocidad
            self.voltear = True

        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            self.vel_x = self.velocidad
            self.voltear = False

        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            if self.en_suelo:
                self.vel_y = self.fuerza_salto
                self.en_suelo = False

    def aplicar_gravedad(self):
        if self.modo_cohete and self.chaqueta_cohete:
            if self.vel_y < 0:
                self.vel_y += self.gravedad * 0.1
            else:
                self.vel_y += self.gravedad * 0.5
        else:
            self.vel_y += self.gravedad

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
            pies = self.obtener_hitbox_pies()

            for p in plataformas:
                if pies.colliderect(p):
                    self.forma.bottom = p.top
                    self.vel_y = 0
                    self.en_suelo = True
        else:
            cabeza = self.obtener_hitbox_cabeza()

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

        if self.forma.top > alto_total + 200:
            return "cayo_fuera"

        return None
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

        pantalla.blit(img, (x, y))
        self.actualizar_particulas(pantalla, cam_x, cam_y)
    def activar_cohete(self, tecla_space):
        if not self.chaqueta_cohete:
            if self.modo_cohete:
                self.modo_cohete = False
                self.generar_particulas = False
            return

        if self.cohete_tiempo == 0 and tecla_space:
            self.cohete_tiempo = pygame.time.get_ticks()

        
        if self.cohete_tiempo > 0:
            ahora = pygame.time.get_ticks()
            if ahora - self.cohete_tiempo >= self.duracion_cohete:
                self.chaqueta_cohete = False
                self.modo_cohete = False
                self.generar_particulas = False
                self.cohete_tiempo = 0
                return

        
        if tecla_space:
            if not self.modo_cohete:
                
                self.vel_y = -14
                self.modo_cohete = True
            else:
                
                self.vel_y = -10
            self.generar_particulas = True
        else:
            self.modo_cohete = False
            self.generar_particulas = False

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

class SierraCae(EntidadJuego):
    VELOCIDAD_CAIDA = 4
    RADIO_ACTIVACION = 150

    def __init__(self, x, y, tamano=35):
        super().__init__(tamano)
        self.x = float(x)
        self.y = float(y)
        self.y_original = float(y)
        self.velocidad = 0
        self.activada = False
        self.activa = True
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

    def actualizar(self, jugador_rect, plataformas):
        if not self.activa:
            return

        if not self.activada:
            dist = math.hypot(
                jugador_rect.centerx - self.x,
                jugador_rect.centery - self.y
            )
            if dist < self.RADIO_ACTIVACION:
                self.activada = True
                self.velocidad = self.VELOCIDAD_CAIDA
            return

        self.velocidad += 0.5
        self.y += self.velocidad

        hitbox = pygame.Rect(
            self.x - self.tamano,
            self.y - self.tamano,
            self.tamano * 2,
            self.tamano * 2
        )

        for p in plataformas:
            if hitbox.colliderect(p):
                self.y = p.top - self.tamano
                self.activa = False
                return

    def corta_cable(self, origen, pos_jugador):
        if not self.activa:
            return False
        ax, ay = origen
        bx, by = pos_jugador
        dx = bx - ax
        dy = by - ay

        if dx == 0 and dy == 0:
            return math.hypot(self.x - ax, self.y - ay) < 25

        t = ((self.x - ax) * dx + (self.y - ay) * dy) / (dx * dx + dy * dy)
        t = max(0.0, min(1.0, t))

        cx = ax + t * dx
        cy = ay + t * dy

        return math.hypot(self.x - cx, self.y - cy) < 25

    def dibujar(self, pantalla, cam_x=0, cam_y=0):
        if not self.activa or self.imagen_original is None:
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

class PlataformaFantasma:
    def __init__(self, rect):
        self.rect = rect
        self.activada = False
        self.desaparecida = False
        self.alpha = 255
        self.tiempo_inicio = 0
    def pisar(self):
        if not self.activada:
            self.activada = True
            self.tiempo_inicio = pygame.time.get_ticks()
    def actualizar(self):
        if self.activada and not self.desaparecida:
            tiempo = pygame.time.get_ticks() - self.tiempo_inicio
            self.alpha = max(0, 255 - tiempo)
            if tiempo > 500:
                self.desaparecida = True

    def es_solida(self):
        return not self.desaparecida

class EnemigoPatrulla(EntidadJuego):
    def __init__(self, x, y, plataforma,
                 velocidad=2, tamano=40):

        super().__init__(tamano)

        self.forma = pygame.Rect(x, y, tamano, tamano)

        self.velocidad = velocidad

        self.min_x = plataforma.left
        self.max_x = plataforma.right - tamano
        self.plataforma = plataforma
        self.estado = "patrulla"
        self.rango_deteccion = 250
        self.velocidad_perseguir = 3
        self.ultimo_disparo = 0
        self.tiempo_recarga = 1500
        
        try:
            self.imagen = pygame.image.load(
                "assets/images/enemigo.png"
            ).convert_alpha()

            self.imagen = pygame.transform.scale(
                self.imagen,
                (tamano, tamano)
            )
        except:
            self.imagen = None

    def actualizar(self, jugador):
        distancia_x = abs(jugador.forma.centerx - self.forma.centerx)
        distancia_y = abs(jugador.forma.centery - self.forma.centery)

        if distancia_x < self.rango_deteccion and distancia_y < 100:
            self.estado = "perseguir"
        else:
            self.estado = "patrulla"

        if self.estado == "patrulla":
            self.forma.x += self.velocidad

            if self.forma.x <= self.min_x:
                self.forma.x = self.min_x
                self.velocidad *= -1
                self.voltear = False
            elif self.forma.x >= self.max_x:
                self.forma.x = self.max_x
                self.velocidad *= -1
                self.voltear = True

        elif self.estado == "perseguir":
            if jugador.forma.centerx < self.forma.centerx:
                self.forma.x -= self.velocidad_perseguir
                self.voltear = True
            else:
                self.forma.x += self.velocidad_perseguir
                self.voltear = False

            if self.forma.x < self.min_x:
                self.forma.x = self.min_x
            elif self.forma.x > self.max_x:
                self.forma.x = self.max_x

    def intentar_disparar(self, jugador, ahora):
        proyectiles = []
        distancia_x = jugador.forma.centerx - self.forma.centerx
        distancia_y = jugador.forma.centery - self.forma.centery
        distancia_total = (distancia_x ** 2 + distancia_y ** 2) ** 0.5

        if distancia_total < self.rango_deteccion and ahora - self.ultimo_disparo > self.tiempo_recarga:
            self.ultimo_disparo = ahora
            if distancia_x > 0:
                vel_x = 6
            else:
                vel_x = -6
            proyectiles.append(ProyectilEnemigo(
                self.forma.centerx,
                self.forma.centery,
                vel_x, 0
            ))

        return proyectiles

class ProyectilEnemigo:
    def __init__(self, x, y, vel_x=0, vel_y=0, tamano=8):
        self.forma = pygame.Rect(x, y, tamano, tamano)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.activo = True

    def actualizar(self):
        self.forma.x += self.vel_x
        self.forma.y += self.vel_y

    def dibujar(self, pantalla, cam_x, cam_y):
        pygame.draw.circle(
            pantalla,
            (255, 100, 0),
            (self.forma.centerx - cam_x, self.forma.centery - cam_y),
            self.forma.width // 2
        )
class EnemigoEmergente(EntidadJuego):

    def __init__(self, x, y, altura_subida=80,
                 velocidad=2, tamano=40):

        super().__init__(tamano)

        self.forma = pygame.Rect(
            x,
            y,
            tamano,
            tamano
        )

        self.y_base = y
        self.y_arriba = y - altura_subida

        self.velocidad = velocidad

        self.estado = "subiendo"

        self.tiempo_estado = pygame.time.get_ticks()

        try:
            self.imagen = pygame.image.load(
                "assets/images/planta.png"
            ).convert_alpha()

            self.imagen = pygame.transform.scale(
                self.imagen,
                (tamano, tamano)
            )

        except:
            self.imagen = None

    def actualizar(self):

        ahora = pygame.time.get_ticks()

        if self.estado == "subiendo":

            self.forma.y -= self.velocidad

            if self.forma.y <= self.y_arriba:
                self.forma.y = self.y_arriba
                self.estado = "espera_arriba"
                self.tiempo_estado = ahora

        elif self.estado == "espera_arriba":

            if ahora - self.tiempo_estado > 2000:
                self.estado = "bajando"

        elif self.estado == "bajando":

            self.forma.y += self.velocidad

            if self.forma.y >= self.y_base:
                self.forma.y = self.y_base
                self.estado = "espera_abajo"
                self.tiempo_estado = ahora

        elif self.estado == "espera_abajo":

            if ahora - self.tiempo_estado > 2000:
                self.estado = "subiendo"

    def toca_jugador(self, jugador):
        return self.forma.colliderect(jugador.forma)
    
class ChaquetaCohete:
    def __init__(self, x, y, duracion=2500):
        self.x = x
        self.y = y
        self.radio = 20
        self.activa = True

        # estado power-up
        self.recogida = False
        self.activada = False

        self.duracion = duracion
        self.tiempo_inicio = 0

        try:
            self.imagen = pygame.image.load(
                "assets/images/chaqueta_item.png"
            ).convert_alpha()
            self.imagen = pygame.transform.scale(self.imagen, (40, 40))
        except:
            self.imagen = None

    def recoger(self, jugador):
        if not self.activa:
            return

        dist = math.hypot(
            jugador.forma.centerx - self.x,
            jugador.forma.centery - self.y
        )

        if dist < self.radio + 20:
            self.recogida = True
            self.activa = False
            jugador.chaqueta_cohete = True  # nuevo estado en jugador

    def activar(self, jugador):
        if not jugador.chaqueta_cohete:
            return

        self.activada = True
        self.tiempo_inicio = pygame.time.get_ticks()

        # efecto inicial fuerte
        jugador.vel_y = -18  # impulso hacia arriba
        jugador.vel_x *= 1.5  # boost horizontal

    def actualizar(self, jugador):
        if not self.activada:
            return

        ahora = pygame.time.get_ticks()

    # SOLO impulso momentáneo (no afecta gravedad base)
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            jugador.vel_y = -12  # impulso hacia arriba fuerte
        else:
        # no forzamos caída lenta, dejamos la gravedad normal actuar
            pass

        if ahora - self.tiempo_inicio >= self.duracion:
            self.activada = False
            jugador.chaqueta_cohete = False
            jugador.cohete_activo = False

    def dibujar(self, pantalla, cam_x=0, cam_y=0):
        if not self.activa:
            return

        if self.imagen:
            pantalla.blit(
                self.imagen,
                (self.x - cam_x, self.y - cam_y)
            )
        else:
            pygame.draw.circle(
                pantalla,
                (255, 200, 0),
                (int(self.x - cam_x), int(self.y - cam_y)),
                self.radio
            )