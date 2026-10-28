import random
from collections import deque
from dataclasses import dataclass, replace
from functools import cached_property
from pathlib import Path

from src.core import settings

DIRECTIONS = {"U": (0, -1), "R": (1, 0), "D": (0, 1), "L": (-1, 0)}
MOVE_ORDER = tuple(settings.MOVE_ORDER)
LEGEND = set("#.PEGo")


class LevelError(ValueError):
    pass


def move(position: tuple, direction: str) -> tuple:
    dx, dy = DIRECTIONS[direction]
    return position[0] + dx, position[1] + dy


def manhattan(a: tuple, b: tuple) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


@dataclass(frozen=True)
class Level:
    name: str
    width: int
    height: int
    walls: frozenset
    start: tuple
    goal: tuple
    ghosts: tuple
    pellets: frozenset

    def in_bounds(self, tile: tuple) -> bool:
        return 0 <= tile[0] < self.width and 0 <= tile[1] < self.height

    def passable(self, tile: tuple) -> bool:
        return self.in_bounds(tile) and tile not in self.walls

    def neighbors(self, tile: tuple):
        for direction in MOVE_ORDER:
            next_tile = move(tile, direction)
            if self.passable(next_tile):
                yield direction, next_tile

    @cached_property
    def floor_tiles(self) -> frozenset:
        return frozenset((x, y) for y in range(self.height) for x in range(self.width) if (x, y) not in self.walls)

    @cached_property
    def adjacency(self) -> dict:
        return {tile: tuple(self.neighbors(tile)) for tile in self.floor_tiles}

    @cached_property
    def safe_zone(self) -> frozenset:
        return frozenset(tile for tile, distance in bfs_dist(self, self.goal).items() if distance <= settings.SAFE_RADIUS)


def bfs_dist(level: Level, source: tuple, blocked: frozenset = frozenset()) -> dict:
    distances = {source: 0}
    frontier = deque([source])
    while frontier:
        tile = frontier.popleft()
        for _, next_tile in level.adjacency.get(tile, ()):
            if next_tile not in distances and next_tile not in blocked:
                distances[next_tile] = distances[tile] + 1
                frontier.append(next_tile)
    return distances


def parse_level(text: str, name: str) -> Level:
    rows = [line.rstrip() for line in text.splitlines()]
    while rows and not rows[-1]:
        rows.pop()
    if not rows:
        raise LevelError(f"{name}: the level is empty")
    width = max(len(row) for row in rows)
    tiles = {}
    for y, row in enumerate(rows):
        for x, char in enumerate(row.ljust(width, "#")):
            if char not in LEGEND:
                raise LevelError(f"{name}: unknown character {char!r} at ({x}, {y})")
            tiles.setdefault(char, []).append((x, y))
    for char in "PE":
        if len(tiles.get(char, [])) != 1:
            raise LevelError(f"{name}: needs exactly one {char!r}")
    return Level(
        name=name,
        width=width,
        height=len(rows),
        walls=frozenset(tiles.get("#", [])),
        start=tiles["P"][0],
        goal=tiles["E"][0],
        ghosts=tuple(tiles.get("G", [])),
        pellets=frozenset(tiles.get("o", [])),
    )


def validate_level(level: Level):
    if not 1 <= len(level.ghosts) <= settings.MAX_GHOSTS:
        raise LevelError(f"{level.name}: needs 1 to {settings.MAX_GHOSTS} ghosts, has {len(level.ghosts)}")
    if len(level.pellets) > settings.MAX_PELLETS:
        raise LevelError(f"{level.name}: has {len(level.pellets)} pellets, the limit is {settings.MAX_PELLETS}")
    unreachable = level.floor_tiles - bfs_dist(level, level.start).keys()
    if unreachable:
        raise LevelError(f"{level.name}: {len(unreachable)} floor tiles can't be reached from P, e.g. {min(unreachable)}")
    for ghost in level.ghosts:
        if ghost in level.safe_zone:
            raise LevelError(f"{level.name}: ghost at {ghost} starts inside the safe zone")


def load_level(path: Path) -> Level:
    path = Path(path)
    level = parse_level(path.read_text(), path.stem)
    validate_level(level)
    return level


def _carve_maze(width: int, height: int, rng: random.Random) -> set:
    cells = {(x, y) for x in range(1, width - 1, 2) for y in range(1, height - 1, 2)}
    floor = {(1, 1)}
    stack = [(1, 1)]
    while stack:
        x, y = stack[-1]
        options = [
            (dx, dy) for dx, dy in DIRECTIONS.values()
            if (x + 2 * dx, y + 2 * dy) in cells and (x + 2 * dx, y + 2 * dy) not in floor
        ]
        if not options:
            stack.pop()
            continue
        dx, dy = rng.choice(options)
        floor |= {(x + dx, y + dy), (x + 2 * dx, y + 2 * dy)}
        stack.append((x + 2 * dx, y + 2 * dy))
    for x, y in sorted(cells):
        open_sides = [(dx, dy) for dx, dy in DIRECTIONS.values() if (x + dx, y + dy) in floor]
        if len(open_sides) != 1 or rng.random() >= settings.BRAID_CHANCE:
            continue
        closed_sides = [
            (dx, dy) for dx, dy in DIRECTIONS.values()
            if (x + dx, y + dy) not in floor and (x + 2 * dx, y + 2 * dy) in cells
        ]
        if closed_sides:
            dx, dy = rng.choice(closed_sides)
            floor.add((x + dx, y + dy))
    return floor


def _farthest(distances: dict) -> tuple:
    return max(distances, key=distances.get)


def _route_tiles(level: Level, stops: tuple) -> set:
    tiles = set()
    for a, b in zip(stops, stops[1:]):
        dist_a = bfs_dist(level, a)
        dist_b = bfs_dist(level, b)
        tiles |= {tile for tile in dist_a if dist_a[tile] + dist_b.get(tile, dist_a[b] + 1) == dist_a[b]}
    return tiles


def _pick_ghosts(level: Level, count: int, rng: random.Random) -> tuple:
    dist_start = bfs_dist(level, level.start)
    excluded = _route_tiles(level, (level.start, level.goal)) | level.safe_zone | level.pellets
    candidates = [
        tile for tile in sorted(level.floor_tiles)
        if tile not in excluded and dist_start[tile] >= settings.GHOST_MIN_START_DISTANCE
    ]
    rng.shuffle(candidates)
    for spacing in settings.GHOST_SPACINGS:
        chosen = []
        for tile in candidates:
            if all(manhattan(tile, other) >= spacing for other in chosen):
                chosen.append(tile)
            if len(chosen) == count:
                return tuple(chosen)
    raise LevelError(f"{level.name}: not enough tiles for {count} ghost spawns")


def generate_level(width: int, height: int, seed: int, pellet_count: int, ghost_count: int = settings.MAX_GHOSTS) -> Level:
    rng = random.Random(seed)
    floor = _carve_maze(width, height, rng)
    walls = frozenset((x, y) for y in range(height) for x in range(width) if (x, y) not in floor)
    corner = (1, 1)
    level = Level(f"random {width}x{height} #{seed}", width, height, walls, corner, corner, (), frozenset())
    goal = _farthest(bfs_dist(level, corner))
    start = _farthest(bfs_dist(level, goal))
    level = replace(level, start=start, goal=goal)
    pellet_spots = sorted(level.floor_tiles - level.safe_zone - {start})
    level = replace(level, pellets=frozenset(rng.sample(pellet_spots, pellet_count)))
    level = replace(level, ghosts=_pick_ghosts(level, ghost_count, rng))
    validate_level(level)
    return level
