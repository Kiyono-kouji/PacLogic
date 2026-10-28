import pygame

from src.core import settings
from src.core.resource_loader import animation_frame, load_sprite
from src.entities.character import Character


class Enemy(Character):
    def __init__(
        self, index: int = 0, tile: tuple[int, int] = (0, 0), direction: str = "D"
    ):
        super().__init__(tile, direction)
        self.index: int = index
        self.selected: bool = False
        self.folder: str = settings.GHOST_SPRITES[index % len(settings.GHOST_SPRITES)]

    def sprite_name(self) -> str:
        if self.selected:
            return f"ghosts/{self.folder}/selected/selected-down.png"
        name = settings.DIRECTION_NAMES[self.direction]
        frame = animation_frame(settings.GHOST_FRAME_COUNT, settings.GHOST_FRAME_MS) + 1
        return f"ghosts/{self.folder}/move-{name}/move-{name}-{frame}.png"

    def draw(self, surface: pygame.Surface):
        sprite = load_sprite(self.sprite_name(), self.tile_size)
        surface.blit(sprite, sprite.get_rect(center=self.center()))
