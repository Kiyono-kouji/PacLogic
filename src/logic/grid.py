from dataclasses import dataclass
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


def load_level(path: Path) -> Level:
    path = Path(path)
    level = parse_level(path.read_text(), path.stem)
    return level