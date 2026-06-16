# src/main.py
import pygame
import sys
from src.models import Grid, Player, Direction, TileType, GameState

# --- CONSTANTES DEL JUEGO (Lógica) ---
GRID_WIDTH = 5
GRID_HEIGHT = 5
TITLE = "Puzzle Laberinto TDD - Pantalla Completa"
FPS = 60

# Colores
COLORS = {
    TileType.EMPTY: (47, 79, 79),
    TileType.WALL: (128, 128, 128),
    TileType.BLOCK: (139, 69, 19),
    TileType.PLAYER: (30, 144, 255),
    TileType.GOAL: (50, 205, 50),
    TileType.BLOCK_ON_GOAL: (255, 215, 0)  # Dorado
}

INITIAL_PLAYER_X, INITIAL_PLAYER_Y = 1, 1
INITIAL_TIME = 30


def setup_level(grid: Grid, player: Player):
    grid.clear()
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

    grid.set_tile(player.x, player.y, TileType.PLAYER)


def draw_controls(screen, font, monitor_width, monitor_height):
    """Dibuja la leyenda de controles centrada en la parte inferior"""
    controls_text = "CONTROLES: [Flechas/WASD] Mover  |  [P] Pausa  |  [R] Reiniciar  |  [ESC] Salir"
    text_surface = font.render(controls_text, True, (200, 200, 200))
    text_rect = text_surface.get_rect(center=(monitor_width // 2, monitor_height - 30))
    screen.blit(text_surface, text_rect)


def main():
    pygame.init()

    # 1. OBTENER RESOLUCIÓN DEL MONITOR Y ACTIVAR PANTALLA COMPLETA
    info = pygame.display.Info()
    monitor_width = info.current_w
    monitor_height = info.current_h

    # pygame.FULLSCREEN ocupa toda la pantalla.
    # (Opcional: puedes usar pygame.MAXIMIZED si prefieres ventana maximizada con barra de tareas)
    screen = pygame.display.set_mode((monitor_width, monitor_height), pygame.FULLSCREEN)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # 2. CÁLCULO DINÁMICO DE TAMAÑOS (Para que se vea bien en cualquier monitor)
    # Reservamos 80% del ancho y 70% del alto para el tablero, el resto para HUD y controles
    max_tile_w = int((monitor_width * 0.8) // GRID_WIDTH)
    max_tile_h = int((monitor_height * 0.7) // GRID_HEIGHT)

    # El tamaño de la celda será el menor de los dos para mantener la cuadrícula cuadrada
    TILE_SIZE = min(max_tile_w, max_tile_h)

    # Ajustamos el tamaño de la fuente en base al tamaño de la celda para que sea legible
    font_size = max(24, TILE_SIZE // 2)
    font_small = pygame.font.SysFont(None, font_size)
    font_medium = pygame.font.SysFont(None, int(font_size * 1.5))
    font_big = pygame.font.SysFont(None, int(font_size * 2.5))

    # Calcular offsets para centrar el tablero perfectamente en la pantalla
    grid_width_px = TILE_SIZE * GRID_WIDTH
    grid_height_px = TILE_SIZE * GRID_HEIGHT
    offset_x = (monitor_width - grid_width_px) // 2
    offset_y = (monitor_height - grid_height_px) // 2 + (font_size)  # Un poco más abajo para el HUD

    # 3. INSTANCIAR LÓGICA (¡Intacta y probada con TDD!)
    grid = Grid(width=GRID_WIDTH, height=GRID_HEIGHT)
    player = Player(x=INITIAL_PLAYER_X, y=INITIAL_PLAYER_Y)
    game_state = GameState(time_left=INITIAL_TIME, moves_count=0)
    setup_level(grid, player)

    time_accumulator = 0.0
    running = True

    while running:
        # A. MANEJO DE EVENTOS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # 1. Salir del juego (CRUCIAL en pantalla completa)
                if event.key == pygame.K_ESCAPE:
                    running = False

                # 2. Iniciar juego desde el Menú
                elif game_state.status == "MENU" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game_state.start_game()

                # 3. Reinicio (Tecla R)
                elif event.key == pygame.K_r and game_state.status != "MENU":
                    game_state.reset(INITIAL_TIME)
                    player.reset(INITIAL_PLAYER_X, INITIAL_PLAYER_Y)
                    setup_level(grid, player)

                # 4. Pausa (Tecla P)
                elif event.key == pygame.K_p and game_state.status != "MENU":
                    game_state.toggle_pause()

                # 5. Movimiento (Solo si está en PLAYING)
                elif game_state.status == "PLAYING":
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
                        if player.move(direction, grid):
                            game_state.increment_moves()
                            if grid.check_victory():
                                game_state.status = "VICTORIA"

        # B. ACTUALIZACIÓN DE LÓGICA
        delta_time = clock.tick(FPS) / 1000.0
        if game_state.status == "PLAYING":
            time_accumulator += delta_time
            if time_accumulator >= 1.0:
                game_state.tick()
                time_accumulator -= 1.0

        # C. DIBUJADO
        screen.fill((20, 20, 30))  # Fondo oscuro elegante

        # 1. Dibujar Menú Principal
        if game_state.status == "MENU":
            title = font_big.render("PUZZLE LABERINTO", True, (255, 215, 0))
            subtitle = font_medium.render("Presiona ENTER o ESPACIO para jugar", True, (255, 255, 255))

            screen.blit(title, title.get_rect(center=(monitor_width // 2, monitor_height // 2 - 50)))
            screen.blit(subtitle, subtitle.get_rect(center=(monitor_width // 2, monitor_height // 2 + 30)))
            draw_controls(screen, font_small, monitor_width, monitor_height)

        # 2. Dibujar Juego Activo / Pausa / Fin
        else:
            # Tablero (usando los offsets calculados para centrarlo)
            for y in range(grid.height):
                for x in range(grid.width):
                    tile = grid.get_tile(x, y)
                    color = COLORS.get(tile, (255, 255, 255))
                    rect = pygame.Rect(offset_x + x * TILE_SIZE, offset_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (0, 0, 0), rect, 3)  # Borde un poco más grueso para pantallas grandes

            # HUD Superior (Centrado arriba del tablero)
            time_txt = font_medium.render(f"Tiempo: {game_state.time_left}s", True, (255, 255, 255))
            moves_txt = font_medium.render(f"Movimientos: {game_state.moves_count}", True, (255, 255, 255))
            screen.blit(time_txt, (offset_x, offset_y - font_size - 10))
            screen.blit(moves_txt, (offset_x + grid_width_px - moves_txt.get_width(), offset_y - font_size - 10))

            # Mensajes de Estado Final o Pausa
            msg_text = ""
            msg_color = (255, 255, 255)

            if game_state.status == "GAME_OVER":
                msg_text = "TIEMPO AGOTADO"
                msg_color = (255, 50, 50)
            elif game_state.status == "VICTORIA":
                msg_text = "¡VICTORIA!"
                msg_color = (50, 255, 50)
            elif game_state.status == "PAUSED":
                msg_text = "PAUSA"
                msg_color = (255, 255, 0)

            if game_state.status in ("GAME_OVER", "VICTORIA", "PAUSED"):
                overlay = pygame.Surface((monitor_width, monitor_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))

                msg = font_big.render(msg_text, True, msg_color)
                msg_rect = msg.get_rect(center=(monitor_width // 2, monitor_height // 2))
                screen.blit(msg, msg_rect)

                if game_state.status in ("GAME_OVER", "VICTORIA"):
                    sub_msg = font_medium.render("Presiona 'R' para reiniciar", True, (200, 200, 200))
                    sub_rect = sub_msg.get_rect(center=(monitor_width // 2, monitor_height // 2 + font_size * 2))
                    screen.blit(sub_msg, sub_rect)

            # Barra de controles inferior
            draw_controls(screen, font_small, monitor_width, monitor_height)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()