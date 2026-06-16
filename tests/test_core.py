# tests/test_core.py
import pytest
from src.models import Grid, Player, Direction, TileType, GameState


# ==============================================================================
# --- PRUEBAS DE MOVIMIENTO ---
# ==============================================================================

def test_player_moves_to_empty_tile():
    # Arrange: se crea el tablero
    grid = Grid(width=3, height=3)
    grid.set_tile(0, 0, TileType.PLAYER)  # jugador en coordenadas 0,0
    grid.set_tile(1, 0, TileType.EMPTY)  # dejamos la casilla vacía

    player = Player(x=0, y=0)

    # Act: mover a la derecha
    success = player.move(Direction.RIGHT, grid)

    # Assert: verificar si fue exitoso y coordenadas actualizadas
    assert success is True
    assert player.x == 1
    assert player.y == 0
    # casillas anteriores marcadas como Empty / Player
    assert grid.get_tile(0, 0) == TileType.EMPTY
    assert grid.get_tile(1, 0) == TileType.PLAYER


def test_player_successfully_pushes_block():
    # Arrange
    grid = Grid(width=3, height=1)
    grid.set_tile(0, 0, TileType.PLAYER)  # jugador en 0,0
    grid.set_tile(1, 0, TileType.BLOCK)  # Bloque en 1,0
    grid.set_tile(2, 0, TileType.EMPTY)  # vacío en 2,0

    player = Player(x=0, y=0)

    # Act: jugador se mueve a la derecha
    success = player.move(Direction.RIGHT, grid)

    # Assert: verifica movimiento exitoso y cambios de estado
    assert success is True
    assert player.x == 1
    assert grid.get_tile(1, 0) == TileType.PLAYER
    assert grid.get_tile(2, 0) == TileType.BLOCK


def test_player_cannot_push_block_into_wall():
    # Arrange
    grid = Grid(width=3, height=1)
    grid.set_tile(0, 0, TileType.PLAYER)  # jugador en 0,0
    grid.set_tile(1, 0, TileType.BLOCK)  # Bloque en 1,0
    grid.set_tile(2, 0, TileType.WALL)  # Pared en 2,0

    player = Player(x=0, y=0)
    initial_x = player.x

    # Act: jugador se mueve a la derecha
    success = player.move(Direction.RIGHT, grid)

    # Assert: movimiento fallido, estados sin variación
    assert success is False
    assert player.x == initial_x
    assert grid.get_tile(1, 0) == TileType.BLOCK
    assert grid.get_tile(2, 0) == TileType.WALL


# ==============================================================================
# --- PRUEBAS DEL TEMPORIZADOR ---
# ==============================================================================

def test_game_timer_decreases_on_tick():
    # Arrange: estado del juego con 10s y estado EXPLÍCITO "PLAYING"
    state = GameState(time_left=10, status="PLAYING")  # <-- AQUÍ ESTÁ EL CAMBIO
    assert state.status == "PLAYING"

    # Act: simulamos el paso del tiempo
    for _ in range(10):
        state.tick()

    # Assert: verificamos tiempo 0 y estado "GAME_OVER"
    assert state.time_left == 0
    assert state.status == "GAME_OVER"


def test_game_stops_ticking_when_game_over():
    # Arrange
    state = GameState(time_left=0, status="GAME_OVER")

    # Act
    state.tick()

    # Assert: No debe bajar a negativos
    assert state.time_left == 0
    assert state.status == "GAME_OVER"


# ==============================================================================
# --- PRUEBAS DE PROGRESO Y VICTORIA ---
# ==============================================================================

def test_game_tracks_successful_moves():
    # Arrange: Un estado de juego EXPLÍCITAMENTE en PLAYING
    state = GameState(time_left=30, status="PLAYING", moves_count=0)
    grid = Grid(width=3, height=1)
    grid.set_tile(0, 0, TileType.PLAYER)
    grid.set_tile(1, 0, TileType.EMPTY)
    player = Player(x=0, y=0)

    # Act 1: El jugador se mueve exitosamente
    success = player.move(Direction.RIGHT, grid)
    if success:
        state.increment_moves()

    # Act 2: El jugador intenta moverse contra una pared (falla)
    grid.set_tile(2, 0, TileType.WALL)
    success_fail = player.move(Direction.RIGHT, grid)
    if success_fail:
        state.increment_moves()

    # Assert: El contador solo aumenta con movimientos válidos
    assert state.moves_count == 1
    assert success is True
    assert success_fail is False


def test_game_detects_victory_when_block_reaches_goal():
    # Arrange: Un tablero donde la meta está en (2,0)
    grid = Grid(width=3, height=1)
    grid.set_tile(0, 0, TileType.PLAYER)
    grid.set_tile(1, 0, TileType.BLOCK)
    grid.set_tile(2, 0, TileType.GOAL)  # La meta está aquí
    player = Player(x=0, y=0)
    state = GameState(time_left=30, status="PLAYING")

    # Act: El jugador empuja el bloque hacia la derecha (hacia la meta)
    player.move(Direction.RIGHT, grid)

    # Assert: El juego detecta que el bloque está en la meta
    has_won = grid.check_victory()
    assert has_won is True
    assert grid.get_tile(2, 0) == TileType.BLOCK_ON_GOAL



# --- PRUEBAS DE PAUSA Y REINICIO ---

def test_pause_stops_timer_and_changes_state():
    # Arrange
    state = GameState(time_left=10, status="PLAYING")

    # Act: Pausar
    state.toggle_pause()

    # Assert: Estado cambia y el tiempo no baja al hacer tick
    assert state.status == "PAUSED"
    state.tick()
    assert state.time_left == 10

    # Act: Reanudar
    state.toggle_pause()

    # Assert
    assert state.status == "PLAYING"


def test_game_state_reset_restores_initial_values():
    # Arrange: Un juego que ya se usó (tiempo bajo, muchos movimientos, game over)
    state = GameState(time_left=5, status="GAME_OVER", moves_count=15)

    # Act: Reiniciar con tiempo inicial de 30
    state.reset(initial_time=30)

    # Assert: Todo vuelve a cero o al valor inicial
    assert state.time_left == 30
    assert state.status == "PLAYING"
    assert state.moves_count == 0

def test_player_reset_position():
    # Arrange
    player = Player(x=5, y=5)

    # Act: Reiniciar a posición inicial (1, 1)
    player.reset(1, 1)

    # Assert
    assert player.x == 1
    assert player.y == 1


# --- PRUEBAS DEL MENÚ PRINCIPAL ---
def test_game_starts_in_menu_and_transitions_to_playing():
    # Arrange: Un nuevo estado de juego (por defecto debería ser MENU)
    state = GameState(time_left=30)
    assert state.status == "MENU"

    # Act/Assert: El tiempo NO debe bajar en el menú
    state.tick()
    assert state.time_left == 30

    state.start_game()

    # Assert: El estado cambia a PLAYING y el tiempo ahora sí baja
    assert state.status == "PLAYING"
    state.tick()
    assert state.time_left == 29
