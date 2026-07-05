"""GA training loop for the Snake agent.

Selection: tournament (configurable size). Elitism: top-N copied unchanged.
Crossover: BLX-alpha blend. Mutation: per-gene Gaussian noise.
Fitness: mean over N seeded games of (score * 1000 + steps), with a
starvation limit handled in agent.play_game.
"""

import argparse
import csv
import os
import time
from multiprocessing import Pool

import numpy as np

import agent
from agent import NeuralNet

GAMES_PER_EVAL = 3
BLX_ALPHA = 0.3


def evaluate_genome(args):
    genome, seeds = args
    fitnesses = []
    for seed in seeds:
        score, steps = agent.play_game(genome, seed=seed)
        fitnesses.append(score * 1000 + steps)
    return float(np.mean(fitnesses))


def tournament_select(rng, fitnesses, k):
    contenders = rng.integers(0, len(fitnesses), size=k)
    return int(contenders[np.argmax(fitnesses[contenders])])


def crossover(rng, a, b):
    lo = np.minimum(a, b) - BLX_ALPHA * np.abs(a - b)
    hi = np.maximum(a, b) + BLX_ALPHA * np.abs(a - b)
    return rng.uniform(lo, hi)


def mutate(rng, genome, rate, sigma):
    mask = rng.random(genome.shape) < rate
    genome = genome.copy()
    genome[mask] += rng.normal(0.0, sigma, size=int(mask.sum()))
    return genome


def main():
    parser = argparse.ArgumentParser(description="Train a Snake agent with a GA")
    parser.add_argument("--pop", type=int, default=200)
    parser.add_argument("--generations", type=int, default=300)
    parser.add_argument("--tournament", type=int, default=5)
    parser.add_argument("--elitism", type=int, default=2)
    parser.add_argument("--mutation-rate", type=float, default=0.05)
    parser.add_argument("--mutation-sigma", type=float, default=0.3)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--workers", type=int, default=os.cpu_count())
    parser.add_argument("--out", type=str, default=None,
                        help="output dir (default runs/<timestamp>)")
    args = parser.parse_args()

    out_dir = args.out or os.path.join("runs", time.strftime("%Y%m%d-%H%M%S"))
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "fitness.csv")
    best_path = os.path.join(out_dir, "best.npy")

    rng = np.random.default_rng(args.seed)
    genome_size = NeuralNet.genome_size()
    population = [rng.normal(0.0, 1.0, size=genome_size) for _ in range(args.pop)]

    best_fitness_ever = -np.inf
    pool = Pool(args.workers) if args.workers > 1 else None
    mapper = pool.map if pool else map

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["generation", "best", "mean", "median"])

        try:
            for gen in range(args.generations):
                base_seed = args.seed * 1_000_000 + gen * 1000
                seeds = [base_seed + i for i in range(GAMES_PER_EVAL)]
                jobs = [(genome, seeds) for genome in population]
                fitnesses = np.array(list(mapper(evaluate_genome, jobs)))

                best_idx = int(np.argmax(fitnesses))
                best, mean, median = (
                    float(fitnesses[best_idx]),
                    float(fitnesses.mean()),
                    float(np.median(fitnesses)),
                )
                writer.writerow([gen, f"{best:.1f}", f"{mean:.1f}", f"{median:.1f}"])
                f.flush()
                print(f"gen {gen:4d}  best {best:10.1f}  mean {mean:10.1f}  median {median:10.1f}")

                if best > best_fitness_ever:
                    best_fitness_ever = best
                    np.save(best_path, population[best_idx])

                order = np.argsort(fitnesses)[::-1]
                next_pop = [population[i].copy() for i in order[: args.elitism]]
                while len(next_pop) < args.pop:
                    pa = population[tournament_select(rng, fitnesses, args.tournament)]
                    pb = population[tournament_select(rng, fitnesses, args.tournament)]
                    child = crossover(rng, pa, pb)
                    child = mutate(rng, child, args.mutation_rate, args.mutation_sigma)
                    next_pop.append(child)
                population = next_pop
        finally:
            if pool:
                pool.close()
                pool.join()

    print(f"done. best fitness {best_fitness_ever:.1f}; genome saved to {best_path}")


if __name__ == "__main__":
    main()
