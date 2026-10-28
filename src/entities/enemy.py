import math
import pygame

from src.core import settings
from src.entities.character import Character

class Enemy(Character):
    def __init__(
        self, index: int = 0, tile: tuple[int, int] = (0, 0), direction: str = "D"
    ):
        super().__init__(tile, direction)
        self.index: int = index
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
        for i in range(settings.GHOST_DOME_SEGMENTS + 1):
            angle = math.pi - math.pi * (i / settings.GHOST_DOME_SEGMENTS)
            px = x + radius + radius * math.cos(angle)
            py = y + radius - radius * math.sin(angle)
            points.append((px, py))

        points.append((x + w, y + h))

        for i in range(settings.GHOST_WAVE_SEGMENTS + 1):
            t = i / settings.GHOST_WAVE_SEGMENTS
            bx = x + w * (1.0 - t)
            wave_offset = abs(
                math.sin(t * settings.GHOST_WAVE_CYCLES * math.pi)
            ) * (h * settings.GHOST_WAVE_HEIGHT)
            by = y + h - wave_offset
            points.append((bx, by))

        points.append((x, y + radius))

        pygame.draw.polygon(surface, self.color, points)

        eye_w = max(3, int(w * settings.GHOST_EYE_WIDTH))
        eye_h = max(4, int(h * settings.GHOST_EYE_HEIGHT))
        eye_y = y + int(h * settings.GHOST_EYE_Y)
        left_eye_x = x + int(w * settings.GHOST_EYE_X_LEFT)
        right_eye_x = x + int(w * settings.GHOST_EYE_X_RIGHT)

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
