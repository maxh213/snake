import numpy as np

import agent
import engine
from agent import NeuralNet, observe, OBS_SIZE
from engine import SnakeGame, GRID_WIDTH, GRID_HEIGHT


def make_game():
    g = SnakeGame(seed=0)
    g.body = [(10, 7)]
    g.direction = engine.RIGHT_DIR
    g.food = (0, 0)
    g.bonus = None
    return g


def test_observation_length_and_dtype():
    g = make_game()
    obs = observe(g)
    assert obs.shape == (OBS_SIZE,)
    assert obs.dtype == np.float64


def test_danger_flags():
    g = make_game()
    # body ahead (11,7), left is up (10,6), right is down (10,8)
    g.body = [(10, 7), (11, 7), (10, 6), (9, 6), (9, 7), (9, 8)]
    g.food = (0, 0)
    obs = observe(g)
    assert obs[0] == 1.0  # danger straight at (11,7)
    assert obs[1] == 1.0  # danger left at (10,6)
    assert obs[2] == 0.0  # (10,8) is free


def test_food_direction_ahead():
    g = make_game()
    g.food = (13, 7)  # 3 cells ahead, moving right
    obs = observe(g)
    assert obs[3] > 0  # ahead
    assert obs[4] == 0  # not to either side
    assert obs[3] == 3 / (max(GRID_WIDTH, GRID_HEIGHT) / 2.0)


def test_food_direction_right_side():
    g = make_game()
    g.food = (10, 10)  # 3 cells below; moving right => below is to the right
    obs = observe(g)
    assert obs[3] == 0
    assert obs[4] > 0


def test_food_direction_wraps_toroidally():
    g = make_game()
    g.body = [(19, 7)]
    g.food = (1, 7)  # 2 ahead through the wrap, not 18 behind
    obs = observe(g)
    assert obs[3] == 2 / (max(GRID_WIDTH, GRID_HEIGHT) / 2.0)


def test_bonus_used_when_nearer():
    g = make_game()
    g.food = (10, 14)
    g.bonus = (12, 7)  # distance 2 < food distance
    obs = observe(g)
    assert obs[3] == 2 / (max(GRID_WIDTH, GRID_HEIGHT) / 2.0)
    assert obs[4] == 0


def test_length_normalization():
    g = make_game()
    g.body = [(x, 7) for x in range(10, 0, -1)]
    obs = observe(g)
    assert obs[5] == 10 / (GRID_WIDTH * GRID_HEIGHT)


def test_genome_roundtrip():
    rng = np.random.default_rng(42)
    genome = rng.normal(size=NeuralNet.genome_size())
    net = NeuralNet.from_genome(genome)
    assert np.allclose(net.to_genome(), genome)


def test_genome_size_rejects_wrong_shape():
    import pytest

    with pytest.raises(ValueError):
        NeuralNet.from_genome(np.zeros(5))


def test_act_deterministic_and_valid():
    rng = np.random.default_rng(7)
    genome = rng.normal(size=NeuralNet.genome_size())
    net = NeuralNet.from_genome(genome)
    obs = observe(make_game())
    actions = {net.act(obs) for _ in range(10)}
    assert len(actions) == 1
    assert actions.pop() in (0, 1, 2)


def test_play_game_runs_and_scores():
    rng = np.random.default_rng(3)
    genome = rng.normal(size=NeuralNet.genome_size())
    score, steps = agent.play_game(genome, seed=1)
    assert steps > 0
    assert score >= 0
    # deterministic
    assert agent.play_game(genome, seed=1) == (score, steps)
