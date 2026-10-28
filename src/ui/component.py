import pygame


class Component:
    def __init__(self):
        self.visible: bool = True

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface):
        raise NotImplementedError
