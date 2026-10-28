from src.core import settings
from src.logic.grid import Level
from src.logic.search import ASTAR, plan
from src.logic.search_core import SearchResult


class PacManBrain:
    def __init__(self, level: Level, difficulty: str, pellet_mode: bool, algorithm: str = ASTAR):
        self.level = level
        self.difficulty = difficulty
        self.config = settings.DIFFICULTIES[difficulty]
        self.pellet_mode = pellet_mode
        self.algorithm = algorithm
        self.plans_made = 0
        self.nodes_expanded = 0
        self.last_ms = 0.0
        self.slowest_ms = 0.0
        first = self.make_plan(level.start, level.pellets)
        self.optimal_cost = first.cost
        self.planned_route = list(first.path)
        self.route = list(first.path)

    def make_plan(
        self,
        position: tuple,
        pellets: frozenset,
        blocked: frozenset = frozenset(),
        danger: dict | None = None,
    ) -> SearchResult:
        result = plan(self.level, position, pellets, self.pellet_mode, blocked, danger, self.algorithm)
        self.plans_made += 1
        self.nodes_expanded += result.expanded
        self.last_ms = result.ms
        self.slowest_ms = max(self.slowest_ms, result.ms)
        return result

    def next_move(self, position: tuple, pellets: frozenset, ghosts: tuple) -> str | None:
        return self.route.pop(0) if self.route else None
