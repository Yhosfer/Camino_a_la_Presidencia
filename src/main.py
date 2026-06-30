# src/main.py
import pygame
import sys
import os
import math
from src.models import Grid, Player, Direction, TileType, GameState, load_level_from_file

GRID_WIDTH = 15
GRID_HEIGHT = 15
TITLE = "Puzzle Laberinto TDD - Proyecto Final"
FPS = 60
TOTAL_LEVELS = 3
INITIAL_TIME = 90

COLORS = {
    TileType.EMPTY: (30, 35, 50),
    TileType.WALL: (70, 85, 110),
    TileType.BLOCK: (180, 100, 40),
    TileType.PLAYER: (0, 160, 255),
    TileType.GOAL: (20, 200, 100),
    TileType.BLOCK_ON_GOAL: (255, 200, 0),
    TileType.PORTAL_BLUE: (0, 220, 255),
    TileType.PORTAL_RED: (255, 60, 60)
}

MAIN_MENU_OPTIONS = ["Iniciar Juego", "Salir"]
PAUSE_OPTIONS = ["Continuar", "Deshacer Movimiento", "Reiniciar Nivel", "Menú Principal"]


def get_level_path(level_num: int) -> str:
    current_file_path = os.path.abspath(__file__)
    src_dir = os.path.dirname(current_file_path)
    project_root = os.path.dirname(src_dir)
    return os.path.join(project_root, "levels", f"nivel{level_num}.txt")


def draw_text_centered(screen, font, text, color, y_pos, monitor_width):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, text_surface.get_rect(center=(monitor_width // 2, y_pos)))


def draw_tile(screen, tile_type, rect, font_icon):
    """Dibuja una celda con color de fondo y símbolo representativo."""
    ts = rect.width
    cx, cy = rect.centerx, rect.centery
    bg = COLORS.get(tile_type, (50, 50, 80))
    pygame.draw.rect(screen, bg, rect)

    if tile_type == TileType.WALL:
        # Borde iluminado 3D
        light = tuple(min(255, c + 60) for c in bg)
        dark  = tuple(max(0,   c - 40) for c in bg)
        pygame.draw.line(screen, light, rect.topleft, rect.topright, 2)
        pygame.draw.line(screen, light, rect.topleft, rect.bottomleft, 2)
        pygame.draw.line(screen, dark,  rect.bottomleft, rect.bottomright, 2)
        pygame.draw.line(screen, dark,  rect.topright, rect.bottomright, 2)
        # Detalle interno de ladrillo
        inner_rect = rect.inflate(-6, -6)
        pygame.draw.rect(screen, (50, 60, 80), inner_rect, 1)

    elif tile_type == TileType.PLAYER:
        # Sombra suave desplazada
        pygame.draw.circle(screen, (10, 12, 20), (cx + 2, cy + 2), ts // 3)
        # Cuerpo
        r = ts // 3
        pygame.draw.circle(screen, (0, 120, 220), (cx, cy), r)
        pygame.draw.circle(screen, (180, 230, 255), (cx, cy), r, 2)
        # Brillo tridimensional
        shine_r = max(1, r // 4)
        pygame.draw.circle(screen, (255, 255, 255), (cx - r // 3, cy - r // 3), shine_r)

    elif tile_type == TileType.BLOCK:
        margin = max(3, ts // 6)
        inner = rect.inflate(-margin * 2, -margin * 2)
        # Sombra del bloque
        pygame.draw.rect(screen, (10, 12, 20), inner.move(2, 2), border_radius=4)
        # Cuerpo marrón
        pygame.draw.rect(screen, (220, 130, 60), inner, border_radius=4)
        pygame.draw.rect(screen, (255, 180, 100), inner, 2, border_radius=4)
        # Cruz de refuerzo de madera clásica (Sokoban)
        pygame.draw.line(screen, (160, 80, 30), inner.topleft, inner.bottomright, 2)
        pygame.draw.line(screen, (160, 80, 30), inner.topright, inner.bottomleft, 2)

    elif tile_type == TileType.GOAL:
        ticks = pygame.time.get_ticks()
        pulse = math.sin(ticks * 0.006) * 3
        r = max(3, int(ts // 5 + pulse))
        # Halo de luz suave
        glow_surf = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (20, 220, 110, 30), (r * 2, r * 2), r * 2)
        screen.blit(glow_surf, glow_surf.get_rect(center=(cx, cy)))
        # Cruz verde
        pygame.draw.line(screen, (20, 220, 110), (cx - r, cy), (cx + r, cy), 3)
        pygame.draw.line(screen, (20, 220, 110), (cx, cy - r), (cx, cy + r), 3)
        pygame.draw.circle(screen, (20, 220, 110), (cx, cy), max(2, r // 2))

    elif tile_type == TileType.BLOCK_ON_GOAL:
        ticks = pygame.time.get_ticks()
        pulse = math.sin(ticks * 0.008) * 3
        margin = max(3, ts // 6)
        inner = rect.inflate(-margin * 2, -margin * 2)
        # Halo de victoria dorado pulsante
        glow_r = int(ts // 3 + pulse)
        glow_surf = pygame.Surface((glow_r * 4, glow_r * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 200, 0, 40), (glow_r * 2, glow_r * 2), glow_r * 2)
        screen.blit(glow_surf, glow_surf.get_rect(center=(cx, cy)))
        # Bloque dorado
        pygame.draw.rect(screen, (255, 200, 0), inner, border_radius=4)
        pygame.draw.rect(screen, (255, 240, 120), inner, 2, border_radius=4)
        pygame.draw.circle(screen, (255, 255, 200), (cx, cy), max(2, ts // 7))

    elif tile_type == TileType.PORTAL_BLUE:
        ticks = pygame.time.get_ticks()
        angle = (ticks * 0.003) % (2 * math.pi)
        r = max(3, ts // 4)
        # Elipse central
        pygame.draw.ellipse(screen, (0, 150, 255), (cx - r, cy - r // 2, r * 2, r), 0)
        pygame.draw.ellipse(screen, (180, 240, 255), (cx - r, cy - r // 2, r * 2, r), 2)
        # Partículas orbitales (sentido horario)
        orbit_r = r + 3
        for i in range(3):
            theta = angle + i * (2 * math.pi / 3)
            ox = int(cx + orbit_r * math.cos(theta))
            oy = int(cy + orbit_r * math.sin(theta) * 0.5)
            pygame.draw.circle(screen, (200, 255, 255), (ox, oy), 2)

    elif tile_type == TileType.PORTAL_RED:
        ticks = pygame.time.get_ticks()
        angle = -(ticks * 0.003) % (2 * math.pi)
        r = max(3, ts // 4)
        # Elipse central
        pygame.draw.ellipse(screen, (255, 60, 60), (cx - r, cy - r // 2, r * 2, r), 0)
        pygame.draw.ellipse(screen, (255, 180, 180), (cx - r, cy - r // 2, r * 2, r), 2)
        # Partículas orbitales (sentido antihorario)
        orbit_r = r + 3
        for i in range(3):
            theta = angle + i * (2 * math.pi / 3)
            ox = int(cx + orbit_r * math.cos(theta))
            oy = int(cy + orbit_r * math.sin(theta) * 0.5)
            pygame.draw.circle(screen, (255, 200, 200), (ox, oy), 2)

    # Borde sutil entre celdas
    if tile_type != TileType.WALL:
        pygame.draw.rect(screen, (0, 0, 0, 60), rect, 1)


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

    grid = Grid(width=GRID_WIDTH, height=GRID_HEIGHT)
    player = Player(x=0, y=0)
    game_state = GameState(time_left=INITIAL_TIME, moves_count=0, current_level=1)
    load_level_from_file(get_level_path(1), grid, player)

    time_accumulator = 0.0
    main_menu_index = 0
    pause_menu_index = 0
    game_completed_timer = 0.0
    total_moves = 0
    level_completed_timer = 0.0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F4 and (event.mod & pygame.KMOD_ALT): running = False

                # MENÚ PRINCIPAL
                if game_state.status == "MENU":
                    if event.key == pygame.K_UP:
                        main_menu_index = (main_menu_index - 1) % len(MAIN_MENU_OPTIONS)
                    elif event.key == pygame.K_DOWN:
                        main_menu_index = (main_menu_index + 1) % len(MAIN_MENU_OPTIONS)
                    elif event.key == pygame.K_RETURN:
                        if main_menu_index == 0:
                            total_moves = 0
                            game_state.start_game()
                            load_level_from_file(get_level_path(1), grid, player)
                        elif main_menu_index == 1:
                            game_state.quit_game()
                            running = False

                # MENÚ DE PAUSA
                elif event.key == pygame.K_ESCAPE:
                    if game_state.status == "PLAYING":
                        game_state.toggle_pause()
                        pause_menu_index = 0
                    elif game_state.status == "PAUSE_MENU":
                        game_state.resume_game()
                    elif game_state.status == "GAME_OVER":
                        game_state.return_to_main_menu(INITIAL_TIME)
                        load_level_from_file(get_level_path(1), grid, player)
                        main_menu_index = 0

                elif game_state.status == "PAUSE_MENU":
                    if event.key == pygame.K_UP:
                        pause_menu_index = (pause_menu_index - 1) % len(PAUSE_OPTIONS)
                    elif event.key == pygame.K_DOWN:
                        pause_menu_index = (pause_menu_index + 1) % len(PAUSE_OPTIONS)
                    elif event.key == pygame.K_RETURN:
                        if pause_menu_index == 0:
                            game_state.resume_game()
                        elif pause_menu_index == 1:
                            game_state.undo(grid, player)
                            game_state.resume_game()
                        elif pause_menu_index == 2:
                            game_state.reset(INITIAL_TIME)
                            load_level_from_file(get_level_path(game_state.current_level), grid, player)
                        elif pause_menu_index == 3:
                            game_state.return_to_main_menu(INITIAL_TIME)
                            load_level_from_file(get_level_path(1), grid, player)
                            main_menu_index = 0

                # CONTROLES DE JUEGO
                elif event.key == pygame.K_r and game_state.status in ("PLAYING", "GAME_OVER"):
                    game_state.reset(INITIAL_TIME)
                    load_level_from_file(get_level_path(game_state.current_level), grid, player)

                elif event.key == pygame.K_z and game_state.status == "PLAYING":
                    game_state.undo(grid, player)

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
                        game_state.save_state(grid, player)  # Guardar estado ANTES de mover
                        if player.move(direction, grid):
                            game_state.increment_moves()
                            if grid.check_victory():
                                game_state.status = "NIVEL_COMPLETADO"
                                level_completed_timer = 2.5

        delta_time = clock.tick(FPS) / 1000.0
        if game_state.status == "PLAYING":
            time_accumulator += delta_time
            if time_accumulator >= 1.0:
                game_state.tick()
                time_accumulator -= 1.0
        elif game_state.status == "NIVEL_COMPLETADO":
            level_completed_timer -= delta_time
            if level_completed_timer <= 0.0:
                total_moves += game_state.moves_count
                game_state.advance_to_next_level(TOTAL_LEVELS, INITIAL_TIME)
                if game_state.status == "PLAYING":
                    load_level_from_file(get_level_path(game_state.current_level), grid, player)
        elif game_state.status == "JUEGO_COMPLETADO":
            game_completed_timer += delta_time
            if game_completed_timer >= 3.0:
                game_state.return_to_main_menu(INITIAL_TIME)
                load_level_from_file(get_level_path(1), grid, player)
                game_completed_timer = 0.0
                main_menu_index = 0

        # DIBUJADO
        screen.fill((15, 18, 28))

        if game_state.status == "MENU":
            # Subtítulo decorativo
            draw_text_centered(screen, font_small, "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", (80, 100, 140),
                               monitor_height // 2 - 100, monitor_width)
            draw_text_centered(screen, font_big, "CAMINO A LA PRESIDENCIA", (255, 215, 0),
                               monitor_height // 2 - 140, monitor_width)
            draw_text_centered(screen, font_small, "Puzzle de Laberinto · 3 Niveles", (140, 160, 200),
                               monitor_height // 2 - 70, monitor_width)
            draw_text_centered(screen, font_small, "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", (80, 100, 140),
                               monitor_height // 2 - 40, monitor_width)
            for i, option in enumerate(MAIN_MENU_OPTIONS):
                color = (255, 215, 0) if i == main_menu_index else (180, 190, 210)
                # Pointer pulse animation
                ticks = pygame.time.get_ticks()
                pulse_x = int(math.sin(ticks * 0.01) * 3)
                prefix = "▶  " if i == main_menu_index else "    "
                draw_text_centered(screen, font_medium, prefix + option, color, monitor_height // 2 + 20 + i * 65,
                                   monitor_width)
            draw_text_centered(screen, font_small, "[↑↓] Seleccionar  |  [ENTER] Confirmar", (90, 110, 150),
                               monitor_height - 50, monitor_width)
            # Leyenda de símbolos
            legend_y = monitor_height - 120
            legend_items = [
                ("● Jugador", (0, 160, 255)),
                ("■ Bloque",  (180, 100, 40)),
                ("✦ Meta",    (20, 200, 100)),
                ("◎ Portal",  (0, 220, 255)),
            ]
            total_w = len(legend_items) * 200
            start_x = (monitor_width - total_w) // 2
            for li, (ltext, lcolor) in enumerate(legend_items):
                surf = font_small.render(ltext, True, lcolor)
                screen.blit(surf, (start_x + li * 200, legend_y))

        elif game_state.status == "PAUSE_MENU":
            # Marco del tablero
            grid_border_rect = pygame.Rect(offset_x - 4, offset_y - 4, grid_width_px + 8, grid_height_px + 8)
            pygame.draw.rect(screen, (70, 85, 110), grid_border_rect, 4, border_radius=6)

            for y in range(grid.height):
                for x in range(grid.width):
                    rect = pygame.Rect(offset_x + x * TILE_SIZE, offset_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    draw_tile(screen, grid.get_tile(x, y), rect, font_small)

            # Overlay semitransparente
            overlay = pygame.Surface((monitor_width, monitor_height), pygame.SRCALPHA)
            overlay.fill((5, 8, 20, 200))
            screen.blit(overlay, (0, 0))
            draw_text_centered(screen, font_big, "⏸  PAUSA", (255, 220, 50), monitor_height // 2 - 160, monitor_width)
            for i, option in enumerate(PAUSE_OPTIONS):
                color = (255, 215, 0) if i == pause_menu_index else (180, 190, 210)
                prefix = "▶  " if i == pause_menu_index else "    "
                draw_text_centered(screen, font_medium, prefix + option, color, monitor_height // 2 - 60 + i * 65,
                                   monitor_width)
            draw_text_centered(screen, font_small, "[↑↓] Seleccionar  |  [ENTER] Confirmar", (90, 110, 150),
                               monitor_height - 50, monitor_width)

        elif game_state.status == "NIVEL_COMPLETADO":
            # Marco del tablero
            grid_border_rect = pygame.Rect(offset_x - 4, offset_y - 4, grid_width_px + 8, grid_height_px + 8)
            pygame.draw.rect(screen, (70, 85, 110), grid_border_rect, 4, border_radius=6)

            for y in range(grid.height):
                for x in range(grid.width):
                    rect = pygame.Rect(offset_x + x * TILE_SIZE, offset_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    draw_tile(screen, grid.get_tile(x, y), rect, font_small)

            # Overlay semitransparente verde de éxito
            overlay = pygame.Surface((monitor_width, monitor_height), pygame.SRCALPHA)
            overlay.fill((10, 30, 20, 200))
            screen.blit(overlay, (0, 0))

            ticks = pygame.time.get_ticks()
            pulse = int(math.sin(ticks * 0.008) * 8)
            draw_text_centered(screen, font_big, "¡NIVEL COMPLETADO!", (50, 255, 120), monitor_height // 2 - 80 + pulse, monitor_width)
            draw_text_centered(screen, font_medium, f"Movimientos: {game_state.moves_count}", (200, 240, 210), monitor_height // 2, monitor_width)
            draw_text_centered(screen, font_medium, f"Tiempo restante: {game_state.time_left}s", (200, 240, 210), monitor_height // 2 + 50, monitor_width)

            # Barra de progreso
            bar_w = 300
            bar_h = 8
            bar_x = (monitor_width - bar_w) // 2
            bar_y = monitor_height // 2 + 120
            pygame.draw.rect(screen, (30, 50, 40), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
            progress = max(0.0, level_completed_timer / 2.5)
            pygame.draw.rect(screen, (50, 255, 120), (bar_x, bar_y, int(bar_w * (1.0 - progress)), bar_h), border_radius=4)

        else:
            # Marco del tablero
            grid_border_rect = pygame.Rect(offset_x - 4, offset_y - 4, grid_width_px + 8, grid_height_px + 8)
            pygame.draw.rect(screen, (70, 85, 110), grid_border_rect, 4, border_radius=6)

            for y in range(grid.height):
                for x in range(grid.width):
                    rect = pygame.Rect(offset_x + x * TILE_SIZE, offset_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    draw_tile(screen, grid.get_tile(x, y), rect, font_small)

            # HUD: Temporizador con color dinámico
            t = game_state.time_left
            if t > 30:
                time_color = (80, 220, 120)
            elif t > 10:
                time_color = (255, 200, 50)
            else:
                time_color = (255, 60, 60)
            screen.blit(font_medium.render(f"⏱  {game_state.time_left}s", True, time_color), (20, 15))
            
            # HUD: Barra de progreso de tiempo
            bar_max_w = 200
            time_ratio = max(0.0, min(1.0, game_state.time_left / INITIAL_TIME))
            bar_w = int(bar_max_w * time_ratio)
            pygame.draw.rect(screen, (40, 45, 60), (20, 50, bar_max_w, 6), border_radius=3)
            pygame.draw.rect(screen, time_color, (20, 50, bar_w, 6), border_radius=3)

            screen.blit(font_medium.render(f"👣 {game_state.moves_count} movs", True, (180, 195, 220)),
                        (monitor_width - 220, 15))
            draw_text_centered(screen, font_medium,
                               f"Nivel  {game_state.current_level} / {TOTAL_LEVELS}",
                               (255, 215, 80), 22, monitor_width)

            if game_state.status in ("GAME_OVER", "JUEGO_COMPLETADO"):
                overlay = pygame.Surface((monitor_width, monitor_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 220))
                screen.blit(overlay, (0, 0))
                msg = "⏰  TIEMPO AGOTADO" if game_state.status == "GAME_OVER" else "🏆  ¡JUEGO COMPLETADO!"
                color = (255, 70, 70) if game_state.status == "GAME_OVER" else (255, 215, 0)
                draw_text_centered(screen, font_big, msg, color, monitor_height // 2 - 60, monitor_width)
                
                if game_state.status == "GAME_OVER":
                    sub = "Presiona  R  para reiniciar o  ESC  para salir"
                else:
                    sub = f"¡Completado en {total_moves} movimientos! Volviendo al menú..."
                draw_text_centered(screen, font_medium, sub, (200, 210, 230), monitor_height // 2 + 30, monitor_width)

            draw_text_centered(screen, font_small,
                               "[Flechas/WASD] Mover  |  [Z] Deshacer  |  [ESC] Pausa  |  [R] Reiniciar",
                               (70, 90, 130), monitor_height - 22, monitor_width)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()