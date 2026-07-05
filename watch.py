"""Replay a saved genome in the pygame renderer.

Usage: python watch.py runs/<dir>/best.npy [--seed N] [--fps N]
"""

import argparse

import numpy as np
import pygame

import engine
import snake as ui
from agent import NeuralNet, observe


def main():
    parser = argparse.ArgumentParser(description="Watch a trained Snake agent play")
    parser.add_argument("genome", help="path to best.npy")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--fps", type=int, default=10, help="snake moves per second")
    args = parser.parse_args()

    net = NeuralNet.from_genome(np.load(args.genome))
    game = engine.SnakeGame(seed=args.seed)

    pygame.init()
    screen = pygame.display.set_mode((ui.SCREEN_WIDTH, ui.SCREEN_HEIGHT))
    pygame.display.set_caption("Snake GA - Best Agent")
    clock = pygame.time.Clock()
    hud_font = pygame.font.SysFont("monospace", 20, bold=True)
    font = pygame.font.SysFont("monospace", 28, bold=True)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False

        if not game.done:
            action = net.act(observe(game))
            game.step(action)

        screen.fill(ui.BG_COLOR)
        ui.draw_grid(screen)
        ui.draw_food(screen, game.food)
        if game.bonus:
            ui.draw_bonus(screen, game.bonus)
        ui.draw_snake(screen, game.body)

        score_text = hud_font.render(f"Score: {game.score}", True, ui.FG_COLOR)
        screen.blit(score_text, (10, 10))
        steps_text = hud_font.render(f"Steps: {game.steps}", True, ui.FG_COLOR)
        screen.blit(steps_text, (ui.SCREEN_WIDTH - 10 - steps_text.get_width(), 10))

        if game.done:
            ui.draw_text(screen, "GAME OVER", font, -20)
            ui.draw_text(screen, f"Final Score: {game.score}", hud_font, 20)
            ui.draw_text(screen, "Q to Quit", hud_font, 50)

        pygame.display.flip()
        clock.tick(args.fps)

    pygame.quit()


if __name__ == "__main__":
    main()
