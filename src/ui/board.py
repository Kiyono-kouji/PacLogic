import pygame

from src.entities.ghost import Ghost
from src.entities.pac_man import PacMan
from src.logic.grid import Level
from src.ui.component import Component
from src.ui.map_view import MapView


class Board(Component):
    def __init__(self, level: Level, area: pygame.Rect, ghost_count: int):
        super().__init__()
        self.level = level
        self.map_view = MapView(level, area)
        self.pac_man = PacMan(self.map_view)
        self.ghosts = [Ghost(self.map_view, index) for index in range(ghost_count)]
        self.show_start()

    def show_start(self):
        self.pac_man.place(self.level.start, self.pac_man.direction)
        for ghost, tile in zip(self.ghosts, self.level.ghosts):
            ghost.place(tile, ghost.direction)

    def show_sim(self, sim):
        self.pac_man.place(sim.pac_tile, sim.pac_direction)
        for ghost, tile, direction in zip(self.ghosts, sim.ghost_tiles, sim.ghost_directions):
            ghost.place(tile, direction)

    def select_ghost(self, index: int | None):
        for ghost in self.ghosts:
            ghost.selected = ghost.index == index

    def ghost_at(self, mouse_position: tuple) -> int | None:
        tile = self.map_view.tile_at(mouse_position)
        return next((ghost.index for ghost in self.ghosts if ghost.tile == tile), None)

    def draw(self, surface: pygame.Surface, pellets=None, route=()):
        route = list(route)
        self.map_view.draw(surface, pellets, [tile for tile, _, _ in route])
        self.map_view.draw_costs(surface, route)
        for ghost in self.ghosts:
            ghost.draw(surface)
        self.pac_man.draw(surface)
