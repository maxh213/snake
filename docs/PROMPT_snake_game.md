# Nokia 3310 Snake Clone

## Overview
Build a faithful Pygame clone of the classic Nokia 3310 Snake game. The player controls a snake that moves on a grid, eats food to grow longer, and must avoid colliding with walls or itself. The game features a retro LCD aesthetic, score tracking, high-score persistence, and increasing difficulty as the snake grows.

## Context & Constraints
- **Stack:** Python 3.x + Pygame 2.x
- **No external dependencies beyond Pygame**
- **Single-module architecture:** All game logic lives in `snake.py`
- **Assumptions made:**
  - Screen resolution: 640×480 (retro feel, easily scalable)
  - Grid size: 20×15 cells (32px per cell)
  - Target frame rate: 60 FPS, but snake moves on a fixed tick (e.g., every 8 frames, decreasing as score increases)
  - Retro green-on-black LCD color scheme (#9BBC0F background, #0F380F foreground)
  - No sound effects (Out of Scope)
  - No menu music (Out of Scope)

## Phases

### Phase 1: Game Loop & Grid Rendering
- Initialize Pygame window with retro LCD color scheme.
- Render a visible grid of 20×15 cells.
- Implement a fixed-tick game clock (snake moves once per N frames).
- Handle clean window close / quit event.
- **Deliverables:** `snake.py` runs and displays a static grid.
- **Verify:** `python snake.py` opens a window showing the grid; closes cleanly on Q or window X.

### Phase 2: Snake Movement & Input
- Create a Snake class: represented as a list of (x, y) grid coordinates.
- Implement directional movement (Up/Down/Left/Right) with arrow keys.
- Prevent 180-degree direction reversals (e.g., cannot go Left while moving Right).
- Render snake as filled cells on the grid.
- **Deliverables:** Controllable snake that moves smoothly across the grid.
- **Verify:** Run `python snake.py`; snake moves with arrow keys and cannot reverse into itself.

### Phase 3: Food, Growth & Collision
- Spawn food at random empty grid cells.
- Detect when snake head reaches food; grow snake by one segment.
- Detect wall collisions and self-collisions; print "GAME OVER" to console and exit.
- **Deliverables:** Playable core loop: eat food, grow, die on collision.
- **Verify:** Run `python snake.py`; snake grows on eating food, game ends on wall/self collision.

### Phase 4: Score, HUD & Game Over Screen
- Add a score counter (+10 per food eaten).
- Display current score and high score on-screen during gameplay.
- Replace console "GAME OVER" with an on-screen "GAME OVER" overlay.
- Allow restart via R key or quit via Q key from game over screen.
- **Deliverables:** In-game HUD and polished game-over flow.
- **Verify:** Run `python snake.py`; score updates live, game over screen appears, R restarts.

### Phase 5: Difficulty Progression & High Score Persistence
- Increase snake speed (reduce tick interval) every 50 points.
- Persist high score to a local file (`highscore.txt`) and load it on startup.
- **Deliverables:** Speed increases with score; high score survives between sessions.
- **Verify:** Run `python snake.py`; snake visibly speeds up, `highscore.txt` is created/updated.

### Phase 6: Polish & Start Screen
- Add a start screen with title and "Press ENTER to Start" prompt.
- Add a pause feature (P key toggles pause overlay).
- Ensure all text uses a legible built-in Pygame font (or bundled pixel font if preferred).
- **Deliverables:** Complete game with start screen and pause functionality.
- **Verify:** Run `python snake.py`; start screen → game → pause → resume → game over → restart.

## Success Criteria (all must be true)
- [ ] `python snake.py` launches without errors and displays a window.
- [ ] Player can control the snake with arrow keys; 180-degree reversals are blocked.
- [ ] Eating food causes the snake to grow by one segment and increases score by 10.
- [ ] Colliding with walls or the snake's own body triggers a Game Over screen.
- [ ] Score and high score are rendered on-screen during gameplay.
- [ ] High score persists to `highscore.txt` and is read on next launch.
- [ ] Snake movement speed increases at least once as score grows.
- [ ] A start screen and pause functionality are both present and functional.
- [ ] The game uses the specified retro LCD green-on-black color scheme.

## Out of Scope
- Sound effects or music
- Multiple levels or maze walls
- Online leaderboards
- Mobile / touchscreen controls
- Packaging into an executable
- Settings / options menu
- Power-ups or special items

## Rules for the Implementing Agent
- Never delete, skip, or weaken a test to make it pass; flag suspect tests in `PROGRESS.md` instead.
- Record failed approaches and key decisions in `PROGRESS.md` as you go.
- Commit after each completed phase.
- Keep the code in a single file (`snake.py`) unless adding `highscore.txt` or assets.
