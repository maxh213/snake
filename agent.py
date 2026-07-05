"""Agent: observation builder + fixed-topology feed-forward neural net.

Observation vector (length 6), all relative to the snake's current heading so
the policy is rotation-invariant:

    [0] danger_straight : 1.0 if the cell one step ahead is snake body, else 0.0
    [1] danger_left     : 1.0 if the cell one step to the left is snake body, else 0.0
    [2] danger_right    : 1.0 if the cell one step to the right is snake body, else 0.0
    [3] target_forward  : signed toroidal distance to target along heading,
                          normalized to [-1, 1] (positive = ahead)
    [4] target_right    : signed toroidal distance to target perpendicular to
                          heading, normalized to [-1, 1] (positive = to the right)
    [5] length_norm     : snake length / grid area, in (0, 1]

Target = the nearer (toroidal manhattan distance) of food and bonus; food if
no bonus exists.

Network: 6 -> 16 (tanh) -> 3, argmax over outputs = action (0=left, 1=straight,
2=right), matching engine.LEFT/STRAIGHT/RIGHT.
"""

import numpy as np

import engine
from engine import GRID_WIDTH, GRID_HEIGHT, turn_left, turn_right

OBS_SIZE = 6
HIDDEN_SIZE = 16
OUT_SIZE = 3


def _wrap_delta(a, b, size):
    """Signed shortest toroidal delta from a to b on an axis of given size."""
    return (b - a + size // 2) % size - size // 2


def _toroidal_manhattan(a, b):
    return abs(_wrap_delta(a[0], b[0], GRID_WIDTH)) + abs(
        _wrap_delta(a[1], b[1], GRID_HEIGHT)
    )


def observe(game):
    """Build the observation vector for the current game state."""
    head = game.body[0]
    heading = game.direction
    left_dir = turn_left(heading)
    right_dir = turn_right(heading)
    body = set(game.body[1:])

    def danger(direction):
        cell = (
            (head[0] + direction[0]) % GRID_WIDTH,
            (head[1] + direction[1]) % GRID_HEIGHT,
        )
        return 1.0 if cell in body else 0.0

    target = game.food
    if game.bonus is not None and _toroidal_manhattan(head, game.bonus) < _toroidal_manhattan(head, game.food):
        target = game.bonus

    dx = _wrap_delta(head[0], target[0], GRID_WIDTH)
    dy = _wrap_delta(head[1], target[1], GRID_HEIGHT)

    forward = dx * heading[0] + dy * heading[1]
    rightward = dx * right_dir[0] + dy * right_dir[1]

    half = max(GRID_WIDTH, GRID_HEIGHT) / 2.0

    return np.array(
        [
            danger(heading),
            danger(left_dir),
            danger(right_dir),
            forward / half,
            rightward / half,
            len(game.body) / (GRID_WIDTH * GRID_HEIGHT),
        ],
        dtype=np.float64,
    )


class NeuralNet:
    """Fixed-topology feed-forward net: OBS_SIZE -> HIDDEN_SIZE (tanh) -> OUT_SIZE."""

    def __init__(self, w1, b1, w2, b2):
        self.w1 = w1
        self.b1 = b1
        self.w2 = w2
        self.b2 = b2

    @staticmethod
    def genome_size():
        return (
            OBS_SIZE * HIDDEN_SIZE
            + HIDDEN_SIZE
            + HIDDEN_SIZE * OUT_SIZE
            + OUT_SIZE
        )

    @classmethod
    def from_genome(cls, genome):
        genome = np.asarray(genome, dtype=np.float64)
        if genome.shape != (cls.genome_size(),):
            raise ValueError(
                f"expected genome of shape ({cls.genome_size()},), got {genome.shape}"
            )
        i = 0
        w1 = genome[i : i + OBS_SIZE * HIDDEN_SIZE].reshape(OBS_SIZE, HIDDEN_SIZE)
        i += OBS_SIZE * HIDDEN_SIZE
        b1 = genome[i : i + HIDDEN_SIZE]
        i += HIDDEN_SIZE
        w2 = genome[i : i + HIDDEN_SIZE * OUT_SIZE].reshape(HIDDEN_SIZE, OUT_SIZE)
        i += HIDDEN_SIZE * OUT_SIZE
        b2 = genome[i : i + OUT_SIZE]
        return cls(w1, b1, w2, b2)

    def to_genome(self):
        return np.concatenate(
            [self.w1.ravel(), self.b1, self.w2.ravel(), self.b2]
        )

    def act(self, observation):
        """Return action (0=left, 1=straight, 2=right) for an observation."""
        h = np.tanh(observation @ self.w1 + self.b1)
        out = h @ self.w2 + self.b2
        return int(np.argmax(out))


def play_game(genome, seed, max_steps=50000, starvation_limit=None):
    """Play one seeded game with a genome. Returns (score, steps)."""
    if starvation_limit is None:
        starvation_limit = 100 * GRID_WIDTH * GRID_HEIGHT // 3
    net = NeuralNet.from_genome(genome)
    game = engine.SnakeGame(seed=seed)
    while not game.done and game.steps < max_steps:
        if game.steps_since_food >= starvation_limit:
            break
        action = net.act(observe(game))
        game.step(action)
    return game.score, game.steps
