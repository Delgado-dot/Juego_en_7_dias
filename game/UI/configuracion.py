import pygame
import math


DEFAULTS = {
    "vol_musica": 0.5,
    "vol_efectos": 0.7,
    "pantalla_completa": True,
    "particulas": True,
}


class PanelConfiguracion:

    ANCHO_PANEL = 540
    ALTO_PANEL = 620

    COLOR_FONDO = (15, 20, 35, 180)
    COLOR_BORDE = (0, 220, 255)
    COLOR_TEXTO = (230, 230, 230)
    COLOR_TEXTO_DIM = (170, 170, 180)
    COLOR_ACENTO = (120, 230, 255)
    COLOR_SLIDER_LINEA = (60, 80, 110)
    COLOR_SLIDER_ACTIVO = (0, 220, 255)
    COLOR_SLIDER_KNOB = (255, 255, 255)
    COLOR_TOGGLE_ON = (0, 220, 130)
    COLOR_TOGGLE_OFF = (110, 110, 130)
    COLOR_BOTON = (50, 60, 90)
    COLOR_BOTON_HOVER = (80, 100, 150)
    COLOR_X = (255, 80, 80)

    def __init__(self, pantalla, ancho, alto, config):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.config = config

        for k, v in DEFAULTS.items():
            self.config.setdefault(k, v)

        self._snapshot = dict(self.config)

        try:
            self.fuente_titulo = pygame.font.Font(
                "assets/fonts/PressStart2P-Regular.ttf", 26
            )
            self.fuente_etiqueta = pygame.font.Font(
                "assets/fonts/PressStart2P-Regular.ttf", 16
            )
            self.fuente_valor = pygame.font.Font(
                "assets/fonts/PressStart2P-Regular.ttf", 14
            )
            self.fuente_peq = pygame.font.Font(
                "assets/fonts/PressStart2P-Regular.ttf", 10
            )
        except Exception:
            self.fuente_titulo = pygame.font.SysFont("Arial", 26, bold=True)
            self.fuente_etiqueta = pygame.font.SysFont("Arial", 16, bold=True)
            self.fuente_valor = pygame.font.SysFont("Arial", 14)
            self.fuente_peq = pygame.font.SysFont("Arial", 10)

        self._calcular_rect_panel()

        self._slider_arrastrando = None

    def _calcular_rect_panel(self):
        alto_panel = min(self.ALTO_PANEL, int(self.alto * 0.9))
        ancho_panel = min(self.ANCHO_PANEL, int(self.ancho * 0.9))
        self.rect_panel = pygame.Rect(
            self.ancho // 2 - ancho_panel // 2,
            self.alto // 2 - alto_panel // 2,
            ancho_panel,
            alto_panel,
        )
        self._ancho_panel_efectivo = ancho_panel
        self._alto_panel_efectivo = alto_panel

    def actualizar_dimensiones(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self._calcular_rect_panel()

    def dibujar_panel(self, pantalla):
        mouse = pygame.mouse.get_pos()

        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 90))
        pantalla.blit(overlay, (0, 0))

        aw = self._ancho_panel_efectivo
        ah = self._alto_panel_efectivo
        panel = pygame.Surface((aw, ah), pygame.SRCALPHA)
        panel.fill(self.COLOR_FONDO)

        for grosor, alpha in [(6, 30), (2, 220)]:
            borde = pygame.Surface(
                (aw + grosor * 2, ah + grosor * 2), pygame.SRCALPHA,
            )
            pygame.draw.rect(
                borde,
                (self.COLOR_BORDE[0], self.COLOR_BORDE[1], self.COLOR_BORDE[2], alpha),
                (grosor, grosor, aw, ah),
                grosor,
                border_radius=18,
            )
            pantalla.blit(
                borde,
                (self.rect_panel.x - grosor, self.rect_panel.y - grosor),
            )

        pantalla.blit(panel, self.rect_panel.topleft)

        pulso = (math.sin(pygame.time.get_ticks() * 0.004) + 1) / 2
        escala = 1.0 + pulso * 0.05
        titulo_base = self.fuente_titulo.render(
            "CONFIGURACION", True, self.COLOR_ACENTO
        )
        tw, th = titulo_base.get_size()
        titulo = pygame.transform.smoothscale(
            titulo_base, (int(tw * escala), int(th * escala))
        )
        pantalla.blit(
            titulo,
            titulo.get_rect(
                center=(self.rect_panel.centerx, self.rect_panel.y + 38)
            ),
        )

        ly = self.rect_panel.y + 70
        pygame.draw.line(
            pantalla,
            (0, 220, 255),
            (self.rect_panel.x + 60, ly),
            (self.rect_panel.right - 60, ly),
            2,
        )

        self.rect_cerrar = pygame.Rect(
            self.rect_panel.right - 36, self.rect_panel.y + 12, 24, 24
        )
        hover_x = self.rect_cerrar.collidepoint(mouse)
        color_x = (255, 120, 120) if hover_x else self.COLOR_X
        pygame.draw.circle(
            pantalla,
            (40, 20, 25, 200),
            self.rect_cerrar.center,
            13,
        )
        pygame.draw.circle(
            pantalla, color_x, self.rect_cerrar.center, 13, 2
        )
        cx, cy = self.rect_cerrar.center
        pygame.draw.line(
            pantalla, color_x, (cx - 6, cy - 6), (cx + 6, cy + 6), 2
        )
        pygame.draw.line(
            pantalla, color_x, (cx + 6, cy - 6), (cx - 6, cy + 6), 2
        )

        contenido_x = self.rect_panel.x + 40
        contenido_y = self.rect_panel.y + 100
        ancho_util = self.ANCHO_PANEL - 80

        contenido_y = self._dibujar_slider(
            pantalla, contenido_x, contenido_y, ancho_util,
            "MUSICA", self.config["vol_musica"],
            clave="vol_musica",
        )

        contenido_y = self._dibujar_slider(
            pantalla, contenido_x, contenido_y + 14, ancho_util,
            "EFECTOS", self.config["vol_efectos"],
            clave="vol_efectos",
        )

        contenido_y += 22
        pygame.draw.line(
            pantalla, (60, 70, 90),
            (contenido_x, contenido_y),
            (contenido_x + ancho_util, contenido_y), 1,
        )
        contenido_y += 18

        contenido_y = self._dibujar_toggle(
            pantalla, contenido_x, contenido_y, ancho_util,
            "PANTALLA COMPLETA", self.config["pantalla_completa"],
            clave="pantalla_completa",
        )

        contenido_y = self._dibujar_toggle(
            pantalla, contenido_x, contenido_y + 10, ancho_util,
            "PARTICULAS", self.config["particulas"],
            clave="particulas",
        )

        contenido_y += 20

        contenido_y = self._dibujar_boton(
            pantalla, contenido_x, contenido_y, ancho_util,
            "RESTABLECER VALORES", accion="restablecer",
            alto=32,
        )

        contenido_y += 12

        gap = 12
        ancho_boton = (ancho_util - gap) // 2
        contenido_y = self._dibujar_boton(
            pantalla, contenido_x, contenido_y, ancho_boton,
            "CANCELAR", accion="cancelar",
            color_borde=(180, 80, 80), color_texto=(255, 150, 150),
        )
        contenido_y_guardar = self._dibujar_boton(
            pantalla, contenido_x + ancho_boton + gap, contenido_y - 40,
            ancho_boton, "GUARDAR", accion="guardar",
            color_borde=(0, 220, 130), color_texto=(0, 255, 160),
        )

        hint = self.fuente_peq.render(
            "Guardar aplica los cambios  |  Cancelar descarta",
            True, (140, 140, 160),
        )
        pantalla.blit(
            hint,
            hint.get_rect(
                center=(
                    self.rect_panel.centerx,
                    self.rect_panel.bottom - 14,
                )
            ),
        )

    def _dibujar_slider(self, pantalla, x, y, ancho, etiqueta, valor,
                        clave, max_valor=1.0):
        render_etq = self.fuente_etiqueta.render(etiqueta, True, self.COLOR_TEXTO)
        pantalla.blit(render_etq, (x, y))

        texto_val = f"{int(valor * 100)}%"
        render_val = self.fuente_valor.render(texto_val, True, self.COLOR_ACENTO)
        pantalla.blit(
            render_val,
            render_val.get_rect(topright=(x + ancho, y + 2)),
        )

        ly = y + 36
        ancho_linea = ancho - 20
        lx = x + 10
        pygame.draw.rect(
            pantalla, self.COLOR_SLIDER_LINEA,
            (lx, ly - 3, ancho_linea, 6), border_radius=3,
        )
        ancho_valor = int(ancho_linea * valor)
        pygame.draw.rect(
            pantalla, self.COLOR_SLIDER_ACTIVO,
            (lx, ly - 3, ancho_valor, 6), border_radius=3,
        )
        kx = lx + ancho_valor
        ky = ly
        pygame.draw.circle(pantalla, (20, 30, 50), (kx, ky), 11)
        pygame.draw.circle(pantalla, self.COLOR_SLIDER_KNOB, (kx, ky), 9)
        pygame.draw.circle(pantalla, self.COLOR_SLIDER_ACTIVO, (kx, ky), 9, 2)

        self._rects_sliders = getattr(self, "_rects_sliders", {})
        self._rects_sliders[clave] = pygame.Rect(
            lx, ly - 12, ancho_linea, 24
        )
        return ly + 18

    def _dibujar_toggle(self, pantalla, x, y, ancho, etiqueta, activo, clave):
        render_etq = self.fuente_etiqueta.render(etiqueta, True, self.COLOR_TEXTO)
        pantalla.blit(render_etq, (x, y + 4))

        pill_w, pill_h = 68, 32
        pill_x = x + ancho - pill_w
        pill_y = y
        color_pill = self.COLOR_TOGGLE_ON if activo else self.COLOR_TOGGLE_OFF

        sombra = pygame.Surface((pill_w + 4, pill_h + 4), pygame.SRCALPHA)
        pygame.draw.rect(
            sombra, (0, 0, 0, 80),
            (2, 2, pill_w, pill_h), border_radius=pill_h // 2,
        )
        pantalla.blit(sombra, (pill_x - 2, pill_y - 2))

        pygame.draw.rect(
            pantalla, color_pill,
            (pill_x, pill_y, pill_w, pill_h),
            border_radius=pill_h // 2,
        )
        pygame.draw.rect(
            pantalla, (255, 255, 255, 60),
            (pill_x, pill_y, pill_w, pill_h),
            2, border_radius=pill_h // 2,
        )
        texto = "ON" if activo else "OFF"
        color_texto = (255, 255, 255) if activo else (200, 200, 210)
        render_txt = self.fuente_valor.render(texto, True, color_texto)
        text_x = pill_x + 12 if not activo else pill_x + pill_w - 12 - render_txt.get_width()
        pantalla.blit(
            render_txt,
            (text_x, pill_y + pill_h // 2 - render_txt.get_height() // 2),
        )
        knob_x = pill_x + pill_w - pill_h // 2 - 3 if activo else pill_x + pill_h // 2 + 3
        pygame.draw.circle(
            pantalla, (255, 255, 255),
            (knob_x, pill_y + pill_h // 2),
            pill_h // 2 - 4,
        )
        pygame.draw.circle(
            pantalla, (180, 180, 190),
            (knob_x, pill_y + pill_h // 2),
            pill_h // 2 - 4, 1,
        )

        self._rects_toggles = getattr(self, "_rects_toggles", {})
        self._rects_toggles[clave] = pygame.Rect(
            pill_x, pill_y, pill_w, pill_h
        )
        return pill_y + pill_h + 6

    def _dibujar_boton(self, pantalla, x, y, ancho, etiqueta, accion,
                       alto=40, color_borde=None, color_texto=None):
        btn_h = alto
        rect = pygame.Rect(x, y, ancho, btn_h)
        mouse = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse)
        color = self.COLOR_BOTON_HOVER if hover else self.COLOR_BOTON
        pygame.draw.rect(pantalla, color, rect, border_radius=8)
        if color_borde is None:
            color_borde = self.COLOR_BORDE
        pygame.draw.rect(pantalla, color_borde, rect, 2, border_radius=8)
        if color_texto is None:
            color_texto = self.COLOR_ACENTO
        render = self.fuente_etiqueta.render(etiqueta, True, color_texto)
        pantalla.blit(
            render, render.get_rect(center=rect.center),
        )

        self._rects_botones = getattr(self, "_rects_botones", {})
        self._rects_botones[accion] = rect
        return y + btn_h + 6

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            self._slider_arrastrando = None
            if evento.key == pygame.K_ESCAPE:
                self._restaurar_snapshot()
                return "cancelar"
            return None

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            mouse = evento.pos

            if self.rect_cerrar.collidepoint(mouse):
                self._slider_arrastrando = None
                self._restaurar_snapshot()
                return "cancelar"

            if not self.rect_panel.collidepoint(mouse):
                self._slider_arrastrando = None
                self._restaurar_snapshot()
                return "cancelar"

            botones = getattr(self, "_rects_botones", {})
            if "restablecer" in botones and botones["restablecer"].collidepoint(mouse):
                for k, v in DEFAULTS.items():
                    self.config[k] = v
                return None

            if "guardar" in botones and botones["guardar"].collidepoint(mouse):
                self._slider_arrastrando = None
                self._snapshot = dict(self.config)
                return "guardar"

            if "cancelar" in botones and botones["cancelar"].collidepoint(mouse):
                self._slider_arrastrando = None
                self._restaurar_snapshot()
                return "cancelar"

            toggles = getattr(self, "_rects_toggles", {})
            for clave, rect in toggles.items():
                if rect.collidepoint(mouse):
                    self.config[clave] = not self.config[clave]
                    return None

            sliders = getattr(self, "_rects_sliders", {})
            for clave, rect in sliders.items():
                if rect.collidepoint(mouse):
                    self._slider_arrastrando = clave
                    self._actualizar_valor_slider(clave, mouse[0], rect)
                    return None

        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self._slider_arrastrando = None

        elif evento.type == pygame.MOUSEMOTION:
            if self._slider_arrastrando is not None:
                sliders = getattr(self, "_rects_sliders", {})
                clave = self._slider_arrastrando
                if clave in sliders:
                    self._actualizar_valor_slider(clave, evento.pos[0], sliders[clave])

        return None

    def _restaurar_snapshot(self):
        for k, v in self._snapshot.items():
            self.config[k] = v
        try:
            pygame.mixer.music.set_volume(self.config["vol_musica"])
        except pygame.error:
            pass

    def _actualizar_valor_slider(self, clave, mouse_x, rect_slider):
        rel = (mouse_x - rect_slider.x) / rect_slider.width
        rel = max(0.0, min(1.0, rel))
        self.config[clave] = round(rel, 3)
        if clave == "vol_musica":
            try:
                pygame.mixer.music.set_volume(self.config["vol_musica"])
            except pygame.error:
                pass

    def aplicar_cambios(self, pantalla, ancho_actual, alto_actual,
                        fullscreen_actual=True):
        try:
            pygame.mixer.music.set_volume(self.config["vol_musica"])
        except pygame.error:
            pass

        fullscreen_deseado = self.config["pantalla_completa"]
        if fullscreen_deseado != fullscreen_actual:
            flags = pygame.FULLSCREEN if fullscreen_deseado else 0
            try:
                pantalla = pygame.display.set_mode(
                    (ancho_actual, alto_actual), flags
                )
                pygame.display.set_caption("Jumper rack")
                fullscreen_actual = fullscreen_deseado
            except pygame.error as e:
                print(f"[CONFIG] No se pudo cambiar fullscreen: {e}")

        return pantalla, ancho_actual, alto_actual, fullscreen_actual
