# Snake Genetic Learning Algorithm

## Overview
Evolve an agent that learns to play the existing Nokia-style Snake game (`snake.py`) using a genetic algorithm with tournament selection. The GA evolves the weights of a small feed-forward neural network that maps game-state observations to a move each tick. The goal is to maximize game score. Deliverables: a headless game engine, a training script, per-generation fitness logging/plotting, and a pygame viewer to watch the best evolved agent play.

## Context & Constraints
- **Project root:** `/home/maxh/workspace/snake/` — all new files go here.
- **Existing code:** `snake.py` is a working human-playable pygame Snake game (grid 20×15, toroidal wrapping — walls wrap, only self-collision kills; food = +10, occasional bonus = +50 and +3 length; speed-up is a rendering concern only and irrelevant to a per-tick agent).
- **Stack:** Python 3.x. `pygame` (already used), `numpy` (net math), `matplotlib` (fitness plot). `multiprocessing` from stdlib allowed for parallel evaluation.
- **Refactor is allowed:** extract the game rules out of `snake.py` into an importable headless engine; `snake.py` must remain playable by a human exactly as before.
- **Assumptions made during planning (do not re-litigate):**
  - Genome = flat numpy vector of neural-net weights. User asked for **tournament selection** as the selection operator; the genome representation was left to us, so: fixed-topology feed-forward net, no topology evolution (no NEAT).
  - Observation vector (input features), all relative to the snake's current heading so the policy is rotation-invariant: danger (self-body) straight/left/right within 1 cell; food direction (ahead/behind, left/right) using shortest toroidal distance; normalized snake length. If a bonus exists, treat the nearer of food/bonus as the target.
  - Network: input → 1 hidden layer (16 units, tanh) → 3 outputs (turn left / straight / turn right), argmax.
  - Fitness = final score, plus a small tie-breaker of steps survived (e.g. `score * 1000 + steps`) so early generations that never eat still get a gradient. A starvation limit (e.g. 100×grid-area steps without eating) kills loops.
  - Success target = "maximum score": interpret as demonstrable strong learned play — best agent averages ≥ 200 points (20 foods) over 20 evaluation games, and fitness curve shows sustained improvement.
  - GA defaults: population 200, tournament size 5, elitism 2, uniform/BLX crossover, per-gene Gaussian mutation (rate ~0.05, σ ~0.3), ≥ 300 generations or until target reached.
  - Each genome is evaluated over ≥ 3 games with different RNG seeds; fitness = mean, to reduce luck.

## Phases

### Phase 1: Headless engine refactor
- Create `engine.py`: a `SnakeGame` class containing all rules (grid constants, snake movement, wrapping, self-collision, food/bonus spawning and scoring) with a `step(action)` method (`action ∈ {left, straight, right}` relative turns or absolute direction — pick one and document it), returning `(done, score)`. Must accept an optional `random.Random`/seed for reproducibility. No pygame imports in `engine.py`.
- Rewrite `snake.py` to import and use `engine.SnakeGame` for all game logic, keeping rendering, input, HUD, pause, start/game-over screens, and `highscore.txt` behaviour identical.
- Add `tests/test_engine.py` (pytest): movement, wrapping at all four edges, growth on food, self-collision death, no-180°-reversal, food never spawns on snake, seeded games are deterministic.
Deliverables: `engine.py`, refactored `snake.py`, `tests/test_engine.py`.
Verify: `python -m pytest tests/ -q` exits 0; `python -c "import engine; g=engine.SnakeGame(seed=1); [g.step(0) for _ in range(50)]"` exits 0; `python snake.py` still opens and plays (manual check, note in PROGRESS.md).

### Phase 2: Agent — observations and neural net
- Create `agent.py`: `observe(game) -> np.ndarray` building the feature vector (documented per-feature), and `NeuralNet` with `from_genome(flat_vector)`, `genome_size()`, and `act(observation) -> action`.
- Deterministic: same genome + same observation → same action.
- Add `tests/test_agent.py`: observation vector has documented fixed length and correct values on hand-built board states (danger flags, food direction); genome round-trips through the net; `act` is deterministic.
Deliverables: `agent.py`, `tests/test_agent.py`.
Verify: `python -m pytest tests/ -q` exits 0.

### Phase 3: GA training loop
- Create `train.py`: population init, fitness evaluation (mean over ≥3 seeded games per genome, with starvation limit), **tournament selection** (size 5), elitism (2), crossover, Gaussian mutation.
- Parallel evaluation via `multiprocessing.Pool` (fall back to serial with a `--workers 1` flag).
- CLI flags with the defaults from Assumptions: `--pop`, `--generations`, `--tournament`, `--mutation-rate`, `--seed`, `--workers`, `--out DIR`.
- Each generation: print and append `generation,best,mean,median` to `runs/<timestamp>/fitness.csv`; save best genome so far to `runs/<timestamp>/best.npy` whenever it improves.
- `--generations 2 --pop 20` must complete in under a minute for smoke testing.
Deliverables: `train.py`, `runs/` output structure.
Verify: `python train.py --pop 20 --generations 2 --workers 2 --seed 42 --out runs/smoke` exits 0 and produces `runs/smoke/fitness.csv` (3 lines incl. header) and `runs/smoke/best.npy`.

### Phase 4: Visualization
- Create `watch.py`: loads a `best.npy` genome and replays it in the existing pygame renderer (reuse `snake.py`'s drawing or a shared render module) at watchable speed; shows score; `Q` quits; `--seed` flag; `--fps` flag.
- Create `plot_fitness.py`: reads a `fitness.csv`, writes `fitness.png` (best & mean per generation) with matplotlib `Agg` backend (no display needed).
Deliverables: `watch.py`, `plot_fitness.py`.
Verify: `python plot_fitness.py runs/smoke/fitness.csv` exits 0 and creates `runs/smoke/fitness.png`; `python watch.py runs/smoke/best.npy --seed 1` opens a window and replays (manual check, note in PROGRESS.md).

### Phase 5: Full training run to target
- Run full training (defaults; raise generations if needed) until best agent's mean score over 20 fresh evaluation games ≥ 200, or until 3 consecutive runs of ≥300 generations plateau (then record best achieved + analysis in PROGRESS.md and stop — do not loop forever).
- Add `evaluate.py`: loads a genome, plays N games (`--games 20`), prints mean/min/max score, exits 0 if mean ≥ threshold (`--threshold 200`) else 1.
- Commit the winning `best.npy` and its `fitness.csv`/`fitness.png` under `results/`.
Deliverables: `evaluate.py`, `results/best.npy`, `results/fitness.csv`, `results/fitness.png`.
Verify: `python evaluate.py results/best.npy --games 20 --threshold 200` exits 0 (or documented plateau analysis in PROGRESS.md).

## Success Criteria (all must be true)
- [ ] `python -m pytest tests/ -q` passes with ≥ 10 tests covering engine and agent.
- [ ] `engine.py` contains no pygame import (`grep -c pygame engine.py` outputs 0).
- [ ] `python snake.py` remains human-playable with identical rules/HUD (manual check recorded in PROGRESS.md).
- [ ] Seeded engine games are deterministic (test asserts identical state sequences for same seed).
- [ ] `train.py` uses tournament selection (size configurable) with elitism, crossover, and mutation.
- [ ] Smoke train command (Phase 3 Verify) exits 0 in < 60s and writes `fitness.csv` + `best.npy`.
- [ ] `plot_fitness.py` produces a `fitness.png` from any `fitness.csv` without a display.
- [ ] `watch.py` replays a saved genome in the pygame window.
- [ ] `results/best.npy` achieves mean score ≥ 200 over 20 games via `evaluate.py` (or a documented plateau analysis exists in PROGRESS.md with best achieved score).
- [ ] `results/fitness.png` shows best fitness increasing over generations.

## Out of Scope
- NEAT or any topology-evolving algorithm.
- Reinforcement learning (DQN, PPO, etc.).
- Changing game rules (grid size, wrapping, scoring) to make learning easier.
- GPU acceleration.
- Web UI / dashboards. Do not build unless asked.
- Hyperparameter auto-search (manual tweaks during Phase 5 are fine; record them).

## Rules for the Implementing Agent
- Never delete, skip, or weaken a test to make it pass; flag suspect tests in PROGRESS.md instead.
- Record failed approaches, hyperparameter changes, and key decisions in PROGRESS.md as you go.
- Commit after each completed phase.
- All work happens inside `/home/maxh/workspace/snake/`.
