import math
import random

import pygame

from src.core import settings
from src.core.resource_loader import load_font
from src.ui.component import Component
from src.ui.effects import ease_out_back
from src.ui.menu_shapes import progress, shift_points, tag_surface


class MenuTitle(Component):
    def __init__(self, text: str):
        super().__init__()
        self.elapsed = 0.0
        self.letters = _letter_tiles(text.upper())
        self.places = _letter_places(self.letters)
        self.subtitle = pygame.transform.rotate(
            tag_surface(
                settings.MENU_SUBTITLE_TEXT,
                settings.MENU_SUBTITLE_SIZE,
                (settings.MENU_BLACK, settings.MENU_WHITE, settings.MENU_WHITE),
                settings.MENU_SUBTITLE_PADDING,
                settings.MENU_SUBTITLE_SKEW,
                settings.MENU_SUBTITLE_SHADOW,
            ),
            settings.MENU_SUBTITLE_TILT,
        )

    def update(self, dt: float):
        self.elapsed += dt

    def draw(self, surface: pygame.Surface):
        for index, (tile, place) in enumerate(zip(self.letters, self.places)):
            linear = progress(self.elapsed, index * settings.MENU_TITLE_STAGGER, settings.MENU_TITLE_DROP_SECONDS)
            if linear <= 0:
                continue
            eased = ease_out_back(linear, settings.MENU_OVERSHOOT)
            bob = math.sin(self.elapsed * settings.MENU_TITLE_BOB_SPEED + index * settings.MENU_TITLE_BOB_PHASE)
            center = (
                place[0],
                place[1] - (1 - eased) * settings.MENU_TITLE_DROP_PIXELS + bob * settings.MENU_TITLE_BOB_PIXELS,
            )
            image = tile if linear >= 1 else pygame.transform.rotozoom(tile, 0, max(0.01, eased))
            surface.blit(image, image.get_rect(center=center))
        linear = progress(self.elapsed, settings.MENU_SUBTITLE_DELAY, settings.MENU_INTRO_SECONDS)
        if linear > 0:
            slide = (1 - ease_out_back(linear, settings.MENU_OVERSHOOT)) * settings.MENU_SHAPE_SLIDE
            center = (settings.MENU_SUBTITLE_CENTER[0] - slide, settings.MENU_SUBTITLE_CENTER[1])
            surface.blit(self.subtitle, self.subtitle.get_rect(center=center))


def _letter_tiles(text: str) -> list:
    rng = random.Random(settings.MENU_TITLE_SEED)
    tiles = []
    for index, letter in enumerate(text):
        size = settings.MENU_TITLE_SIZES[index % len(settings.MENU_TITLE_SIZES)]
        style = settings.MENU_LETTER_STYLES[settings.MENU_TITLE_STYLE_ORDER[index % len(settings.MENU_TITLE_STYLE_ORDER)]]
        tilt = settings.MENU_TITLE_TILTS[index % len(settings.MENU_TITLE_TILTS)]
        tiles.append(pygame.transform.rotate(_letter_tile(letter, size, style, rng), tilt))
    return tiles


def _letter_tile(letter: str, size: int, style: tuple, rng: random.Random) -> pygame.Surface:
    box_color, text_color, shadow_color = style
    face = load_font(size).render(letter, True, text_color)
    padding = settings.MENU_LETTER_PADDING
    jitter = settings.MENU_LETTER_JITTER
    shadow = settings.MENU_LETTER_SHADOW
    width = face.get_width() + 2 * (padding + jitter)
    height = face.get_height() + 2 * jitter
    corners = [
        (jitter, jitter),
        (width - jitter, jitter),
        (width - jitter, height - jitter),
        (jitter, height - jitter),
    ]
    box = [(x + rng.randint(-jitter, jitter), y + rng.randint(-jitter, jitter)) for x, y in corners]
    surface = pygame.Surface((width + shadow[0], height + shadow[1]), pygame.SRCALPHA)
    pygame.draw.polygon(surface, shadow_color, shift_points(box, shadow))
    pygame.draw.polygon(surface, box_color, box)
    surface.blit(face, face.get_rect(center=(width // 2, height // 2)))
    return surface


def _letter_places(tiles: list) -> list:
    advances = [tile.get_width() - settings.MENU_LETTER_OVERLAP for tile in tiles]
    left = settings.MENU_TITLE_CENTER[0] - sum(advances) / 2
    places = []
    for index, advance in enumerate(advances):
        lift = settings.MENU_TITLE_LIFTS[index % len(settings.MENU_TITLE_LIFTS)]
        places.append((left + advance / 2, settings.MENU_TITLE_CENTER[1] + lift))
        left += advance
    return places
