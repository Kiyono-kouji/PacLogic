import math

import pygame

from src.core.resource_loader import load_font


def approach(current: float, target: float, rate: float, dt: float) -> float:
    return target + (current - target) * math.exp(-rate * dt)


def progress(elapsed: float, delay: float, seconds: float) -> float:
    return max(0.0, min(1.0, (elapsed - delay) / seconds))


def rotate_points(points: list, center: tuple, degrees: float) -> list:
    angle = math.radians(-degrees)
    cos, sin = math.cos(angle), math.sin(angle)
    return [
        (center[0] + x * cos - y * sin, center[1] + x * sin + y * cos)
        for x, y in points
    ]


def shift_points(points, offset: tuple) -> list:
    return [(x + offset[0], y + offset[1]) for x, y in points]


def slanted_box(rect: pygame.Rect, skew: int) -> list:
    rect = pygame.Rect(rect)
    return [
        (rect.left + skew, rect.top),
        (rect.right, rect.top),
        (rect.right - skew, rect.bottom),
        (rect.left, rect.bottom),
    ]


def outlined_text(text: str, size: int, color: tuple, outline_color: tuple, outline: int) -> pygame.Surface:
    font = load_font(size)
    face = font.render(text, True, color)
    edge = font.render(text, True, outline_color)
    surface = pygame.Surface((face.get_width() + 2 * outline, face.get_height() + 2 * outline), pygame.SRCALPHA)
    for dx in range(-outline, outline + 1):
        for dy in range(-outline, outline + 1):
            if dx * dx + dy * dy <= outline * outline:
                surface.blit(edge, (outline + dx, outline + dy))
    surface.blit(face, (outline, outline))
    return surface


def tag_surface(text: str, size: int, colors: tuple, padding: tuple, skew: int, shadow: tuple) -> pygame.Surface:
    box_color, text_color, shadow_color = colors
    face = load_font(size).render(text, True, text_color)
    width = face.get_width() + 2 * padding[0] + skew
    height = face.get_height() + 2 * padding[1]
    surface = pygame.Surface((width + abs(shadow[0]), height + abs(shadow[1])), pygame.SRCALPHA)
    box = slanted_box((0, 0, width, height), skew)
    pygame.draw.polygon(surface, shadow_color, shift_points(box, shadow))
    pygame.draw.polygon(surface, box_color, box)
    surface.blit(face, face.get_rect(center=(width // 2, height // 2)))
    return surface


def wrap_text(text: str, font: pygame.font.Font, width: int) -> list:
    lines = []
    for paragraph in text.split("\n"):
        line = ""
        for word in paragraph.split(" "):
            candidate = f"{line} {word}".strip()
            if line and font.size(candidate)[0] > width:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
    return lines


def draw_lines(surface: pygame.Surface, lines: list, font: pygame.font.Font, color: tuple, topleft: tuple, line_height: int, characters: int | None = None):
    left, top = topleft
    remaining = sum(len(line) for line in lines) if characters is None else characters
    for row, line in enumerate(lines):
        if remaining <= 0:
            return
        shown = line[:remaining]
        remaining -= len(line)
        if shown:
            surface.blit(font.render(shown, True, color), (left, top + row * line_height))
