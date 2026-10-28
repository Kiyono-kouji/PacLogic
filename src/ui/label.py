import pygame

from src.core import settings
from src.core.resource_loader import load_font
from src.ui.component import Component


class Label(Component):
    def __init__(
        self,
        text: str,
        position: tuple[int, int],
        size: int = settings.FONT_MEDIUM,
        color: tuple = settings.TEXT_COLOR,
        anchor: str = "topleft",
    ):
        super().__init__()
        self.position = position
        self.anchor = anchor
        self.font = load_font(size)
        self.text: str | None = None
        self.color: tuple | None = None
        self.set_text(text, color)

    def set_text(self, text: str, color: tuple | None = None):
        text = str(text)
        color = self.color if color is None else color
        if text == self.text and color == self.color:
            return
        self.text = text
        self.color = color
        self.surface = self.font.render(text, True, color)
        self.rect = self.surface.get_rect(**{self.anchor: self.position})

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surface, self.rect)
