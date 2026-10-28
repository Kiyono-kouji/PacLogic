from collections.abc import Callable

import pygame

from src.core import settings
from src.core.resource_loader import load_font
from src.ui.component import Component


class Button(Component):
    def __init__(self, rect: pygame.Rect, on_click: Callable[[], None], text: str):
        super().__init__()
        self.rect = pygame.Rect(rect)
        self.on_click = on_click
        self.text = text
        self.hovered = False
        self.pressed = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.pressed = True
            self.hovered = True
            return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False
            if was_pressed and self.rect.collidepoint(event.pos):
                self.on_click()
                return True
        return False

    def color(self) -> tuple[int, int, int]:
        if self.pressed and self.hovered:
            return settings.BUTTON_PRESSED_COLOR
        if self.hovered:
            return settings.BUTTON_HOVER_COLOR
        return settings.BUTTON_COLOR

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return
        pygame.draw.rect(surface, self.color(), self.rect, border_radius=settings.BUTTON_RADIUS)
        text_surface = load_font(settings.BUTTON_FONT_SIZE).render(self.text, True, settings.BUTTON_TEXT_COLOR)
        surface.blit(text_surface, text_surface.get_rect(center=self.rect.center))
