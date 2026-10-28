import pygame

from src.ui.component import Component


class BaseScene:
    def __init__(self, game, session):
        self.game = game
        self.session = session
        self.ui: list[Component] = []

    def handle_event(self, event: pygame.event.Event):
        raise NotImplementedError

    def update(self, dt: float):
        raise NotImplementedError

    def draw(self, surface: pygame.Surface):
        raise NotImplementedError

    def forward_event(self, event: pygame.event.Event):
        for component in self.ui:
            component.handle_event(event)

    def update_ui(self, dt: float):
        for component in self.ui:
            component.update(dt)

    def draw_ui(self, surface: pygame.Surface):
        for component in self.ui:
            if component.visible:
                component.draw(surface)
