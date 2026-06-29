"""
PuzzleTopologia — construir la topología de red objetivo.

El jugador debe conectar nodos formando una topología específica
(Estrella, Anillo, Árbol o Mesh) que se muestra como referencia.
"""

import math
import random
from collections import deque

import pygame

from game.UI.puzzles.puzzle_base import BasePuzzle


TOPOLOGIAS = ["ESTRELLA", "ANILLO", "ARBOL", "MESH"]


class PuzzleTopologia(BasePuzzle):
    TITULO = "TOPOLOGIA"
    HINT = "Click en 2 nodos para crear enlace  |  Click derecho para eliminar  |  VALIDAR"
    HIT_NODO = 15

    def _tiene_boton_validar(self):
        return True

    def _construir(self):
        if self.dificultad <= 2:
            n_nodos = 5
        elif self.dificultad <= 4:
            n_nodos = 6
        else:
            n_nodos = 7

        rng = random.Random(pygame.time.get_ticks())

        # Elegir topología objetivo (con restricciones de dificultad)
        if self.dificultad <= 2:
            topologia = rng.choice(["ESTRELLA", "ANILLO"])
        elif self.dificultad <= 4:
            topologia = rng.choice(["ANILLO", "ARBOL"])
        else:
            topologia = rng.choice(TOPOLOGIAS)

        self.topologia = topologia
        self.n = n_nodos

        ref_w = 220
        ref_h = 180
        pad_nodos = 60

        nodo_area = pygame.Rect(
            self.area.x + pad_nodos,
            self.area.y + pad_nodos,
            self.area.width - ref_w - pad_nodos * 2,
            self.area.height - pad_nodos * 2
        )

        cols = math.ceil(math.sqrt(n_nodos * nodo_area.width / nodo_area.height))
        filas = math.ceil(n_nodos / cols)

        cell_w = nodo_area.width / cols
        cell_h = nodo_area.height / filas

        self.nodos = []
        idx = 0
        for fila in range(filas):
            for col in range(cols):
                if idx >= n_nodos:
                    break
                cx = nodo_area.x + (col + 0.5) * cell_w
                cy = nodo_area.y + (fila + 0.5) * cell_h
                self.nodos.append({
                    "id": idx,
                    "x": int(cx),
                    "y": int(cy),
                    "grado": 0,
                })
                idx += 1

        self.aristas = []
        self.nodo_seleccionado = None

        self.ref_rect = pygame.Rect(
            self.area.x + self.area.width - ref_w - 20,
            self.area.y + 40,
            ref_w, ref_h
        )

    def _verificar_victoria(self):
        if self.topologia == "ESTRELLA":
            # Un nodo central con grado N-1, todos los otros con grado 1
            grados = [n["grado"] for n in self.nodos]
            grados.sort(reverse=True)
            if grados[0] != self.n - 1:
                return False
            for g in grados[1:]:
                if g != 1:
                    return False
            # Verificar que el nodo central esté conectado a todos los demás
            central = self.nodos[grados.index(grados[0])]
            for n in self.nodos:
                if n["id"] != central["id"]:
                    par = tuple(sorted((central["id"], n["id"])))
                    if par not in [tuple(sorted(e)) for e in self.aristas]:
                        return False
            return True

        elif self.topologia == "ANILLO":
            # Todos los nodos con grado exactamente 2, y debe haber n aristas
            if len(self.aristas) != self.n:
                return False
            grados = [n["grado"] for n in self.nodos]
            return all(g == 2 for g in grados)

        elif self.topologia == "ARBOL":
            # N-1 aristas, conexo, sin ciclos
            if len(self.aristas) != self.n - 1:
                return False
            return self._es_conexo() and not self._tiene_ciclo()

        elif self.topologia == "MESH":
            # Todos los nodos con grado N-1 (grafo completo)
            if len(self.aristas) != self.n * (self.n - 1) // 2:
                return False
            grados = [n["grado"] for n in self.nodos]
            return all(g == self.n - 1 for g in grados)

        return False

    def _es_conexo(self):
        """BFS desde el nodo 0 para ver si todos son alcanzables."""
        if self.n == 0:
            return True
        visitados = set([0])
        cola = deque([0])
        while cola:
            u = cola.popleft()
            for (a, b) in self.aristas:
                if a == u and b not in visitados:
                    visitados.add(b)
                    cola.append(b)
                elif b == u and a not in visitados:
                    visitados.add(a)
                    cola.append(a)
        return len(visitados) == self.n

    def _tiene_ciclo(self):
        """Detecta si hay un ciclo usando DFS."""
        if self.n == 0:
            return False
        adj = {i: [] for i in range(self.n)}
        for (a, b) in self.aristas:
            adj[a].append(b)
            adj[b].append(a)

        visitados = set()

        def dfs(u, padre):
            visitados.add(u)
            for v in adj[u]:
                if v not in visitados:
                    if dfs(v, u):
                        return True
                elif v != padre:
                    return True
            return False

        return dfs(0, -1)

    def _manejar_evento(self, evento):
        if evento.type != pygame.MOUSEBUTTONDOWN:
            return None

        mouse_pos = pygame.mouse.get_pos()
        nodo_clickeado = self._nodo_en_pos(mouse_pos)

        # Click derecho: eliminar arista cerca del cursor
        if evento.button == 3:
            if self._eliminar_arista_cerca(mouse_pos):
                self._reproducir(self.sonido_error)
            return None

        # Click izquierdo
        if evento.button != 1:
            return None

        if nodo_clickeado is None:
            self.nodo_seleccionado = None
            return None

        if self.nodo_seleccionado is None:
            self.nodo_seleccionado = nodo_clickeado
            return None

        if self.nodo_seleccionado == nodo_clickeado:
            self.nodo_seleccionado = None
            return None

        # Toggle: si la arista ya existe, eliminarla; si no, crearla
        par = tuple(sorted((self.nodo_seleccionado, nodo_clickeado)))
        existente = None
        for i, (a, b) in enumerate(self.aristas):
            if tuple(sorted((a, b))) == par:
                existente = i
                break

        if existente is not None:
            # Eliminar
            del self.aristas[existente]
            self.nodos[self.nodo_seleccionado]["grado"] -= 1
            self.nodos[nodo_clickeado]["grado"] -= 1
            self._reproducir(self.sonido_error)
        else:
            # Crear
            self.aristas.append((self.nodo_seleccionado, nodo_clickeado))
            self.nodos[self.nodo_seleccionado]["grado"] += 1
            self.nodos[nodo_clickeado]["grado"] += 1
            self._reproducir(self.sonido_conectar)

        self.nodo_seleccionado = None
        return None

    def _nodo_en_pos(self, pos):
        for n in self.nodos:
            dx = pos[0] - n["x"]
            dy = pos[1] - n["y"]
            if dx * dx + dy * dy <= self.HIT_NODO ** 2:
                return n["id"]
        return None

    def _eliminar_arista_cerca(self, pos):
        for i, (a, b) in enumerate(self.aristas):
            ax, ay = self.nodos[a]["x"], self.nodos[a]["y"]
            bx, by = self.nodos[b]["x"], self.nodos[b]["y"]
            # Distancia del punto a la línea
            dist = self._distancia_punto_a_segmento(pos, (ax, ay), (bx, by))
            if dist < 8:
                del self.aristas[i]
                self.nodos[a]["grado"] -= 1
                self.nodos[b]["grado"] -= 1
                return True
        return False

    @staticmethod
    def _distancia_punto_a_segmento(p, a, b):
        """Distancia del punto p al segmento ab."""
        px, py = p
        ax, ay = a
        bx, by = b
        dx = bx - ax
        dy = by - ay
        if dx == 0 and dy == 0:
            return math.hypot(px - ax, py - ay)
        t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
        cx = ax + t * dx
        cy = ay + t * dy
        return math.hypot(px - cx, py - cy)

    def _actualizar_subclase(self, dt):
        pass

    def _dibujar_subclase(self):
        # 1) Aristas permanentes
        for (a, b) in self.aristas:
            ax, ay = self.nodos[a]["x"], self.nodos[a]["y"]
            bx, by = self.nodos[b]["x"], self.nodos[b]["y"]

            halo = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
            pygame.draw.line(halo, (0, 220, 255, 90), (ax, ay), (bx, by), 10)
            self.pantalla.blit(halo, (0, 0))

            pygame.draw.line(self.pantalla, (50, 80, 120), (ax, ay), (bx, by), 5)
            pygame.draw.line(self.pantalla, (0, 200, 255), (ax, ay), (bx, by), 2)
            pygame.draw.line(self.pantalla, (180, 240, 255), (ax, ay), (bx, by), 1)

        # 2) Línea temporal (nodo seleccionado → cursor)
        if self.nodo_seleccionado is not None:
            sx, sy = self.nodos[self.nodo_seleccionado]["x"], self.nodos[self.nodo_seleccionado]["y"]
            mx, my = pygame.mouse.get_pos()
            halo = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
            pygame.draw.line(halo, (0, 220, 255, 140), (sx, sy), (mx, my), 8)
            self.pantalla.blit(halo, (0, 0))
            pygame.draw.line(self.pantalla, (80, 180, 220), (sx, sy), (mx, my), 3)
            pygame.draw.line(self.pantalla, (180, 240, 255), (sx, sy), (mx, my), 1)

        # 3) Nodos
        for n in self.nodos:
            self._dibujar_nodo(n)

        # 4) Referencia
        self._dibujar_referencia()

    def _dibujar_nodo(self, n):
        x, y = n["x"], n["y"]
        radio = self.HIT_NODO
        seleccionado = (self.nodo_seleccionado == n["id"])

        if seleccionado:
            ahora = pygame.time.get_ticks()
            pulso = (math.sin(ahora * 0.01) + 1) / 2
            halo = pygame.Surface((radio * 6, radio * 6), pygame.SRCALPHA)
            pygame.draw.circle(
                halo, (0, 220, 255, 100 + int(pulso * 100)),
                (radio * 3, radio * 3), radio + 6 + int(pulso * 4)
            )
            self.pantalla.blit(halo, (x - radio * 3, y - radio * 3))

        color_borde = (255, 255, 255)
        color_relleno = (40, 60, 90) if not seleccionado else (30, 80, 120)

        surf = pygame.Surface((radio * 2 + 4, radio * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(surf, color_relleno, (radio + 2, radio + 2), radio)
        pygame.draw.circle(surf, color_borde, (radio + 2, radio + 2), radio, 2)

        num = self.fuente_etiqueta.render(str(n["id"] + 1), True, (240, 240, 250))
        surf.blit(
            num,
            (radio + 2 - num.get_width() // 2,
             radio + 2 - num.get_height() // 2)
        )

        self.pantalla.blit(surf, (x - radio - 2, y - radio - 2))

    def _dibujar_referencia(self):
        rect = self.ref_rect

        # Fondo del recuadro de referencia
        fondo = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        fondo.fill((20, 30, 50, 200))
        pygame.draw.rect(fondo, (0, 200, 255), (0, 0, rect.width, rect.height), 2, border_radius=10)

        # Título
        titulo = self.fuente_etiqueta.render("OBJETIVO", True, (200, 230, 255))
        fondo.blit(titulo, (rect.width // 2 - titulo.get_width() // 2, 10))

        # Subtítulo (nombre de la topología)
        subtitulo = self.fuente_grande.render(self.topologia, True, (255, 220, 100))
        fondo.blit(subtitulo, (rect.width // 2 - subtitulo.get_width() // 2, 35))

        # Línea separadora
        pygame.draw.line(fondo, (0, 200, 255, 120),
                         (20, 75), (rect.width - 20, 75), 1)

        # Mini-diagrama de la topología objetivo
        cx = rect.width // 2
        cy = (75 + rect.height) // 2 + 10
        radio = 12
        self._dibujar_topologia_referencia(fondo, cx, cy, radio)

        self.pantalla.blit(fondo, rect.topleft)

    def _dibujar_topologia_referencia(self, surf, cx, cy, radio):
        """Dibuja una miniatura de la topología objetivo dentro de surf."""
        n = min(self.n, 6)  # Limitar a 6 nodos para la miniatura
        color = (255, 255, 255)
        color_linea = (120, 200, 255)

        # Calcular posiciones según topología
        posiciones = []

        if self.topologia == "ESTRELLA":
            # Centro + nodos alrededor
            posiciones = [(cx, cy)]
            for i in range(n - 1):
                angulo = i * 2 * math.pi / max(1, n - 1) - math.pi / 2
                r = 50
                posiciones.append((cx + math.cos(angulo) * r,
                                   cy + math.sin(angulo) * r))
        elif self.topologia == "ANILLO":
            for i in range(n):
                angulo = i * 2 * math.pi / n - math.pi / 2
                r = 50
                posiciones.append((cx + math.cos(angulo) * r,
                                   cy + math.sin(angulo) * r))
        elif self.topologia == "ARBOL":
            # Layout jerárquico simple
            niveles = [
                [(cx, cy - 40)],  # raíz
                [(cx - 30, cy + 10), (cx + 30, cy + 10)],
                [(cx - 50, cy + 50), (cx - 10, cy + 50), (cx + 30, cy + 50)],
            ]
            for nivel in niveles:
                posiciones.extend(nivel)
            posiciones = posiciones[:n]
        elif self.topologia == "MESH":
            for i in range(n):
                angulo = i * 2 * math.pi / n - math.pi / 2
                r = 50
                posiciones.append((cx + math.cos(angulo) * r,
                                   cy + math.sin(angulo) * r))

        # Dibujar aristas de la topología objetivo
        aristas_obj = self._aristas_objetivo(len(posiciones))
        for (a, b) in aristas_obj:
            if a < len(posiciones) and b < len(posiciones):
                ax, ay = posiciones[a]
                bx, by = posiciones[b]
                pygame.draw.line(surf, color_linea, (ax, ay), (bx, by), 2)

        # Dibujar nodos
        for (x, y) in posiciones:
            pygame.draw.circle(surf, color, (int(x), int(y)), radio)
            pygame.draw.circle(surf, (50, 100, 150), (int(x), int(y)), radio, 1)

    def _aristas_objetivo(self, n):
        """Genera las aristas de la topología objetivo para `n` nodos."""
        if self.topologia == "ESTRELLA":
            return [(0, i) for i in range(1, n)]
        elif self.topologia == "ANILLO":
            return [(i, (i + 1) % n) for i in range(n)]
        elif self.topologia == "ARBOL":
            aristas = []
            for i in range(1, n):
                padre = (i - 1) // 2
                aristas.append((padre, i))
            return aristas
        elif self.topologia == "MESH":
            return [(i, j) for i in range(n) for j in range(i + 1, n)]
        return []
