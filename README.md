# 🎮 Juego en 7 Días

Juego de plataformas 2D hecho en **Python + Pygame** como proyecto colaborativo.

El jugador es un cuadrado que tiene que ir del **punto A** (rojo) al **punto B** (verde) **sin perder el cable**. Un triángulo morado patrulla por el escenario y **corta el cable** si pasa muy cerca de él. Si lo corta, hay que volver al punto A para recuperarlo.

> Un juego para experimentar y mejorar la lógica de estudiantes.

---

## 🚀 Cómo correr el juego

```bash
pip install pygame
python main.py
```

Requiere Python 3.x y Pygame.

---

## 🕹️ Controles

| Acción | Teclas |
|---|---|
| Mover izquierda | `A` o `←` |
| Mover derecha | `D` o `→` |
| Saltar | `W`, `↑` o `Espacio` |

---

## 📁 Estructura del proyecto

```
.
├── Entidades.py    → Todas las clases del mundo (Personaje, Enemigo, etc.)
├── main.py         → Ventana, bucle del juego y dibujado
└── README.md
```

Solo hay **2 archivos** de código. La idea es que cada quien toque su parte sin pisarse.

---

## 🧱 Arquitectura

```
EntidadJuego  (clase base: forma, animación, draw)
   ├── Personaje   → jugador controlable
   └── Enemigo     → triángulo que patrulla
```

- **`EntidadJuego`**: lo que **todas** las entidades tienen en común (hitbox, sprite, flip, animación por frames). No se toca, se hereda.
- **`Personaje`**: movimiento, salto, gravedad, colisión con plataformas, **cable**.
- **`Enemigo`**: patrulla entre dos puntos y dice si el cable pasa muy cerca.

---

## 🛠️ Guía para el equipo

### Quiero cambiar el salto / movimiento / cable del jugador
➡️ `Entidades.py` → clase **`Personaje`**

Constantes que probablemente vas a tocar:
```python
self.velocidad = 5        # velocidad horizontal
self.gravedad = 0.6       # qué tan rápido cae
self.fuerza_salto = -13   # qué tan alto salta
self.distancia_recuperar_cable = 35  # radio del punto A para recuperar el cable
```

### Quiero cambiar el triángulo o añadir otro enemigo
➡️ `Entidades.py` → clase **`Enemigo`**

Constantes:
```python
self.velocidad = 3     # qué tan rápido patrulla
self.radio_corte = 25  # qué tan cerca del cable tiene que pasar para cortarlo
```

Para crear un enemigo nuevo, **hereda** de `Enemigo` y solo cambia lo que necesites:
```python
class EnemigoRapido(Enemigo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidad=8)
```

### Quiero cambiar el nivel / plataformas / puntos A-B
➡️ `main.py` → arriba del todo, en la sección **"Nivel"**:
```python
PUNTO_A = (80, 420)
PUNTO_B = (720, 120)

PLATAFORMAS = [
    pygame.Rect(0,   460, 800, 40),
    pygame.Rect(160, 370, 160, 20),
    pygame.Rect(400, 290, 160, 20),
    pygame.Rect(610, 200, 130, 20),
]
```

### Quiero añadir una nueva entidad (sabio, item, proyectil…)
➡️ `Entidades.py` → nueva clase que herede de `EntidadJuego`:
```python
class Sabio(EntidadJuego):
    def __init__(self, x, y):
        super().__init__(tile=64)
        self.forma = pygame.Rect(x, y, 64, 64)
        # tu lógica aquí
```

Después la instancias en `main.py` igual que `Personaje` o `Enemigo`.

---

## 🤝 Reglas para no romper nada

1. **No edites `EntidadJuego`** salvo que avises al equipo: la usan todas las subclases.
2. Si añades métodos a `Personaje` o `Enemigo`, usa nombres claros (`recuperar_cable`, no `rc`).
3. Antes de mergear, corre el juego y verifica que:
   - El jugador se mueve y salta bien
   - El cable se corta y se puede recuperar
   - El triángulo patrulla
   - Se puede ganar llegando al punto B con cable
4. Si cambias constantes (gravedad, salto, velocidad…), déjalas **arriba del `__init__`** para que sean fáciles de encontrar.

---

## 📋 Ideas / cosas pendientes

- [ ] Sprites reales (ahora se dibujan formas geométricas)
- [ ] Sonidos (salto, cable cortado, victoria)
- [ ] Más niveles
- [ ] Más tipos de enemigo
- [ ] Pantalla de inicio y de Game Over
