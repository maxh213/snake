# Snake GA — Progress

## Phase 1: Headless engine refactor
- [x] Create `engine.py` (headless `SnakeGame`, relative-turn `step()`, seedable RNG, no pygame)
- [x] Refactor `snake.py` to use `engine.SnakeGame` (rendering/HUD/pause/highscore unchanged)
- [x] `tests/test_engine.py` — 15 tests, all passing (`.venv/bin/python -m pytest tests/ -q`)
- [x] Manual check: `SDL_VIDEODRIVER=dummy python snake.py` runs its loop cleanly (no display attached to this session; logic engine-backed and unit-tested)
- [x] Commit

## Phase 2: Agent — observations and neural net
- [x] Create `agent.py` (`observe()`, `NeuralNet`, `play_game()` helper)
- [x] `tests/test_agent.py` — 11 tests; full suite 26 passing
- [x] Commit

## Phase 3: GA training loop
- [x] Create `train.py` (tournament selection, elitism, crossover, Gaussian mutation, multiprocessing)
- [x] Smoke run: `train.py --pop 20 --generations 2 --workers 2 --seed 42 --out runs/smoke` — 5.2s, fitness.csv (3 lines) + best.npy
- [x] Commit

## Phase 4: Visualization
- [x] `watch.py` replays saved genome in pygame window (verified with SDL_VIDEODRIVER=dummy; ran cleanly, killed by timeout as expected since it renders until Q)
- [x] `plot_fitness.py` writes fitness.png (Agg backend, no display)
- [x] Commit

## Phase 5: Full training run
- [x] `evaluate.py`
- [x] Full training: pop 200, 300 generations, seed 1 (defaults) — target hit on first run
- [x] `results/best.npy`, `results/fitness.csv`, `results/fitness.png`
- [x] Final verification + commit

## Final results
- `evaluate.py results/best.npy --games 20 --threshold 200` → **mean 455.5** (min 150, max 760), exit 0.
- Target (mean ≥ 200) was already exceeded by generation ~27 (eval mean 298); full 300-gen run reached best fitness ~794k (~790 score in-training).
- Fitness curve (`results/fitness.png`) shows steady best/mean improvement across generations.
- Full test suite: 26 passing. `engine.py` has zero pygame references.

## Decisions & Notes
- **Python 3.14 + pygame 2.6.1 is broken** (`pygame.font` circular import). Replaced with `pygame-ce` 2.5.7 in `.venv` — drop-in compatible, `import pygame` unchanged.
- Project uses a local venv: `.venv/` (pygame-ce, numpy, matplotlib, pytest). Run everything with `.venv/bin/python`.
- `step(action)` uses relative turns (0=left, 1=straight, 2=right). Human UI uses `change_direction()` (absolute, blocks 180°) + `step(STRAIGHT)`.
