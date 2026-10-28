import heapq
import math
import time
from itertools import count

from src.core import settings
from src.logic.bfs_search import maze_heuristic, plan_bfs
from src.logic.grid import Level, manhattan
from src.logic.search_core import SearchResult, elapsed_ms, make_goal_test, make_successors, rebuild_path

ASTAR = "A*"
GREEDY = "Greedy"
BFS = "BFS"
ALGORITHMS = (ASTAR, GREEDY, BFS)


def best_first(start: tuple, is_goal, successors, h, g_weight: int = 1) -> SearchResult:
    started = time.perf_counter()
    order = count()
    best_g = {start: 0}
    parents = {start: None}
    closed = set()
    start_h = h(start)
    frontier = [(start_h, start_h, next(order), start)]
    expanded = 0
    max_frontier = 1
    while frontier:
        state = heapq.heappop(frontier)[3]
        if state in closed:
            continue
        if is_goal(state):
            path = rebuild_path(parents, state)
            return SearchResult(path, best_g[state], expanded, max_frontier, elapsed_ms(started))
        closed.add(state)
        expanded += 1
        for direction, next_state, step_cost in successors(state):
            if next_state in closed:
                continue
            g = best_g[state] + step_cost
            if g < best_g.get(next_state, math.inf):
                best_g[next_state] = g
                parents[next_state] = (state, direction)
                next_h = h(next_state)
                heapq.heappush(frontier, (g_weight * g + next_h, next_h, next(order), next_state))
        max_frontier = max(max_frontier, len(frontier))
    return SearchResult([], None, expanded, max_frontier, elapsed_ms(started))


def manhattan_heuristic(level: Level):
    def estimate(state: tuple) -> int:
        position, remaining = state
        return max([manhattan(position, level.goal), *(manhattan(position, pellet) for pellet in remaining)])

    return estimate


def heuristic_for(level: Level, pellet_mode: bool):
    return maze_heuristic(level) if pellet_mode else manhattan_heuristic(level)


def _ghost_reach(level: Level, ghost: tuple) -> set:
    reached = {ghost}
    frontier = {ghost}
    for _ in range(settings.DANGER_RADIUS):
        frontier = {
            tile
            for current in frontier
            for _, tile in level.adjacency.get(current, ())
            if tile not in reached and tile not in level.safe_zone
        }
        reached |= frontier
    return reached


def danger_map(level: Level, ghosts) -> dict:
    danger = {}
    for ghost in ghosts:
        for tile in _ghost_reach(level, ghost):
            danger[tile] = settings.DANGER_PENALTY
    return danger


def plan(
    level: Level,
    position: tuple,
    pellets: frozenset,
    pellet_mode: bool,
    blocked: frozenset = frozenset(),
    danger: dict | None = None,
    algorithm: str = ASTAR,
) -> SearchResult:
    if algorithm not in ALGORITHMS:
        raise ValueError(f"unknown search algorithm {algorithm!r}")
    if algorithm == BFS:
        return plan_bfs(level, position, pellets, pellet_mode)
    start = (position, frozenset(pellets) if pellet_mode else frozenset())
    successors = make_successors(level, frozenset(blocked), danger or {})
    g_weight = 1 if algorithm == ASTAR else 0
    return best_first(start, make_goal_test(level), successors, heuristic_for(level, pellet_mode), g_weight)
