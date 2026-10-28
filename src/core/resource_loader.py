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
