import math

import pygame

from src.core import settings
from src.logic import blocks
from src.scenes import play_scene
from src.scenes.base_scene import BaseScene
from src.ui.board import Board
from src.ui.button import Button
from src.ui.flash_message import FlashMessage
from src.ui.label import Label
from src.ui.program_editor import ProgramEditor


class PlanScene(BaseScene):
    def __init__(self, game, session):
        super().__init__(game, session)
        level, ghost_count = session.level, session.ghost_count
        self.overview = Board(level, pygame.Rect(settings.PLAN_OVERVIEW_RECT), ghost_count)
        self.side_board = Board(level, pygame.Rect(settings.PLAN_SIDE_MAP_RECT), ghost_count)
        self.route = session.route if session.config["preview"] else []
        self.flash = FlashMessage()
        self.editor = ProgramEditor(session.config["block_limit"], self.flash)
        self.title = Label("Plan your ghosts", settings.PLAN_TITLE_POSITION, settings.FONT_LARGE)
        self.timer = Label("", settings.PLAN_TIMER_POSITION, settings.FONT_LARGE, anchor="topright")
        self.hint = Label("", settings.PLAN_HINT_POSITION, settings.FONT_SMALL, settings.TEXT_DIM_COLOR)
        self.lock_button = Button(settings.PLAN_LOCK_RECT, self.lock_and_run, "Lock & Run")
        self.selected: int | None = None
        self.ui = [self.title, self.timer, self.hint, self.editor, self.lock_button, self.flash]
        self.select(None)

    def active_board(self) -> Board:
        return self.overview if self.selected is None else self.side_board

    def select(self, index: int | None):
        self.editor.finish()
        self.selected = index
        self.editor.visible = index is not None
        self.side_board.select_ghost(index)
        if index is None:
            self.hint.set_text("Click a ghost to write its program")
            return
        self.editor.program = self.session.programs[index]
        self.editor.scroll_by(0)
        self.hint.set_text(f"Ghost {index + 1}: drag blocks in, right-click to delete, Esc to close")

    def lock_and_run(self):
        self.editor.finish()
        self.session.trees = [blocks.parse(program) for program in self.session.programs]
        self.game.change_scene(play_scene.PlayScene(self.game, self.session))

    def handle_event(self, event: pygame.event.Event):
        if self.editor.handle_event(event):
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.select(None)
            return
        if self.lock_button.handle_event(event):
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            index = self.active_board().ghost_at(event.pos)
            if index is not None:
                self.select(index)

    def update(self, dt: float):
        self.session.seconds_left = max(0.0, self.session.seconds_left - dt)
        self.update_ui(dt)
        seconds = math.ceil(self.session.seconds_left)
        warning = seconds < settings.TIMER_WARNING_SECONDS
        self.timer.set_text(f"{seconds // 60}:{seconds % 60:02d}", settings.WARNING_COLOR if warning else settings.TEXT_COLOR)
        if self.session.seconds_left <= 0:
            self.lock_and_run()

    def draw(self, surface: pygame.Surface):
        surface.fill(settings.BG_COLOR)
        self.active_board().draw(surface, route=self.route)
        self.draw_ui(surface)
