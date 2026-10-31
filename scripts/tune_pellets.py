import csv
import dataclasses
import random

from scripts.sample_programs import controllers_for
from src.core import settings
from src.logic.brain import PacManBrain
from src.logic.grid import Level, load_level
from src.logic.search import ALGORITHMS
from src.logic.sim import Sim

RESULTS_FILE = settings.ROOT_DIR / "results" / "pellet_tuning.csv"
LEVEL_FILE = "hard.txt"
DIFFICULTY = "Hard"
PELLET_COUNTS = (7, 8, 9, 10)
SEEDS = 8
REPEATS = 2
TICK_MS = settings.PLAY_TICK_SECONDS * 1000
BUDGET_MS = TICK_MS / 2


def _pellet_tiles(level: Level) -> list:
    return sorted(level.floor_tiles - level.safe_zone - {level.start, level.goal} - set(level.ghosts))


def _round_slowest_ms(level: Level, algorithm: str) -> float:
    ghost_count = min(settings.MAX_GHOSTS, len(level.ghosts))
    brain = PacManBrain(level, DIFFICULTY, True, algorithm)
    Sim(level, brain, True, ghost_count, controllers_for(DIFFICULTY, ghost_count)).run()
    return brain.slowest_ms


def slowest_plan_ms(level: Level, algorithm: str) -> float:
    return min(_round_slowest_ms(level, algorithm) for _ in range(REPEATS))


def tuning_rows() -> list[dict]:
    base = load_level(settings.LEVELS_DIR / LEVEL_FILE)
    tiles = _pellet_tiles(base)
    rows = []
    for count in PELLET_COUNTS:
        levels = [dataclasses.replace(base, pellets=frozenset(random.Random(seed).sample(tiles, count))) for seed in range(SEEDS)]
        for algorithm in ALGORITHMS:
            slowest = max(slowest_plan_ms(level, algorithm) for level in levels)
            rows.append({"pellets": count, "algorithm": algorithm, "slowest_ms": round(slowest, 1), "within_budget": slowest < BUDGET_MS})
            print(f"{count:>3} pellets  {algorithm:<7}{slowest:>9.1f} ms", flush=True)
    return rows


def main():
    print(f"{LEVEL_FILE}, {DIFFICULTY}, pellet mode, {SEEDS} pellet layouts per count, best of {REPEATS} runs, one tick = {TICK_MS:.0f} ms, budget = half a tick = {BUDGET_MS:.0f} ms")
    rows = tuning_rows()
    RESULTS_FILE.parent.mkdir(exist_ok=True)
    with open(RESULTS_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    largest = 0
    for count in PELLET_COUNTS:
        if not all(row["within_budget"] for row in rows if row["pellets"] == count):
            break
        largest = count
    print(f"\nLargest pellet count within budget for every algorithm: {largest} (MAX_PELLETS = {settings.MAX_PELLETS})")
    print(f"Saved {RESULTS_FILE}")


if __name__ == "__main__":
    main()
