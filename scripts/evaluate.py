import csv
from collections import deque
from statistics import median

from scripts.levels_for_evaluation import evaluation_levels
from src.core import settings
from src.logic.grid import Level
from src.logic.search import ALGORITHMS, ASTAR, BFS, heuristic_for, plan

RESULTS_FILE = settings.ROOT_DIR / "results" / "evaluation.csv"
RUNS = 5
COLUMNS = ("level", "mode", "algorithm", "cost", "optimal_cost", "optimal", "nodes_expanded", "max_frontier", "median_ms")


def measure(level: Level, pellet_mode: bool, algorithm: str) -> dict:
    results = [plan(level, level.start, level.pellets, pellet_mode, algorithm=algorithm) for _ in range(RUNS)]
    first = results[0]
    return {
        "cost": first.cost,
        "nodes_expanded": first.expanded,
        "max_frontier": first.max_frontier,
        "median_ms": round(median(result.ms for result in results), 3),
    }


def evaluation_rows() -> list[dict]:
    rows = []
    for level, mode, pellet_mode in evaluation_levels():
        stats = {algorithm: measure(level, pellet_mode, algorithm) for algorithm in ALGORITHMS}
        optimal_cost = stats[BFS]["cost"]
        for algorithm, values in stats.items():
            row = {"level": level.name, "mode": mode, "algorithm": algorithm, **values}
            row.update(optimal_cost=optimal_cost, optimal=values["cost"] == optimal_cost)
            rows.append(row)
    return rows


def true_costs_left(level: Level, pellet_mode: bool) -> dict:
    pellets = level.pellets if pellet_mode else frozenset()
    goal = (level.goal, frozenset())
    costs = {goal: 0}
    frontier = deque([goal])
    while frontier:
        tile, remaining = frontier.popleft()
        befores = [remaining, remaining | {tile}] if tile in pellets else [remaining]
        for _, previous_tile in level.adjacency[tile]:
            for before in befores:
                previous = (previous_tile, before)
                if previous_tile not in before and previous not in costs:
                    costs[previous] = costs[(tile, remaining)] + 1
                    frontier.append(previous)
    return costs


def heuristic_checks() -> list[dict]:
    checks = []
    for level, mode, pellet_mode in evaluation_levels():
        estimate = heuristic_for(level, pellet_mode)
        costs = true_costs_left(level, pellet_mode)
        overestimates = sum(estimate(state) > cost for state, cost in costs.items())
        checks.append({"level": level.name, "mode": mode, "states": len(costs), "overestimates": overestimates})
    return checks


def print_table(rows: list[dict]):
    print(f"{'Level':<8}{'Mode':<9}{'Algorithm':<10}{'Cost':>6}{'Optimal':>9}{'Expanded':>10}{'Frontier':>10}{'Median ms':>11}")
    for row in rows:
        verdict = "yes" if row["optimal"] else "no"
        print(
            f"{row['level']:<8}{row['mode']:<9}{row['algorithm']:<10}{row['cost']:>6}{verdict:>9}"
            f"{row['nodes_expanded']:>10}{row['max_frontier']:>10}{row['median_ms']:>11.3f}"
        )


def main():
    rows = evaluation_rows()
    RESULTS_FILE.parent.mkdir(exist_ok=True)
    with open(RESULTS_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print_table(rows)
    astar_rows = [row for row in rows if row["algorithm"] == ASTAR]
    print(f"\nA* matches the optimal cost on {sum(row['optimal'] for row in astar_rows)} of {len(astar_rows)} level/mode pairs")
    print("\nHeuristic check: h(n) against the true cost left, for every state that can reach the exit")
    for check in heuristic_checks():
        verdict = "never overestimates" if check["overestimates"] == 0 else f"OVERESTIMATES in {check['overestimates']} states"
        print(f"{check['level']:<8}{check['mode']:<9}{check['states']:>7} states  {verdict}")
    print(f"\nSaved {RESULTS_FILE}")


if __name__ == "__main__":
    main()
