import heapq
import math
import time
from itertools import count

from src.core import settings
from src.logic.bfs_search import maze_heuristic, plan_bfs
from src.logic.grid import Level, manhattan, maze_distances
from src.logic.search_core import SearchResult, elapsed_ms, make_goal_test, make_successors, rebuild_path

ASTAR = "A*"
GREEDY = "Greedy"
BFS = "BFS"
ALGORITHMS = (ASTAR, GREEDY, BFS)


# A* and Greedy share this loop. use_path_cost=True is A* (priority g + h), False is Greedy (h only).
def best_first(start: tuple, is_goal, successors, h, use_path_cost: bool = True) -> SearchResult:
    started = time.perf_counter()
    order = count()
    best_g = {start: 0}
    parents = {start: None}
    closed = set()
    start_h = h(start)
    # The heap is a plain list kept in order by heapq. Entry: (priority, h, insertion order, state).
    # Tuples compare left to right: smaller h, then older entry break ties, so states are never compared.
    frontier = [(start_h, start_h, next(order), start)]
    expanded = 0
    max_frontier = 1
    while frontier:
        state = heapq.heappop(frontier)[3]
        # An old copy of a state already expanded through a cheaper path: skip it.
        if state in closed:
            continue
        # The goal came out of the heap first, so this route is the cheapest.
        if is_goal(state):
            path = rebuild_path(parents, state)
            return SearchResult(path, best_g[state], expanded, max_frontier, elapsed_ms(started))
        closed.add(state)
        expanded += 1
        for direction, next_state, step_cost in successors(state):
            if next_state in closed:
                continue
            # g = real steps from the start (danger cost included on Hard).
            g = best_g[state] + step_cost
            # Keep this path only if it is the cheapest way found so far to reach next_state.
            if g < best_g.get(next_state, math.inf):
                best_g[next_state] = g
                parents[next_state] = (state, direction)
                next_h = h(next_state)
                # The only line that differs: A* uses f = g + h, Greedy uses h alone.
                priority = g + next_h if use_path_cost else next_h
                heapq.heappush(frontier, (priority, next_h, next(order), next_state))
        max_frontier = max(max_frontier, len(frontier))
    return SearchResult([], None, expanded, max_frontier, elapsed_ms(started))


# Exit-mode h: Manhattan distance to the exit (remaining is always empty in exit mode).
# Never too high, because walls can only make the real walk longer.
def manhattan_heuristic(level: Level):
    def estimate(state: tuple) -> int:
        position, remaining = state
        return max([manhattan(position, level.goal), *(manhattan(position, pellet) for pellet in remaining)])

    return estimate


def heuristic_for(level: Level, pellet_mode: bool):
    return maze_heuristic(level) if pellet_mode else manhattan_heuristic(level)


def _ghost_reach(level: Level, ghost: tuple) -> set: #Computes the set of tiles that a ghost can reach within settings.DANGER_RADIUS steps, excluding tiles in the safe zone.
    reached = {ghost}
    frontier = {ghost}
    for _ in range(settings.DANGER_RADIUS):
        frontier = {
            tile
            for current in frontier
            for _, tile in level.adjacency.get(current, ())
            if tile not in reached and tile not in level.safe_zone
        }
        reached |= frontier # union is for combining sets, so we keep track of all the tiles that have been reached by the ghost, and we don't want to revisit them. We also don't want to revisit tiles in the safe zone, because those are not reachable by the ghost.
    return reached


def _reachable_tiles(level: Level, position: tuple, blocked: frozenset) -> frozenset:
    return frozenset(maze_distances(level, position, blocked)) if blocked else level.floor_tiles


# Hard only, rebuilt from scratch every tick from where the ghosts are now.
# Tiles within DANGER_RADIUS (2) steps of a ghost cost DANGER_PENALTY (+4) extra.
# It is set with "=", so two ghosts don't stack. The +4 goes into the step cost g, not into h.
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
    started = time.perf_counter()
    start = (position, frozenset(pellets) if pellet_mode else frozenset())
    reachable = _reachable_tiles(level, position, frozenset(blocked))
    # Exit or a pellet cut off by ghosts: no route, so stop early instead of searching everything.
    if any(target not in reachable for target in (level.goal, *start[1])):
        return SearchResult([], None, 0, 0, elapsed_ms(started))
    successors = make_successors(level, frozenset(blocked), danger or {})
    # The game always uses A*. Greedy and BFS are only chosen by the evaluation scripts.
    use_path_cost = algorithm == ASTAR
    return best_first(start, make_goal_test(level), successors, heuristic_for(level, pellet_mode), use_path_cost)


def plan_to_pellet(
    level: Level,
    position: tuple,
    pellets: frozenset,
    blocked: frozenset = frozenset(),
    danger: dict | None = None,
) -> SearchResult:
    remaining = frozenset(pellets)
    reachable = _reachable_tiles(level, position, frozenset(blocked))
    if not any(pellet in reachable for pellet in remaining):
        return SearchResult([], None, 0, 0, 0.0)
    successors = make_successors(level, frozenset(blocked), danger or {})

    def ate_pellet(state: tuple) -> bool:
        return len(state[1]) < len(remaining)

    # Hard fallback: the goal is "eat any one pellet", and h = Manhattan to the nearest one.
    def nearest_pellet(state: tuple) -> int:
        tile, left = state
        return 0 if len(left) < len(remaining) else min(manhattan(tile, pellet) for pellet in left)

    return best_first((position, remaining), ate_pellet, successors, nearest_pellet)
