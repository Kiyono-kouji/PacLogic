import pygame

from src.core import settings
from src.core.session import OPTIONS
from src.scenes import preview_scene
from src.scenes.base_scene import BaseScene
from src.ui.button import Button
from src.ui.label import Label
from src.ui.panel import Panel

OPTION_NAMES = {
    "level": "Level",
    "ai": "AI",
    "ghosts": "Ghosts",
    "mode": "Mode",
    "time": "Planning time",
}


class MenuScene(BaseScene):
    def __init__(self, game, session):
        super().__init__(game, session)
        self.menu_ui = [
            Label(settings.TITLE, settings.MENU_TITLE_POSITION, settings.FONT_LARGE, settings.ACCENT_COLOR, "center"),
            Label(
                "An A* Pac-Man versus block programmed ghosts",
                settings.MENU_SUBTITLE_POSITION,
                settings.FONT_SMALL,
                settings.TEXT_DIM_COLOR,
                "center",
            ),
            Button(settings.MENU_PLAY_RECT, self.open_setup, "Play"),
            Button(settings.MENU_QUIT_RECT, self.game.quit, "Quit"),
        ]
        self.value_labels = {}
        self.setup_ui = [
            Panel(settings.SETUP_PANEL_RECT),
            Label("Round setup", settings.SETUP_TITLE_POSITION, settings.FONT_MEDIUM, settings.TEXT_COLOR, "center"),
            *self.option_rows(),
            Button(settings.SETUP_BACK_RECT, self.close_setup, "Back"),
            Button(settings.SETUP_START_RECT, self.start, "Start"),
        ]
        self.dim_layer = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.dim_layer.fill(settings.MENU_DIM_COLOR)
        self.ui = self.menu_ui

    def option_rows(self) -> list:
        size = settings.SETUP_ARROW_SIZE
        value_x = (settings.SETUP_LEFT_ARROW_X + size + settings.SETUP_RIGHT_ARROW_X) // 2
        components = []
        for row, option in enumerate(OPTIONS):
            top = settings.SETUP_ROW_TOP + row * settings.SETUP_ROW_HEIGHT
            middle = top + size // 2
            value = Label(self.session.option_text(option), (value_x, middle), settings.FONT_MEDIUM, settings.TEXT_COLOR, "center")
            self.value_labels[option] = value
            components += [
                Label(OPTION_NAMES[option], (settings.SETUP_NAME_X, middle), settings.FONT_MEDIUM, settings.TEXT_DIM_COLOR, "midleft"),
                Button((settings.SETUP_LEFT_ARROW_X, top, size, size), self.cycler(option, -1), "<"),
                value,
                Button((settings.SETUP_RIGHT_ARROW_X, top, size, size), self.cycler(option, 1), ">"),
            ]
        return components

    def cycler(self, option: str, delta: int):
        def cycle():
            self.session.cycle(option, delta)
            self.refresh_values()

        return cycle

    def refresh_values(self):
        for option, label in self.value_labels.items():
            label.set_text(self.session.option_text(option))

    def setup_open(self) -> bool:
        return self.ui is self.setup_ui

    def open_setup(self):
        self.refresh_values()
        self.ui = self.setup_ui

    def close_setup(self):
        self.ui = self.menu_ui

    def start(self):
        self.session.prepare()
        self.game.change_scene(preview_scene.PreviewScene(self.game, self.session))

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.setup_open():
            self.close_setup()
            return
        self.forward_event(event)

    def update(self, dt: float):
        self.update_ui(dt)

    def draw(self, surface: pygame.Surface):
        surface.fill(settings.BG_COLOR)
        if self.setup_open():
            for component in self.menu_ui:
                component.draw(surface)
            surface.blit(self.dim_layer, (0, 0))
        self.draw_ui(surface)
