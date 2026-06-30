# src/main.py
import pygame
import sys
import os
from src.models import Grid, Player, Direction, TileType, GameState, load_level_from_file

# --- CONSTANTES DEL JUEGO ---
GRID_WIDTH = 7  # Ajustado para el nivel más grande
GRID_HEIGHT = 7
TITLE = "Puzzle Laberinto TDD - Semana 3 (Múltiples Niveles)"
FPS = 60
TOTAL_LEVELS = 3

COLORS = {
    TileType.EMPTY: (47, 79, 79),
    TileType.WALL: (128, 128, 128),
    TileType.BLOCK: (139, 69, 19),
    TileType.PLAYER: (30, 144, 255),
    TileType.GOAL: (50, 205, 50),
    TileType.BLOCK_ON_GOAL: (255, 215, 0)
}

INITIAL_TIME = 30
PAUSE_OPTIONS = ["Continuar", "Reiniciar Nivel", "Menú Principal"]


def get_level_path(level_num: int) -> str:
    """Obtiene la ruta absoluta del archivo de nivel, sin importar desde dónde se ejecute"""
    # 1. Obtener la ruta absoluta de este archivo (main.py)
    current_file_path = os.path.abspath(__file__)

    # 2. Obtener el directorio donde está main.py (que es la carpeta 'src/')
    src_dir = os.path.dirname(current_file_path)

    # 3. Subir un nivel para llegar a la raíz del proyecto (donde está 'levels/')
    project_root = os.path.dirname(src_dir)

    # 4. Construir la ruta completa a la carpeta 'levels' y al archivo
    levels_dir = os.path.join(project_root, "levels")
    return os.path.join(levels_dir, f"nivel{level_num}.txt")


def draw_controls(screen, font, monitor_width, monitor_height):
    controls_text = "CONTROLES: [↑↓←→/WASD] Mover  |  [ESC] Pausa  |  [R] Reiniciar"
    text_surface = font.render(controls_text, True, (200, 200, 200))
    text_rect = text_surface.get_rect(center=(monitor_width // 2, monitor_height - 40))
    screen.blit(text_surface, text_rect)


def draw_pause_menu(screen, font_big, font_medium, monitor_width, monitor_height, selected_index):
    overlay = pygame.Surface((monitor_width, monitor_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    title = font_big.render("PAUSA", True, (255, 255, 0))
    screen.blit(title, title.get_rect(center=(monitor_width // 2, monitor_height // 2 - 120)))

    for i, option in enumerate(PAUSE_OPTIONS):
        color = (255, 215, 0) if i == selected_index else (200, 200, 200)
        prefix = "▶ " if i == selected_index else "   "
        text = font_medium.render(prefix + option, True, color)
        screen.blit(text, text.get_rect(center=(monitor_width // 2, monitor_height // 2 + i * 60)))

    hint = font_medium.render("[↑↓] Seleccionar   [ENTER] Confirmar", True, (150, 150, 150))
    screen.blit(hint, hint.get_rect(center=(monitor_width // 2, monitor_height // 2 + 200)))


def main():
    pygame.init()

    info = pygame.display.Info()
    monitor_width = info.current_w
    monitor_height = info.current_h
    screen = pygame.display.set_mode((monitor_width, monitor_height), pygame.FULLSCREEN)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    max_tile_w = int((monitor_width * 0.8) // GRID_WIDTH)
    max_tile_h = int((monitor_height * 0.7) // GRID_HEIGHT)
    TILE_SIZE = min(max_tile_w, max_tile_h)

    font_size = max(24, TILE_SIZE // 2)
    font_small = pygame.font.SysFont(None, font_size)
    font_medium = pygame.font.SysFont(None, int(font_size * 1.5))
    font_big = pygame.font.SysFont(None, int(font_size * 2.5))

    grid_width_px = TILE_SIZE * GRID_WIDTH
    grid_height_px = TILE_SIZE * GRID_HEIGHT
    offset_x = (monitor_width - grid_width_px) // 2
    offset_y = (monitor_height - grid_height_px) // 2 + font_size

    # Instanciar lógica
    grid = Grid(width=GRID_WIDTH, height=GRID_HEIGHT)
    player = Player(x=0, y=0)
    game_state = GameState(time_left=INITIAL_TIME, moves_count=0, current_level=1)

    # Cargar primer nivel
    load_level_from_file(get_level_path(1), grid, player)

    time_accumulator = 0.0
    pause_menu_index = 0
    game_completed_timer = 0.0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F4 and (event.mod & pygame.KMOD_ALT):
                    running = False

                elif event.key == pygame.K_ESCAPE:
                    if game_state.status == "PLAYING":
                        game_state.toggle_pause()
                        pause_menu_index = 0
                    elif game_state.status == "PAUSE_MENU":
                        game_state.resume_game()

                elif game_state.status == "PAUSE_MENU":
                    if event.key == pygame.K_UP:
                        pause_menu_index = (pause_menu_index - 1) % len(PAUSE_OPTIONS)
                    elif event.key == pygame.K_DOWN:
                        pause_menu_index = (pause_menu_index + 1) % len(PAUSE_OPTIONS)
                    elif event.key == pygame.K_RETURN:
                        if pause_menu_index == 0:
                            game_state.resume_game()
                        elif pause_menu_index == 1:
                            game_state.reset(INITIAL_TIME)
                            load_level_from_file(get_level_path(game_state.current_level), grid, player)
                        elif pause_menu_index == 2:
                            game_state.return_to_main_menu(INITIAL_TIME)
                            load_level_from_file(get_level_path(1), grid, player)

                elif game_state.status == "MENU" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game_state.start_game()
                    load_level_from_file(get_level_path(1), grid, player)

                elif event.key == pygame.K_r and game_state.status == "PLAYING":
                    game_state.reset(INITIAL_TIME)
                    load_level_from_file(get_level_path(game_state.current_level), grid, player)

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
                                game_state.advance_to_next_level(TOTAL_LEVELS, INITIAL_TIME)
                                if game_state.status == "PLAYING":
                                    load_level_from_file(get_level_path(game_state.current_level), grid, player)

        delta_time = clock.tick(FPS) / 1000.0

        if game_state.status == "PLAYING":
            time_accumulator += delta_time
            if time_accumulator >= 1.0:
                game_state.tick()
                time_accumulator -= 1.0

        elif game_state.status == "JUEGO_COMPLETADO":
            game_completed_timer += delta_time
            if game_completed_timer >= 3.0:
                game_state.return_to_main_menu(INITIAL_TIME)
                load_level_from_file(get_level_path(1), grid, player)
                game_completed_timer = 0.0

        screen.fill((20, 20, 30))

        if game_state.status == "MENU":
            title = font_big.render("PUZZLE LABERINTO", True, (255, 215, 0))
            subtitle = font_medium.render("Presiona ENTER o ESPACIO para jugar", True, (255, 255, 255))
            screen.blit(title, title.get_rect(center=(monitor_width // 2, monitor_height // 2 - 50)))
            screen.blit(subtitle, subtitle.get_rect(center=(monitor_width // 2, monitor_height // 2 + 30)))
            draw_controls(screen, font_small, monitor_width, monitor_height)

        elif game_state.status == "PAUSE_MENU":
            for y in range(grid.height):
                for x in range(grid.width):
                    tile = grid.get_tile(x, y)
                    color = COLORS.get(tile, (255, 255, 255))
                    rect = pygame.Rect(offset_x + x * TILE_SIZE, offset_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (0, 0, 0), rect, 3)

            time_txt = font_medium.render(f"Tiempo: {game_state.time_left}s", True, (255, 255, 255))
            moves_txt = font_medium.render(f"Movimientos: {game_state.moves_count}", True, (255, 255, 255))
            level_txt = font_medium.render(f"Nivel: {game_state.current_level}/{TOTAL_LEVELS}", True, (255, 255, 255))
            screen.blit(time_txt, (20, 20))
            screen.blit(moves_txt, (monitor_width - moves_txt.get_width() - 20, 20))
            screen.blit(level_txt, (monitor_width // 2 - level_txt.get_width() // 2, 20))

            draw_pause_menu(screen, font_big, font_medium, monitor_width, monitor_height, pause_menu_index)

        else:
            for y in range(grid.height):
                for x in range(grid.width):
                    tile = grid.get_tile(x, y)
                    color = COLORS.get(tile, (255, 255, 255))
                    rect = pygame.Rect(offset_x + x * TILE_SIZE, offset_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (0, 0, 0), rect, 3)

            time_txt = font_medium.render(f"Tiempo: {game_state.time_left}s", True, (255, 255, 255))
            moves_txt = font_medium.render(f"Movimientos: {game_state.moves_count}", True, (255, 255, 255))
            level_txt = font_medium.render(f"Nivel: {game_state.current_level}/{TOTAL_LEVELS}", True, (255, 255, 255))
            screen.blit(time_txt, (20, 20))
            screen.blit(moves_txt, (monitor_width - moves_txt.get_width() - 20, 20))
            screen.blit(level_txt, (monitor_width // 2 - level_txt.get_width() // 2, 20))

            msg_text = ""
            msg_color = (255, 255, 255)

            if game_state.status == "GAME_OVER":
                msg_text = "TIEMPO AGOTADO"
                msg_color = (255, 50, 50)
            elif game_state.status == "VICTORIA":
                msg_text = "¡NIVEL COMPLETADO!"
                msg_color = (50, 255, 50)
            elif game_state.status == "JUEGO_COMPLETADO":
                msg_text = "¡JUEGO COMPLETADO!"
                msg_color = (255, 215, 0)

            if game_state.status in ("GAME_OVER", "VICTORIA", "JUEGO_COMPLETADO"):
                overlay = pygame.Surface((monitor_width, monitor_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))

                msg = font_big.render(msg_text, True, msg_color)
                screen.blit(msg, msg.get_rect(center=(monitor_width // 2, monitor_height // 2)))

                if game_state.status == "GAME_OVER":
                    sub_msg = font_medium.render("Presiona 'R' para reiniciar", True, (200, 200, 200))
                    screen.blit(sub_msg,
                                sub_msg.get_rect(center=(monitor_width // 2, monitor_height // 2 + font_size * 2)))
                elif game_state.status == "JUEGO_COMPLETADO":
                    sub_msg = font_medium.render("Volviendo al menú principal...", True, (200, 200, 200))
                    screen.blit(sub_msg,
                                sub_msg.get_rect(center=(monitor_width // 2, monitor_height // 2 + font_size * 2)))

            draw_controls(screen, font_small, monitor_width, monitor_height)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()