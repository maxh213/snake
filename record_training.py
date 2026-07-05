"""Record a training-progress video: run a short GA and capture frames of the
best genome replaying at selected generations, then encode with ffmpeg.

Renders to an off-screen pygame Surface (no window needed).

Usage: python record_training.py --out media/training [--pop 60] [--generations 40]
Produces <out>/frames/*.png; encode with ffmpeg afterwards (see README).
"""

import argparse
import os

import numpy as np
import pygame

import engine
from agent import NeuralNet, observe
from train import evaluate_genome, tournament_select, crossover, mutate, GAMES_PER_EVAL

BG_COLOR = (0x9B, 0xBC, 0x0F)
FG_COLOR = (0x0F, 0x38, 0x0F)
CELL = 32
W = engine.GRID_WIDTH * CELL
H = engine.GRID_HEIGHT * CELL
MAX_REPLAY_STEPS = 600


def draw_frame(surface, game, font, generation, label):
    surface.fill(BG_COLOR)
    for x in range(0, W + 1, CELL):
        pygame.draw.line(surface, FG_COLOR, (x, 0), (x, H), 1)
    for y in range(0, H + 1, CELL):
        pygame.draw.line(surface, FG_COLOR, (0, y), (W, y), 1)
    fx, fy = game.food
    pygame.draw.rect(surface, FG_COLOR, (fx * CELL + 1, fy * CELL + 1, CELL - 2, CELL - 2))
    if game.bonus:
        bx, by = game.bonus
        pygame.draw.rect(surface, FG_COLOR, (bx * CELL - 2, by * CELL - 2, CELL + 4, CELL + 4))
    for sx, sy in game.body:
        pygame.draw.rect(surface, FG_COLOR, (sx * CELL + 1, sy * CELL + 1, CELL - 2, CELL - 2))
    gen_text = font.render(f"Generation {generation}  {label}", True, FG_COLOR)
    surface.blit(gen_text, (10, 10))
    score_text = font.render(f"Score: {game.score}", True, FG_COLOR)
    surface.blit(score_text, (W - 10 - score_text.get_width(), 10))


def replay_and_capture(genome, seed, generation, label, font, frames_dir, frame_idx,
                       hold_last=20):
    net = NeuralNet.from_genome(genome)
    game = engine.SnakeGame(seed=seed)
    surface = pygame.Surface((W, H))
    while not game.done and game.steps < MAX_REPLAY_STEPS:
        if game.steps_since_food >= 300:
            break
        game.step(net.act(observe(game)))
        draw_frame(surface, game, font, generation, label)
        pygame.image.save(surface, os.path.join(frames_dir, f"{frame_idx:06d}.png"))
        frame_idx += 1
    for _ in range(hold_last):
        pygame.image.save(surface, os.path.join(frames_dir, f"{frame_idx:06d}.png"))
        frame_idx += 1
    return frame_idx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pop", type=int, default=60)
    parser.add_argument("--generations", type=int, default=40)
    parser.add_argument("--seed", type=int, default=3)
    parser.add_argument("--capture-gens", type=str, default="0,2,5,10,20,39",
                        help="comma-separated generations to record")
    parser.add_argument("--out", type=str, default="media/training")
    args = parser.parse_args()

    frames_dir = os.path.join(args.out, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    capture_gens = {int(g) for g in args.capture_gens.split(",")}

    pygame.font.init()
    font = pygame.font.SysFont("monospace", 20, bold=True)

    rng = np.random.default_rng(args.seed)
    population = [rng.normal(0.0, 1.0, size=NeuralNet.genome_size())
                  for _ in range(args.pop)]
    frame_idx = 0

    for gen in range(args.generations):
        base_seed = args.seed * 1_000_000 + gen * 1000
        seeds = [base_seed + i for i in range(GAMES_PER_EVAL)]
        fitnesses = np.array([evaluate_genome((g, seeds)) for g in population])
        best_idx = int(np.argmax(fitnesses))
        best = float(fitnesses[best_idx])
        print(f"gen {gen:3d}  best {best:10.1f}")

        if gen in capture_gens:
            label = f"best fitness {best:,.0f}"
            frame_idx = replay_and_capture(
                population[best_idx], seeds[0], gen, label, font,
                frames_dir, frame_idx)

        order = np.argsort(fitnesses)[::-1]
        next_pop = [population[i].copy() for i in order[:2]]
        while len(next_pop) < args.pop:
            pa = population[tournament_select(rng, fitnesses, 5)]
            pb = population[tournament_select(rng, fitnesses, 5)]
            next_pop.append(mutate(rng, crossover(rng, pa, pb), 0.05, 0.3))
        population = next_pop

    print(f"{frame_idx} frames in {frames_dir}")


if __name__ == "__main__":
    main()
