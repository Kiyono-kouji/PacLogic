from src.core import settings
from src.core.resource_loader import animation_frame
from src.entities.character import Character


class PacMan(Character):
    def __init__(self, map_view):
        super().__init__(map_view, "R")

    def sprite_name(self) -> str:
        name = settings.DIRECTION_NAMES[self.direction]
        frame = animation_frame(settings.PACMAN_FRAME_COUNT, settings.PACMAN_FRAME_MS) + 1
        return f"pacman/eat-{name}/eat-{name}-{frame}.png"
