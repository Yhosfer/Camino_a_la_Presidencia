# src/models.py
from enum import Enum
from typing import Tuple


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


class Grid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # Inicializamos el tablero con celdas vacías
        self.tiles = [[TileType.EMPTY for _ in range(width)] for _ in range(height)]

    def set_tile(self, x: int, y: int, tile_type: TileType) -> None:
        self.tiles[y][x] = tile_type

    def get_tile(self, x: int, y: int) -> TileType:
        return self.tiles[y][x]


class Player:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def move(self, direction: Direction, grid: Grid) -> bool:
        dx, dy = direction.value
        new_x = self.x + dx
        new_y = self.y + dy

        # 1. Verificar límites del tablero
        if not (0 <= new_x < grid.width and 0 <= new_y < grid.height):
            return False

        target_tile = grid.get_tile(new_x, new_y)

        # 2. Movimiento a casilla vacía (o meta, por simplicidad en este avance)
        if target_tile in (TileType.EMPTY, TileType.GOAL):
            grid.set_tile(self.x, self.y, TileType.EMPTY)
            self.x = new_x
            self.y = new_y
            grid.set_tile(self.x, self.y, TileType.PLAYER)
            return True

        # 3. Intentar empujar un bloque
        elif target_tile == TileType.BLOCK:
            block_new_x = new_x + dx
            block_new_y = new_y + dy

            # Verificar que el bloque no salga del tablero
            if not (0 <= block_new_x < grid.width and 0 <= block_new_y < grid.height):
                return False

            block_target_tile = grid.get_tile(block_new_x, block_new_y)

            # El bloque solo se puede empujar a casillas vacías o metas
            if block_target_tile in (TileType.EMPTY, TileType.GOAL):
                # 1. Limpiar la posición antigua del jugador
                grid.set_tile(self.x, self.y, TileType.EMPTY)

                # 2. Actualizar coordenadas del jugador y colocarlo donde estaba el bloque
                self.x = new_x
                self.y = new_y
                grid.set_tile(self.x, self.y, TileType.PLAYER)

                # 3. Colocar el bloque en su nueva posición definitiva
                grid.set_tile(block_new_x, block_new_y, TileType.BLOCK)

                return True

        # 4. Cualquier otro caso (Pared, otro bloque, etc.) es movimiento inválido
        return False


class GameState:
    def __init__(self, time_left: int, status: str = "PLAYING"):
        self.time_left = time_left
        self.status = status

    def tick(self) -> None:
        if self.status == "PLAYING":
            self.time_left -= 1
            if self.time_left <= 0:
                self.time_left = 0
                self.status = "GAME_OVER"