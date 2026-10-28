import pygame

from src.logic.grid import Level
from src.ui.component import Component
from src.ui.map_view import MapView


class Board(Component):
    def __init__(self, level: Level, area: pygame.Rect, ghost_count: int):
        super().__init__()
        self.level = level
        self.ghost_count = ghost_count
        self.map_view = MapView(level, area)
        self.selected_ghost = None
        self.show_start()

    def show_start(self):
        self.pac_tile = self.level.start
        self.ghost_tiles = list(self.level.ghosts[:self.ghost_count])

    def select_ghost(self, index: int | None):
        self.selected_ghost = index

    def ghost_at(self, mouse_position: tuple) -> int | None:
        tile = self.map_view.tile_at(mouse_position)
        return self.ghost_tiles.index(tile) if tile in self.ghost_tiles else None

    def draw(self, surface: pygame.Surface, pellets=None, route=()):
        route = list(route)
        self.map_view.draw(surface, pellets, [tile for tile, _, _ in route])
        self.map_view.draw_costs(surface, route)
