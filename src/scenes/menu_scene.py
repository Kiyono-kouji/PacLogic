import pygame

from src.core import settings
from src.core.session import OPTIONS
from src.scenes import preview_scene
from src.scenes.base_scene import BaseScene
from src.ui.effects import Shake
from src.ui.menu_backdrop import MenuBackdrop
from src.ui.menu_title import MenuTitle
from src.ui.menu_wipe import MenuWipe
from src.ui.setup_card import SetupCard
from src.ui.slash_menu import SlashMenu

OPTION_NAMES = {
    "level": "Level",
    "random": "Random maze",
    "difficulty": "AI",
    "ghosts": "Ghosts",
    "mode": "Mode",
    "time": "Planning time",
}


class MenuScene(BaseScene):
    shows_tutorial_button = False

    def __init__(self, game, session):
        super().__init__(game, session)
        self.backdrop = MenuBackdrop()
        self.title = MenuTitle(settings.TITLE)
        self.menu = SlashMenu(list(settings.MENU_ITEMS), self.choose)
        self.setup = SetupCard(OPTIONS, OPTION_NAMES, self.session.option_text, self.session.cycle, self.close_setup, self.start)
        self.setup.visible = False
        self.menu_ui = [self.backdrop, self.title, self.menu]
        self.ui = self.menu_ui
        self.shake = Shake()
        self.wipe = MenuWipe()
        self.canvas = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.dim_layer = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.dim_layer.fill(settings.MENU_DIM_COLOR)

    def choose(self, name: str):
        if name == "tutorial":
            self.game.tutorial.open()
            return
        self.shake.start(settings.MENU_SHAKE_SECONDS, settings.MENU_SHAKE_PIXELS)
        if name == "play":
            self.open_setup()
        else:
            self.wipe.start(self.game.quit)

    def setup_open(self) -> bool:
        return self.setup.visible

    def open_setup(self):
        self.setup.open()
        self.ui = [*self.menu_ui[:2], self.setup]

    def close_setup(self):
        self.ui = self.menu_ui

    def start(self):
        self.shake.start(settings.MENU_SHAKE_SECONDS, settings.MENU_SHAKE_PIXELS)
        self.wipe.start(self.enter_preview)

    def enter_preview(self):
        self.session.prepare(new_maze=True)
        self.game.change_scene(preview_scene.PreviewScene(self.game, self.session))

    def handle_event(self, event: pygame.event.Event):
        if self.wipe.running():
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.setup_open():
            self.setup.close()
            return
        self.forward_event(event)

    def update(self, dt: float):
        self.backdrop.update(dt)
        self.title.update(dt)
        self.menu.update(dt)
        self.setup.update(dt)
        self.shake.update(dt)
        self.wipe.update(dt)

    def draw(self, surface: pygame.Surface):
        self.backdrop.draw(self.canvas)
        self.title.draw(self.canvas)
        self.menu.draw(self.canvas)
        if self.setup_open():
            self.dim_layer.set_alpha(round(255 * min(1.0, max(0.0, self.setup.amount()))))
            self.canvas.blit(self.dim_layer, (0, 0))
            self.setup.draw(self.canvas)
        surface.fill(settings.MENU_BLACK)
        surface.blit(self.canvas, self.shake.offset())
        self.wipe.draw(surface)
