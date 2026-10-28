import pygame

from src.core import settings
from src.ui.label import Label


class FlashMessage(Label):
    def __init__(self):
        super().__init__(
            "",
            settings.FLASH_POSITION,
            settings.FONT_SMALL,
            settings.WARNING_COLOR,
            "midtop",
        )
        self.visible = False
        self.time_left = 0.0

    def show(self, text: str, seconds: float = settings.FLASH_DURATION):
        self.set_text(text)
        self.time_left = seconds
        self.visible = True

    def update(self, dt: float):
        if not self.visible:
            return
        self.time_left -= dt
        if self.time_left <= 0:
            self.visible = False

    def draw(self, surface: pygame.Surface):
        if self.visible:
            super().draw(surface)
