"""Evaluate a saved genome over N games.

Usage: python evaluate.py results/best.npy --games 20 --threshold 200
Exits 0 if mean score >= threshold, else 1.
"""

import argparse
import sys

import numpy as np

import agent


def main():
    parser = argparse.ArgumentParser(description="Evaluate a trained Snake genome")
    parser.add_argument("genome", help="path to best.npy")
    parser.add_argument("--games", type=int, default=20)
    parser.add_argument("--threshold", type=float, default=200.0)
    parser.add_argument("--seed", type=int, default=10_000_000,
                        help="base seed for evaluation games")
    args = parser.parse_args()

    genome = np.load(args.genome)
    scores = []
    for i in range(args.games):
        score, steps = agent.play_game(genome, seed=args.seed + i)
        scores.append(score)
        print(f"game {i + 1:3d}  score {score:5d}  steps {steps}")

    mean = float(np.mean(scores))
    print(f"\nmean {mean:.1f}  min {min(scores)}  max {max(scores)}  "
          f"(threshold {args.threshold:.0f})")
    sys.exit(0 if mean >= args.threshold else 1)


if __name__ == "__main__":
    main()
