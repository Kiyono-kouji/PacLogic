import pygame

from src.entities.enemy import Enemy
from src.entities.player import Player
from src.logic.grid import Level
from src.ui.component import Component
from src.ui.map_view import MapView


class Board(Component):
    def __init__(self, level: Level, area: pygame.Rect, ghost_count: int):
        super().__init__()
        self.level = level
        self.ghost_count = ghost_count
        self.map_view = MapView(level, area)
        self.player = Player()
        self.enemies = [Enemy(index) for index in range(ghost_count)]
        self.selected_ghost = None
        self.show_start()

    def place(self, character, tile: tuple, direction: str):
        character.place(tile, direction, self.map_view)

    def show_start(self):
        self.pac_tile = self.level.start
        self.ghost_tiles = list(self.level.ghosts[:self.ghost_count])
        self.place(self.player, self.pac_tile, self.player.direction)
        for enemy, tile in zip(self.enemies, self.ghost_tiles):
            self.place(enemy, tile, enemy.direction)

    def show_sim(self, sim):
        self.pac_tile = sim.pac
        self.ghost_tiles = list(sim.ghosts)
        self.place(self.player, sim.pac, sim.pac_dir)
        for enemy, tile, direction in zip(self.enemies, sim.ghosts, sim.facing):
            self.place(enemy, tile, direction)

    def select_ghost(self, index: int | None):
        self.selected_ghost = index
        for enemy in self.enemies:
            enemy.selected = enemy.index == index

    def ghost_at(self, mouse_position: tuple) -> int | None:
        tile = self.map_view.tile_at(mouse_position)
        return self.ghost_tiles.index(tile) if tile in self.ghost_tiles else None

    def draw(self, surface: pygame.Surface, pellets=None, route=()):
        route = list(route)
        self.map_view.draw(surface, pellets, [tile for tile, _, _ in route])
        self.map_view.draw_costs(surface, route)
        for enemy in self.enemies:
            enemy.draw(surface)
        self.player.draw(surface)
