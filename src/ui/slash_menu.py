import math
from collections.abc import Callable

import pygame

from src.core import settings
from src.core.resource_loader import load_font
from src.ui.component import Component
from src.ui.effects import ease_out_back
from src.ui.menu_shapes import approach, outlined_text, progress, rotate_points, shift_points

UP_KEYS = (pygame.K_UP, pygame.K_w)
DOWN_KEYS = (pygame.K_DOWN, pygame.K_s)
CONFIRM_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)


class SlashMenu(Component):
    def __init__(self, items: list, on_choose: Callable[[str], None]):
        super().__init__()
        self.on_choose = on_choose
        self.names = [name for name, _ in items]
        self.plain = []
        self.chosen = []
        self.centers = []
        for index, (_, text) in enumerate(items):
            self.plain.append(
                pygame.transform.rotate(
                    outlined_text(text, settings.MENU_ITEM_SIZE, settings.MENU_WHITE, settings.MENU_BLACK, settings.MENU_ITEM_OUTLINE),
                    settings.MENU_ITEM_TILT,
                )
            )
            self.chosen.append(load_font(settings.MENU_ITEM_SIZE).render(text, True, settings.MENU_BLACK))
            self.centers.append(
                (
                    settings.MENU_ITEMS_START[0] + index * settings.MENU_ITEMS_STEP[0],
                    settings.MENU_ITEMS_START[1] + index * settings.MENU_ITEMS_STEP[1],
                )
            )
        self.selected = 0
        self.pressed: int | None = None
        self.elapsed = 0.0
        self.pop = 1.0
        self.pop_scale = settings.MENU_POP_SCALE
        self.cursor = list(self.centers[0])
        self.cursor_width = float(self.chosen[0].get_width())

    def select(self, index: int):
        if index == self.selected:
            return
        self.selected = index
        self.pop = 0.0
        self.pop_scale = settings.MENU_POP_SCALE

    def choose(self, index: int):
        self.select(index)
        self.pop = 0.0
        self.pop_scale = settings.MENU_CONFIRM_SCALE
        self.on_choose(self.names[index])

    def item_at(self, position: tuple) -> int | None:
        for index, center in enumerate(self.centers):
            rect = self.plain[index].get_rect(center=center).inflate(settings.MENU_ITEM_HIT_PADDING, settings.MENU_ITEM_HIT_PADDING)
            if rect.collidepoint(position):
                return index
        return None

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key in UP_KEYS:
                self.select((self.selected - 1) % len(self.names))
                return True
            if event.key in DOWN_KEYS:
                self.select((self.selected + 1) % len(self.names))
                return True
            if event.key in CONFIRM_KEYS:
                self.choose(self.selected)
                return True
        if event.type == pygame.MOUSEMOTION:
            index = self.item_at(event.pos)
            if index is not None:
                self.select(index)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed = self.item_at(event.pos)
            return self.pressed is not None
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            pressed, self.pressed = self.pressed, None
            if pressed is not None and self.item_at(event.pos) == pressed:
                self.choose(pressed)
                return True
        return False

    def update(self, dt: float):
        self.elapsed += dt
        self.pop = min(1.0, self.pop + dt / settings.MENU_POP_SECONDS)
        target = self.centers[self.selected]
        rate = settings.MENU_HIGHLIGHT_FOLLOW
        self.cursor[0] = approach(self.cursor[0], target[0], rate, dt)
        self.cursor[1] = approach(self.cursor[1], target[1], rate, dt)
        self.cursor_width = approach(self.cursor_width, self.chosen[self.selected].get_width(), rate, dt)

    def slide(self, index: int) -> float:
        delay = settings.MENU_ITEM_DELAY + index * settings.MENU_ITEM_STAGGER
        linear = progress(self.elapsed, delay, settings.MENU_INTRO_SECONDS)
        return (1 - ease_out_back(linear, settings.MENU_OVERSHOOT)) * settings.MENU_SHAPE_SLIDE

    def scale(self) -> float:
        return 1 + self.pop_scale * (1 - self.pop) ** 2

    def draw(self, surface: pygame.Surface):
        for index, image in enumerate(self.plain):
            if index != self.selected:
                center = (self.centers[index][0] + self.slide(index), self.centers[index][1])
                surface.blit(image, image.get_rect(center=center))
        self.draw_highlight(surface)
        image = pygame.transform.rotozoom(self.chosen[self.selected], settings.MENU_ITEM_TILT, self.scale())
        center = (self.cursor[0] + self.slide(self.selected), self.cursor[1])
        surface.blit(image, image.get_rect(center=center))

    def draw_highlight(self, surface: pygame.Surface):
        scale = self.scale()
        half_width = (self.cursor_width / 2 + settings.MENU_HIGHLIGHT_PADDING[0]) * scale
        half_height = (self.chosen[self.selected].get_height() / 2 + settings.MENU_HIGHLIGHT_PADDING[1]) * scale
        wobble = settings.MENU_HIGHLIGHT_WOBBLE
        phase = self.elapsed * settings.MENU_HIGHLIGHT_WOBBLE_SPEED
        shape = [
            (-half_width, -half_height * 0.8),
            (half_width * 1.08, -half_height),
            (half_width, half_height * 0.9),
            (-half_width * 1.12, half_height),
        ]
        shape = [
            (x + math.sin(phase + corner * 1.9) * wobble, y + math.cos(phase * 1.3 + corner) * wobble)
            for corner, (x, y) in enumerate(shape)
        ]
        center = (self.cursor[0] + self.slide(self.selected), self.cursor[1])
        points = rotate_points(shape, center, settings.MENU_ITEM_TILT)
        pygame.draw.polygon(surface, settings.MENU_BLACK, shift_points(points, settings.MENU_HIGHLIGHT_SHADOW))
        pygame.draw.polygon(surface, settings.MENU_WHITE, points)
        size = settings.MENU_POINTER_SIZE
        tip = -half_width * 1.12 - size * 0.4
        pointer = [(tip, 0), (tip - size * 1.6, -size), (tip - size, 0), (tip - size * 1.6, size)]
        pointer_points = rotate_points(pointer, center, settings.MENU_ITEM_TILT)
        pygame.draw.polygon(surface, settings.MENU_BLACK, shift_points(pointer_points, settings.MENU_HIGHLIGHT_SHADOW))
        pygame.draw.polygon(surface, settings.MENU_BLUE, pointer_points)
        pygame.draw.polygon(surface, settings.MENU_BLACK, pointer_points, settings.MENU_POINTER_OUTLINE)
