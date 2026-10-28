import pygame

from src.core import settings
from src.core.resource_loader import animation_frame, load_sprite
from src.entities.character import Character


class Player(Character):
    def __init__(self, tile: tuple[int, int] = (0, 0), direction: str = "R"):
        super().__init__(tile, direction)

    def sprite_name(self) -> str:
        name = settings.DIRECTION_NAMES[self.direction]
        frame = animation_frame(settings.PACMAN_FRAME_COUNT, settings.PACMAN_FRAME_MS) + 1
        return f"pacman/eat-{name}/eat-{name}-{frame}.png"

    def draw(self, surface: pygame.Surface):
        sprite = load_sprite(self.sprite_name(), self.tile_size)
        surface.blit(sprite, sprite.get_rect(center=self.center()))
