from typing import Iterator

from src.core import settings
from src.logic.grid import DIRECTIONS, Level, move

RUNNING = "running"
CAUGHT = "caught"
ESCAPED = "escaped"
BLOCKED = "blocked"


def idle() -> Iterator[None]:
    while True:
        yield None


class Sim:
    def __init__(
        self,
        level: Level,
        brain,
        pellet_mode: bool,
        ghost_count: int,
        controllers: tuple | list | None = None,
    ):
        self.level = level
        self.brain = brain
        self.pellet_mode = pellet_mode
        self.pac_tile: tuple[int, int] = level.start
        self.pac_direction: str = "R"
        self.previous_pac_tile: tuple[int, int] = self.pac_tile
        self.ghost_tiles: list[tuple[int, int]] = list(level.ghosts[:ghost_count])
        self.ghost_directions: list[str] = ["D"] * len(self.ghost_tiles)
        self.pellets: set[tuple[int, int]] = set(level.pellets) if pellet_mode else set()
        self.tick: int = 0
        self.status: str = RUNNING
        self.tick_cap: int = int(
            settings.TICK_CAP_FACTOR * brain.optimal_cost + settings.TICK_CAP_BONUS
        )
        self.controllers: list[Iterator] = [
            controllers[i]
            if controllers and i < len(controllers) and controllers[i] is not None
            else idle()
            for i in range(len(self.ghost_tiles))
        ]

    def ghost_can_enter(self, tile: tuple[int, int]) -> bool:
        return self.level.passable(tile) and tile not in self.level.safe_zone

    def is_caught(self) -> bool:
        return any(ghost in (self.pac_tile, self.previous_pac_tile) for ghost in self.ghost_tiles)

    def step(self):
        if self.status != RUNNING:
            return
        self.previous_pac_tile = self.pac_tile
        for i, controller in enumerate(self.controllers):
            action = next(controller, None)
            if action in DIRECTIONS:
                self.ghost_directions[i] = action
                next_tile = move(self.ghost_tiles[i], action)
                if self.ghost_can_enter(next_tile):
                    self.ghost_tiles[i] = next_tile
        pac_move = self.brain.next_move(
            self.pac_tile, frozenset(self.pellets), tuple(self.ghost_tiles)
        )
        if pac_move in DIRECTIONS:
            self.pac_direction = pac_move
            next_pac_tile = move(self.pac_tile, pac_move)
            if self.level.passable(next_pac_tile):
                self.pac_tile = next_pac_tile
        self.tick += 1
        if self.is_caught():
            self.status = CAUGHT
            return
        if self.pac_tile in self.pellets:
            self.pellets.discard(self.pac_tile)
        if self.pac_tile == self.level.goal and (
            not self.pellet_mode or len(self.pellets) == 0
        ):
            self.status = ESCAPED
            return
        if self.tick >= self.tick_cap:
            self.status = BLOCKED
            return

    def run(self, max_ticks: int | None = None) -> str:
        while self.status == RUNNING:
            if max_ticks is not None and self.tick >= max_ticks:
                break
            self.step()
        return self.status


def score_breakdown(sim: Sim, seconds_left: float) -> dict[str, int]:
    if sim.status == CAUGHT:
        time_points = max(0, int(seconds_left)) * settings.SCORE["time_factor"]
        ticks_left = max(0, sim.tick_cap - sim.tick)
        ticks_points = ticks_left * settings.SCORE["ticks_factor"]
        return {
            "Outcome": settings.SCORE["caught"],
            "Time bonus": time_points,
            "Ticks bonus": ticks_points,
        }
    if sim.status == BLOCKED:
        return {
            "Outcome": settings.SCORE["blocked"],
        }
    return {
        "Outcome": settings.SCORE["escaped"],
    }


def total_score(breakdown: dict[str, int]) -> int:
    return sum(breakdown.values())
