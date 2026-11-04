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
            self.hovered = self.rect.collidepoint(event.pos) #collidepoint checks if the mouse is over the button, event.pos is the position of the mouse, and self.rect is the rectangle of the button. If the mouse is over the button, self.hovered is set to True, otherwise it is set to False.
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos): #event.button == 1 checks if the left mouse button is pressed, and self.rect.collidepoint(event.pos) checks if the mouse is over the button. If both conditions are true, then the button is pressed.
            self.pressed = True
            self.hovered = True
            return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False
            # Click only counts if it was pressed AND released inside the button.
            # on_click is the function passed in (e.g. self.start), called here.
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
        pygame.draw.rect(surface, self.color(), self.rect.inflate(-2 * settings.BUTTON_STEP, 0))
        pygame.draw.rect(surface, self.color(), self.rect.inflate(0, -2 * settings.BUTTON_STEP))
        text_surface = load_font(settings.BUTTON_FONT_SIZE).render(self.text, True, settings.BUTTON_TEXT_COLOR)
        surface.blit(text_surface, text_surface.get_rect(center=self.rect.center))
