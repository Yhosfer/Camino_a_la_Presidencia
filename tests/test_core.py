# tests/test_core.py
import pytest
from src.models import Grid, Player, Direction, TileType, GameState, load_level_from_file


# --- PRUEBAS DE MOVIMIENTO ---
def test_player_moves_to_empty_tile():
    grid = Grid(width=3, height=3)
    grid.set_tile(0, 0, TileType.PLAYER)
    grid.set_tile(1, 0, TileType.EMPTY)
    player = Player(x=0, y=0)
    success = player.move(Direction.RIGHT, grid)
    assert success is True
    assert player.x == 1
    assert grid.get_tile(0, 0) == TileType.EMPTY
    assert grid.get_tile(1, 0) == TileType.PLAYER


def test_player_successfully_pushes_block():
    grid = Grid(width=3, height=1)
    grid.set_tile(0, 0, TileType.PLAYER)
    grid.set_tile(1, 0, TileType.BLOCK)
    grid.set_tile(2, 0, TileType.EMPTY)
    player = Player(x=0, y=0)
    success = player.move(Direction.RIGHT, grid)
    assert success is True
    assert player.x == 1
    assert grid.get_tile(2, 0) == TileType.BLOCK


def test_player_cannot_push_block_into_wall():
    grid = Grid(width=3, height=1)
    grid.set_tile(0, 0, TileType.PLAYER)
    grid.set_tile(1, 0, TileType.BLOCK)
    grid.set_tile(2, 0, TileType.WALL)
    player = Player(x=0, y=0)
    initial_x = player.x
    success = player.move(Direction.RIGHT, grid)
    assert success is False
    assert player.x == initial_x


# --- PRUEBAS DEL TEMPORIZADOR ---
def test_game_timer_decreases_on_tick():
    state = GameState(time_left=10, status="PLAYING")
    for _ in range(10):
        state.tick()
    assert state.time_left == 0
    assert state.status == "GAME_OVER"


def test_game_stops_ticking_when_game_over():
    state = GameState(time_left=0, status="GAME_OVER")
    state.tick()
    assert state.time_left == 0


# --- PRUEBAS DE PROGRESO Y VICTORIA ---
def test_game_tracks_successful_moves():
    state = GameState(time_left=30, status="PLAYING", moves_count=0)
    grid = Grid(width=3, height=1)
    grid.set_tile(0, 0, TileType.PLAYER)
    grid.set_tile(1, 0, TileType.EMPTY)
    player = Player(x=0, y=0)
    if player.move(Direction.RIGHT, grid): state.increment_moves()
    grid.set_tile(2, 0, TileType.WALL)
    if player.move(Direction.RIGHT, grid): state.increment_moves()
    assert state.moves_count == 1


def test_game_detects_victory_when_block_reaches_goal():
    grid = Grid(width=3, height=1)
    grid.set_tile(0, 0, TileType.PLAYER)
    grid.set_tile(1, 0, TileType.BLOCK)
    grid.set_tile(2, 0, TileType.GOAL)
    player = Player(x=0, y=0)
    player.move(Direction.RIGHT, grid)
    assert grid.check_victory() is True
    assert grid.get_tile(2, 0) == TileType.BLOCK_ON_GOAL


# --- PRUEBAS DE PAUSA Y REINICIO ---
def test_pause_stops_timer_and_changes_state():
    state = GameState(time_left=10, status="PLAYING")
    state.toggle_pause()
    assert state.status == "PAUSE_MENU"
    state.tick()
    assert state.time_left == 10
    state.resume_game()
    assert state.status == "PLAYING"


def test_game_state_reset_restores_initial_values():
    state = GameState(time_left=5, status="GAME_OVER", moves_count=15)
    state.reset(initial_time=30)
    assert state.time_left == 30
    assert state.status == "PLAYING"
    assert state.moves_count == 0


def test_player_reset_position():
    player = Player(x=5, y=5)
    player.reset(1, 1)
    assert player.x == 1 and player.y == 1


# --- PRUEBAS DEL MENÚ PRINCIPAL ---
def test_game_starts_in_menu_and_transitions_to_playing():
    state = GameState(time_left=30)
    assert state.status == "MENU"
    state.tick()
    assert state.time_left == 30
    state.start_game()
    assert state.status == "PLAYING"
    state.tick()
    assert state.time_left == 29


def test_main_menu_has_quit_option():
    state = GameState(time_left=30, status="MENU")
    state.quit_game()
    assert state.status == "QUIT"


# --- PRUEBAS DE MÚLTIPLES NIVELES ---
def test_level_loader_reads_file_correctly(tmp_path):
    level_file = tmp_path / "test_level.txt"
    level_file.write_text("WWWWW\nW.P.W\nW.B.W\nW.G.W\nWWWWW")
    grid = Grid(width=5, height=5)
    player = Player(x=0, y=0)
    load_level_from_file(str(level_file), grid, player)
    assert grid.get_tile(2, 1) == TileType.PLAYER
    assert grid.get_tile(2, 2) == TileType.BLOCK
    assert grid.get_tile(2, 3) == TileType.GOAL


def test_level_transitions_on_victory():
    state = GameState(time_left=30, status="PLAYING", moves_count=5, current_level=1)
    state.advance_to_next_level(total_levels=3, initial_time=30)
    assert state.current_level == 2
    assert state.status == "PLAYING"


def test_game_completed_after_last_level():
    state = GameState(time_left=30, status="PLAYING", moves_count=10, current_level=3)
    state.advance_to_next_level(total_levels=3, initial_time=30)
    assert state.status == "JUEGO_COMPLETADO"


# --- PRUEBAS DEL SISTEMA UNDO (DESHACER) ---
def test_undo_restores_previous_state():
    grid = Grid(width=3, height=1)
    grid.set_tile(0, 0, TileType.PLAYER)
    grid.set_tile(1, 0, TileType.EMPTY)
    player = Player(x=0, y=0)
    state = GameState(time_left=30, status="PLAYING", moves_count=0, current_level=1)

    state.save_state(grid, player)
    player.move(Direction.RIGHT, grid)
    state.increment_moves()
    state.undo(grid, player)

    assert player.x == 0
    assert state.moves_count == 0
    assert grid.get_tile(0, 0) == TileType.PLAYER


def test_undo_does_nothing_when_history_empty():
    grid = Grid(width=3, height=1)
    grid.set_tile(0, 0, TileType.PLAYER)
    player = Player(x=0, y=0)
    state = GameState(time_left=30, status="PLAYING", moves_count=0, current_level=1)

    initial_x = player.x
    state.undo(grid, player)
    assert player.x == initial_x


def test_reset_clears_undo_history():
    grid = Grid(width=3, height=1)
    grid.set_tile(0, 0, TileType.PLAYER)
    grid.set_tile(1, 0, TileType.EMPTY)
    player = Player(x=0, y=0)
    state = GameState(time_left=30, status="PLAYING", moves_count=0, current_level=1)

    state.save_state(grid, player)
    player.move(Direction.RIGHT, grid)
    state.reset(initial_time=30)

    initial_x = player.x
    state.undo(grid, player)
    assert player.x == initial_x


# --- PRUEBAS DEL SISTEMA DE PORTALES ---

def test_player_teleports_through_blue_portal():
    grid = Grid(width=7, height=7)
    grid.set_tile(1, 1, TileType.PLAYER)
    grid.set_tile(1, 2, TileType.PORTAL_BLUE)
    grid.set_tile(5, 5, TileType.PORTAL_BLUE)
    player = Player(x=1, y=1)

    player.move(Direction.DOWN, grid)

    assert player.x == 5
    assert player.y == 5


def test_player_teleports_through_red_portal():
    grid = Grid(width=7, height=7)
    grid.set_tile(3, 3, TileType.PLAYER)
    grid.set_tile(3, 4, TileType.PORTAL_RED)
    grid.set_tile(6, 6, TileType.PORTAL_RED)
    player = Player(x=3, y=3)

    player.move(Direction.DOWN, grid)

    assert player.x == 6
    assert player.y == 6


def test_block_cannot_use_portals():
    # Arrange: Bloque junto a un portal
    grid = Grid(width=7, height=7)
    grid.set_tile(2, 2, TileType.PLAYER)
    grid.set_tile(2, 3, TileType.BLOCK)
    grid.set_tile(2, 4, TileType.PORTAL_BLUE)
    grid.set_tile(5, 5, TileType.PORTAL_BLUE)
    player = Player(x=2, y=2)

    # Act: Jugador empuja bloque hacia el portal
    player.move(Direction.DOWN, grid)

    # Assert: El bloque NO se mueve al portal (se queda en 2,3) y el portal sigue en 2,4
    assert grid.get_tile(2, 3) == TileType.BLOCK
    assert grid.get_tile(2, 4) == TileType.PORTAL_BLUE
    assert player.x == 2  # El jugador tampoco se movió porque el bloque no cedió


def test_portal_does_not_teleport_if_destination_is_blocked():
    # Arrange: Portal de salida bloqueado por una pared
    grid = Grid(width=7, height=7)
    grid.set_tile(1, 1, TileType.PLAYER)
    grid.set_tile(1, 2, TileType.PORTAL_BLUE)
    # El destino (5,5) es una pared, no un portal válido para salir
    grid.set_tile(5, 5, TileType.WALL)
    player = Player(x=1, y=1)

    # Act: Jugador intenta entrar al portal
    player.move(Direction.DOWN, grid)

    # Assert: Jugador NO se mueve porque el portal está "roto" (sin salida válida)
    assert player.x == 1
    assert player.y == 1


# --- PRUEBAS DE RESTAURACIÓN DE CASILLAS PISADAS Y EMPUJE EN METAS ---
def test_player_stepping_on_and_off_goal_restores_goal():
    grid = Grid(width=3, height=3)
    grid.set_tile(0, 0, TileType.PLAYER)
    grid.set_tile(1, 0, TileType.GOAL)
    grid.set_tile(2, 0, TileType.EMPTY)
    player = Player(x=0, y=0)

    # Move onto goal
    player.move(Direction.RIGHT, grid)
    assert player.x == 1
    assert grid.get_tile(1, 0) == TileType.PLAYER
    assert grid.get_tile(0, 0) == TileType.EMPTY

    # Move off goal
    player.move(Direction.RIGHT, grid)
    assert player.x == 2
    assert grid.get_tile(2, 0) == TileType.PLAYER
    assert grid.get_tile(1, 0) == TileType.GOAL


def test_player_stepping_on_and_off_portal_restores_portal():
    grid = Grid(width=5, height=5)
    grid.set_tile(0, 0, TileType.PLAYER)
    grid.set_tile(1, 0, TileType.PORTAL_BLUE)
    grid.set_tile(3, 3, TileType.PORTAL_BLUE)
    grid.set_tile(3, 4, TileType.EMPTY)
    player = Player(x=0, y=0)

    # Teleport to (3,3)
    player.move(Direction.RIGHT, grid)
    assert player.x == 3
    assert player.y == 3
    assert grid.get_tile(3, 3) == TileType.PLAYER
    assert grid.get_tile(1, 0) == TileType.PORTAL_BLUE # original remains

    # Step off (3,3)
    player.move(Direction.RIGHT, grid)
    assert player.x == 4
    assert player.y == 3
    assert grid.get_tile(3, 3) == TileType.PORTAL_BLUE # restored destination portal


def test_player_pushes_block_on_goal():
    grid = Grid(width=4, height=1)
    grid.set_tile(0, 0, TileType.PLAYER)
    grid.set_tile(1, 0, TileType.BLOCK_ON_GOAL)
    grid.set_tile(2, 0, TileType.GOAL)
    grid.set_tile(3, 0, TileType.EMPTY)
    player = Player(x=0, y=0)

    # Push block_on_goal to goal
    success = player.move(Direction.RIGHT, grid)
    assert success is True
    assert player.x == 1
    # Player is now on the first goal, block is on second goal
    assert grid.get_tile(1, 0) == TileType.PLAYER
    assert player.standing_on == TileType.GOAL
    assert grid.get_tile(2, 0) == TileType.BLOCK_ON_GOAL

    # Push again onto empty
    success = player.move(Direction.RIGHT, grid)
    assert success is True
    assert player.x == 2
    # Player is on second goal, block is on empty space
    assert grid.get_tile(2, 0) == TileType.PLAYER
    assert player.standing_on == TileType.GOAL
    assert grid.get_tile(3, 0) == TileType.BLOCK
    # First goal is restored
    assert grid.get_tile(1, 0) == TileType.GOAL