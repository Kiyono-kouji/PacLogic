import pygame

from src.core import settings
from src.logic.sim import score_breakdown, total_score
from src.scenes import menu_scene, preview_scene
from src.scenes.base_scene import BaseScene
from src.ui.button import Button
from src.ui.effects import Flash
from src.ui.hud import OUTCOME_TEXT
from src.ui.label import Label
from src.ui.panel import Panel

class ResultScene(BaseScene):
    def __init__(self, game, session, sim):
        super().__init__(game, session)
        title, color = OUTCOME_TEXT[sim.status]
        breakdown = score_breakdown(sim, session.seconds_left)
        rows = [*breakdown.items(), ("Total", total_score(breakdown))]
        self.counters: list = []
        self.count_seconds = 0.0
        self.ui = [
            Panel(settings.RESULT_PANEL_RECT),
            Label(title, settings.RESULT_TITLE_POSITION, settings.FONT_LARGE, color, "center"),
            Label(
                f"{sim.level.name.capitalize()} level, {session.difficulty} AI   Ticks: {sim.tick} / {sim.tick_cap}",
                settings.RESULT_TICKS_POSITION,
                settings.FONT_SMALL,
                settings.TEXT_DIM_COLOR,
                "center",
            ),
            *self.score_labels(rows),
            Button(settings.RESULT_AGAIN_RECT, self.play_again, "Play again"),
            Button(settings.RESULT_MENU_RECT, self.back_to_menu, "Menu"),
        ]
        self.flash = Flash(settings.END_FLASH_COLOR, 255, settings.END_FLASH_IN_SECONDS, False)
        self.flash.start()

    def update(self, dt: float):
        self.update_ui(dt)
        self.flash.update(dt)
        self.count_seconds += dt
        for index, (label, points) in enumerate(self.counters):
            started = self.count_seconds - settings.RESULT_COUNT_DELAY - index * settings.RESULT_COUNT_STAGGER
            linear = min(1.0, max(0.0, started / settings.RESULT_COUNT_SECONDS))
            label.set_text(str(round(points * (1 - (1 - linear) ** 3))))

    def score_labels(self, rows: list) -> list:
        labels = []
        for row, (name, points) in enumerate(rows):
            y = settings.RESULT_ROW_TOP + row * settings.RESULT_ROW_HEIGHT
            color = settings.ACCENT_COLOR if row == len(rows) - 1 else settings.TEXT_COLOR
            labels.append(Label(name, (settings.RESULT_NAME_X, y), settings.FONT_MEDIUM, color))
            value = Label("0", (settings.RESULT_VALUE_X, y), settings.FONT_MEDIUM, color, "topright")
            self.counters.append((value, points))
            labels.append(value)
        return labels

    def play_again(self):
        self.session.prepare(new_maze=True)
        self.game.change_scene(preview_scene.PreviewScene(self.game, self.session))

    def back_to_menu(self):
        self.game.change_scene(menu_scene.MenuScene(self.game, self.session))

    def draw(self, surface: pygame.Surface):
        surface.fill(settings.BG_COLOR)
        self.draw_ui(surface)
        self.flash.draw(surface)
