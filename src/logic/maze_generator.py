import dataclasses
import itertools
import math
import random

from src.core import settings
from src.logic.grid import Level, LevelError, maze_distances, move, validate_level
from src.logic.search import plan

CELL_STEPS = ((0, -2), (2, 0), (0, 2), (-2, 0))


def generate_level(template: Level, rng: random.Random) -> Level:
    for _ in range(settings.RANDOM_MAX_ATTEMPTS):
        level = _attempt(template, rng)
        if level is not None:
            return level
    raise LevelError(f"{template.name}: no playable random maze in {settings.RANDOM_MAX_ATTEMPTS} attempts")


def route_tiles(start: tuple, directions: list) -> list:
    tiles = []
    for direction in directions:
        start = move(start, direction)
        tiles.append(start)
    return tiles


def intercept_moves(level: Level, ghost: tuple, route: list) -> list | None:
    reach = maze_distances(level, ghost, level.safe_zone)
    for tick, tile in enumerate(route, start=1):
        if tile in level.safe_zone or reach.get(tile, math.inf) > tick:
            continue
        moves = _straight_path(level, ghost, tile)
        if block_count(moves) <= settings.RANDOM_MAX_INTERCEPT_BLOCKS:
            return moves
    return None


def block_count(moves: list) -> int:
    runs = [len(list(group)) for _, group in itertools.groupby(moves)]
    return sum(1 if length == 1 else 2 * math.ceil(length / settings.REPEAT_MAX) for length in runs)


def _attempt(template: Level, rng: random.Random) -> Level | None:
    floor = _carve_floor(template.width, template.height, rng)
    _open_loops(floor, template.width, template.height, rng)
    level = _with_start_and_exit(template, floor, rng)
    level = _with_pellets(level, floor, len(template.pellets), rng)
    if level is None:
        return None
    routes = [plan(level, level.start, level.pellets, pellet_mode) for pellet_mode in (False, True)]
    if any(result.cost is None for result in routes) or routes[1].expanded > settings.RANDOM_MAX_PLAN_NODES:
        return None
    level = _with_ghosts(level, [route_tiles(level.start, result.path) for result in routes], len(template.ghosts), rng)
    if level is None:
        return None
    try:
        validate_level(level)
    except LevelError:
        return None
    return level


def _carve_floor(width: int, height: int, rng: random.Random) -> set:
    cells = {(x, y) for y in range(1, height - 1, 2) for x in range(1, width - 1, 2)}
    first = rng.choice(sorted(cells))
    floor = {first}
    active = [first]
    while active:
        index = rng.randrange(len(active))
        x, y = active[index]
        unvisited = [(x + dx, y + dy) for dx, dy in CELL_STEPS if (x + dx, y + dy) in cells and (x + dx, y + dy) not in floor]
        if not unvisited:
            active.pop(index)
            continue
        next_x, next_y = rng.choice(unvisited)
        floor |= {((x + next_x) // 2, (y + next_y) // 2), (next_x, next_y)}
        active.append((next_x, next_y))
    return floor


def _open_loops(floor: set, width: int, height: int, rng: random.Random):
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if (x, y) in floor or (x + y) % 2 == 0:
                continue
            across = (x - 1, y) in floor and (x + 1, y) in floor
            down = (x, y - 1) in floor and (x, y + 1) in floor
            if across != down and rng.random() < settings.RANDOM_LOOP_CHANCE:
                floor.add((x, y))


def _with_start_and_exit(template: Level, floor: set, rng: random.Random) -> Level:
    walls = frozenset((x, y) for y in range(template.height) for x in range(template.width) if (x, y) not in floor)
    corner = min(floor)
    blank = Level(
        name=f"random {template.name}",
        width=template.width,
        height=template.height,
        walls=walls,
        start=corner,
        goal=corner,
        ghosts=(),
        pellets=frozenset(),
    )
    tables = {tile: maze_distances(blank, tile) for tile in sorted(floor)}
    longest = max(max(table.values()) for table in tables.values())
    pairs = [
        (start, goal)
        for start, table in tables.items()
        for goal, steps in table.items()
        if steps >= settings.RANDOM_EXIT_MIN_FRACTION * longest
    ]
    start, goal = rng.choice(pairs)
    return dataclasses.replace(blank, start=start, goal=goal)


def _with_pellets(level: Level, floor: set, count: int, rng: random.Random) -> Level | None:
    open_tiles = sorted(floor - {level.start, level.goal} - level.safe_zone)
    if len(open_tiles) < count:
        return None
    return dataclasses.replace(level, pellets=frozenset(rng.sample(open_tiles, count)))


def _with_ghosts(level: Level, routes: list, count: int, rng: random.Random) -> Level | None:
    on_route = set().union(*routes)
    from_start = maze_distances(level, level.start)
    spawns = sorted(
        tile
        for tile, steps in from_start.items()
        if steps >= settings.RANDOM_GHOST_MIN_DISTANCE
        and tile not in level.safe_zone
        and tile not in level.pellets
        and tile not in on_route
    )
    if len(spawns) < count:
        return None
    rng.shuffle(spawns)
    leader = next((tile for tile in spawns if all(intercept_moves(level, tile, route) is not None for route in routes)), None)
    if leader is None:
        return None
    others = [tile for tile in spawns if tile != leader][: count - 1]
    return dataclasses.replace(level, ghosts=(leader, *others))


def _straight_path(level: Level, source: tuple, target: tuple) -> list:
    to_target = maze_distances(level, target, level.safe_zone)
    moves = []
    heading = None
    while source != target:
        steps = [(direction, tile) for direction, tile in level.adjacency[source] if to_target.get(tile) == to_target[source] - 1]
        heading, source = min(steps, key=lambda step: step[0] != heading)
        moves.append(heading)
    return moves
