from functools import lru_cache

import pygame

from src.core import settings


@lru_cache(maxsize=None)
def load_font(size: int) -> pygame.font.Font:
    pygame.font.init()
    try:
        return pygame.font.Font(settings.DEFAULT_FONT, size)
    except (FileNotFoundError, OSError):
        print(f"Could not load {settings.DEFAULT_FONT}, using the default font")
        return pygame.font.Font(None, size)


def sprite_size(tile: int) -> int:
    if tile < settings.SPRITE_PIXELS:
        return tile
    return tile // settings.SPRITE_PIXELS * settings.SPRITE_PIXELS


@lru_cache(maxsize=None)
def load_sprite(name: str, tile: int) -> pygame.Surface:
    image = pygame.image.load(settings.SPRITES_DIR / name).convert_alpha()
    size = sprite_size(tile)
    return pygame.transform.scale(image, (size, size))


def animation_frame(frame_count: int, frame_ms: int) -> int:
    return pygame.time.get_ticks() // frame_ms % frame_count
