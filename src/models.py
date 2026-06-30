# src/models.py
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
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x] == TileType.BLOCK_ON_GOAL:
                    return True
        return False

    def clear(self) -> None:
        """Limpia el tablero para poder reiniciar el nivel"""
        self.tiles = [[TileType.EMPTY for _ in range(self.width)] for _ in range(self.height)]


class Player:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def reset(self, initial_x: int, initial_y: int) -> None:
        self.x = initial_x
        self.y = initial_y

    def move(self, direction: Direction, grid: 'Grid') -> bool:
        dx, dy = direction.value
        new_x = self.x + dx
        new_y = self.y + dy

        if not (0 <= new_x < grid.width and 0 <= new_y < grid.height):
            return False

        target_tile = grid.get_tile(new_x, new_y)

        if target_tile in (TileType.EMPTY, TileType.GOAL):
            grid.set_tile(self.x, self.y, TileType.EMPTY)
            self.x = new_x
            self.y = new_y
            grid.set_tile(self.x, self.y, TileType.PLAYER)
            return True

        elif target_tile == TileType.BLOCK:
            block_new_x = new_x + dx
            block_new_y = new_y + dy

            if not (0 <= block_new_x < grid.width and 0 <= block_new_y < grid.height):
                return False

            block_target_tile = grid.get_tile(block_new_x, block_new_y)

            if block_target_tile in (TileType.EMPTY, TileType.GOAL):
                grid.set_tile(self.x, self.y, TileType.EMPTY)
                self.x = new_x
                self.y = new_y
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

    def increment_moves(self) -> None:
        self.moves_count += 1

    def start_game(self) -> None:
        self.status = "PLAYING"
        self.current_level = 1

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

    def reset(self, initial_time: int) -> None:
        self.time_left = initial_time
        self.status = "PLAYING"
        self.moves_count = 0

    def advance_to_next_level(self, total_levels: int, initial_time: int) -> None:
        """Avanza al siguiente nivel o completa el juego"""
        if self.current_level < total_levels:
            self.current_level += 1
            self.time_left = initial_time
            self.status = "PLAYING"
            self.moves_count = 0
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
        lines = f.readlines()

    for y, line in enumerate(lines):
        line = line.strip()
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
            elif char == '.':
                grid.set_tile(x, y, TileType.EMPTY)

