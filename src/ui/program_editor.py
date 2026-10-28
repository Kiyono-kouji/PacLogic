import pygame

from src.core import settings
from src.logic import blocks
from src.ui import block_view
from src.ui.component import Component
from src.ui.flash_message import FlashMessage
from src.ui.panel import Panel


class ProgramEditor(Component):
    def __init__(self, limit: int, flash: FlashMessage):
        super().__init__()
        self.limit = limit
        self.flash = flash
        self.program: list = []
        self.palette_panel = Panel(settings.PALETTE_RECT)
        self.program_panel = Panel(settings.PROGRAM_RECT)
        left = self.palette_panel.rect.left + settings.EDITOR_PADDING
        top = self.palette_panel.rect.top + settings.EDITOR_PADDING
        step = settings.BLOCK_HEIGHT + settings.PALETTE_GAP
        self.palette_slots = [
            (block_view.block_rect((left, top + index * step)), template)
            for index, template in enumerate(blocks.PALETTE)
        ]
        self.header_position = (
            self.program_panel.rect.left + settings.EDITOR_PADDING,
            self.program_panel.rect.top + settings.EDITOR_PADDING,
        )
        self.held: list = []
        self.source: int | None = None
        self.press_position: tuple[int, int] | None = None
        self.dragging = False
        self.mouse = (0, 0)

    def origin(self) -> tuple[int, int]:
        return self.header_position[0], self.header_position[1] + settings.BLOCK_HEIGHT

    def block_at(self, position: tuple[int, int]) -> int | None:
        if not self.program_panel.rect.collidepoint(position):
            return None
        index = (position[1] - self.origin()[1]) // settings.BLOCK_HEIGHT
        return index if 0 <= index < len(self.program) else None

    def insertion_index(self, position: tuple[int, int]) -> int:
        offset = position[1] - self.origin()[1] + settings.BLOCK_HEIGHT // 2
        return max(0, min(len(self.program), offset // settings.BLOCK_HEIGHT))

    def press(self, position: tuple[int, int]) -> bool:
        for rect, template in self.palette_slots:
            if rect.collidepoint(position):
                self.held, self.source = [blocks.new_block(template, 0)], None
                self.press_position = position
                return True
        index = self.block_at(position)
        if index is None:
            return False
        start, stop = blocks.block_span(self.program, index)
        self.held, self.source = [dict(block) for block in self.program[start:stop]], start
        self.press_position = position
        return True

    def start_drag(self):
        self.dragging = True
        if self.source is not None:
            del self.program[self.source:self.source + len(self.held)]

    def drop(self, position: tuple[int, int]):
        if self.program_panel.rect.collidepoint(position):
            if self.source is None and not blocks.can_add(self.program, self.limit):
                return
            index = self.insertion_index(position)
            low, high = blocks.depth_range(self.program, index)
            depth = max(low, min(high, (position[0] - self.origin()[0]) // settings.INDENT))
            self.place(index, depth - self.held[0]["depth"])
        elif self.source is not None:
            self.place(self.source, 0)

    def place(self, index: int, shift: int):
        moved = [{**block, "depth": block["depth"] + shift} for block in self.held]
        self.program[index:index] = moved

    def release(self, position: tuple[int, int]):
        if self.dragging:
            self.drop(position)
        self.held, self.source, self.press_position, self.dragging = [], None, None, False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.mouse = event.pos
            if self.press_position and not self.dragging:
                moved_x = event.pos[0] - self.press_position[0]
                moved_y = event.pos[1] - self.press_position[1]
                if max(abs(moved_x), abs(moved_y)) > settings.DRAG_THRESHOLD:
                    self.start_drag()
            return self.dragging
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.press(event.pos)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.press_position:
            self.release(event.pos)
            return True
        return False

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return
        self.palette_panel.draw(surface)
        self.program_panel.draw(surface)
        for rect, template in self.palette_slots:
            block_view.draw_block(surface, template, rect.topleft)
        block_view.draw_block(surface, {"type": block_view.START}, self.header_position)
        block_view.draw_program(surface, self.program, self.origin())
        if self.dragging:
            head_indent = self.held[0]["depth"] * settings.INDENT
            block_view.draw_program(surface, self.held, (self.mouse[0] - head_indent, self.mouse[1]))
