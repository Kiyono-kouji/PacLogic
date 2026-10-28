import pygame

from src.core import settings
from src.ui.component import Component


class Panel(Component):
    def __init__(self, rect: pygame.Rect):
        super().__init__()
        self.rect = pygame.Rect(rect)

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return
        pygame.draw.rect(surface, settings.PANEL_COLOR, self.rect)
        pygame.draw.rect(surface, settings.PANEL_BORDER_COLOR, self.rect, settings.PANEL_BORDER_WIDTH)
