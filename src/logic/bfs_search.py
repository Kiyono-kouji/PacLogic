from functools import lru_cache

from src.logic.grid import Level, bfs_dist


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
