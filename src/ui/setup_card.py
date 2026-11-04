from collections.abc import Callable

import pygame

from src.core import settings
from src.core.resource_loader import load_font
from src.ui.component import Component
from src.ui.effects import ease_in_back, ease_out_back
from src.ui.menu_shapes import outlined_text, shift_points, slanted_box, tag_surface
from src.ui.slash_menu import CONFIRM_KEYS, DOWN_KEYS, UP_KEYS

LEFT_KEYS = (pygame.K_LEFT, pygame.K_a)
RIGHT_KEYS = (pygame.K_RIGHT, pygame.K_d)
ACTIONS = ("back", "start")


class SetupCard(Component):
    def __init__(self, options: list, names: dict, value_text: Callable[[str], str], on_cycle, on_back, on_start):
        super().__init__()
        self.options = list(options)
        self.names = names
        self.value_text = value_text
        self.on_cycle = on_cycle
        self.on_back = on_back
        self.on_start = on_start
        self.rect = pygame.Rect(settings.SETUP_CARD_RECT)
        self.header = pygame.transform.rotate(
            tag_surface(
                settings.SETUP_HEADER_TEXT,
                settings.SETUP_HEADER_SIZE,
                (settings.MENU_BLUE, settings.MENU_WHITE, settings.MENU_BLACK),
                settings.SETUP_HEADER_PADDING,
                settings.SETUP_ROW_SKEW,
                settings.SETUP_ROW_SHADOW,
            ),
            settings.SETUP_HEADER_TILT,
        )
        self.row_count = len(self.options) + 1
        self.selected = 0
        self.action = 1
        self.elapsed = 0.0
        self.closing = False
        self.kicks = {option: [0.0, 0] for option in self.options}

    def open(self):
        self.visible = True
        self.closing = False
        self.elapsed = 0.0

    def close(self):
        if not self.closing:
            self.closing = True
            self.elapsed = 0.0

    def amount(self) -> float:
        linear = min(1.0, self.elapsed / settings.SETUP_CARD_SECONDS)
        if self.closing:
            return 1 - ease_in_back(linear, settings.MENU_OVERSHOOT)
        return ease_out_back(linear, settings.MENU_OVERSHOOT)

    def offset(self) -> int:
        return round((1 - self.amount()) * settings.SCREEN_WIDTH)

    def update(self, dt: float):
        if not self.visible:
            return
        self.elapsed += dt
        for kick in self.kicks.values():
            kick[0] = max(0.0, kick[0] - dt / settings.SETUP_ARROW_KICK_SECONDS)
        if self.closing and self.elapsed >= settings.SETUP_CARD_SECONDS:
            self.visible = False
            self.on_back()

    def cycle(self, option: str, delta: int):
        self.on_cycle(option, delta)
        self.kicks[option] = [1.0, delta]

    def row_rect(self, row: int) -> pygame.Rect:
        top = self.rect.top + settings.SETUP_ROW_TOP + row * settings.SETUP_ROW_HEIGHT
        left = self.rect.left + settings.SETUP_ROW_INSET
        return pygame.Rect(left, top, self.rect.width - 2 * settings.SETUP_ROW_INSET, settings.SETUP_ROW_STRIP_HEIGHT)

    def arrow_centers(self, row: int) -> tuple:
        rect = self.row_rect(row)
        return (
            (rect.left + settings.SETUP_VALUE_LEFT, rect.centery),
            (rect.left + settings.SETUP_VALUE_RIGHT, rect.centery),
        )

    def action_rect(self, index: int) -> pygame.Rect:
        width = settings.SETUP_ACTION_WIDTH
        total = 2 * width + settings.SETUP_ACTION_GAP
        left = self.rect.centerx - total // 2 + index * (width + settings.SETUP_ACTION_GAP)
        return pygame.Rect(left, self.rect.top + settings.SETUP_ACTION_TOP, width, settings.SETUP_ACTION_HEIGHT)

    def activate_action(self):
        if ACTIONS[self.action] == "start":
            self.on_start()
        else:
            self.close()

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or self.closing:
            return False
        if event.type == pygame.KEYDOWN:
            return self.handle_key(event.key)
        if event.type == pygame.MOUSEMOTION:
            self.hover(event.pos)
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.click(event.pos)
        return False

    def handle_key(self, key: int) -> bool:
        on_actions = self.selected == len(self.options)
        if key in UP_KEYS:
            self.selected = (self.selected - 1) % self.row_count
        elif key in DOWN_KEYS:
            self.selected = (self.selected + 1) % self.row_count
        elif key in LEFT_KEYS + RIGHT_KEYS:
            delta = -1 if key in LEFT_KEYS else 1
            if on_actions:
                self.action = (self.action + delta) % len(ACTIONS)
            else:
                self.cycle(self.options[self.selected], delta)
        elif key in CONFIRM_KEYS:
            if on_actions:
                self.activate_action()
            else:
                self.cycle(self.options[self.selected], 1)
        else:
            return False
        return True

    def hover(self, position: tuple):
        for row in range(len(self.options)):
            if self.row_rect(row).collidepoint(position):
                self.selected = row
                return
        for index in range(len(ACTIONS)):
            if self.action_rect(index).collidepoint(position):
                self.selected = len(self.options)
                self.action = index
                return

    def click(self, position: tuple) -> bool:
        for row, option in enumerate(self.options):
            for delta, center in zip((-1, 1), self.arrow_centers(row)):
                hit = pygame.Rect(0, 0, settings.SETUP_ARROW_HIT, settings.SETUP_ARROW_HIT)
                hit.center = center
                if hit.collidepoint(position):
                    self.selected = row
                    self.cycle(option, delta)
                    return True
            if self.row_rect(row).collidepoint(position):
                self.selected = row
                self.cycle(option, 1)
                return True
        for index in range(len(ACTIONS)):
            if self.action_rect(index).collidepoint(position):
                self.selected = len(self.options)
                self.action = index
                self.activate_action()
                return True
        return False

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return
        shift = (self.offset(), 0)
        card = slanted_box(self.rect, settings.SETUP_CARD_SKEW)
        border = slanted_box(self.rect.inflate(2 * settings.SETUP_CARD_BORDER, 2 * settings.SETUP_CARD_BORDER), settings.SETUP_CARD_SKEW)
        pygame.draw.polygon(surface, settings.MENU_BLACK, shift_points(border, (shift[0] + settings.SETUP_CARD_SHADOW[0], settings.SETUP_CARD_SHADOW[1])))
        pygame.draw.polygon(surface, settings.MENU_WHITE, shift_points(border, shift))
        pygame.draw.polygon(surface, settings.MENU_BLACK, shift_points(card, shift))
        header_at = (self.rect.left + settings.SETUP_HEADER_OFFSET[0] + shift[0], self.rect.top + settings.SETUP_HEADER_OFFSET[1])
        surface.blit(self.header, header_at)
        for row, option in enumerate(self.options):
            self.draw_row(surface, row, option, shift)
        for index, name in enumerate(ACTIONS):
            self.draw_action(surface, index, name, shift)

    def draw_row(self, surface: pygame.Surface, row: int, option: str, shift: tuple):
        rect = self.row_rect(row).move(shift)
        selected = row == self.selected
        strip = slanted_box(rect, settings.SETUP_ROW_SKEW)
        if selected:
            pygame.draw.polygon(surface, settings.MENU_BLUE, shift_points(strip, settings.SETUP_ROW_SHADOW))
            pygame.draw.polygon(surface, settings.MENU_WHITE, strip)
        else:
            pygame.draw.polygon(surface, settings.MENU_GRAY, strip)
        ink = settings.MENU_BLACK if selected else settings.MENU_WHITE
        name = load_font(settings.SETUP_NAME_SIZE).render(self.names[option].upper(), True, ink)
        surface.blit(name, name.get_rect(midleft=(rect.left + settings.SETUP_NAME_INSET, rect.centery)))
        kick, direction = self.kicks[option]
        pop = 1 + kick * kick * settings.MENU_POP_SCALE
        value = load_font(settings.SETUP_VALUE_SIZE).render(self.value_text(option), True, settings.MENU_BLUE if selected else ink)
        if pop > 1:
            value = pygame.transform.rotozoom(value, 0, pop)
        left_center, right_center = (shift_points(self.arrow_centers(row), shift))
        middle = ((left_center[0] + right_center[0]) / 2, rect.centery)
        surface.blit(value, value.get_rect(center=middle))
        size = settings.SETUP_ARROW_SIZE
        push = kick * settings.SETUP_ARROW_KICK
        for side, center in ((-1, left_center), (1, right_center)):
            x = center[0] + (side * push if side == direction else 0)
            arrow = [(x + side * size, center[1]), (x - side * size * 0.6, center[1] - size), (x - side * size * 0.6, center[1] + size)]
            pygame.draw.polygon(surface, settings.MENU_BLUE if selected else settings.MENU_WHITE, arrow)

    def draw_action(self, surface: pygame.Surface, index: int, name: str, shift: tuple):
        rect = self.action_rect(index).move(shift)
        selected = self.selected == len(self.options) and self.action == index
        box = slanted_box(rect, settings.SETUP_ACTION_SKEW)
        if selected:
            pygame.draw.polygon(surface, settings.MENU_BLUE, shift_points(box, settings.SETUP_ROW_SHADOW))
            pygame.draw.polygon(surface, settings.MENU_WHITE, box)
            text = load_font(settings.SETUP_ACTION_SIZE).render(name.upper(), True, settings.MENU_BLACK)
        else:
            pygame.draw.polygon(surface, settings.MENU_BLUE if name == "start" else settings.MENU_GRAY, box)
            text = outlined_text(name.upper(), settings.SETUP_ACTION_SIZE, settings.MENU_WHITE, settings.MENU_BLACK, settings.SETUP_ACTION_OUTLINE)
        surface.blit(text, text.get_rect(center=rect.center))
