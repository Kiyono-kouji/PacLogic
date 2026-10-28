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


def rebuild_path(parents: dict, state: tuple) -> list:
    path = []
    while parents[state] is not None:
        state, direction = parents[state]
        path.append(direction)
    path.reverse()
    return path


def make_successors(level: Level, blocked: frozenset, danger: dict):
    def successors(state: tuple):
        position, remaining = state
        for direction, tile in level.adjacency.get(position, ()):
            if tile in blocked:
                continue
            next_remaining = remaining - {tile} if tile in remaining else remaining
            yield direction, (tile, next_remaining), 1 + danger.get(tile, 0)

    return successors


def make_goal_test(level: Level):
    def is_goal(state: tuple) -> bool:
        position, remaining = state
        return position == level.goal and not remaining

    return is_goal
