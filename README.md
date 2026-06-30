# 🧩 Camino a la Presidencia

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Pygame-CE](https://img.shields.io/badge/Engine-Pygame--CE-orange.svg)](https://github.com/pygame-community/pygame-ce)
[![Testing](https://img.shields.io/badge/Testing-pytest-green.svg)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Un videojuego de puzzles 2D estilo **Sokoban** desarrollado en **Python** y **Pygame-CE** aplicando estrictamente las metodologías **TDD (Test-Driven Development)**, **BDD (Behavior-Driven Development)** y **ATDD (Acceptance Test-Driven Development)**.

---

## 🎮 Sobre el Juego

El objetivo del juego es empujar todos los bloques marrones hacia las metas verdes correspondientes en cada uno de los 3 niveles antes de que el temporizador llegue a cero.

### ⚙️ Mecánicas Principales
* **Movimiento por Cuadrícula (15x15):** Controla al jugador en un entorno cerrado con bordes y obstáculos.
* **Física de Empuje:** Empuja bloques marrones (`BLOCK`). Si un bloque entra en una meta se convierte en bloque dorado (`BLOCK_ON_GOAL`). Los bloques en meta pueden seguir empujándose hacia otras metas o espacios vacíos.
* **Restauración de Casillas Pisadas:** Sistema inteligente `standing_on` en el modelo del jugador. Al caminar sobre metas (`GOAL`) o portales y luego retirarse, la casilla recupera su estado y diseño original, previniendo que se borren o desaparezcan.
* **Mecánica Portales:** Portales azules (`PORTAL_BLUE`) interconectados que actúan como atajos de teletransportación inmediata (solo para el jugador, los bloques no pasan por portales).
* **Gestión de Tiempo Inteligente:** Un temporizador global que disminuye en tiempo real. Cuenta con una barra de progreso visual de color dinámico (verde → amarillo → rojo).
* **Deshacer Movimiento (Undo):** Implementado con el **Patrón Memento**, lo que permite retroceder movimientos ilimitadamente con la tecla `Z` para evitar bloqueos del nivel (deadlocks).

### ⌨️ Controles
* **Flechas del Teclado / W, A, S, D:** Mover al jugador.
* **Z:** Deshacer movimiento anterior (Undo).
* **R:** Reiniciar el nivel actual (Habilitado en partida y en la pantalla de *Game Over*).
* **ESC:**
  * Durante el juego: Abre/Cierra el menú de pausa.
  * En menú de pausa: Reanuda la partida.
  * En pantalla de *Game Over*: Vuelve al menú principal.

---

## 🏗️ Arquitectura: Separación de Responsabilidades

El núcleo del proyecto está diseñado con desacoplamiento total entre lógica y representación visual:

1. **`src/models.py` (Lógica Pura):** Contiene el modelo de datos e interactores independientes (`Grid`, `Player`, `GameState`, `TileType`). No importa librerías gráficas, lo que facilita pruebas automatizadas ultrarrápidas.
2. **`src/main.py` (Vista Pasiva):** Traduce los eventos de entrada del teclado y se encarga del renderizado gráfico mediante Pygame-CE, HUD, menús y animaciones de partículas.
3. **`levels/` (Niveles Externos):** Almacena mapas de 15x15 en texto plano (`nivel1.txt`, `nivel2.txt`, `nivel3.txt`).

---

## 🎨 Pulido Gráfico y Efectos (High Fidelity)

* **Animaciones Senoidales en Tiempo Real:**
  * **Metas (G):** Emiten un halo circular de luz verde esmeralda que pulsa suavemente.
  * **Bloques en metas (BLOCK_ON_GOAL):** Presentan un halo dorado brillante de éxito.
* **Efecto de Partículas Orbitales en Portales (X, Y):** Los portales azules poseen 3 partículas celestes orbitando en sentido horario, mientras que los rojos rotan en sentido antihorario.
* **Efectos 3D y Sombras:** Sombra proyectada en el jugador, refuerzos clásicos de madera en los bloques y sombreado 3D en las paredes.
* **Pantalla de Transición Inter-Nivel:** Al resolver un puzzle, se congela el tiempo de juego y se muestra una pantalla de éxito durante 2.5 segundos que resume movimientos, tiempo y presenta una barra de progreso de carga animada.
* **Marcador Global:** Se acumula el total de movimientos de la sesión completa, mostrando la puntuación definitiva al ganar en la pantalla final de *Juego Completado*.

---

## 🧪 Pruebas Unitarias (TDD / BDD)

La lógica del juego está blindada con **25 pruebas unitarias automatizadas** que cubren el 100% de la lógica crítica, incluyendo:
* Reglas de movimiento sobre casillas vacías y colisiones contra paredes.
* Reglas de empuje de bloques (hacia suelo, hacia metas y bloqueos).
* Mecánica de teletransportación por portales y validaciones de salidas bloqueadas.
* Patrón Memento (Undo y deshecho de estados).
* Restauración de casillas originales (metas y portales) tras el paso del jugador.

### Ejecución de Pruebas
Activa tu entorno virtual e instala los requerimientos si aún no lo has hecho:
```bash
pip install -r requirements.txt
pytest -v
```

---

## 👨‍💻 Autores
* Centeno Lopez Jose Alfredo
* Pozu Vargas Luis Anthony
* Quispe Sullca Yhosfer Anderson
* Ramos Alatrista Eddy Robinson
