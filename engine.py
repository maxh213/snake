"""Headless Snake game engine.

Contains all game rules with no rendering dependencies.

Coordinate system: (x, y) grid cells, x in [0, GRID_WIDTH), y in [0, GRID_HEIGHT).
The grid is toroidal: moving off one edge wraps to the opposite edge.
Only self-collision ends the game.

Actions for `step(action)` are RELATIVE turns with respect to the snake's
current heading:

    LEFT = 0      turn 90 degrees left, then move one cell
    STRAIGHT = 1  keep heading, move one cell
    RIGHT = 2     turn 90 degrees right, then move one cell

Absolute direction changes (used by the human-playable UI) are available via
`change_direction((dx, dy))`, which ignores 180-degree reversals, followed by
`step(STRAIGHT)`.
"""

import random

GRID_WIDTH = 20
GRID_HEIGHT = 15

FOOD_SCORE = 10
BONUS_CHANCE = 0.1
BONUS_SCORE = 50
BONUS_LENGTH = 3

LEFT = 0
STRAIGHT = 1
RIGHT = 2

UP = (0, -1)
DOWN = (0, 1)
LEFT_DIR = (-1, 0)
RIGHT_DIR = (1, 0)


def turn_left(direction):
    dx, dy = direction
    return (dy, -dx)


def turn_right(direction):
    dx, dy = direction
    return (-dy, dx)


class SnakeGame:
    """Headless Snake game. Deterministic when given a seed."""

    def __init__(self, seed=None, rng=None):
        self.rng = rng if rng is not None else random.Random(seed)
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT_DIR
        self.score = 0
        self.done = False
        self.steps = 0
        self.steps_since_food = 0
        self._grow = False
        self.bonus = None
        self.food = self._spawn_food()

    def _spawn_food(self):
        while True:
            pos = (
                self.rng.randint(0, GRID_WIDTH - 1),
                self.rng.randint(0, GRID_HEIGHT - 1),
            )
            if pos not in self.body and pos != self.bonus:
                return pos

    def _spawn_bonus(self):
        while True:
            pos = (
                self.rng.randint(0, GRID_WIDTH - 1),
                self.rng.randint(0, GRID_HEIGHT - 1),
            )
            if pos not in self.body and pos != self.food:
                return pos

    def change_direction(self, new_direction):
        """Absolute direction change; 180-degree reversals are ignored."""
        if (-new_direction[0], -new_direction[1]) != self.direction:
            self.direction = new_direction

    def step(self, action=STRAIGHT):
        """Apply a relative turn and advance the game one tick.

        Returns (done, score).
        """
        if self.done:
            return self.done, self.score

        if action == LEFT:
            self.direction = turn_left(self.direction)
        elif action == RIGHT:
            self.direction = turn_right(self.direction)

        head_x, head_y = self.body[0]
        new_head = (
            (head_x + self.direction[0]) % GRID_WIDTH,
            (head_y + self.direction[1]) % GRID_HEIGHT,
        )
        self.body.insert(0, new_head)
        if self._grow:
            self._grow = False
        else:
            self.body.pop()

        self.steps += 1
        self.steps_since_food += 1

        if new_head in self.body[1:]:
            self.done = True
            return self.done, self.score

        if new_head == self.food:
            self._grow = True
            self.score += FOOD_SCORE
            self.steps_since_food = 0
            self.food = self._spawn_food()
            if self.bonus is None and self.rng.random() < BONUS_CHANCE:
                self.bonus = self._spawn_bonus()

        if self.bonus is not None and new_head == self.bonus:
            self._grow = True
            self.score += BONUS_SCORE
            self.steps_since_food = 0
            for _ in range(BONUS_LENGTH - 1):
                self.body.append(self.body[-1])
            self.bonus = None

        return self.done, self.score
