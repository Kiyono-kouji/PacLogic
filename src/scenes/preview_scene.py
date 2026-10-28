import pygame

from src.core import settings
from src.scenes import menu_scene, plan_scene
from src.scenes.base_scene import BaseScene
from src.ui.board import Board
from src.ui.button import Button
from src.ui.label import Label
from src.ui.panel import Panel


class PreviewScene(BaseScene):
    def __init__(self, game, session):
        super().__init__(game, session)
        self.board = Board(session.level, pygame.Rect(settings.PREVIEW_MAP_RECT), session.ghost_count)
        self.route = session.route if session.config["preview"] else []
        panel = Panel(settings.PREVIEW_PANEL_RECT)
        self.ui = [
            Label("Preview", settings.PREVIEW_TITLE_POSITION, settings.FONT_LARGE),
            panel,
            *self.info_labels(panel.rect),
            Button(settings.PREVIEW_START_RECT, self.start_planning, "Start planning"),
            Button(settings.PREVIEW_BACK_RECT, self.back, "Back"),
        ]

    def info_lines(self) -> list:
        session = self.session
        return [
            ("Level", session.option_text("level")),
            ("Mode", session.option_text("mode")),
            ("Difficulty", session.difficulty),
            ("Optimal cost", str(session.optimal_cost)),
        ]

    def info_labels(self, panel_rect: pygame.Rect) -> list:
        x = panel_rect.x + settings.PREVIEW_INFO_PADDING
        labels = []
        for row, (name, value) in enumerate(self.info_lines()):
            y = panel_rect.y + settings.PREVIEW_INFO_PADDING + row * settings.PREVIEW_LINE_HEIGHT
            labels.append(Label(name, (x, y), settings.FONT_SMALL, settings.TEXT_DIM_COLOR))
            labels.append(Label(value, (x, y + settings.FONT_SMALL), settings.FONT_MEDIUM))
        return labels

    def start_planning(self):
        self.game.change_scene(plan_scene.PlanScene(self.game, self.session))

    def back(self):
        self.game.change_scene(menu_scene.MenuScene(self.game, self.session))

    def handle_event(self, event: pygame.event.Event):
        self.forward_event(event)

    def update(self, dt: float):
        self.update_ui(dt)

    def draw(self, surface: pygame.Surface):
        surface.fill(settings.BG_COLOR)
        self.board.draw(surface, route=self.route)
        self.draw_ui(surface)
