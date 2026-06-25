import pygame
import random
import os
from config import BASE_DIR


TAM_BLOQUE = 14
DURACION = 1500


class BloquePaquete:

    def __init__(self, gx, gy, menu_surf, slide_surf, ancho, alto):
        self.gx = gx
        self.gy = gy
        self.x = float(gx * TAM_BLOQUE)
        self.y = float(gy * TAM_BLOQUE)
        self.origen_x = self.x
        self.origen_y = self.y

        sx = min(gx * TAM_BLOQUE, slide_surf.get_width() - TAM_BLOQUE)
        sy = min(gy * TAM_BLOQUE, slide_surf.get_height() - TAM_BLOQUE)
        sx = max(0, sx)
        sy = max(0, sy)

        sw = min(TAM_BLOQUE, slide_surf.get_width() - sx)
        sh = min(TAM_BLOQUE, slide_surf.get_height() - sy)
        sw = max(1, sw)
        sh = max(1, sh)

        self.slide_recorte = slide_surf.subsurface(
            pygame.Rect(sx, sy, sw, sh)
        ).copy()

        mx = min(gx * TAM_BLOQUE, menu_surf.get_width() - TAM_BLOQUE)
        my = min(gy * TAM_BLOQUE, menu_surf.get_height() - TAM_BLOQUE)
        mx = max(0, mx)
        my = max(0, my)

        mw = min(TAM_BLOQUE, menu_surf.get_width() - mx)
        mh = min(TAM_BLOQUE, menu_surf.get_height() - my)
        mw = max(1, mw)
        mh = max(1, mh)

        self.menu_recorte = menu_surf.subsurface(
            pygame.Rect(mx, my, mw, mh)
        ).copy()

        self.estado = "normal"
        self.vel_x = 0.0
        self.timer = 0
        self.retraso = 0
        self.alpha = 255
        self.glitch_offset = 0
        self.perdido = False
        self.rastro_alpha = 0

        r = random.random()
        if r < 0.12:
            self.estado = "congelado"
            self.timer = random.randint(8, 25)
        elif r < 0.28:
            self.estado = "retrasado"
            self.retraso = random.randint(10, 40)
            self.timer = self.retraso
        elif r < 0.50:
            self.estado = "perdido"
            self.vel_x = random.uniform(10, 25)
            self.perdido = True
        else:
            self.estado = "viajando"
            self.vel_x = random.uniform(12, 30)

    def actualizar(self):
        if self.estado == "normal":
            self.estado = "viajando"
            self.vel_x = random.uniform(12, 30)

        elif self.estado == "congelado":
            self.timer -= 1
            if self.timer <= 0:
                self.estado = "viajando"
                self.vel_x = random.uniform(12, 30)

        elif self.estado == "retrasado":
            self.timer -= 1
            if self.timer <= 0:
                self.estado = "viajando"
                self.vel_x = random.uniform(12, 30)

        elif self.estado == "viajando":
            self.x += self.vel_x
            if random.random() < 0.015 and not self.perdido:
                self.estado = "perdido"
                self.perdido = True
                self.vel_x = random.uniform(10, 25)

        elif self.estado == "perdido":
            self.x += self.vel_x
            self.rastro_alpha = min(255, self.rastro_alpha + 15)

        elif self.estado == "llego":
            self.alpha = max(0, self.alpha - 12)

    def dibujar(self, pantalla):
        if self.estado == "congelado" and self.timer > 0:
            pantalla.blit(self.menu_recorte, (int(self.origen_x), int(self.origen_y)))
            return

        if self.estado == "retrasado" and self.timer > 0:
            return

        if self.estado in ("viajando", "perdido") and self.x < pantalla.get_width() + TAM_BLOQUE:
            if self.perdido and self.rastro_alpha > 0:
                rastro = pygame.Surface((TAM_BLOQUE, TAM_BLOQUE), pygame.SRCALPHA)
                rastro.fill((140, 40, 220, min(80, self.rastro_alpha)))
                pantalla.blit(rastro, (int(self.x) - 3, int(self.y)))

            recorte = self.menu_recorte.copy()
            recorte.set_alpha(self.alpha)
            pantalla.blit(recorte, (int(self.x), int(self.y)))

            if random.random() < 0.1:
                self.glitch_offset = random.randint(-3, 3)
            else:
                self.glitch_offset = 0

        if self.estado == "llego" and self.alpha > 0:
            recorte = self.slide_recorte.copy()
            recorte.set_alpha(255 - self.alpha)
            pantalla.blit(recorte, (int(self.origen_x), int(self.origen_y)))


class TransicionAHistoria:

    def __init__(self, pantalla, ancho=None, alto=None):
        self.pantalla = pantalla
        self.ancho = pantalla.get_width() if ancho is None else ancho
        self.alto = pantalla.get_height() if alto is None else alto

    def ejecutar(self):
        menu_capture = self.pantalla.copy()

        slide_path = os.path.join(
            BASE_DIR, "assets", "images", "slides", "slide_01.png"
        )
        slide_img = pygame.image.load(slide_path).convert()
        slide_img = pygame.transform.scale(slide_img, (self.ancho, self.alto))

        cols = (self.ancho // TAM_BLOQUE) + 1
        filas = (self.alto // TAM_BLOQUE) + 1

        bloques = []
        for gy in range(filas):
            for gx in range(cols):
                b = BloquePaquete(gx, gy, menu_capture, slide_img, self.ancho, self.alto)
                bloques.append(b)

        reloj = pygame.time.Clock()
        tiempo_inicio = pygame.time.get_ticks()
        total = len(bloques)
        llegados = 0

        while True:
            ahora = pygame.time.get_ticks()
            transcurrido = ahora - tiempo_inicio

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        return

            self.pantalla.blit(slide_img, (0, 0))

            for b in bloques:
                b.actualizar()

            for b in bloques:
                if b.estado == "perdido" and b.x > self.ancho + TAM_BLOQUE * 3:
                    b.estado = "llego"
                    b.alpha = 255

            for b in bloques:
                if b.estado == "viajando" and b.x > self.ancho + TAM_BLOQUE * 2:
                    b.estado = "llego"
                    b.alpha = 255

            llegados = sum(1 for b in bloques if b.estado == "llego")

            for b in bloques:
                b.dibujar(self.pantalla)

            if random.random() < 0.15:
                ly = random.randint(0, self.alto - 2)
                lw = random.randint(40, self.ancho // 2)
                lx = random.randint(0, self.ancho - lw)
                ls = pygame.Surface((lw, random.choice([1, 2])), pygame.SRCALPHA)
                ls.fill((0, 200, 255, random.randint(30, 70)))
                self.pantalla.blit(ls, (lx, ly))

            if random.random() < 0.08:
                sy = random.randint(0, self.alto - 1)
                ss = pygame.Surface((self.ancho, 1), pygame.SRCALPHA)
                ss.fill((255, 255, 255, 15))
                self.pantalla.blit(ss, (0, sy))

            if random.random() < 0.05:
                gx_offset = random.randint(-4, 4)
                slice_y = random.randint(0, self.alto - 20)
                slice_h = random.randint(4, 20)
                try:
                    slice_surf = self.pantalla.subsurface(
                        (0, slice_y, self.ancho, slice_h)
                    ).copy()
                    self.pantalla.blit(slice_surf, (gx_offset, slice_y))
                except:
                    pass

            progreso = transcurrido / DURACION

            if progreso >= 1.0:
                self.pantalla.blit(slide_img, (0, 0))
                pygame.display.flip()
                return

            pygame.display.flip()
            reloj.tick(60)
