# 🧩 Puzzle Laberinto TDD

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Pygame-CE](https://img.shields.io/badge/Engine-Pygame--CE-orange.svg)](https://github.com/pygame-community/pygame-ce)
[![Testing](https://img.shields.io/badge/Testing-pytest-green.svg)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Un juego de puzzles 2D desarrollado con **Python** y **Pygame-CE**, donde debes empujar bloques hacia la meta antes de que se agote el tiempo. 

**Característica destacada:** Este proyecto fue desarrollado íntegramente aplicando la metodología **Test Driven Development (TDD)**, garantizando una lógica robusta, mantenible, escalable y con alta cobertura de pruebas unitarias.

---

## 🎮 Sobre el Juego

### Mecánicas Principales
- **Movimiento por cuadrícula:** Controla al personaje en un entorno de rejilla (grid) 2D.
- **Física de empuje:** Empuja bloques marrones hacia la zona verde (meta).
- **Gestión del tiempo:** Resuelve el puzzle antes de que el temporizador llegue a cero.
- **Colisiones inteligentes:** El sistema impide movimientos inválidos (empujar bloques contra paredes o fuera del mapa).

### Controles
- **Flechas del teclado** o **W, A, S, D**: Mover al jugador.
- **ESC** o cerrar la ventana: Salir del juego.

---

## 🚀 Instalación y Ejecución

### Requisitos Previos
- Python 3.10 o superior (Probado en Python 3.14).
- `pip` (gestor de paquetes de Python).

### Pasos de Instalación

1. **Clona este repositorio:**
   ```bash
   git clone https://github.com/[TU_USUARIO]/puzzle_laberinto.git
   cd puzzle_laberinto

   ```

2. **Crea y activa un entorno virtual:**

   ```bash
   python -m venv .venv
   ```

   **En Windows:**

   ```bash
   .venv\Scripts\activate
   ```

   **En Linux / macOS:**

   ```bash
   source .venv/bin/activate
   ```

   > Deberías ver `(.venv)` al principio de tu línea de comandos, indicando que el entorno virtual está activo.

3. **Instala las dependencias del proyecto:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecuta las pruebas unitarias:**

   ```bash
   pytest
   ```

   > Deberías ver las pruebas pasando correctamente, validando la lógica del movimiento y el temporizador.

5. **¡A jugar!**

   ```bash
   python src/main.py
   ```

---

## 🧪 Desarrollo con Test Driven Development (TDD)

Este proyecto sigue estrictamente el ciclo **Rojo → Verde → Refactor**:

- 🔴 **Rojo:** Se escribe una prueba que falla porque la funcionalidad aún no existe.
- 🟢 **Verde:** Se implementa el código mínimo necesario para que la prueba pase.
- 🔵 **Refactor:** Se mejora y limpia el código sin cambiar su comportamiento, con la seguridad de que las pruebas lo respaldan.

### Ejemplo de Prueba Unitaria

Así se ve una prueba real del proyecto ubicada en `tests/test_core.py`:

python def test_player_can_move_to_empty_cell(): grid = Grid(width=5, height=5) player = Player(x=1, y=1)


---

## 🏗️ Arquitectura: Separación de Responsabilidades

El mayor desafío del TDD en videojuegos es aislar la lógica del renderizado.  
Este proyecto lo resuelve separando claramente la lógica del juego, la vista y las pruebas.

### Componentes principales

- **`src/models.py`**  
  Contiene el 100% de la lógica pura del juego, como `Grid`, `Player` y `GameState`.  
  No importa ninguna librería gráfica.

- **`src/main.py`**  
  Funciona como una vista sencilla.  
  Lee los datos de `models.py`, dibuja los elementos del juego y traduce las teclas en comandos.

- **`tests/test_core.py`**  
  Valida la lógica del juego en milisegundos, sin abrir ventanas ni depender de hardware gráfico.

Gracias a esta arquitectura, el motor gráfico pudo cambiarse de `arcade` a `pygame-ce` en minutos sin tocar una sola línea de la lógica principal del juego.

---

## 📁 Estructura del Proyecto

```text
puzzle_laberinto/
├── src/
│   ├── main.py
│   └── models.py
├── tests/
│   └── test_core.py
├── requirements.txt
├── README.md
└── LICENSE
```
---

## 🎯 Roadmap

Próximas mejoras planeadas para el proyecto:

- Implementar condición de victoria al detectar cuando el bloque está sobre la meta.
- Cargar niveles dinámicamente desde archivos externos, como `.json` o `.txt`.
- Añadir múltiples niveles con dificultad progresiva.
- Integrar efectos de sonido para movimiento, choque, victoria y game over.
- Reemplazar los cuadrados de colores por sprites reales.
- Añadir un menú principal.
- Añadir pantalla de reinicio.
- Mejorar la interfaz visual del temporizador.

---

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia **MIT**.

Puedes usarlo, modificarlo y aprender de él libremente.

---

## 👨‍💻 Autor

Desarrollado por **[TU_NOMBRE]** como proyecto práctico para dominar el desarrollo de videojuegos aplicando metodologías ágiles y **Test Driven Development**.

- 🔗 **GitHub:** [@TU_USUARIO](https://github.com/TU_USUARIO)
- 📧 **Contacto:** [tu-email@ejemplo.com](mailto:tu-email@ejemplo.com)

