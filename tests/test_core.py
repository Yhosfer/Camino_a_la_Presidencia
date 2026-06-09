# tests/test_core.py
import pytest
from src.models import Grid, Player, Direction, TileType, GameState


# --- PRUEBAS DE MOVIMIENTO ---
# Validacion de la funcionalidad de navegación en el tablero y estados
def test_player_moves_to_empty_tile():
    grid = Grid(width=3, height=3) # se crea el tablero
    grid.set_tile(0, 0, TileType.PLAYER) # jugador en cordenadas 0,0
    grid.set_tile(1, 0, TileType.EMPTY) # dejamos la casilla vacia

    player = Player(x=0, y=0)
    success = player.move(Direction.RIGHT, grid) # mover a la derecha

    assert success is True # verificar si fue exitoso
    assert player.x == 1  # cordenadas actualizadas
    assert player.y == 0
    # casillas anteriores marcadas como Empty
    assert grid.get_tile(0, 0) == TileType.EMPTY
    assert grid.get_tile(1, 0) == TileType.PLAYER

# Validación de impedimento de acciones
def test_player_successfully_pushes_block():
    grid = Grid(width=3, height=1)
    grid.set_tile(0, 0, TileType.PLAYER) # jugador en 0,0
    grid.set_tile(1, 0, TileType.BLOCK) # Bloque en 1,0
    grid.set_tile(2, 0, TileType.EMPTY) # vacio en 2,0

    player = Player(x=0, y=0)
    # jugador se mueve a la derecha
    success = player.move(Direction.RIGHT, grid)

    assert success is True # verifica movimiento exitoso
    assert player.x == 1 # cordenada actualizada
    #cambios de estado
    assert grid.get_tile(1, 0) == TileType.PLAYER
    assert grid.get_tile(2, 0) == TileType.BLOCK

# Validación de impedimento de acciones
def test_player_cannot_push_block_into_wall():
    grid = Grid(width=3, height=1)
    grid.set_tile(0, 0, TileType.PLAYER) # jugador en 0,0
    grid.set_tile(1, 0, TileType.BLOCK) # Bloque en 1,0
    grid.set_tile(2, 0, TileType.WALL) # Pared en 2,0

    player = Player(x=0, y=0)
    initial_x = player.x
    # jugador se mueve a la derecha
    success = player.move(Direction.RIGHT, grid)

    assert success is False # movimiento fallido
    assert player.x == initial_x # se mantiene el mismo lugar
    # estados sin variación
    assert grid.get_tile(1, 0) == TileType.BLOCK
    assert grid.get_tile(2, 0) == TileType.WALL


# --- PRUEBAS DEL TEMPORIZADOR ---
# validar que el progreso y la condicion de derrota
def test_game_timer_decreases_on_tick():
    # estado del juego con 10s y estado "Jugando"
    state = GameState(time_left=10)
    assert state.status == "PLAYING"
    # simulamos el paso del tiempo
    for _ in range(10):
        state.tick()
    # entonces
    # verificamos tiempo 0 y estado "game over"
    assert state.time_left == 0
    assert state.status == "GAME_OVER"

# verificar tiempos no invalidos
def test_game_stops_ticking_when_game_over():
    state = GameState(time_left=0, status="GAME_OVER")
    state.tick()

    assert state.time_left == 0  # No debe bajar a negativos
    assert state.status == "GAME_OVER"
