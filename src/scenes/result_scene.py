import pygame

from src.core import settings
from src.logic.sim import BLOCKED, CAUGHT, ESCAPED, score_breakdown, total_score
from src.scenes import menu_scene, preview_scene
from src.scenes.base_scene import BaseScene
from src.ui.button import Button
from src.ui.label import Label
from src.ui.panel import Panel

OUTCOME_TITLES = {
    CAUGHT: ("Caught! Ghosts win", settings.ACCENT_COLOR),
    ESCAPED: ("Escaped! Pac-Man wins", settings.WARNING_COLOR),
    BLOCKED: ("Blocked: out of ticks", settings.TEXT_COLOR),
}


class ResultScene(BaseScene):
    def __init__(self, game, session, sim):
        super().__init__(game, session)
        title, color = OUTCOME_TITLES[sim.status]
        breakdown = score_breakdown(sim, session.seconds_left)
        rows = [*breakdown.items(), ("Total", total_score(breakdown))]
        self.ui = [
            Panel(settings.RESULT_PANEL_RECT),
            Label(title, settings.RESULT_TITLE_POSITION, settings.FONT_LARGE, color, "center"),
            Label(
                f"Ticks: {sim.tick} / {sim.tick_cap}",
                settings.RESULT_TICKS_POSITION,
                settings.FONT_SMALL,
                settings.TEXT_DIM_COLOR,
                "center",
            ),
            *self.score_labels(rows),
            Button(settings.RESULT_AGAIN_RECT, self.play_again, "Play again"),
            Button(settings.RESULT_MENU_RECT, self.back_to_menu, "Menu"),
        ]

    def score_labels(self, rows: list) -> list:
        labels = []
        for row, (name, points) in enumerate(rows):
            y = settings.RESULT_ROW_TOP + row * settings.RESULT_ROW_HEIGHT
            color = settings.ACCENT_COLOR if row == len(rows) - 1 else settings.TEXT_COLOR
            labels.append(Label(name, (settings.RESULT_NAME_X, y), settings.FONT_MEDIUM, color))
            labels.append(Label(str(points), (settings.RESULT_VALUE_X, y), settings.FONT_MEDIUM, color, "topright"))
        return labels

    def play_again(self):
        self.session.prepare()
        self.game.change_scene(preview_scene.PreviewScene(self.game, self.session))

    def back_to_menu(self):
        self.game.change_scene(menu_scene.MenuScene(self.game, self.session))

    def handle_event(self, event: pygame.event.Event):
        self.forward_event(event)

    def update(self, dt: float):
        self.update_ui(dt)

    def draw(self, surface: pygame.Surface):
        surface.fill(settings.BG_COLOR)
        self.draw_ui(surface)
