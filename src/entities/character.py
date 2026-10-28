import pygame

from src.core import settings


class Character:
    def __init__(self, tile: tuple[int, int] = (0, 0), direction: str = "R"):
        self.tile: tuple[int, int] = tile
        self.direction: str = direction
        self.tile_size: int = settings.DEFAULT_TILE_SIZE
        self.position: tuple[int, int] = (
            tile[0] * self.tile_size,
            tile[1] * self.tile_size,
        )
        self.map_view = None

    def place(self, tile: tuple[int, int], direction: str = "", map_view=None):
        self.tile = tile
        if direction:
            self.direction = direction
        if map_view is not None:
            self.map_view = map_view
        if self.map_view is not None:
            self.tile_size = self.map_view.tile
            self.position = self.map_view.tile_topleft(tile)
        else:
            self.position = (tile[0] * self.tile_size, tile[1] * self.tile_size)

    def center(self) -> tuple[int, int]:
        return self.position[0] + self.tile_size // 2, self.position[1] + self.tile_size // 2

    def draw(self, surface: pygame.Surface):
        raise NotImplementedError
