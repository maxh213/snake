"""Plot best/mean fitness per generation from a fitness.csv.

Usage: python plot_fitness.py runs/<dir>/fitness.csv [-o out.png]
Writes fitness.png next to the CSV by default.
"""

import argparse
import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description="Plot GA fitness progress")
    parser.add_argument("csv_path", help="path to fitness.csv")
    parser.add_argument("-o", "--out", default=None, help="output PNG path")
    args = parser.parse_args()

    generations, best, mean = [], [], []
    with open(args.csv_path, newline="") as f:
        for row in csv.DictReader(f):
            generations.append(int(row["generation"]))
            best.append(float(row["best"]))
            mean.append(float(row["mean"]))

    out_path = args.out or os.path.join(os.path.dirname(args.csv_path), "fitness.png")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(generations, best, label="best", linewidth=1.5)
    ax.plot(generations, mean, label="mean", linewidth=1.5, alpha=0.7)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness (score*1000 + steps)")
    ax.set_title("Snake GA fitness per generation")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
