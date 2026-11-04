from collections.abc import Callable

import pygame

from src.core import settings
from src.ui.menu_shapes import progress, slanted_box


class MenuWipe:
    def __init__(self):
        self.elapsed = 0.0
        self.on_covered: Callable[[], None] | None = None

    def running(self) -> bool:
        return self.on_covered is not None

    def start(self, on_covered: Callable[[], None]):
        self.elapsed = 0.0
        self.on_covered = on_covered

    def total_seconds(self) -> float:
        return settings.MENU_WIPE_SECONDS + (settings.MENU_WIPE_STRIPES - 1) * settings.MENU_WIPE_STAGGER

    def update(self, dt: float):
        if not self.running():
            return
        self.elapsed += dt
        if self.elapsed >= self.total_seconds() + settings.MENU_WIPE_HOLD:
            on_covered, self.on_covered = self.on_covered, None
            on_covered()

    def draw(self, surface: pygame.Surface):
        if not self.running():
            return
        height = settings.SCREEN_HEIGHT / settings.MENU_WIPE_STRIPES
        skew = settings.MENU_WIPE_SKEW
        full = settings.SCREEN_WIDTH + 2 * skew
        for stripe in range(settings.MENU_WIPE_STRIPES):
            linear = progress(self.elapsed, stripe * settings.MENU_WIPE_STAGGER, settings.MENU_WIPE_SECONDS)
            if linear <= 0:
                continue
            reach = full * linear * linear * (3 - 2 * linear)
            top = round(stripe * height)
            rect = pygame.Rect(-skew, top, reach + settings.MENU_WIPE_EDGE, round(height) + 1)
            pygame.draw.polygon(surface, settings.MENU_BLUE, slanted_box(rect, -skew))
            pygame.draw.polygon(surface, settings.MENU_BLACK, slanted_box(rect.inflate(-2 * settings.MENU_WIPE_EDGE, 0).move(-settings.MENU_WIPE_EDGE, 0), -skew))
