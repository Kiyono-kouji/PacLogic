import csv
import random

from scripts.check_optimal import check
from src.core import settings
from src.logic.brain import PacManBrain
from src.logic.grid import Level, load_level, maze_distances
from src.logic.maze_generator import block_count, generate_level, intercept_moves, route_tiles
from src.logic.sim import CAUGHT, ESCAPED, Sim

RESULTS_FILE = settings.ROOT_DIR / "results" / "random_levels.csv"
SEEDS = 20
COLUMNS = (
    "level",
    "seed",
    "mode",
    "astar_cost",
    "bfs_cost",
    "optimal",
    "admissible",
    "exit_steps",
    "nearest_ghost",
    "idle_ghosts",
    "interceptor",
    "interceptor_blocks",
    "hard_interceptor",
    "hard_slowest_ms",
)


def play(level: Level, difficulty: str, pellet_mode: bool, leader_moves: list | None) -> Sim:
    controllers = [iter(leader_moves)] if leader_moves is not None else None
    brain = PacManBrain(level, difficulty, pellet_mode)
    sim = Sim(level, brain, pellet_mode, len(level.ghosts), controllers)
    sim.run()
    return sim


def check_maze(level: Level, seed: int, mode: str, pellet_mode: bool) -> dict:
    result = check(level, pellet_mode)
    from_start = maze_distances(level, level.start)
    planned = PacManBrain(level, "Easy", pellet_mode).planned_route
    leader_moves = intercept_moves(level, level.ghosts[0], route_tiles(level.start, planned))
    hard = play(level, "Hard", pellet_mode, leader_moves or [])
    return {
        "level": level.name,
        "seed": seed,
        "mode": mode,
        "astar_cost": result["astar"],
        "bfs_cost": result["bfs"],
        "optimal": result["astar"] == result["bfs"] == result["start_cost"],
        "admissible": not result["too_high"],
        "exit_steps": from_start[level.goal],
        "nearest_ghost": min(from_start[ghost] for ghost in level.ghosts),
        "idle_ghosts": play(level, "Easy", pellet_mode, None).status,
        "interceptor": play(level, "Easy", pellet_mode, leader_moves).status if leader_moves else "none",
        "interceptor_blocks": block_count(leader_moves) if leader_moves else None,
        "hard_interceptor": hard.status,
        "hard_slowest_ms": round(hard.brain.slowest_ms, 1),
    }


def playable(row: dict) -> bool:
    return (
        row["optimal"]
        and row["admissible"]
        and row["idle_ghosts"] == ESCAPED
        and row["interceptor"] == CAUGHT
        and row["nearest_ghost"] >= settings.RANDOM_GHOST_MIN_DISTANCE
    )


def main():
    rows = []
    for name in settings.LEVEL_FILES:
        template = load_level(settings.LEVELS_DIR / name)
        for seed in range(SEEDS):
            level = generate_level(template, random.Random(seed))
            rows += [check_maze(level, seed, mode, pellet_mode) for mode, pellet_mode in settings.WIN_MODES]
    RESULTS_FILE.parent.mkdir(exist_ok=True)
    with open(RESULTS_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{'Level':<14}{'Mode':<9}{'Mazes':>6}{'Optimal':>9}{'Admiss.':>9}{'Escape':>8}{'Caught':>8}{'Blocks':>8}{'Ghost>=':>8}{'Hard caught':>12}{'Slowest ms':>11}")
    for name in settings.LEVEL_FILES:
        for mode, _ in settings.WIN_MODES:
            group = [row for row in rows if row["level"] == f"random {name[:-4]}" and row["mode"] == mode]
            print(
                f"{group[0]['level']:<14}{mode:<9}{len(group):>6}"
                f"{sum(row['optimal'] for row in group):>9}"
                f"{sum(row['admissible'] for row in group):>9}"
                f"{sum(row['idle_ghosts'] == ESCAPED for row in group):>8}"
                f"{sum(row['interceptor'] == CAUGHT for row in group):>8}"
                f"{max(row['interceptor_blocks'] or 0 for row in group):>8}"
                f"{min(row['nearest_ghost'] for row in group):>8}"
                f"{sum(row['hard_interceptor'] == CAUGHT for row in group):>12}"
                f"{max(row['hard_slowest_ms'] for row in group):>11}"
            )
    failures = [row for row in rows if not playable(row)]
    for row in failures:
        print(f"NOT PLAYABLE: {row}")
    print(f"\n{len(rows) - len(failures)} of {len(rows)} random maze/mode pairs are playable")
    print(f"Saved {RESULTS_FILE}")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
