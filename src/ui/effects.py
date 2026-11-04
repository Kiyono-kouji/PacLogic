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

    def draw(self, surface: pygame.Surface):
        for particle in self.items:
            size = max(1, round(particle["size"] * particle["life"] / particle["max_life"]))
            left = round(particle["x"]) - size // 2
            top = round(particle["y"]) - size // 2
            pygame.draw.rect(surface, particle["color"], (left, top, size, size))


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
