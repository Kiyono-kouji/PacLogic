from src.logic.grid import Level
from src.logic.search_core import SearchResult

ASTAR = "A*"
GREEDY = "Greedy"
BFS = "BFS"
ALGORITHMS = (ASTAR, GREEDY, BFS)


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
    raise NotImplementedError(f"{algorithm} is not built yet")
