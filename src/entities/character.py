import pygame

from src.core.resource_loader import load_sprite


class Character:
    def __init__(self, map_view, direction: str):
        self.map_view = map_view
        self.direction: str = direction
        self.tile: tuple[int, int] = (0, 0)

    def place(self, tile: tuple[int, int], direction: str):
        self.tile = tile
        self.direction = direction

    def sprite_name(self) -> str:
        raise NotImplementedError

    def draw(self, surface: pygame.Surface):
        sprite = load_sprite(self.sprite_name(), self.map_view.tile_size)
        surface.blit(sprite, sprite.get_rect(center=self.map_view.tile_center(self.tile)))
