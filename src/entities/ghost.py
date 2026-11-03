from src.core import settings
from src.core.resource_loader import animation_frame
from src.entities.character import Character


class Ghost(Character):
    def __init__(self, map_view, index: int):
        super().__init__(map_view, "D")
        self.index: int = index
        self.selected: bool = False
        self.folder: str = settings.GHOST_SPRITES[index % len(settings.GHOST_SPRITES)]

    def sprite_name(self) -> str:
        if self.selected:
            return f"ghosts/{self.folder}/selected/selected-down.png"
        name = settings.DIRECTION_NAMES[self.direction]
        frame = animation_frame(settings.GHOST_FRAME_COUNT, settings.GHOST_FRAME_MS) + 1
        return f"ghosts/{self.folder}/move-{name}/move-{name}-{frame}.png"
