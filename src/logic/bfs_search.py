import time
from collections import deque
from functools import lru_cache

from src.logic.grid import Level, maze_distances
from src.logic.search_core import SearchResult, elapsed_ms, make_goal_test, make_successors, rebuild_path


# A BFS distance table: dict of floor tile -> real steps from source (around walls).
# lru_cache: built once per (level, source), then the same dict is reused. Never change it.
@lru_cache(maxsize=None)
def distance_table(level: Level, source: tuple) -> dict:
    return maze_distances(level, source)


# Pellet-mode h (every difficulty). Every pellet must be eaten before the exit, so the
# trip is at least here -> p -> exit for every pellet p. The biggest of those is still
# never too high (A* stays optimal) and is the closest to the truth (A* expands fewer states).
def maze_heuristic(level: Level):
    # One table from the exit and one per pellet; no new BFS after the first time.
    to_goal = distance_table(level, level.goal)
    pellet_tables = {pellet: distance_table(level, pellet) for pellet in level.pellets}
    # h per state, so a state reached twice in one search isn't computed twice.
    memo = {}

    def estimate(state: tuple) -> int:
        if state not in memo:
            position, remaining = state
            # For each pellet not eaten yet: steps to it + steps from it to the exit.
            via_pellets = (pellet_tables[pellet][position] + to_goal[pellet] for pellet in remaining)
            # Keep the biggest, including going straight to the exit.
            memo[state] = max([to_goal[position], *via_pellets])
        return memo[state]

    return estimate


# BFS as a search: a queue (oldest first), no h, every step counted as 1.
# Only the evaluation scripts use it, as a baseline. parents also acts as the "seen" set.
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
