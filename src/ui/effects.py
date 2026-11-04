import math
import random

import pygame

from src.core import settings


class Particles:
    def __init__(self):
        self.items: list = []

    def burst(self, center: tuple, count: int, colors: tuple):
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(*settings.PARTICLE_SPEED)
            life = random.uniform(*settings.PARTICLE_LIFE)
            self.items.append(
                {
                    "x": float(center[0]),
                    "y": float(center[1]),
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": life,
                    "max_life": life,
                    "size": random.randint(*settings.PARTICLE_SIZE),
                    "color": random.choice(colors),
                }
            )

    def update(self, dt: float):
        slowdown = math.exp(-settings.PARTICLE_DRAG * dt)
        for particle in self.items:
            particle["vx"] *= slowdown
            particle["vy"] = particle["vy"] * slowdown + settings.PARTICLE_GRAVITY * dt
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["life"] -= dt
        self.items = [particle for particle in self.items if particle["life"] > 0]

    def draw(
        self,
        surface: pygame.Surface,
        view: pygame.Rect | None = None,
        target: pygame.Rect | None = None,
        offset: tuple = (0, 0),
    ):
        view = view or surface.get_rect()
        target = target or surface.get_rect()
        scale_x = target.width / view.width
        scale_y = target.height / view.height
        for particle in self.items:
            size = max(1, round(particle["size"] * scale_x * particle["life"] / particle["max_life"]))
            x = target.left + (particle["x"] - view.left) * scale_x + offset[0]
            y = target.top + (particle["y"] - view.top) * scale_y + offset[1]
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
            self.elapsed += dt

    def eased(self, seconds: float) -> float:
        if self.focus is None:
            return 0.0
        linear = min(1.0, self.elapsed / seconds)
        return linear * linear * (3 - 2 * linear)

    def zoom_progress(self) -> float:
        if self.focus is None:
            return 0.0
        return ease_out_back(min(1.0, self.elapsed / settings.CATCH_ZOOM_SECONDS), settings.CATCH_ZOOM_OVERSHOOT)

    def view(self, area: pygame.Rect) -> pygame.Rect:
        ease = self.zoom_progress()
        if ease == 0:
            return pygame.Rect(area)
        zoom = 1 + (settings.CATCH_ZOOM - 1) * ease
        width, height = area.width / zoom, area.height / zoom
        center_x = area.centerx + (self.focus[0] - area.centerx) * ease
        center_y = area.centery + (self.focus[1] - area.centery) * ease
        return pygame.Rect(round(center_x - width / 2), round(center_y - height / 2), round(width), round(height))

    def zoomed(self, canvas: pygame.Surface, area: pygame.Rect, background: tuple) -> pygame.Surface:
        view = self.view(area)
        sample = pygame.Surface(view.size)
        sample.fill(background)
        sample.blit(canvas, (-view.left, -view.top))
        return pygame.transform.scale(sample, area.size)

    def desaturate(self, frame: pygame.Surface):
        amount = self.eased(settings.CATCH_GRAY_SECONDS)
        if amount == 0:
            return
        gray = pygame.transform.grayscale(frame)
        gray.set_alpha(round(255 * amount))
        frame.blit(gray, (0, 0))


def ease_out_back(linear: float, overshoot: float) -> float:
    return 1 + (overshoot + 1) * (linear - 1) ** 3 + overshoot * (linear - 1) ** 2


class DeadPacMan:
    def __init__(self):
        self.sprite: pygame.Surface | None = None
        self.center = (0, 0)
        self.elapsed = 0.0

    def start(self, sprite: pygame.Surface, center: tuple):
        self.sprite = sprite
        self.center = center
        self.elapsed = 0.0

    def update(self, dt: float):
        if self.sprite is not None:
            self.elapsed += dt

    def draw(self, surface: pygame.Surface):
        if self.sprite is None:
            return
        image = self.sprite.copy()
        if self.elapsed < settings.DEAD_PACMAN_BLINK_SECONDS:
            if int(self.elapsed / settings.DEAD_PACMAN_BLINK_INTERVAL) % 2 == 0:
                image.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
        else:
            shade = settings.DEAD_PACMAN_SHADE
            image.fill((shade, shade, shade), special_flags=pygame.BLEND_RGB_MULT)
        surface.blit(image, image.get_rect(center=self.center))


class GhostFlyAway:
    def __init__(self):
        self.ghosts: list = []
        self.elapsed = 0.0

    @property
    def started(self) -> bool:
        return bool(self.ghosts)

    def start(self, ghosts: list):
        self.ghosts = [(sprite, _body_mask(sprite), center) for sprite, center in ghosts]
        self.elapsed = 0.0

    def update(self, dt: float):
        if self.started:
            self.elapsed += dt

    def draw(self, surface: pygame.Surface, tile_size: int):
        for order, (sprite, body, center) in enumerate(self.ghosts):
            progress = (self.elapsed - order * settings.ESCAPE_GHOST_STAGGER) / settings.ESCAPE_GHOST_SECONDS
            progress = min(max(progress, 0.0), 1.0)
            if progress >= 1:
                continue
            whiteness = round(255 * min(1.0, progress / settings.ESCAPE_GHOST_WHITEN_SHARE))
            whitening = body.copy()
            whitening.fill((whiteness, whiteness, whiteness), special_flags=pygame.BLEND_RGB_MULT)
            image = sprite.copy()
            image.blit(whitening, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            fade_from = 1 - settings.ESCAPE_GHOST_FADE_SHARE
            if progress > fade_from:
                image.set_alpha(round(255 * (1 - (progress - fade_from) / settings.ESCAPE_GHOST_FADE_SHARE)))
            rise = settings.ESCAPE_GHOST_RISE_TILES * tile_size * progress * progress
            surface.blit(image, image.get_rect(center=(center[0], center[1] - rise)))


def _body_mask(sprite: pygame.Surface) -> pygame.Surface:
    mask = pygame.Surface(sprite.get_size())
    mask.fill((0, 0, 0))
    for x in range(sprite.get_width()):
        for y in range(sprite.get_height()):
            pixel = sprite.get_at((x, y))
            if pixel.a and tuple(pixel)[:3] != settings.GHOST_PUPIL_COLOR:
                mask.set_at((x, y), (255, 255, 255))
    return mask


class Shake:
    def __init__(self):
        self.seconds = 1.0
        self.pixels = 0
        self.seconds_left = 0.0

    def start(self, seconds: float, pixels: int):
        self.seconds = seconds
        self.pixels = pixels
        self.seconds_left = seconds

    def update(self, dt: float):
        self.seconds_left = max(0.0, self.seconds_left - dt)

    def offset(self) -> tuple:
        reach = round(self.pixels * self.seconds_left / self.seconds)
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


class WarningPulse:
    def __init__(self):
        self.glow = _edge_glow()
        self.elapsed = 0.0
        self.strength = 0.0

    def update(self, dt: float, active: bool):
        step = dt / settings.TIME_WARNING_FADE_SECONDS
        self.strength = min(1.0, self.strength + step) if active else max(0.0, self.strength - step)
        self.elapsed = self.elapsed + dt if self.strength > 0 else 0.0

    def draw(self, surface: pygame.Surface):
        if self.strength <= 0:
            return
        wave = 0.5 - 0.5 * math.cos(math.tau * self.elapsed / settings.TIME_WARNING_PULSE_SECONDS)
        level = settings.TIME_WARNING_LOW + (settings.TIME_WARNING_HIGH - settings.TIME_WARNING_LOW) * wave
        self.glow.set_alpha(round(255 * level * self.strength))
        surface.blit(self.glow, (0, 0))


def _edge_glow() -> pygame.Surface:
    glow = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
    full = glow.get_rect()
    for inset in range(settings.TIME_WARNING_EDGE):
        alpha = round(settings.TIME_WARNING_EDGE_ALPHA * (1 - inset / settings.TIME_WARNING_EDGE) ** 2)
        pygame.draw.rect(glow, (*settings.TIME_WARNING_COLOR, alpha), full.inflate(-2 * inset, -2 * inset), 1)
    return glow
