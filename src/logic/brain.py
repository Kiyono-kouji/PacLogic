import math

from src.core import settings
from src.logic.bfs_search import distance_table
from src.logic.grid import Level, bfs_dist, move
from src.logic.search import ASTAR, danger_map, plan, plan_to_pellet
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

    def record(self, result: SearchResult) -> SearchResult:
        self.plans_made += 1
        self.nodes_expanded += result.expanded
        self.last_ms = result.ms
        self.slowest_ms = max(self.slowest_ms, result.ms)
        return result

    def make_plan(
        self,
        position: tuple,
        pellets: frozenset,
        blocked: frozenset = frozenset(),
        danger: dict | None = None,
    ) -> SearchResult:
        return self.record(plan(self.level, position, pellets, self.pellet_mode, blocked, danger, self.algorithm))

    def next_move(self, position: tuple, pellets: frozenset, ghosts: tuple) -> str | None:
        if self.config["replan"]:
            danger = danger_map(self.level, ghosts)
            if not self.replan(position, pellets, ghosts, danger) and not self.detour_to_pellet(position, pellets, ghosts, danger):
                return self.hold_move(position, ghosts)
        return self.route.pop(0) if self.route else None

    def replan(self, position: tuple, pellets: frozenset, ghosts: tuple, danger: dict) -> bool:
        result = self.make_plan(position, pellets, frozenset(ghosts), danger)
        self.route = list(result.path)
        return result.cost is not None

    def detour_to_pellet(self, position: tuple, pellets: frozenset, ghosts: tuple, danger: dict) -> bool:
        if not self.pellet_mode or not pellets:
            return False
        result = self.record(plan_to_pellet(self.level, position, pellets, frozenset(ghosts), danger))
        self.route = list(result.path)
        return result.cost is not None

    def hold_move(self, position: tuple, ghosts: tuple) -> str | None:
        ghost_distances = [bfs_dist(self.level, ghost, self.level.safe_zone) for ghost in ghosts]
        to_goal = distance_table(self.level, self.level.goal)

        def preference(direction: str | None) -> tuple:
            tile = position if direction is None else move(position, direction)
            nearest_ghost = min((distances.get(tile, math.inf) for distances in ghost_distances), default=math.inf)
            if nearest_ghost > settings.DANGER_RADIUS:
                return True, -to_goal[tile]
            return False, nearest_ghost

        options = [None, *(direction for direction, tile in self.level.adjacency[position] if tile not in ghosts)]
        return max(options, key=preference)
