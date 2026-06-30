# src/models.py
import copy
from enum import Enum

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class TileType(Enum):
    EMPTY = 0
    WALL = 1
    BLOCK = 2
    PLAYER = 3
    GOAL = 4
    BLOCK_ON_GOAL = 5
    PORTAL_BLUE = 6
    PORTAL_RED = 7

class Grid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles = [[TileType.EMPTY for _ in range(width)] for _ in range(height)]

    def set_tile(self, x: int, y: int, tile_type: TileType) -> None:
        self.tiles[y][x] = tile_type

    def get_tile(self, x: int, y: int) -> TileType:
        return self.tiles[y][x]

    def check_victory(self) -> bool:
        """Victoria solo cuando TODAS las metas estan cubiertas y no quedan bloques sueltos."""
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                # Si queda alguna meta vacia o algun bloque sin colocar, no hay victoria
                if tile in (TileType.GOAL, TileType.BLOCK):
                    return False
        # Debe haber al menos un BLOCK_ON_GOAL para que sea una victoria real
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x] == TileType.BLOCK_ON_GOAL:
                    return True
        return False

    def clear(self) -> None:
        self.tiles = [[TileType.EMPTY for _ in range(self.width)] for _ in range(self.height)]

    def find_connected_portal(self, portal_type: TileType, current_x: int, current_y: int):
        """Busca el otro portal del mismo color y devuelve sus coordenadas (x, y)"""
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x] == portal_type and (x, y) != (current_x, current_y):
                    return (x, y)
        return None

class Player:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.standing_on = TileType.EMPTY

    def reset(self, initial_x: int, initial_y: int) -> None:
        self.x = initial_x
        self.y = initial_y
        self.standing_on = TileType.EMPTY

    def move(self, direction: Direction, grid: 'Grid') -> bool:
        dx, dy = direction.value
        new_x = self.x + dx
        new_y = self.y + dy

        # 1. Verificar límites del tablero
        if not (0 <= new_x < grid.width and 0 <= new_y < grid.height):
            return False

        target_tile = grid.get_tile(new_x, new_y)

        # 2. LÓGICA DE PORTALES (Solo el jugador puede usarlos)
        if target_tile in (TileType.PORTAL_BLUE, TileType.PORTAL_RED):
            destination = grid.find_connected_portal(target_tile, new_x, new_y)
            if destination:
                dest_x, dest_y = destination
                dest_tile = grid.get_tile(dest_x, dest_y)
                # El destino debe estar libre (EMPTY, GOAL) o ser el otro portal
                if dest_tile in (TileType.EMPTY, TileType.GOAL, TileType.PORTAL_BLUE, TileType.PORTAL_RED):
                    grid.set_tile(self.x, self.y, self.standing_on)
                    self.x = dest_x
                    self.y = dest_y
                    self.standing_on = dest_tile
                    grid.set_tile(self.x, self.y, TileType.PLAYER)
                    return True
            # Si no hay destino o está bloqueado por pared/bloque, el jugador NO se mueve
            return False

        # 3. Movimiento normal a casilla vacía o meta
        if target_tile in (TileType.EMPTY, TileType.GOAL):
            grid.set_tile(self.x, self.y, self.standing_on)
            self.x = new_x
            self.y = new_y
            self.standing_on = target_tile
            grid.set_tile(self.x, self.y, TileType.PLAYER)
            return True

        # 4. Intentar empujar un bloque
        elif target_tile in (TileType.BLOCK, TileType.BLOCK_ON_GOAL):
            block_new_x = new_x + dx
            block_new_y = new_y + dy

            if not (0 <= block_new_x < grid.width and 0 <= block_new_y < grid.height):
                return False

            block_target_tile = grid.get_tile(block_new_x, block_new_y)

            # El bloque solo se mueve a EMPTY o GOAL (Nunca a PORTAL o WALL)
            if block_target_tile in (TileType.EMPTY, TileType.GOAL):
                grid.set_tile(self.x, self.y, self.standing_on)
                self.x = new_x
                self.y = new_y
                self.standing_on = TileType.GOAL if target_tile == TileType.BLOCK_ON_GOAL else TileType.EMPTY
                grid.set_tile(self.x, self.y, TileType.PLAYER)

                new_block_type = TileType.BLOCK_ON_GOAL if block_target_tile == TileType.GOAL else TileType.BLOCK
                grid.set_tile(block_new_x, block_new_y, new_block_type)
                return True

        return False

class GameState:
    def __init__(self, time_left: int, status: str = "MENU", moves_count: int = 0, current_level: int = 1):
        self.time_left = time_left
        self.status = status
        self.moves_count = moves_count
        self.current_level = current_level
        self.history = []

    def increment_moves(self) -> None:
        self.moves_count += 1

    def save_state(self, grid: 'Grid', player: 'Player') -> None:
        snapshot = {
            'time_left': self.time_left,
            'status': self.status,
            'moves_count': self.moves_count,
            'current_level': self.current_level,
            'player_x': player.x,
            'player_y': player.y,
            'player_standing_on': player.standing_on,
            'grid_tiles': copy.deepcopy(grid.tiles)
        }
        self.history.append(snapshot)

    def undo(self, grid: 'Grid', player: 'Player') -> None:
        if not self.history:
            return

        snapshot = self.history.pop()
        self.time_left = snapshot['time_left']
        self.status = snapshot['status']
        self.moves_count = snapshot['moves_count']
        self.current_level = snapshot['current_level']
        player.x = snapshot['player_x']
        player.y = snapshot['player_y']
        player.standing_on = snapshot.get('player_standing_on', TileType.EMPTY)
        grid.tiles = copy.deepcopy(snapshot['grid_tiles'])

    def start_game(self) -> None:
        self.status = "PLAYING"
        self.current_level = 1
        self.history.clear()

    def quit_game(self) -> None:
        self.status = "QUIT"

    def toggle_pause(self) -> None:
        if self.status == "PLAYING":
            self.status = "PAUSE_MENU"
        elif self.status == "PAUSE_MENU":
            self.status = "PLAYING"

    def resume_game(self) -> None:
        self.status = "PLAYING"

    def return_to_main_menu(self, initial_time: int) -> None:
        self.time_left = initial_time
        self.status = "MENU"
        self.moves_count = 0
        self.current_level = 1
        self.history.clear()

    def reset(self, initial_time: int) -> None:
        self.time_left = initial_time
        self.status = "PLAYING"
        self.moves_count = 0
        self.history.clear()

    def advance_to_next_level(self, total_levels: int, initial_time: int) -> None:
        if self.current_level < total_levels:
            self.current_level += 1
            self.time_left = initial_time
            self.status = "PLAYING"
            self.moves_count = 0
            self.history.clear()
        else:
            self.status = "JUEGO_COMPLETADO"

    def tick(self) -> None:
        if self.status == "PLAYING":
            self.time_left -= 1
            if self.time_left <= 0:
                self.time_left = 0
                self.status = "GAME_OVER"

def load_level_from_file(file_path: str, grid: 'Grid', player: 'Player') -> None:
    """Carga un nivel desde un archivo de texto"""
    grid.clear()

    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char == 'W':
                grid.set_tile(x, y, TileType.WALL)
            elif char == 'B':
                grid.set_tile(x, y, TileType.BLOCK)
            elif char == 'G':
                grid.set_tile(x, y, TileType.GOAL)
            elif char == 'P':
                grid.set_tile(x, y, TileType.PLAYER)
                player.x = x
                player.y = y
                player.standing_on = TileType.EMPTY
            elif char == '.':
                grid.set_tile(x, y, TileType.EMPTY)
            elif char == 'X':
                grid.set_tile(x, y, TileType.PORTAL_BLUE)
            elif char == 'Y':
                grid.set_tile(x, y, TileType.PORTAL_RED)