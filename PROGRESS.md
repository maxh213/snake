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
- [ ] Create `train.py` (tournament selection, elitism, crossover, Gaussian mutation, multiprocessing)
- [ ] Smoke run: `train.py --pop 20 --generations 2 --workers 2 --seed 42 --out runs/smoke` (<60s, fitness.csv + best.npy)
- [ ] Commit

## Phase 4: Visualization
- [ ] `watch.py` replays saved genome in pygame window
- [ ] `plot_fitness.py` writes fitness.png (Agg backend)
- [ ] Commit

## Phase 5: Full training run
- [ ] `evaluate.py`
- [ ] Full training to mean ≥ 200 over 20 games (or documented plateau)
- [ ] `results/best.npy`, `results/fitness.csv`, `results/fitness.png`
- [ ] Final verification + commit

## Decisions & Notes
- **Python 3.14 + pygame 2.6.1 is broken** (`pygame.font` circular import). Replaced with `pygame-ce` 2.5.7 in `.venv` — drop-in compatible, `import pygame` unchanged.
- Project uses a local venv: `.venv/` (pygame-ce, numpy, matplotlib, pytest). Run everything with `.venv/bin/python`.
- `step(action)` uses relative turns (0=left, 1=straight, 2=right). Human UI uses `change_direction()` (absolute, blocks 180°) + `step(STRAIGHT)`.
