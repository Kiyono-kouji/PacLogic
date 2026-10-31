from collections import deque

from scripts.levels_for_evaluation import evaluation_levels
from src.logic.bfs_search import plan_bfs
from src.logic.grid import Level
from src.logic.search import ASTAR, heuristic_for, plan


def true_costs_left(level: Level, pellet_mode: bool) -> dict:
    pellets = level.pellets if pellet_mode else frozenset()
    goal = (level.goal, frozenset())
    costs = {goal: 0}
    frontier = deque([goal])
    while frontier:
        state = frontier.popleft()
        tile, remaining = state
        befores = (remaining, remaining | {tile}) if tile in pellets else (remaining,)
        for _, previous_tile in level.adjacency[tile]:
            for before in befores:
                previous = (previous_tile, before)
                if previous_tile not in before and previous not in costs:
                    costs[previous] = costs[state] + 1
                    frontier.append(previous)
    return costs


def check(level: Level, pellet_mode: bool) -> dict:
    pellets = level.pellets if pellet_mode else frozenset()
    astar = plan(level, level.start, level.pellets, pellet_mode, algorithm=ASTAR).cost
    bfs = plan_bfs(level, level.start, level.pellets, pellet_mode).cost
    costs = true_costs_left(level, pellet_mode)
    estimate = heuristic_for(level, pellet_mode)
    too_high = [state for state, cost in costs.items() if estimate(state) > cost]
    return {
        "astar": astar,
        "bfs": bfs,
        "start_cost": costs.get((level.start, pellets)),
        "states": len(costs),
        "too_high": too_high,
    }


def main():
    failures = 0
    print(f"{'Level':<8}{'Mode':<9}{'A*':>5}{'BFS':>6}{'States':>9}  Verdict")
    for level, mode, pellet_mode in evaluation_levels():
        result = check(level, pellet_mode)
        optimal = result["astar"] == result["bfs"] == result["start_cost"]
        admissible = not result["too_high"]
        verdicts = [
            "A* = optimal" if optimal else f"A* MISMATCH (true cost {result['start_cost']})",
            "h(n) admissible" if admissible else f"h(n) TOO HIGH in {len(result['too_high'])} states, e.g. {result['too_high'][0]}",
        ]
        failures += (not optimal) + (not admissible)
        print(f"{level.name:<8}{mode:<9}{result['astar']:>5}{result['bfs']:>6}{result['states']:>9}  {', '.join(verdicts)}")
    print("\nAll checks passed" if failures == 0 else f"\n{failures} checks failed")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
