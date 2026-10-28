import pygame

from src.core import settings
from src.scenes.base_scene import BaseScene


class _PlaceholderScene(BaseScene):
    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface):
        surface.fill(settings.BG_COLOR)


class Game:
    def __init__(self):
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(settings.TITLE)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.session = None
        self._scene: BaseScene = _PlaceholderScene(self, None)
        self._running: bool = True

    def change_scene(self, scene: BaseScene):
        self._scene = scene

    def quit(self):
        self._running = False

    def run(self):
        while self._running:
            raw_dt = self.clock.tick(settings.FPS) / 1000.0
            dt = min(raw_dt, settings.MAX_DT)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                else:
                    self._scene.handle_event(event)
            self._scene.update(dt)
            self._scene.draw(self.screen)
            pygame.display.flip()
        pygame.quit()
