from collections.abc import Callable

from src.core import settings
from src.logic.brain import PacManBrain
from src.logic.grid import Level, move
from src.logic.sim import BLOCKED, CAUGHT, ESCAPED, RUNNING, Sim
from src.ui.tutorial_board import Stamp, TutorialBoard, ghost_sprite, pac_man_sprite

OUTCOME_STAMPS = {
    CAUGHT: ("CAUGHT!", settings.TUTORIAL_STAMP_LIGHT),
    ESCAPED: ("ESCAPED!", settings.TUTORIAL_STAMP_DARK),
    BLOCKED: ("BLOCKED!", settings.TUTORIAL_STAMP_DARK),
}


class SimRunner:
    def __init__(self, loop: bool):
        self.loop = loop
        self.level: Level | None = None
        self.make_controllers: Callable[[], list] = list
        self.sim: Sim | None = None
        self.running = False
        self.clock = 0.0
        self.since_tick = settings.TUTORIAL_TICK_SECONDS
        self.finished_for = 0.0
        self.stamp = Stamp()

    def start(self, level: Level, make_controllers: Callable[[], list], running: bool):
        self.level = level
        self.make_controllers = make_controllers
        self.running = running
        self.restart()

    def restart(self):
        controllers = self.make_controllers()
        brain = PacManBrain(self.level, settings.TUTORIAL_DIFFICULTY, False)
        self.sim = Sim(self.level, brain, False, len(controllers), controllers)
        self.clock = 0.0
        self.since_tick = settings.TUTORIAL_TICK_SECONDS
        self.finished_for = 0.0
        self.stamp.clear()

    def finished(self) -> bool:
        return self.sim.status != RUNNING

    def step(self):
        if self.finished():
            return
        self.sim.step()
        self.since_tick = 0.0
        if self.finished():
            self.stamp.show(*OUTCOME_STAMPS[self.sim.status])

    def update(self, dt: float):
        self.stamp.update(dt)
        self.since_tick += dt
        if self.finished():
            self.finished_for += dt
            if self.loop and self.finished_for >= settings.TUTORIAL_RUNNER_PAUSE:
                self.restart()
            return
        if not self.running:
            return
        self.clock += dt
        while self.clock >= settings.TUTORIAL_TICK_SECONDS and not self.finished():
            self.clock -= settings.TUTORIAL_TICK_SECONDS
            self.step()

    def ghosts_only(self) -> bool:
        return self.since_tick < settings.TUTORIAL_TICK_SECONDS / 2

    def shown_pac_tile(self) -> tuple:
        return self.sim.previous_pac_tile if self.ghosts_only() else self.sim.pac_tile

    def route_tiles(self) -> list:
        tile = self.sim.pac_tile
        tiles = []
        for direction in self.sim.brain.route:
            tile = move(tile, direction)
            tiles.append(tile)
        return tiles

    def draw(self, surface, board: TutorialBoard, show_route: bool):
        if show_route and not self.finished():
            board.draw_route(surface, self.route_tiles())
        board.draw_sprite(surface, pac_man_sprite(self.sim.pac_direction), self.shown_pac_tile())
        for index, tile in enumerate(self.sim.ghost_tiles):
            board.draw_sprite(surface, ghost_sprite(index, self.sim.ghost_directions[index]), tile)
        self.stamp.draw(surface, board.stamp_center())
