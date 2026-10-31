import csv
import itertools
import math

from scripts.levels_for_evaluation import evaluation_levels
from scripts.sample_programs import controllers_for
from src.core import settings
from src.logic.brain import PacManBrain
from src.logic.grid import Level, bfs_dist, move
from src.logic.sim import BLOCKED, CAUGHT, ESCAPED, Sim

RESULTS_FILE = settings.ROOT_DIR / "results" / "danger_tuning.csv"
TUNED_DIFFICULTY = "Hard"
RADII = (1, 2, 3)
PENALTIES = (0, 2, 4, 8)
INTERCEPT_OFFSETS = (0, 2, 4)
OUTCOMES = (CAUGHT, ESCAPED, BLOCKED)


def _path_moves(level: Level, start: tuple, goal: tuple) -> list:
    distances = bfs_dist(level, goal, level.safe_zone)
    if start not in distances:
        return []
    moves, tile = [], start
    while tile != goal:
        direction, tile = next(
            (direction, step) for direction, step in level.adjacency[tile] if distances.get(step) == distances[tile] - 1
        )
        moves.append(direction)
    return moves


def _play_moves(moves: list):
    yield from moves
    while True:
        yield None


def _planned_tiles(level: Level, pellet_mode: bool) -> list:
    tiles = [level.start]
    for direction in PacManBrain(level, TUNED_DIFFICULTY, pellet_mode).planned_route:
        tiles.append(move(tiles[-1], direction))
    return tiles


def interceptor_controllers(level: Level, pellet_mode: bool, ghost_count: int, offset: int) -> list:
    route = _planned_tiles(level, pellet_mode)
    controllers = []
    for index, ghost in enumerate(level.ghosts[:ghost_count]):
        reach = bfs_dist(level, ghost, level.safe_zone)
        targets = [
            tile for step, tile in enumerate(route)
            if tile not in level.safe_zone and reach.get(tile, math.inf) <= step
        ]
        moves = _path_moves(level, ghost, targets[min(len(targets) - 1, offset + index)]) if targets else []
        controllers.append(_play_moves(moves))
    return controllers


def play(level: Level, difficulty: str, pellet_mode: bool, ghost_count: int, controllers: list) -> Sim:
    sim = Sim(level, PacManBrain(level, difficulty, pellet_mode), pellet_mode, ghost_count, controllers)
    sim.run()
    return sim


def walked_into_ghost(sim: Sim) -> bool:
    return sim.status == CAUGHT and sim.pac != sim.previous_pac and sim.pac in sim.ghosts and sim.previous_pac not in sim.ghosts


def opponent_rounds(difficulty: str) -> dict:
    rounds = {"sample": [], "interceptor": []}
    for level, mode, pellet_mode in evaluation_levels():
        for ghost_count in range(1, len(level.ghosts) + 1):
            rounds["sample"].append(play(level, difficulty, pellet_mode, ghost_count, controllers_for(difficulty, ghost_count)))
            for offset in INTERCEPT_OFFSETS:
                controllers = interceptor_controllers(level, pellet_mode, ghost_count, offset)
                rounds["interceptor"].append(play(level, difficulty, pellet_mode, ghost_count, controllers))
    return rounds


def summarize(difficulty: str, opponent: str, sims: list) -> dict:
    counts = {outcome: sum(sim.status == outcome for sim in sims) for outcome in OUTCOMES}
    return {
        "difficulty": difficulty,
        "danger_radius": settings.DANGER_RADIUS,
        "danger_penalty": settings.DANGER_PENALTY,
        "opponent": opponent,
        **counts,
        "rounds": len(sims),
        "catch_rate": round(counts[CAUGHT] / len(sims), 3),
        "walked_into_ghost": sum(walked_into_ghost(sim) for sim in sims),
        "slowest_ms": round(max(sim.brain.slowest_ms for sim in sims), 1),
    }


def tuning_rows() -> list[dict]:
    chosen = (settings.DANGER_RADIUS, settings.DANGER_PENALTY)
    rows = []
    for difficulty in settings.DIFFICULTIES:
        if difficulty != TUNED_DIFFICULTY:
            rows += [summarize(difficulty, opponent, sims) for opponent, sims in opponent_rounds(difficulty).items()]
    for radius, penalty in itertools.product(RADII, PENALTIES):
        settings.DANGER_RADIUS, settings.DANGER_PENALTY = radius, penalty
        rows += [summarize(TUNED_DIFFICULTY, opponent, sims) for opponent, sims in opponent_rounds(TUNED_DIFFICULTY).items()]
    settings.DANGER_RADIUS, settings.DANGER_PENALTY = chosen
    return rows


def print_table(rows: list[dict]):
    chosen = (settings.DANGER_RADIUS, settings.DANGER_PENALTY)
    print(f"{'Difficulty':<11}{'Radius':>7}{'Penalty':>8}  {'Opponent':<12}{'Caught':>9}{'Catch rate':>11}{'Blocked':>8}{'Walked in':>10}{'Slowest ms':>11}")
    for row in rows:
        tuned = row["difficulty"] == TUNED_DIFFICULTY
        radius = row["danger_radius"] if tuned else "-"
        penalty = row["danger_penalty"] if tuned else "-"
        marker = "  <- chosen" if tuned and (row["danger_radius"], row["danger_penalty"]) == chosen else ""
        print(
            f"{row['difficulty']:<11}{radius:>7}{penalty:>8}  {row['opponent']:<12}{row[CAUGHT]:>4} /{row['rounds']:>3}"
            f"{row['catch_rate']:>11.3f}{row[BLOCKED]:>8}{row['walked_into_ghost']:>10}{row['slowest_ms']:>11.1f}{marker}"
        )


def main():
    rows = tuning_rows()
    RESULTS_FILE.parent.mkdir(exist_ok=True)
    with open(RESULTS_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print("Sample: Life's sample programs. Interceptor: each ghost walks to a tile on Pac-Man's first route that it reaches first, then waits.\n")
    print_table(rows)
    print(f"\nChosen for {TUNED_DIFFICULTY}: DANGER_RADIUS = {settings.DANGER_RADIUS}, DANGER_PENALTY = {settings.DANGER_PENALTY}")
    print(f"Saved {RESULTS_FILE}")


if __name__ == "__main__":
    main()
