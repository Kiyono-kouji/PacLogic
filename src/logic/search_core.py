import time
from dataclasses import dataclass

from src.logic.grid import Level


@dataclass
class SearchResult:
    path: list
    cost: int | None
    expanded: int
    max_frontier: int
    ms: float


def elapsed_ms(started: float) -> float:
    return (time.perf_counter() - started) * 1000


# Walks the parents links from the goal back to the start, then reverses them.
# This turns the found goal into the list of moves Pac-Man walks. It is not backtracking.
def rebuild_path(parents: dict, state: tuple) -> list:
    path = []
    while parents[state] is not None:
        state, direction = parents[state]
        path.append(direction)
    path.reverse()
    return path


# The rulebook for one step. Built once per search (fixes level, blocked, danger);
# the search calls successors(state) for every state it expands.
def make_successors(level: Level, blocked: frozenset, danger: dict):
    def successors(state: tuple):
        position, remaining = state
        # adjacency never contains walls, so every route goes around them.
        for direction, tile in level.adjacency.get(position, ()):
            # A ghost on the tile (Hard): treat it like a wall.
            if tile in blocked:
                continue
            # Stepping on a pellet gives a new state without that pellet.
            next_remaining = remaining - {tile} if tile in remaining else remaining
            # Each move: (direction, new state, cost). Cost is 1, or 1 + 4 near a ghost on Hard.
            yield direction, (tile, next_remaining), 1 + danger.get(tile, 0)

    return successors


def make_goal_test(level: Level):
    def is_goal(state: tuple) -> bool:
        position, remaining = state
        return position == level.goal and not remaining

    return is_goal
