import pygame

from src.core import settings
from src.core.session import Session
from src.scenes.base_scene import BaseScene
from src.scenes.menu_scene import MenuScene
from src.scenes.tutorial_slides import load_tutorial_slides
from src.ui.tutorial_button import TutorialButton
from src.ui.tutorial_panel import TutorialPanel


class Game:
    def __init__(self):
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(settings.TITLE)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.session: Session = Session()
        self.scene: BaseScene = MenuScene(self, self.session)
        self.tutorial: TutorialPanel = TutorialPanel(load_tutorial_slides)
        self.tutorial_button: TutorialButton = TutorialButton(self.tutorial.open)
        self.running: bool = True

    def change_scene(self, scene: BaseScene):
        self.scene = scene

    def quit(self):
        self.running = False

    # The tutorial panel gets each event first, then its button, then the current scene.
    def handle_event(self, event: pygame.event.Event):
        if self.tutorial.handle_event(event):
            return
        if self.scene.shows_tutorial_button and self.tutorial_button.handle_event(event):
            return
        self.scene.handle_event(event)

    def run(self):
        while self.running:
            # dt = seconds since the last frame: clock.tick gives milliseconds, / 1000 makes seconds.
            # Capped at MAX_DT so a freeze doesn't make the game jump ahead.
            raw_dt = self.clock.tick(settings.FPS) / 1000.0
            dt = min(raw_dt, settings.MAX_DT)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                else:
                    self.handle_event(event)
            # While the tutorial is open the scene isn't updated, so the game is paused.
            if not self.tutorial.visible:
                self.scene.update(dt)
            self.scene.draw(self.screen)
            if self.scene.shows_tutorial_button:
                self.tutorial_button.draw(self.screen)
            self.tutorial.draw(self.screen)
            pygame.display.flip()
        pygame.quit()
