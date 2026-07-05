"""Live replay of a generation's best genome during training.

Used by train.py --render. Replays the genome on the same seed the
generation was evaluated with, so you see exactly the game that earned
the fitness score.
"""

import pygame

import engine
import snake as ui
from agent import NeuralNet, observe

MAX_REPLAY_STEPS = 2000


class GenerationRenderer:
    def __init__(self, fps=30):
        self.fps = fps
        pygame.init()
        self.screen = pygame.display.set_mode((ui.SCREEN_WIDTH, ui.SCREEN_HEIGHT))
        pygame.display.set_caption("Snake GA - Training")
        self.clock = pygame.time.Clock()
        self.hud_font = pygame.font.SysFont("monospace", 20, bold=True)

    def replay(self, genome, seed, generation, fitness):
        """Replay one game. Returns False if the user closed the window/quit."""
        net = NeuralNet.from_genome(genome)
        game = engine.SnakeGame(seed=seed)
        skip = False
        while not game.done and game.steps < MAX_REPLAY_STEPS and not skip:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return False
                    elif event.key == pygame.K_SPACE:
                        skip = True

            if game.steps_since_food >= 500:
                break
            game.step(net.act(observe(game)))

            self.screen.fill(ui.BG_COLOR)
            ui.draw_grid(self.screen)
            ui.draw_food(self.screen, game.food)
            if game.bonus:
                ui.draw_bonus(self.screen, game.bonus)
            ui.draw_snake(self.screen, game.body)

            gen_text = self.hud_font.render(
                f"Gen {generation}  Fit {fitness:.0f}", True, ui.FG_COLOR)
            self.screen.blit(gen_text, (10, 10))
            score_text = self.hud_font.render(
                f"Score: {game.score}", True, ui.FG_COLOR)
            self.screen.blit(
                score_text,
                (ui.SCREEN_WIDTH - 10 - score_text.get_width(), 10))

            pygame.display.flip()
            self.clock.tick(self.fps)
        return True

    def close(self):
        pygame.quit()
