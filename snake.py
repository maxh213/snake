import pygame
import sys
import os

import engine
from engine import SnakeGame, GRID_WIDTH, GRID_HEIGHT

# LCD color scheme
BG_COLOR = (0x9B, 0xBC, 0x0F)
FG_COLOR = (0x0F, 0x38, 0x0F)

CELL_SIZE = 32
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE

# Timing
FPS = 60
BASE_MOVE_INTERVAL = 8  # base frames per snake move
SPEED_UP_EVERY = 50


def draw_snake(screen, body):
    for segment in body:
        rect = pygame.Rect(
            segment[0] * CELL_SIZE + 1,
            segment[1] * CELL_SIZE + 1,
            CELL_SIZE - 2,
            CELL_SIZE - 2,
        )
        pygame.draw.rect(screen, FG_COLOR, rect)


def draw_food(screen, food_pos):
    """Draw food as a filled cell."""
    rect = pygame.Rect(
        food_pos[0] * CELL_SIZE + 1,
        food_pos[1] * CELL_SIZE + 1,
        CELL_SIZE - 2,
        CELL_SIZE - 2,
    )
    pygame.draw.rect(screen, FG_COLOR, rect)


def draw_bonus(screen, bonus_pos):
    """Draw bonus as a larger filled square (2x2 cells)."""
    if bonus_pos:
        rect = pygame.Rect(
            bonus_pos[0] * CELL_SIZE - 2,
            bonus_pos[1] * CELL_SIZE - 2,
            CELL_SIZE + 4,
            CELL_SIZE + 4,
        )
        pygame.draw.rect(screen, FG_COLOR, rect)
        # Draw inner cross pattern
        pygame.draw.line(screen, BG_COLOR,
            (bonus_pos[0] * CELL_SIZE + CELL_SIZE // 2, bonus_pos[1] * CELL_SIZE + 4),
            (bonus_pos[0] * CELL_SIZE + CELL_SIZE // 2, bonus_pos[1] * CELL_SIZE + CELL_SIZE - 4), 2)
        pygame.draw.line(screen, BG_COLOR,
            (bonus_pos[0] * CELL_SIZE + 4, bonus_pos[1] * CELL_SIZE + CELL_SIZE // 2),
            (bonus_pos[0] * CELL_SIZE + CELL_SIZE - 4, bonus_pos[1] * CELL_SIZE + CELL_SIZE // 2), 2)


def draw_grid(screen):
    """Draw grid lines for retro LCD look."""
    for x in range(0, SCREEN_WIDTH + 1, CELL_SIZE):
        pygame.draw.line(screen, FG_COLOR, (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT + 1, CELL_SIZE):
        pygame.draw.line(screen, FG_COLOR, (0, y), (SCREEN_WIDTH, y), 1)


def draw_text(screen, text, font, y_offset=0):
    """Draw centered text on screen."""
    text_surface = font.render(text, True, FG_COLOR)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(text_surface, text_rect)


def get_move_interval(score):
    """Calculate move interval based on score (speeds up every 50 points)."""
    reduction = score // SPEED_UP_EVERY
    return max(2, BASE_MOVE_INTERVAL - reduction)


def load_high_score():
    """Load high score from file."""
    if os.path.exists("highscore.txt"):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read().strip())
        except ValueError:
            pass
    return 0


def save_high_score(score):
    """Save high score to file."""
    with open("highscore.txt", "w") as f:
        f.write(str(score))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Nokia Snake")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 28, bold=True)
    hud_font = pygame.font.SysFont("monospace", 20, bold=True)

    game = SnakeGame()
    state = "start"  # "start", "playing", "paused", "game_over"
    frame_counter = 0
    high_score = load_high_score()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif state == "start":
                    if event.key == pygame.K_RETURN:
                        game = SnakeGame()
                        state = "playing"
                elif state == "playing":
                    if event.key == pygame.K_UP:
                        game.change_direction(engine.UP)
                    elif event.key == pygame.K_DOWN:
                        game.change_direction(engine.DOWN)
                    elif event.key == pygame.K_LEFT:
                        game.change_direction(engine.LEFT_DIR)
                    elif event.key == pygame.K_RIGHT:
                        game.change_direction(engine.RIGHT_DIR)
                    elif event.key == pygame.K_p:
                        state = "paused"
                elif state == "paused":
                    if event.key == pygame.K_p:
                        state = "playing"
                elif state == "game_over":
                    if event.key == pygame.K_r:
                        game = SnakeGame()
                        state = "playing"
                    elif event.key == pygame.K_q:
                        running = False

        if state == "playing":
            frame_counter += 1
            move_interval = get_move_interval(game.score)
            if frame_counter >= move_interval:
                frame_counter = 0
                done, _ = game.step(engine.STRAIGHT)
                if done:
                    if game.score > high_score:
                        high_score = game.score
                        save_high_score(high_score)
                    state = "game_over"

        # Render
        screen.fill(BG_COLOR)
        draw_grid(screen)
        draw_food(screen, game.food)
        if game.bonus:
            draw_bonus(screen, game.bonus)
        draw_snake(screen, game.body)

        # HUD (visible during playing, paused, and game over)
        if state in ("playing", "paused", "game_over"):
            score_text = hud_font.render(f"Score: {game.score}", True, FG_COLOR)
            screen.blit(score_text, (10, 10))
            high_text = hud_font.render(f"High: {high_score}", True, FG_COLOR)
            screen.blit(high_text, (SCREEN_WIDTH - 10 - high_text.get_width(), 10))

        if state == "start":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BG_COLOR)
            screen.blit(overlay, (0, 0))
            draw_text(screen, "SNAKE", font, -60)
            draw_text(screen, "Press ENTER to Start", font, 10)
            draw_text(screen, "Arrow Keys: Move | P: Pause | Q: Quit", hud_font, 60)
        elif state == "paused":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BG_COLOR)
            screen.blit(overlay, (0, 0))
            draw_text(screen, "PAUSED", font, -20)
            draw_text(screen, "Press P to Resume", font, 30)
        elif state == "game_over":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BG_COLOR)
            screen.blit(overlay, (0, 0))
            draw_text(screen, "GAME OVER", font, -40)
            draw_text(screen, f"Final Score: {game.score}", hud_font, 10)
            draw_text(screen, "Press R to Restart", font, 50)
            draw_text(screen, "Press Q to Quit", font, 90)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
