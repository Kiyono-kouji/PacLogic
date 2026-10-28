import math
import pygame

from src.core import settings
from src.entities.character import Character

GHOST_FRAME_DURATION = 0.15


def ghost_art_folders(count: int) -> tuple[str, ...]:
    names = ("red", "pink", "cyan", "orange")
    return tuple(names[i % len(names)] for i in range(count))


class Enemy(Character):
    def __init__(
        self, index: int = 0, tile: tuple[int, int] = (0, 0), direction: str = "D"
    ):
        super().__init__(tile, direction)
        self.index: int = index
        self.action: str = "move"
        self.selected: bool = False
        self.color: tuple[int, int, int] = settings.GHOST_COLORS[
            index % len(settings.GHOST_COLORS)
        ]

    def draw(self, surface: pygame.Surface):
        pad = max(1, self.tile_size // 8)
        x = int(self.position[0] + pad)
        y = int(self.position[1] + pad)
        w = max(4, self.tile_size - 2 * pad)
        h = max(4, self.tile_size - 2 * pad)
        radius = w // 2

        if self.selected:
            highlight_rect = pygame.Rect(x - 2, y - 2, w + 4, h + 4)
            pygame.draw.rect(
                surface,
                settings.GHOST_SELECTED_COLOR,
                highlight_rect,
                width=2,
                border_radius=radius + 2,
            )

        points: list[tuple[float, float]] = []
        dome_segments = 16
        for i in range(dome_segments + 1):
            angle = math.pi - math.pi * (i / dome_segments)
            px = x + radius + radius * math.cos(angle)
            py = y + radius - radius * math.sin(angle)
            points.append((px, py))

        points.append((x + w, y + h))

        wave_segments = 18
        for i in range(wave_segments + 1):
            t = i / wave_segments
            bx = x + w * (1.0 - t)
            wave_offset = abs(
                math.sin(t * 3.0 * math.pi + self.time * settings.GHOST_WAVE_SPEED)
            ) * (h * 0.18)
            by = y + h - wave_offset
            points.append((bx, by))

        points.append((x, y + radius))

        pygame.draw.polygon(surface, self.color, points)

        eye_w = max(3, int(w * 0.26))
        eye_h = max(4, int(h * 0.34))
        eye_y = y + int(h * 0.22)
        left_eye_x = x + int(w * 0.18)
        right_eye_x = x + int(w * 0.56)

        pygame.draw.ellipse(
            surface,
            settings.GHOST_EYE_COLOR,
            pygame.Rect(left_eye_x, eye_y, eye_w, eye_h),
        )
        pygame.draw.ellipse(
            surface,
            settings.GHOST_EYE_COLOR,
            pygame.Rect(right_eye_x, eye_y, eye_w, eye_h),
        )

        pupil_size = max(2, eye_w // 2)
        shift_x = 0
        shift_y = 0
        if self.direction == "L":
            shift_x = -eye_w // 4
        elif self.direction == "R":
            shift_x = eye_w // 4
        elif self.direction == "U":
            shift_y = -eye_h // 4
        elif self.direction == "D":
            shift_y = eye_h // 4

        pupil_left_x = left_eye_x + (eye_w - pupil_size) // 2 + shift_x
        pupil_right_x = right_eye_x + (eye_w - pupil_size) // 2 + shift_x
        pupil_y = eye_y + (eye_h - pupil_size) // 2 + shift_y

        pygame.draw.ellipse(
            surface,
            settings.GHOST_PUPIL_COLOR,
            pygame.Rect(pupil_left_x, pupil_y, pupil_size, pupil_size),
        )
        pygame.draw.ellipse(
            surface,
            settings.GHOST_PUPIL_COLOR,
            pygame.Rect(pupil_right_x, pupil_y, pupil_size, pupil_size),
        )
