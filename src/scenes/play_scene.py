import pygame

from src.core import settings
from src.logic import blocks
from src.logic.route import route_costs
from src.logic.sim import CAUGHT, RUNNING
from src.scenes import menu_scene, result_scene
from src.scenes.base_scene import BaseScene
from src.ui.board import Board
from src.ui.button import Button
from src.ui.effects import Flash, Particles, Shake
from src.ui.hud import HUD
from src.ui.label import Label
from src.ui.panel import Panel


class PlayScene(BaseScene):
    def __init__(self, game, session):
        super().__init__(game, session)
        controllers = [blocks.run(program) for program in session.parsed_programs]
        self.sim = session.new_sim(controllers)
        self.board = Board(session.level, pygame.Rect(settings.PLAY_MAP_RECT), session.ghost_count)
        self.paused = False
        self.tick_timer = 0.0
        self.hud = HUD(settings.PLAY_STATUS_POSITION, session.pellet_mode, session.seconds_left)
        self.route = []
        self.pause_button = Button(settings.PLAY_PAUSE_RECT, self.toggle_pause, "Pause")
        self.ui = [
            Label("Play", settings.PLAY_TITLE_POSITION, settings.FONT_LARGE),
            Panel(settings.PLAY_PANEL_RECT),
            self.hud,
            self.pause_button,
            Button(settings.PLAY_MENU_RECT, self.back_to_menu, "Menu"),
        ]
        self.canvas = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.particles = Particles()
        self.shake = Shake()
        self.catch_flash = Flash(settings.CATCH_FLASH_COLOR, settings.CATCH_FLASH_ALPHA, settings.CATCH_FLASH_SECONDS, False)
        self.end_flash = Flash(settings.END_FLASH_COLOR, 255, settings.END_FLASH_OUT_SECONDS, True)
        self.show_status()

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.text = "Resume" if self.paused else "Pause"
        self.hud.refresh(self.sim, self.paused)

    def back_to_menu(self):
        self.game.change_scene(menu_scene.MenuScene(self.game, self.session))

    def show_status(self):
        self.hud.refresh(self.sim)
        self.route = self.route_preview()
        self.pause_button.visible = self.sim.status == RUNNING

    def route_preview(self) -> list:
        sim = self.sim
        if not self.session.config["show_route"] or sim.status != RUNNING:
            return []
        costs = route_costs(sim.level, sim.pac_tile, sim.pellets, sim.pellet_mode, sim.brain.route)
        steps_taken = 0 if sim.brain.config["replan"] else sim.tick
        return [(tile, g + steps_taken, h) for tile, g, h in costs]

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.sim.status == RUNNING:
            self.toggle_pause()
            return
        self.forward_event(event)

    def celebrate_catch(self):
        self.particles.burst(self.board.map_view.tile_center(self.sim.pac_tile))
        self.shake.start()
        self.catch_flash.start()

    def update_effects(self, dt: float):
        self.particles.update(dt)
        self.shake.update(dt)
        self.catch_flash.update(dt)
        self.end_flash.update(dt)

    def update(self, dt: float):
        self.update_ui(dt)
        self.update_effects(dt)
        if self.paused:
            return
        # Add up real seconds; a tick runs every PLAY_TICK_SECONDS (1/6 s), whatever the FPS.
        self.tick_timer += dt
        if self.sim.status != RUNNING:
            if self.tick_timer >= settings.PLAY_END_DELAY and not self.end_flash.started:
                self.end_flash.start()
            if self.end_flash.done:
                self.game.change_scene(result_scene.ResultScene(self.game, self.session, self.sim))
            return
        if self.tick_timer < settings.PLAY_TICK_SECONDS:
            return
        # Subtract instead of resetting to 0, so leftover time carries over and it stays 6 per second.
        self.tick_timer -= settings.PLAY_TICK_SECONDS
        self.sim.step()
        self.board.show_sim(self.sim)
        self.show_status()
        if self.sim.status != RUNNING:
            self.tick_timer = 0.0
            if self.sim.status == CAUGHT:
                self.celebrate_catch()

    def draw(self, surface: pygame.Surface):
        self.canvas.fill(settings.BG_COLOR)
        self.board.draw(self.canvas, self.sim.pellets, self.route)
        self.particles.draw(self.canvas)
        self.draw_ui(self.canvas)
        surface.fill(settings.BG_COLOR)
        surface.blit(self.canvas, self.shake.offset())
        self.catch_flash.draw(surface)
        self.end_flash.draw(surface)
