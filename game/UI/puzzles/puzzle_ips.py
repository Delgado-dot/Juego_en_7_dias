"""
PuzzleIPs — asignación de IPs / subnetting.

El jugador debe asignar una IP a cada dispositivo de la red
respetando restricciones (gateway, servidor, etc).
"""

import random

import pygame

from game.UI.puzzles.puzzle_base import BasePuzzle


# Pool de IPs: 192.168.1.1 a 192.168.1.16
POOL_IPS = [f"192.168.1.{i}" for i in range(1, 17)]


# Tipos de dispositivo con sus restricciones
TIPOS_DISPOSITIVO = [
    {
        "tipo": "router",
        "etiqueta": "ROUTER",
        "restriccion": "Necesita IP gateway (.1)",
        "ip_requerida": "192.168.1.1",
        "color": (255, 100, 100),
        "es_gateway": True,
    },
    {
        "tipo": "servidor_dns",
        "etiqueta": "SERVIDOR DNS",
        "restriccion": "Servidor: IP baja (<=.5)",
        "ip_requerida_prefix": "192.168.1.",
        "ip_requerida_max": 5,
        "color": (255, 200, 100),
    },
    {
        "tipo": "servidor_web",
        "etiqueta": "SERVIDOR WEB",
        "restriccion": "Servidor: cualquier IP",
        "color": (130, 220, 180),
    },
    {
        "tipo": "pc",
        "etiqueta": "PC",
        "restriccion": "PC: cualquier IP",
        "color": (100, 180, 255),
    },
    {
        "tipo": "pc_invitado",
        "etiqueta": "PC INVITADO",
        "restriccion": "PC: cualquier IP",
        "color": (180, 130, 255),
    },
    {
        "tipo": "impresora",
        "etiqueta": "IMPRESORA",
        "restriccion": "Periferico: cualquier IP",
        "color": (220, 150, 200),
    },
]


class PuzzleIPs(BasePuzzle):
    TITULO = "DIRECCIONAMIENTO IP"
    HINT = "Asigná una IP a cada dispositivo  |  Click derecho para liberar  |  VALIDAR"

    def _tiene_boton_validar(self):
        return True

    def _construir(self):
        if self.dificultad <= 2:
            n_disp = 4
        elif self.dificultad <= 4:
            n_disp = 5
        else:
            n_disp = 6

        rng = random.Random(pygame.time.get_ticks())

        disponibles = list(TIPOS_DISPOSITIVO)
        rng.shuffle(disponibles)

        tipos_elegidos = [TIPOS_DISPOSITIVO[0]]
        for t in disponibles:
            if len(tipos_elegidos) >= n_disp:
                break
            if t["tipo"] != "router":
                tipos_elegidos.append(t)

        self.dispositivos = []
        for i, t in enumerate(tipos_elegidos):
            self.dispositivos.append({
                "id": i,
                "tipo": t["tipo"],
                "etiqueta": t["etiqueta"],
                "restriccion": t["restriccion"],
                "color": t["color"],
                "ip": None,
                "x": 0, "y": 0,
                "slot_rect": None,
            })

        n = len(self.dispositivos)
        col_x = self.area.x + 220
        col_w = 180
        col_h = 75
        gap_y = (self.area.height - 60 - n * col_h) // max(1, n - 1) if n > 1 else 0
        gap_y = max(30, gap_y)
        y_inicio = self.area.y + 40

        for i, d in enumerate(self.dispositivos):
            dy = y_inicio + i * (col_h + gap_y)
            d["x"] = col_x - col_w // 2
            d["y"] = dy
            slot_w = 210
            slot_h = 34
            d["slot_rect"] = pygame.Rect(
                col_x - slot_w // 2,
                dy + col_h + 8,
                slot_w, slot_h
            )

        self._lineas = []
        for i in range(1, n):
            self._lineas.append((self.dispositivos[0]["x"] + col_w // 2,
                                 self.dispositivos[0]["y"] + col_h // 2,
                                 self.dispositivos[i]["x"] + col_w // 2,
                                 self.dispositivos[i]["y"] + col_h // 2))

        self.ip_pool = list(POOL_IPS)
        rng.shuffle(self.ip_pool)
        self._reposicionar_pool()

        self.ip_arrastrada = None

    def _reposicionar_pool(self):
        col_w = 150
        col_h = 34
        gap_x = 14
        gap_y = 12
        cols = 4
        grid_w = cols * col_w + (cols - 1) * gap_x
        grid_x = self.area.x + self.area.width - grid_w - 30
        grid_y = self.area.y + 50

        self._ip_rects = {}
        for i, ip in enumerate(self.ip_pool):
            col = i % cols
            fila = i // cols
            self._ip_rects[ip] = pygame.Rect(
                grid_x + col * (col_w + gap_x),
                grid_y + fila * (col_h + gap_y),
                col_w, col_h
            )

    def _ip_disponible(self, ip):
        """True si la IP no está asignada a ningún dispositivo."""
        for d in self.dispositivos:
            if d["ip"] == ip:
                return False
        return True

    def _verificar_victoria(self):
        # Todos deben tener IP
        for d in self.dispositivos:
            if d["ip"] is None:
                self._mostrar_toast("Faltan dispositivos por asignar", (255, 120, 120))
                return False

        # Sin duplicados (garantizado por construcción, pero verificamos)
        ips_usadas = [d["ip"] for d in self.dispositivos]
        if len(set(ips_usadas)) != len(ips_usadas):
            self._mostrar_toast("Hay IPs duplicadas", (255, 120, 120))
            return False

        # Router debe tener .1
        router = next((d for d in self.dispositivos if d["tipo"] == "router"), None)
        if router and router["ip"] != "192.168.1.1":
            self._mostrar_toast("El router necesita la IP .1", (255, 120, 120))
            return False

        # Servidor DNS debe tener IP <= .5
        dns = next((d for d in self.dispositivos if d["tipo"] == "servidor_dns"), None)
        if dns:
            try:
                ultimo_octeto = int(dns["ip"].split(".")[-1])
                if ultimo_octeto > 5:
                    self._mostrar_toast("Servidor DNS necesita IP baja (<=.5)", (255, 120, 120))
                    return False
            except Exception:
                pass

        # Dificultad alta: ningún otro dispositivo puede ser .1
        if self.dificultad >= 4:
            for d in self.dispositivos:
                if d["tipo"] != "router" and d["ip"] == "192.168.1.1":
                    self._mostrar_toast("Solo el router puede tener .1", (255, 120, 120))
                    return False

        return True

    def _manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Click izquierdo
            if evento.button == 1:
                # Si hay IP agarrada, intentar soltar en un slot
                if self.ip_arrastrada is not None:
                    for d in self.dispositivos:
                        if d["slot_rect"].collidepoint(mouse_pos):
                            self._asignar_ip(d["id"], self.ip_arrastrada)
                            return None
                    # Soltó fuera, cancelar
                    self.ip_arrastrada = None
                    return None

                # Si no, intentar agarrar una IP del pool
                for ip, rect in self._ip_rects.items():
                    if rect.collidepoint(mouse_pos) and self._ip_disponible(ip):
                        self.ip_arrastrada = ip
                        return None

            # Click derecho: liberar IP de un dispositivo
            elif evento.button == 3:
                for d in self.dispositivos:
                    if d["slot_rect"].collidepoint(mouse_pos) and d["ip"] is not None:
                        d["ip"] = None
                        self._reproducir(self.sonido_error)
                        return None

        return None

    def _asignar_ip(self, disp_id, ip):
        d = self.dispositivos[disp_id]
        ip_anterior = d["ip"]
        d["ip"] = ip
        self.ip_arrastrada = None
        self._reproducir(self.sonido_conectar)

    def _actualizar_subclase(self, dt):
        pass

    def _dibujar_subclase(self):
        # 0) Texto de ayuda
        tiene_router = any(d["tipo"] == "router" for d in self.dispositivos)
        if tiene_router:
            ayuda1 = self.fuente_etiqueta.render("Asigna una IP unica a cada dispositivo.", True, (160, 200, 220))
            ayuda2 = self.fuente_etiqueta.render("El Router normalmente utiliza la primera IP disponible.", True, (180, 180, 120))
            self.pantalla.blit(ayuda1, (self.area.x + 20, self.area.y + 8))
            self.pantalla.blit(ayuda2, (self.area.x + 20, self.area.y + 28))
        else:
            ayuda1 = self.fuente_etiqueta.render("Asigna una IP unica a cada dispositivo.", True, (160, 200, 220))
            self.pantalla.blit(ayuda1, (self.area.x + 20, self.area.y + 8))

        # 1) Líneas del diagrama
        for (x1, y1, x2, y2) in self._lineas:
            pygame.draw.line(
                self.pantalla, (60, 80, 120),
                (x1, y1), (x2, y2), 2
            )

        # 2) Dispositivos
        for d in self.dispositivos:
            self._dibujar_dispositivo(d)

        # 3) Pool de IPs
        self._dibujar_pool_ips()

        # 4) IP arrastrada
        if self.ip_arrastrada is not None:
            mx, my = pygame.mouse.get_pos()
            self._dibujar_ip_pildora(self.ip_arrastrada, mx - 75, my - 17, alpha=240)

    def _dibujar_dispositivo(self, d):
        x, y = d["x"], d["y"]
        w, h = 180, 75
        color = d["color"]

        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((*color, 30))
        pygame.draw.rect(surf, color, (0, 0, w, h), 2, border_radius=8)

        if d["tipo"] == "router":
            pygame.draw.rect(surf, color, (10, 25, 40, 25), border_radius=3)
            pygame.draw.line(surf, color, (20, 25), (15, 10), 2)
            pygame.draw.line(surf, color, (30, 25), (25, 10), 2)
            pygame.draw.line(surf, color, (40, 25), (45, 10), 2)
        elif "servidor" in d["tipo"]:
            pygame.draw.rect(surf, color, (15, 15, 30, 40), border_radius=2)
            for j in range(3):
                pygame.draw.line(surf, (0, 0, 0), (20, 22 + j * 10), (40, 22 + j * 10), 1)
        else:
            pygame.draw.rect(surf, color, (12, 18, 40, 28), border_radius=2)
            pygame.draw.rect(surf, color, (22, 46, 20, 8), border_radius=1)
            pygame.draw.rect(surf, color, (18, 52, 28, 4), border_radius=1)

        etiqueta = self.fuente_etiqueta.render(d["etiqueta"], True, (240, 240, 250))
        surf.blit(etiqueta, (60, 12))

        restr = self.fuente_peq.render(d["restriccion"], True, (200, 210, 230))
        max_w = w - 70
        texto_rest = d["restriccion"]
        while restr.get_width() > max_w and len(texto_rest) > 5:
            texto_rest = texto_rest[:-1]
            restr = self.fuente_peq.render(texto_rest + "...", True, (200, 210, 230))
        surf.blit(restr, (60, 36))

        self.pantalla.blit(surf, (x, y))

        slot = d["slot_rect"]
        slot_surf = pygame.Surface((slot.width, slot.height), pygame.SRCALPHA)
        slot_surf.fill((20, 28, 45, 220))
        pygame.draw.rect(slot_surf, color, (0, 0, slot.width, slot.height), 2, border_radius=6)

        if d["ip"]:
            ip_render = self.fuente_etiqueta.render(d["ip"], True, (220, 255, 240))
        else:
            ip_render = self.fuente_etiqueta.render("?", True, (140, 160, 180))

        slot_surf.blit(
            ip_render,
            (slot.width // 2 - ip_render.get_width() // 2,
             slot.height // 2 - ip_render.get_height() // 2)
        )
        self.pantalla.blit(slot_surf, slot.topleft)

    def _dibujar_pool_ips(self):
        titulo = self.fuente_etiqueta.render("IPs DISPONIBLES", True, (180, 230, 255))
        self.pantalla.blit(
            titulo,
            (self.area.x + self.area.width - titulo.get_width() - 30,
             self.area.y + 32)
        )

        for ip in self.ip_pool:
            rect = self._ip_rects[ip]
            disponible = self._ip_disponible(ip)
            if disponible:
                self._dibujar_ip_pildora(ip, rect.x, rect.y)

    def _dibujar_ip_pildora(self, ip, x, y, alpha=255):
        rect = pygame.Rect(x, y, 150, 34)
        fondo = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        fondo.fill((35, 50, 80, 230))
        pygame.draw.rect(fondo, (120, 200, 255), (0, 0, rect.width, rect.height), 1, border_radius=6)

        texto = self.fuente_etiqueta.render(ip, True, (220, 240, 255))
        fondo.blit(
            texto,
            (rect.width // 2 - texto.get_width() // 2,
             rect.height // 2 - texto.get_height() // 2)
        )

        fondo.set_alpha(alpha)
        self.pantalla.blit(fondo, rect.topleft)
        return rect
