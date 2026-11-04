import math

import pygame

from src.core import settings
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
        self.ghosts_visible = True
        self.pac_man_visible = True
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
        if self.ghosts_visible:
            for ghost in self.ghosts:
                ghost.draw(surface)
        if self.pac_man_visible:
            self.pac_man.draw(surface)

    def draw_ghost_markers(self, surface: pygame.Surface):
        tile = self.map_view.tile_size
        wave = math.sin(math.tau * pygame.time.get_ticks() / settings.GHOST_MARKER_BOB_MS)
        lift = settings.GHOST_MARKER_BOB * tile * (wave + 1) / 2
        half_width = settings.GHOST_MARKER_WIDTH * tile / 2
        for ghost in self.ghosts:
            center_x, center_y = self.map_view.tile_center(ghost.tile)
            tip_y = center_y - tile / 2 - settings.GHOST_MARKER_GAP * tile - lift
            base_y = tip_y - settings.GHOST_MARKER_HEIGHT * tile
            points = [(center_x - half_width, base_y), (center_x + half_width, base_y), (center_x, tip_y)]
            pygame.draw.polygon(surface, _marker_color(ghost), points)
            pygame.draw.polygon(surface, settings.GHOST_MARKER_OUTLINE_COLOR, points, 1)


def _marker_color(ghost: Ghost) -> tuple:
    color = settings.GHOST_COLORS[ghost.index % len(settings.GHOST_COLORS)]
    if ghost.selected:
        return color
    return tuple(round(channel * settings.GHOST_MARKER_DIM) for channel in color)
