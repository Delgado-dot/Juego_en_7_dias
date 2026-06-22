import pygame
import random
import math


class MenuEffects:

    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.particulas = []

        for _ in range(120):
            self.particulas.append({
                "x": random.randint(0, ancho),
                "y": random.randint(0, alto),
                "vx": random.uniform(-0.2, 0.2),
                "vy": random.uniform(0.2, 0.8),
                "radio": random.randint(1, 3),
                "alpha": random.randint(50, 180)
            })

        # --- EFECTOS DE TRANSICION ---
        self.matrix_activo = False
        self.matrix_digitos = []
        self.matrix_tiempo_inicio = 0
        self.matrix_duracion = 1500
        self.matrix_callback = None
        self.matrix_fondo = None

        self.cristal_activo = False
        self.cristal_grietas = []
        self.cristal_tiempo_inicio = 0
        self.cristal_duracion = 1200
        self.cristal_callback = None
        self.cristal_superficie = None

    # =================================
    # PARTICULAS
    # =================================
    def dibujar_particulas(self, pantalla):
        for p in self.particulas:
            p["x"] += p["vx"]
            p["y"] -= p["vy"]

            if p["y"] < -10:
                p["y"] = self.alto + 10
                p["x"] = random.randint(0, self.ancho)

            if p["x"] < -10:
                p["x"] = self.ancho + 10

            if p["x"] > self.ancho + 10:
                p["x"] = -10

            radio = p["radio"]
            surf = pygame.Surface((radio * 6, radio * 6), pygame.SRCALPHA)
            pygame.draw.circle(surf, (120, 220, 255, p["alpha"]), (radio * 3, radio * 3), radio + 1)
            pygame.draw.circle(surf, (255, 255, 255, p["alpha"]), (radio * 3, radio * 3), radio)
            pantalla.blit(surf, (p["x"], p["y"]))

    # =================================
    # PULSO
    # =================================
    def obtener_pulso(self, velocidad=0.005):
        tiempo = pygame.time.get_ticks()
        return (math.sin(tiempo * velocidad) + 1) / 2

    # =================================
    # TEXTO CON PULSO
    # =================================
    def render_texto_pulso(self, fuente, texto, color, escala_base=1, intensidad=0.08):
        pulso = self.obtener_pulso()
        escala = escala_base + pulso * intensidad
        render = fuente.render(texto, True, color)
        return pygame.transform.smoothscale(
            render,
            (int(render.get_width() * escala), int(render.get_height() * escala))
        )

    # =================================
    # PANEL GLASS
    # =================================
    def dibujar_panel_glass(self, pantalla, x, y, ancho, alto, alpha=120):
        panel = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        panel.fill((20, 25, 35, alpha))
        pantalla.blit(panel, (x, y))
        pygame.draw.rect(pantalla, (120, 180, 255), (x, y, ancho, alto), 2, border_radius=20)

    # =================================
    # BOTON SELECCIONADO
    # =================================
    def dibujar_glow_boton(self, pantalla, x, y, ancho, alto):
        pulso = self.obtener_pulso(0.006)
        alpha = 60 + int(pulso * 80)
        glow = pygame.Surface((ancho + 40, alto + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow, (0, 220, 255, alpha), (0, 0, ancho + 40, alto + 20), border_radius=20)
        pantalla.blit(glow, (x - 20, y - 10))
        pygame.draw.rect(pantalla, (0, 220, 255), (x, y, ancho, alto), 2, border_radius=15)

    # =================================
    # EFECTO 1: MATRIX (Ranking)
    # =================================
    def iniciar_matrix(self, callback):
        self.matrix_activo = True
        self.matrix_tiempo_inicio = pygame.time.get_ticks()
        self.matrix_callback = callback
        self.matrix_digitos = []
        self.matrix_fondo = None

        num_columnas = self.ancho // 18
        for col in range(num_columnas):
            x = col * 18 + random.randint(-3, 3)
            altura_col = random.randint(8, 20)
            velocidad = random.uniform(3, 7)
            for fila in range(altura_col):
                brillo = 255 if fila < 3 else max(50, 255 - fila * 15)
                self.matrix_digitos.append({
                    "x": x,
                    "y": -fila * 18 - random.randint(0, 300),
                    "valor": random.choice(["0", "1"]),
                    "velocidad": velocidad,
                    "alpha": brillo,
                    "tamano": 14 if fila < 2 else 12,
                    "es_cabeza": fila < 2
                })

    def actualizar_matrix(self, pantalla):
        if not self.matrix_activo:
            return False

        tiempo_actual = pygame.time.get_ticks()
        transcurrido = tiempo_actual - self.matrix_tiempo_inicio

        if self.matrix_fondo is None:
            self.matrix_fondo = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
            self.matrix_fondo.fill((0, 5, 20, 200))
        pantalla.blit(self.matrix_fondo, (0, 0))

        fuente_matrix = pygame.font.SysFont("Courier New", 14, bold=True)
        fuente_cabeza = pygame.font.SysFont("Courier New", 16, bold=True)

        for dig in self.matrix_digitos:
            dig["y"] += dig["velocidad"]
            if dig["y"] > self.alto + 30:
                dig["y"] = -30
                dig["valor"] = random.choice(["0", "1"])
                dig["alpha"] = 255

            if dig["es_cabeza"]:
                color = (200, 255, 255)
            else:
                intensidad = dig["alpha"]
                color = (0, min(255, intensidad + 50), intensidad)

            fuente_usar = fuente_cabeza if dig["es_cabeza"] else fuente_matrix
            texto = fuente_usar.render(dig["valor"], True, color)

            sombra = fuente_usar.render(dig["valor"], True, (0, 30, 50))
            pantalla.blit(sombra, (dig["x"] + 1, dig["y"] + 1))
            pantalla.blit(texto, (dig["x"], dig["y"]))

        if transcurrido > 400:
            chars_visibles = min(len("ACCEDIENDO A BASE DE DATOS..."), (transcurrido - 400) // 40)
            msg_visible = "ACCEDIENDO A BASE DE DATOS..."[:chars_visibles]
            if chars_visibles < len("ACCEDIENDO A BASE DE DATOS..."):
                msg_visible += "_"

            fuente_msg = pygame.font.SysFont("Courier New", 26, bold=True)
            render = fuente_msg.render(msg_visible, True, (0, 220, 255))
            rect = render.get_rect(center=(self.ancho // 2, self.alto // 2))

            for offset in range(1, 4):
                glow = fuente_msg.render(msg_visible, True, (0, 80, 120))
                pantalla.blit(glow, (rect.x + offset, rect.y + offset))

            if transcurrido % 600 < 300 and chars_visibles >= len("ACCEDIENDO A BASE DE DATOS..."):
                cursor = fuente_msg.render("_", True, (0, 220, 255))
                pantalla.blit(cursor, (rect.right + 5, rect.y))

            pantalla.blit(render, rect)

        if transcurrido > 200:
            barra_ancho = min(400, (transcurrido - 200) * 2)
            barra_x = self.ancho // 2 - 200
            barra_y = self.alto // 2 + 40
            pygame.draw.rect(pantalla, (0, 100, 150), (barra_x - 2, barra_y - 2, 404, 14), 1)
            pygame.draw.rect(pantalla, (0, 200, 255), (barra_x, barra_y, barra_ancho, 10))

        if transcurrido >= self.matrix_duracion:
            self.matrix_activo = False
            if self.matrix_callback:
                self.matrix_callback()
            return True

        return False

    # =================================
    # EFECTO 2: CRISTAL - SOLO GRIETAS (Salir)
    # =================================
    def iniciar_cristal(self, callback, pantalla_actual):
        """Solo grietas finas que aparecen, luego se cierra el juego"""
        self.cristal_activo = True
        self.cristal_tiempo_inicio = pygame.time.get_ticks()
        self.cristal_callback = callback
        self.cristal_superficie = pantalla_actual.copy()
        self.cristal_grietas = []

        num_grietas = 20
        for _ in range(num_grietas):
            x1 = random.randint(0, self.ancho)
            y1 = random.randint(0, self.alto)
            ang = random.uniform(0, 2 * math.pi)
            longitud = random.randint(80, 350)
            puntos = [(x1, y1)]
            x, y = x1, y1

            for _ in range(longitud // 10):
                x += math.cos(ang) * 10 + random.randint(-6, 6)
                y += math.sin(ang) * 10 + random.randint(-6, 6)
                puntos.append((x, y))
                if random.random() < 0.3:
                    ang_rama = ang + random.uniform(-1.0, 1.0)
                    xr = x + math.cos(ang_rama) * random.randint(15, 40)
                    yr = y + math.sin(ang_rama) * random.randint(15, 40)
                    self.cristal_grietas.append({
                        "puntos": [(x, y), (xr, yr)],
                        "alpha": 255,
                        "grosor": 1
                    })

            self.cristal_grietas.append({
                "puntos": puntos,
                "alpha": 255,
                "grosor": random.choice([1, 1, 1, 2])
            })

    def actualizar_cristal(self, pantalla):
        if not self.cristal_activo:
            return False

        tiempo_actual = pygame.time.get_ticks()
        transcurrido = tiempo_actual - self.cristal_tiempo_inicio

        pantalla.blit(self.cristal_superficie, (0, 0))

        progreso = min(1.0, transcurrido / (self.cristal_duracion * 0.7))

        for grieta in self.cristal_grietas:
            puntos_totales = len(grieta["puntos"])
            puntos_visibles = max(2, int(puntos_totales * progreso))
            visibles = grieta["puntos"][:puntos_visibles]

            if len(visibles) >= 2:
                pygame.draw.lines(pantalla, (240, 250, 255), False, visibles, grieta["grosor"])
                if grieta["grosor"] == 1:
                    pygame.draw.lines(pantalla, (100, 200, 255, 150), False,
                                    [(x + 1, y) for x, y in visibles], 1)

        if transcurrido > self.cristal_duracion * 0.5:
            shake = random.randint(-1, 1)
            pantalla.blit(self.cristal_superficie, (shake, shake))

        if transcurrido > self.cristal_duracion * 0.85:
            flash_alpha = int(255 * ((transcurrido - self.cristal_duracion * 0.85) / (self.cristal_duracion * 0.15)))
            flash = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
            flash.fill((255, 255, 255, min(255, flash_alpha)))
            pantalla.blit(flash, (0, 0))

        if transcurrido >= self.cristal_duracion:
            self.cristal_activo = False
            if self.cristal_callback:
                self.cristal_callback()
            return True

        return False

    # =================================
    # VERIFICAR SI ALGUN EFECTO ESTA ACTIVO
    # =================================
    def efecto_activo(self):
        return self.matrix_activo or self.cristal_activo