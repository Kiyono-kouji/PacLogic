import pygame

from src.core import settings
from src.core.resource_loader import load_character_sprite
from src.logic import blocks
from src.logic.route import route_costs
from src.logic.sim import BLOCKED, CAUGHT, ESCAPED, RUNNING
from src.scenes import menu_scene, result_scene
from src.scenes.base_scene import BaseScene
from src.ui.board import Board
from src.ui.button import Button
from src.ui.effects import Banner, CatchCamera, EscapeCelebration, Flash, GhostEatsPacMan, GhostFlyAway, Particles, Shake
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
        self.frame = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.effect_speed = 1.0
        self.end_delay = settings.PLAY_END_DELAY
        self.particles = Particles()
        self.shake = Shake()
        self.fly_away = GhostFlyAway()
        self.camera = CatchCamera()
        self.eaten = GhostEatsPacMan()
        self.celebration = EscapeCelebration()
        self.banner = Banner()
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
        pac_center = self.board.map_view.tile_center(self.sim.pac_tile)
        self.particles.burst(pac_center, settings.CATCH_PARTICLE_COUNT, settings.CATCH_PARTICLE_COLORS)
        self.shake.start(settings.CATCH_SHAKE_SECONDS, settings.CATCH_SHAKE_PIXELS)
        self.camera.start(pac_center)
        tile_size = self.board.map_view.tile_size
        catcher = self.sim.ghost_tiles.index(self.sim.pac_tile)
        pac_sprite = load_character_sprite(self.board.pac_man.sprite_name(), tile_size)
        ghost_sprite = load_character_sprite(self.board.ghosts[catcher].sprite_name(), tile_size)
        self.eaten.start(pac_sprite, ghost_sprite, pac_center)
        self.board.pac_man_visible = False
        self.board.hidden_ghost = catcher
        self.effect_speed = settings.CATCH_SLOW_MOTION
        self.end_delay = settings.CATCH_END_DELAY

    def send_ghosts_away(self):
        tile_size = self.board.map_view.tile_size
        self.fly_away.start(
            [
                (
                    load_character_sprite(f"ghosts/{ghost.folder}/move-up/move-up-1.png", tile_size),
                    self.board.map_view.tile_center(ghost.tile),
                )
                for ghost in self.board.ghosts
            ]
        )
        self.board.ghosts_visible = False
        pac_center = self.board.map_view.tile_center(self.sim.pac_tile)
        self.particles.burst(pac_center, settings.ESCAPE_PARTICLE_COUNT, settings.ESCAPE_PARTICLE_COLORS)
        self.shake.start(settings.ESCAPE_SHAKE_SECONDS, settings.ESCAPE_SHAKE_PIXELS)
        pac_sprite = load_character_sprite(self.board.pac_man.sprite_name(), tile_size)
        self.celebration.start(pac_sprite, pac_center, tile_size)
        self.board.pac_man_visible = False
        self.end_delay = settings.ESCAPE_END_DELAY

    def update_effects(self, dt: float):
        self.particles.update(dt * self.effect_speed)
        self.fly_away.update(dt)
        self.shake.update(dt * self.effect_speed)
        self.camera.update(dt)
        if self.eaten.update(dt):
            self.particles.burst(self.eaten.center, settings.EAT_CRUMB_COUNT, settings.CATCH_PARTICLE_COLORS)
        self.celebration.update(dt)
        self.banner.update(dt)
        self.end_flash.update(dt)

    def update(self, dt: float):
        self.update_ui(dt)
        self.update_effects(dt)
        if self.paused:
            return
        # Add up real seconds; a tick runs every PLAY_TICK_SECONDS (1/6 s), whatever the FPS.
        self.tick_timer += dt
        if self.sim.status != RUNNING:
            if self.tick_timer >= self.end_delay and not self.end_flash.started:
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
            if self.sim.status == ESCAPED:
                self.send_ghosts_away()
            if self.sim.status == BLOCKED:
                self.end_delay = settings.BLOCKED_END_DELAY
            title, subtitle, color, delay = settings.OUTCOME_BANNERS[self.sim.status]
            self.banner.start(title, subtitle, color, delay, self.end_delay)

    def draw(self, surface: pygame.Surface):
        self.canvas.fill(settings.BG_COLOR)
        self.board.draw(self.canvas, self.sim.pellets, self.route)
        self.fly_away.draw(self.canvas, self.board.map_view.tile_size)
        self.eaten.draw(self.canvas)
        area = self.board.map_view.rect
        self.celebration.draw(self.canvas)
        view = self.camera.view(area)
        zoomed = view != area
        self.frame.blit(self.canvas, (0, 0))
        if zoomed:
            self.frame.blit(self.camera.zoomed(self.canvas, area, settings.MAP_FLOOR_COLOR), area.topleft)
        self.draw_ui(self.frame)
        self.camera.desaturate(self.frame)
        offset = self.shake.offset()
        surface.fill(settings.BG_COLOR)
        surface.blit(self.frame, offset)
        if zoomed:
            surface.set_clip(area.move(offset))
        self.particles.draw(surface, view, area, offset)
        surface.set_clip(None)
        pac_y = area.centery if self.camera.focus is not None else self.board.map_view.tile_center(self.sim.pac_tile)[1]
        self.banner.draw(surface, area, pac_y)
        self.end_flash.draw(surface)
