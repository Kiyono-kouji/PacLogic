import math

import pygame

from src.core import settings
from src.core.resource_loader import animation_frame, load_character_sprite
from src.ui.component import Component
from src.ui.effects import ease_out_back
from src.ui.menu_shapes import progress, shift_points, slanted_box


class MenuBackdrop(Component):
    def __init__(self):
        super().__init__()
        self.elapsed = 0.0
        self.halftone = _halftone_layer()

    def update(self, dt: float):
        self.elapsed += dt

    def slide(self) -> float:
        linear = progress(self.elapsed, 0.0, settings.MENU_INTRO_SECONDS)
        return (1 - ease_out_back(linear, settings.MENU_OVERSHOOT)) * settings.MENU_SHAPE_SLIDE

    def draw(self, surface: pygame.Surface):
        surface.fill(settings.MENU_BLUE)
        self.draw_rays(surface)
        surface.blit(self.halftone, (0, 0))
        slide = self.slide()
        pygame.draw.polygon(surface, settings.MENU_BLACK, shift_points(settings.MENU_SLASH_POINTS, (-slide, 0)))
        pygame.draw.polygon(surface, settings.MENU_WHITE, shift_points(settings.MENU_STRIPE_POINTS, (-slide, 0)))
        pygame.draw.polygon(surface, settings.MENU_BLACK, shift_points(settings.MENU_CORNER_POINTS, (slide, -slide)))
        self.draw_chase(surface, slide)

    def draw_rays(self, surface: pygame.Surface):
        center = settings.MENU_RAY_CENTER
        count = settings.MENU_RAY_COUNT
        width = math.tau / count / 2
        turn = math.radians(self.elapsed * settings.MENU_RAY_SPEED)
        length = settings.MENU_RAY_LENGTH
        for ray in range(count):
            angle = turn + ray * math.tau / count
            points = [
                center,
                (center[0] + math.cos(angle) * length, center[1] + math.sin(angle) * length),
                (center[0] + math.cos(angle + width) * length, center[1] + math.sin(angle + width) * length),
            ]
            pygame.draw.polygon(surface, settings.MENU_RAY_COLOR, points)

    def draw_chase(self, surface: pygame.Surface, slide: float):
        top = settings.MENU_CHASE_TOP + slide
        band = pygame.Rect(-settings.MENU_CHASE_SKEW, top, settings.SCREEN_WIDTH + 2 * settings.MENU_CHASE_SKEW, settings.MENU_CHASE_HEIGHT)
        edge = band.inflate(0, 2 * settings.MENU_CHASE_EDGE)
        pygame.draw.polygon(surface, settings.MENU_WHITE, slanted_box(edge, settings.MENU_CHASE_SKEW))
        pygame.draw.polygon(surface, settings.MENU_BLACK, slanted_box(band, settings.MENU_CHASE_SKEW))
        lead = self.elapsed * settings.MENU_CHASE_SPEED % settings.MENU_CHASE_LOOP - settings.MENU_CHASE_SPRITE
        pac_frame = animation_frame(settings.PACMAN_FRAME_COUNT, settings.PACMAN_FRAME_MS) + 1
        ghost_frame = animation_frame(settings.GHOST_FRAME_COUNT, settings.GHOST_FRAME_MS) + 1
        middle = band.centery
        pac_man = load_character_sprite(f"pacman/eat-right/eat-right-{pac_frame}.png", settings.MENU_CHASE_SPRITE)
        surface.blit(pac_man, pac_man.get_rect(center=(lead, middle)))
        for index, folder in enumerate(settings.GHOST_SPRITES):
            x = lead - settings.MENU_CHASE_LEAD - index * settings.MENU_CHASE_GAP
            ghost = load_character_sprite(f"ghosts/{folder}/move-right/move-right-{ghost_frame}.png", settings.MENU_CHASE_SPRITE)
            surface.blit(ghost, ghost.get_rect(center=(x, middle)))


def _halftone_layer() -> pygame.Surface:
    layer = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
    spacing = settings.MENU_HALFTONE_SPACING
    reach = settings.MENU_HALFTONE_REACH
    for row, y in enumerate(range(0, settings.SCREEN_HEIGHT + spacing, spacing)):
        shift = spacing // 2 if row % 2 else 0
        for x in range(shift, settings.SCREEN_WIDTH + spacing, spacing):
            nearest = min(math.dist((x, y), corner) for corner in settings.MENU_HALFTONE_CORNERS)
            radius = round(settings.MENU_HALFTONE_MAX_RADIUS * (1 - nearest / reach))
            if radius > 0:
                pygame.draw.circle(layer, settings.MENU_HALFTONE_COLOR, (x, y), radius)
    return layer
