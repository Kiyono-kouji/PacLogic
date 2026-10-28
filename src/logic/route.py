from src.logic.grid import Level, move
from src.logic.search import heuristic_for


def route_costs(level: Level, position: tuple, pellets, pellet_mode: bool, directions) -> list:
    estimate = heuristic_for(level, pellet_mode)
    remaining = frozenset(pellets) if pellet_mode else frozenset()
    costs = []
    for g, direction in enumerate(directions, start=1):
        position = move(position, direction)
        remaining = remaining - {position}
        costs.append((position, g, estimate((position, remaining))))
    return costs
