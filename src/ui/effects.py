import math
import random

import pygame

from src.core import settings


class Particles:
    def __init__(self):
        self.items: list = []

    def burst(self, center: tuple):
        for _ in range(settings.CATCH_PARTICLE_COUNT):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(*settings.CATCH_PARTICLE_SPEED)
            life = random.uniform(*settings.CATCH_PARTICLE_LIFE)
            self.items.append(
                {
                    "x": float(center[0]),
                    "y": float(center[1]),
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": life,
                    "max_life": life,
                    "size": random.randint(*settings.CATCH_PARTICLE_SIZE),
                    "color": random.choice(settings.CATCH_PARTICLE_COLORS),
                }
            )

    def update(self, dt: float):
        slowdown = math.exp(-settings.CATCH_PARTICLE_DRAG * dt)
        for particle in self.items:
            particle["vx"] *= slowdown
            particle["vy"] = particle["vy"] * slowdown + settings.CATCH_PARTICLE_GRAVITY * dt
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["life"] -= dt
        self.items = [particle for particle in self.items if particle["life"] > 0]

    def draw(self, surface: pygame.Surface, view: pygame.Rect | None = None, offset: tuple = (0, 0)):
        view = view or surface.get_rect()
        scale_x = surface.get_width() / view.width
        scale_y = surface.get_height() / view.height
        for particle in self.items:
            size = max(1, round(particle["size"] * scale_x * particle["life"] / particle["max_life"]))
            x = (particle["x"] - view.left) * scale_x + offset[0]
            y = (particle["y"] - view.top) * scale_y + offset[1]
            pygame.draw.rect(surface, particle["color"], (round(x) - size // 2, round(y) - size // 2, size, size))


class CatchCamera:
    def __init__(self):
        self.focus: tuple | None = None
        self.elapsed = 0.0

    def start(self, focus: tuple):
        self.focus = focus
        self.elapsed = 0.0

    def update(self, dt: float):
        if self.focus is not None:
            self.elapsed = min(settings.CATCH_ZOOM_SECONDS, self.elapsed + dt)

    def progress(self) -> float:
        if self.focus is None:
            return 0.0
        linear = self.elapsed / settings.CATCH_ZOOM_SECONDS
        return linear * linear * (3 - 2 * linear)

    def view(self) -> pygame.Rect:
        width, height = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
        ease = self.progress()
        if ease == 0:
            return pygame.Rect(0, 0, width, height)
        zoom = 1 + (settings.CATCH_ZOOM - 1) * ease
        view_width, view_height = width / zoom, height / zoom
        center_x = width / 2 + (self.focus[0] - width / 2) * ease
        center_y = height / 2 + (self.focus[1] - height / 2) * ease
        left = min(max(center_x - view_width / 2, 0), width - view_width)
        top = min(max(center_y - view_height / 2, 0), height - view_height)
        return pygame.Rect(round(left), round(top), round(view_width), round(view_height))

    def frame(self, canvas: pygame.Surface) -> pygame.Surface:
        ease = self.progress()
        if ease == 0:
            return canvas
        image = pygame.transform.scale(canvas.subsurface(self.view()), canvas.get_size())
        gray = pygame.transform.grayscale(image)
        gray.set_alpha(round(255 * ease))
        image.blit(gray, (0, 0))
        return image


class GhostFlyAway:
    def __init__(self):
        self.ghosts: list = []
        self.elapsed = 0.0

    @property
    def started(self) -> bool:
        return bool(self.ghosts)

    def start(self, ghosts: list):
        self.ghosts = list(ghosts)
        self.elapsed = 0.0

    def update(self, dt: float):
        if self.started:
            self.elapsed += dt

    def draw(self, surface: pygame.Surface, tile_size: int):
        for order, (sprite, center) in enumerate(self.ghosts):
            progress = (self.elapsed - order * settings.ESCAPE_GHOST_STAGGER) / settings.ESCAPE_GHOST_SECONDS
            progress = min(max(progress, 0.0), 1.0)
            if progress >= 1:
                continue
            whiteness = round(255 * min(1.0, progress / settings.ESCAPE_GHOST_WHITEN_SHARE))
            image = sprite.copy()
            image.fill((whiteness, whiteness, whiteness), special_flags=pygame.BLEND_RGB_ADD)
            fade_from = 1 - settings.ESCAPE_GHOST_FADE_SHARE
            if progress > fade_from:
                image.set_alpha(round(255 * (1 - (progress - fade_from) / settings.ESCAPE_GHOST_FADE_SHARE)))
            rise = settings.ESCAPE_GHOST_RISE_TILES * tile_size * progress * progress
            surface.blit(image, image.get_rect(center=(center[0], center[1] - rise)))


class Shake:
    def __init__(self):
        self.seconds_left = 0.0

    def start(self):
        self.seconds_left = settings.CATCH_SHAKE_SECONDS

    def update(self, dt: float):
        self.seconds_left = max(0.0, self.seconds_left - dt)

    def offset(self) -> tuple:
        reach = round(settings.CATCH_SHAKE_PIXELS * self.seconds_left / settings.CATCH_SHAKE_SECONDS)
        return random.randint(-reach, reach), random.randint(-reach, reach)


class Flash:
    def __init__(self, color: tuple, peak_alpha: int, seconds: float, rising: bool):
        self.layer = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.layer.fill(color)
        self.peak_alpha = peak_alpha
        self.seconds = seconds
        self.rising = rising
        self.elapsed: float | None = None

    @property
    def started(self) -> bool:
        return self.elapsed is not None

    @property
    def done(self) -> bool:
        return self.started and self.elapsed >= self.seconds

    def start(self):
        self.elapsed = 0.0

    def update(self, dt: float):
        if self.started:
            self.elapsed = min(self.seconds, self.elapsed + dt)

    def draw(self, surface: pygame.Surface):
        if not self.started:
            return
        progress = self.elapsed / self.seconds
        strength = progress if self.rising else 1 - progress
        if strength <= 0:
            return
        self.layer.set_alpha(round(self.peak_alpha * strength))
        surface.blit(self.layer, (0, 0))
