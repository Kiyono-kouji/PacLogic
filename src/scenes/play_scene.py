import pygame

from src.core import settings
from src.logic import blocks
from src.logic.sim import BLOCKED, CAUGHT, ESCAPED, RUNNING
from src.scenes import menu_scene
from src.scenes.base_scene import BaseScene
from src.ui.board import Board
from src.ui.button import Button
from src.ui.label import Label
from src.ui.panel import Panel

STATUS_TEXT = {
    RUNNING: ("Running", settings.TEXT_COLOR),
    CAUGHT: ("Caught! Ghosts win", settings.ACCENT_COLOR),
    ESCAPED: ("Escaped! Pac-Man wins", settings.WARNING_COLOR),
    BLOCKED: ("Blocked: out of ticks", settings.TEXT_DIM_COLOR),
}


class PlayScene(BaseScene):
    def __init__(self, game, session):
        super().__init__(game, session)
        controllers = [blocks.run(tree, None, index) for index, tree in enumerate(session.trees)]
        self.sim = session.new_sim(controllers)
        self.board = Board(session.level, pygame.Rect(settings.PLAY_MAP_RECT), session.ghost_count)
        self.paused = False
        self.tick_timer = 0.0
        self.status_label = Label("", settings.PLAY_STATUS_POSITION, settings.FONT_MEDIUM)
        self.pause_button = Button(settings.PLAY_PAUSE_RECT, self.toggle_pause, "Pause")
        self.ui = [
            Label("Play", settings.PLAY_TITLE_POSITION, settings.FONT_LARGE),
            Panel(settings.PLAY_PANEL_RECT),
            self.status_label,
            self.pause_button,
            Button(settings.PLAY_MENU_RECT, self.back_to_menu, "Menu"),
        ]
        self.show_status()

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.text = "Resume" if self.paused else "Pause"

    def back_to_menu(self):
        self.game.change_scene(menu_scene.MenuScene(self.game, self.session))

    def show_status(self):
        text, color = STATUS_TEXT[self.sim.status]
        self.status_label.set_text(text, color)
        self.pause_button.visible = self.sim.status == RUNNING

    def handle_event(self, event: pygame.event.Event):
        self.forward_event(event)

    def update(self, dt: float):
        self.update_ui(dt)
        if self.paused or self.sim.status != RUNNING:
            return
        self.tick_timer += dt
        if self.tick_timer < settings.PLAY_TICK_SECONDS:
            return
        self.tick_timer -= settings.PLAY_TICK_SECONDS
        self.sim.step()
        self.board.show_sim(self.sim)
        self.show_status()

    def draw(self, surface: pygame.Surface):
        surface.fill(settings.BG_COLOR)
        self.board.draw(surface, self.sim.pellets)
        self.draw_ui(surface)
