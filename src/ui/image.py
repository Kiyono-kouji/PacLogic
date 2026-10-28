import pygame

from src.ui.component import Component


class Image(Component):
    def __init__(self, path: str, position: tuple[int, int], scale: float = 1.0):
        super().__init__()
        self.position = position
        raw = pygame.image.load(path).convert_alpha()
        if scale != 1.0:
            new_size = (int(raw.get_width() * scale), int(raw.get_height() * scale))
            self._surface = pygame.transform.smoothscale(raw, new_size)
        else:
            self._surface = raw

    def draw(self, surface: pygame.Surface):
        surface.blit(self._surface, self.position)
