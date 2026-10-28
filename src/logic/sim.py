from typing import Iterator

from src.core import settings
from src.logic.grid import DIRECTIONS, Level, move

RUNNING = "running"
CAUGHT = "caught"
ESCAPED = "escaped"
BLOCKED = "blocked"


def idle(sim=None, index: int = 0) -> Iterator[None]:
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
        self.ghost_count = ghost_count
        self.pac: tuple[int, int] = level.start
        self.pac_dir: str = "R"
        self.ghosts: list[tuple[int, int]] = list(level.ghosts[:ghost_count])
        self.facing: list[str] = ["D"] * len(self.ghosts)
        self.previous_pac: tuple[int, int] = self.pac
        self.previous_ghosts: list[tuple[int, int]] = list(self.ghosts)
        self.pellets: set[tuple[int, int]] = set(level.pellets)
        self.tick: int = 0
        self.status: str = RUNNING
        self.tick_cap: int = int(
            settings.TICK_CAP_FACTOR * brain.optimal_cost + settings.TICK_CAP_BONUS
        )
        self.controllers: list[Iterator] = []
        if controllers:
            for i in range(len(self.ghosts)):
                if i < len(controllers) and controllers[i] is not None:
                    self.controllers.append(controllers[i])
                else:
                    self.controllers.append(idle(self, i))
        else:
            for i in range(len(self.ghosts)):
                self.controllers.append(idle(self, i))

    def ghost_can_enter(self, tile: tuple[int, int]) -> bool:
        return self.level.passable(tile) and tile not in self.level.safe_zone

    def is_caught(self) -> bool:
        for i, ghost in enumerate(self.ghosts):
            if ghost == self.pac:
                return True
            if ghost == self.previous_pac and self.pac == self.previous_ghosts[i]:
                return True
        return False

    def step(self):
        if self.status != RUNNING:
            return
        self.previous_pac = self.pac
        self.previous_ghosts = list(self.ghosts)
        for i, controller in enumerate(self.controllers):
            action = next(controller, None)
            if action in DIRECTIONS:
                self.facing[i] = action
                next_tile = move(self.ghosts[i], action)
                if self.ghost_can_enter(next_tile):
                    self.ghosts[i] = next_tile
        pac_move = self.brain.next_move(
            self.pac, frozenset(self.pellets), tuple(self.ghosts)
        )
        if pac_move in DIRECTIONS:
            self.pac_dir = pac_move
            next_pac = move(self.pac, pac_move)
            if self.level.passable(next_pac):
                self.pac = next_pac
        elif isinstance(pac_move, tuple) and self.level.passable(pac_move):
            self.pac = pac_move
        self.tick += 1
        if self.is_caught():
            self.status = CAUGHT
            return
        if self.pac in self.pellets:
            self.pellets.discard(self.pac)
        if self.pac == self.level.goal and (
            not self.pellet_mode or len(self.pellets) == 0
        ):
            self.status = ESCAPED
            return
        if self.tick >= self.tick_cap:
            self.status = BLOCKED
            return
