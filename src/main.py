# src/main.py
import pygame
import sys
from src.models import Grid, Player, Direction, TileType, GameState

# --- CONSTANTES DE VISUALIZACIÓN ---
TILE_SIZE = 64
GRID_WIDTH = 5
GRID_HEIGHT = 5
UI_HEIGHT = 50  # Espacio arriba para el temporizador
SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE + UI_HEIGHT
TITLE = "Puzzle Laberinto TDD - Semana 1"
FPS = 60

# Mapeo de tipos de casilla a colores (Formato RGB)
COLORS = {
    TileType.EMPTY: (47, 79, 79),  # Gris oscuro (Dark Slate Gray)
    TileType.WALL: (128, 128, 128),  # Gris (Pared)
    TileType.BLOCK: (139, 69, 19),  # Marrón (Bloque)
    TileType.PLAYER: (30, 144, 255),  # Azul brillante (Jugador)
    TileType.GOAL: (50, 205, 50)  # Verde lima (Meta)
}


def setup_level(grid: Grid, player: Player):
    """Carga un nivel simple usando caracteres para facilitar la lectura"""
    # P = Player, W = Wall, B = Block, G = Goal, . = Empty
    level_design = [
        "WWWWW",
        "W.P.W",
        "W.B.W",
        "W.G.W",
        "WWWWW"
    ]

    for y, row in enumerate(level_design):
        for x, char in enumerate(row):
            if char == 'W':
                grid.set_tile(x, y, TileType.WALL)
            elif char == 'B':
                grid.set_tile(x, y, TileType.BLOCK)
            elif char == 'G':
                grid.set_tile(x, y, TileType.GOAL)
            elif char == '.':
                grid.set_tile(x, y, TileType.EMPTY)

    # Aseguramos que el grid sepa dónde está el jugador visualmente
    grid.set_tile(player.x, player.y, TileType.PLAYER)


def main():
    # 1. INICIALIZAR PYGAME
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # Fuentes para el texto
    font = pygame.font.SysFont(None, 36)
    big_font = pygame.font.SysFont(None, 72)

    # 2. INSTANCIAR LA LÓGICA (¡Nada de reglas aquí!)
    grid = Grid(width=GRID_WIDTH, height=GRID_HEIGHT)
    player = Player(x=1, y=1)
    game_state = GameState(time_left=30)  # 30 segundos para probar

    # 3. CONFIGURAR NIVEL
    setup_level(grid, player)

    time_accumulator = 0.0

    # --- BUCLE PRINCIPAL DEL JUEGO ---
    running = True
    while running:
        # A. MANEJO DE EVENTOS (Teclado y Cerrar Ventana)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and game_state.status == "PLAYING":
                direction = None
                if event.key in (pygame.K_UP, pygame.K_w):
                    direction = Direction.UP
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    direction = Direction.DOWN
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    direction = Direction.LEFT
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    direction = Direction.RIGHT

                if direction:
                    # ¡MAGIA DEL TDD! Llamamos al método que ya probamos con pytest.
                    player.move(direction, grid)

        # B. ACTUALIZACIÓN DE LÓGICA (Solo el temporizador)
        # clock.tick() devuelve los milisegundos que pasaron desde el último frame
        delta_time = clock.tick(FPS) / 1000.0

        if game_state.status == "PLAYING":
            time_accumulator += delta_time
            if time_accumulator >= 1.0:
                game_state.tick()
                time_accumulator -= 1.0

        # C. DIBUJADO EN PANTALLA
        screen.fill((0, 0, 0))  # Limpiar pantalla con negro

        # Dibujar el tablero (desplazado hacia abajo por UI_HEIGHT)
        for y in range(grid.height):
            for x in range(grid.width):
                tile = grid.get_tile(x, y)
                color = COLORS.get(tile, (255, 255, 255))

                # pygame.Rect(x, y, ancho, alto)
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE + UI_HEIGHT, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 2)  # Borde negro de 2px

        # Dibujar Interfaz de Usuario (UI)
        time_text = font.render(f"Tiempo: {game_state.time_left}s", True, (255, 255, 255))
        screen.blit(time_text, (10, 10))

        # Pantalla de Game Over
        if game_state.status == "GAME_OVER":
            # Fondo semi-transparente
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))
            screen.blit(s, (0, 0))

            go_text = big_font.render("TIEMPO AGOTADO", True, (255, 0, 0))
            text_rect = go_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(go_text, text_rect)

        # Actualizar la pantalla
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()