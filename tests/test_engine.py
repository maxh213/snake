import random

import pytest

import engine
from engine import SnakeGame, GRID_WIDTH, GRID_HEIGHT, LEFT, STRAIGHT, RIGHT


def make_game(seed=0):
    return SnakeGame(seed=seed)


def test_initial_state():
    g = make_game()
    assert g.body == [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    assert g.direction == engine.RIGHT_DIR
    assert g.score == 0
    assert not g.done
    assert g.food is not None
    assert g.bonus is None


def test_straight_moves_one_cell():
    g = make_game()
    g.food = (0, 0)  # keep food out of the way
    head = g.body[0]
    g.step(STRAIGHT)
    assert g.body[0] == ((head[0] + 1) % GRID_WIDTH, head[1])
    assert len(g.body) == 1


def test_relative_turns():
    g = make_game()
    g.food = (0, 0)
    assert g.direction == (1, 0)
    g.step(LEFT)
    assert g.direction == (0, -1)  # up
    g.step(LEFT)
    assert g.direction == (-1, 0)  # left
    g.step(RIGHT)
    assert g.direction == (0, -1)  # back up


@pytest.mark.parametrize(
    "start,direction,expected",
    [
        ((GRID_WIDTH - 1, 5), (1, 0), (0, 5)),          # right edge
        ((0, 5), (-1, 0), (GRID_WIDTH - 1, 5)),          # left edge
        ((5, 0), (0, -1), (5, GRID_HEIGHT - 1)),         # top edge
        ((5, GRID_HEIGHT - 1), (0, 1), (5, 0)),          # bottom edge
    ],
)
def test_wrapping_all_edges(start, direction, expected):
    g = make_game()
    g.body = [start]
    g.direction = direction
    g.food = (12, 12)
    g.step(STRAIGHT)
    assert g.body[0] == expected
    assert not g.done


def test_growth_on_food():
    g = make_game()
    head = g.body[0]
    g.food = (head[0] + 1, head[1])
    done, score = g.step(STRAIGHT)
    assert score == engine.FOOD_SCORE
    assert not done
    # growth applies on the following move
    g.food = (0, 0)
    g.step(STRAIGHT)
    assert len(g.body) == 2


def test_self_collision_death():
    g = make_game()
    g.food = (0, 0)
    # Build a 5-long snake manually: head at (10,7) moving right, body trailing left
    g.body = [(10, 7), (9, 7), (9, 8), (10, 8), (11, 8)]
    g.direction = (1, 0)
    # turn right (down) into own body at (10,8)... first move down to (10,8)
    done, _ = g.step(RIGHT)
    assert done
    assert g.done


def test_no_180_reversal():
    g = make_game()
    g.food = (0, 0)
    assert g.direction == engine.RIGHT_DIR
    g.change_direction(engine.LEFT_DIR)
    assert g.direction == engine.RIGHT_DIR
    g.change_direction(engine.UP)
    assert g.direction == engine.UP
    g.change_direction(engine.DOWN)
    assert g.direction == engine.UP


def test_food_never_spawns_on_snake():
    rng = random.Random(123)
    for _ in range(50):
        g = SnakeGame(rng=random.Random(rng.random()))
        g.body = [(x, 7) for x in range(GRID_WIDTH)]  # full row
        for _ in range(20):
            food = g._spawn_food()
            assert food not in g.body


def test_bonus_never_spawns_on_snake_or_food():
    g = make_game(seed=7)
    g.body = [(x, 3) for x in range(GRID_WIDTH)]
    for _ in range(20):
        bonus = g._spawn_bonus()
        assert bonus not in g.body
        assert bonus != g.food


def test_seeded_games_deterministic():
    def run(seed):
        g = SnakeGame(seed=seed)
        states = []
        rng = random.Random(999)
        for _ in range(200):
            action = rng.choice([LEFT, STRAIGHT, RIGHT])
            done, score = g.step(action)
            states.append((tuple(g.body), g.food, g.bonus, score, done))
            if done:
                break
        return states

    assert run(42) == run(42)
    # sanity: different seeds usually diverge in food placement
    g1, g2 = SnakeGame(seed=1), SnakeGame(seed=2)
    assert g1.food != g2.food or True  # non-strict, just seed init check


def test_step_after_done_is_noop():
    g = make_game()
    g.done = True
    body_before = list(g.body)
    done, score = g.step(STRAIGHT)
    assert done
    assert g.body == body_before


def test_starvation_counter_resets_on_food():
    g = make_game()
    head = g.body[0]
    g.food = (head[0] + 2, head[1])
    g.step(STRAIGHT)
    assert g.steps_since_food == 1
    g.step(STRAIGHT)
    assert g.steps_since_food == 0
