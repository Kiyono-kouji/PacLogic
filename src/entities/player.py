import math
import pygame

from src.core import settings
from src.entities.character import Character

class Player(Character):
    def __init__(self, tile: tuple[int, int] = (0, 0), direction: str = "R"):
        super().__init__(tile, direction)

    def draw(self, surface: pygame.Surface):
        center_x = int(self.position[0] + self.tile_size / 2)
        center_y = int(self.position[1] + self.tile_size / 2)
        center = (center_x, center_y)
        radius = max(2, self.tile_size // 2 - 2)

        direction_angles = {
            "R": 0.0,
            "D": math.pi / 2,
            "L": math.pi,
            "U": -math.pi / 2,
        }
        base_angle = direction_angles.get(self.direction, 0.0)
        half_mouth = settings.PACMAN_MOUTH_ANGLE

        points = [center]
        start_angle = base_angle + half_mouth
        end_angle = base_angle + 2 * math.pi - half_mouth
        for i in range(settings.PACMAN_SEGMENTS + 1):
            theta = start_angle + (end_angle - start_angle) * (
                i / settings.PACMAN_SEGMENTS
            )
            px = center_x + radius * math.cos(theta)
            py = center_y + radius * math.sin(theta)
            points.append((px, py))
        pygame.draw.polygon(surface, settings.PACMAN_COLOR, points)
