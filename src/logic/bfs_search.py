import time
from collections import deque
from functools import lru_cache

from src.logic.grid import Level, bfs_dist
from src.logic.search_core import SearchResult, elapsed_ms, make_goal_test, make_successors, rebuild_path


@lru_cache(maxsize=None)
def distance_table(level: Level, source: tuple) -> dict:
    return bfs_dist(level, source)


def maze_heuristic(level: Level):
    to_goal = distance_table(level, level.goal)
    pellet_tables = {pellet: distance_table(level, pellet) for pellet in level.pellets}
    memo = {}

    def estimate(state: tuple) -> int:
        if state not in memo:
            position, remaining = state
            via_pellets = (pellet_tables[pellet][position] + to_goal[pellet] for pellet in remaining)
            memo[state] = max([to_goal[position], *via_pellets])
        return memo[state]

    return estimate


def breadth_first(start: tuple, is_goal, successors) -> SearchResult:
    started = time.perf_counter()
    parents = {start: None}
    frontier = deque([start])
    expanded = 0
    max_frontier = 1
    while frontier:
        state = frontier.popleft()
        if is_goal(state):
            path = rebuild_path(parents, state)
            return SearchResult(path, len(path), expanded, max_frontier, elapsed_ms(started))
        expanded += 1
        for direction, next_state, _ in successors(state):
            if next_state not in parents:
                parents[next_state] = (state, direction)
                frontier.append(next_state)
        max_frontier = max(max_frontier, len(frontier))
    return SearchResult([], None, expanded, max_frontier, elapsed_ms(started))


def plan_bfs(level: Level, position: tuple, pellets: frozenset, pellet_mode: bool) -> SearchResult:
    start = (position, frozenset(pellets) if pellet_mode else frozenset())
    return breadth_first(start, make_goal_test(level), make_successors(level, frozenset(), {}))
