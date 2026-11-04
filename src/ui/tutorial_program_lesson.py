import pygame

from src.core import settings
from src.core.resource_loader import load_font
from src.logic import blocks
from src.logic.grid import Level
from src.ui.menu_shapes import shift_points, slanted_box, tag_surface
from src.ui.tutorial_board import TutorialBoard
from src.ui.tutorial_lessons import Lesson
from src.ui.tutorial_runner import SimRunner

PALETTE = (
    ("UP", "move-up", {"type": blocks.MOVE, "direction": "U"}),
    ("RIGHT", "move-right", {"type": blocks.MOVE, "direction": "R"}),
    ("DOWN", "move-down", {"type": blocks.MOVE, "direction": "D"}),
    ("LEFT", "move-left", {"type": blocks.MOVE, "direction": "L"}),
    ("WAIT", "wait", {"type": blocks.WAIT, "count": settings.WAIT_MIN}),
)


class ProgramLesson(Lesson):
    title = "GHOST CODE"
    text = "Before a round you give each ghost a program made of blocks. Then it runs alone, one block per tick. Ghosts move first, then Pac-Man."
    hint = "Click blocks to add them, click a placed block to remove it. RUN plays it, STEP goes one tick."
    resettable = True

    def __init__(self, level: Level):
        super().__init__()
        self.level = level
        self.board = TutorialBoard(settings.TUTORIAL_PROGRAM_BOARD)
        self.board.fit(level)
        self.runner = SimRunner(loop=False)
        self.program: list = []
        self.reset()

    def reset(self):
        self.program = []
        self.runner.start(self.level, self.controllers, running=False)

    def controllers(self) -> list:
        return [blocks.run(blocks.parse(self.program))]

    def palette_rect(self, index: int) -> pygame.Rect:
        width, height = settings.TUTORIAL_BLOCK_SIZE
        left = settings.TUTORIAL_PALETTE_LEFT + index * (width + settings.TUTORIAL_BLOCK_GAP)
        return pygame.Rect(left, settings.TUTORIAL_PALETTE_TOP, width, height)

    def slot_rect(self, index: int) -> pygame.Rect:
        width, height = settings.TUTORIAL_SLOT_SIZE
        left = settings.TUTORIAL_PALETTE_LEFT + index * (width + settings.TUTORIAL_SLOT_GAP)
        return pygame.Rect(left, settings.TUTORIAL_PROGRAM_TOP, width, height)

    def edited(self):
        self.runner.running = False
        self.runner.restart()

    def click(self, position: tuple):
        for index, (_, _, template) in enumerate(PALETTE):
            if self.palette_rect(index).collidepoint(position):
                if blocks.can_add(self.program, settings.TUTORIAL_PROGRAM_LIMIT):
                    self.program.append(blocks.new_block(template, 0))
                    self.edited()
                else:
                    self.runner.stamp.show("FULL!", settings.TUTORIAL_STAMP_DARK)
                return
        for index in range(len(self.program)):
            if self.slot_rect(index).collidepoint(position):
                del self.program[index]
                self.edited()
                return
        if pygame.Rect(settings.TUTORIAL_RUN_RECT).collidepoint(position):
            self.runner.restart()
            self.runner.running = True
        elif pygame.Rect(settings.TUTORIAL_STEP_RECT).collidepoint(position):
            self.runner.running = False
            if self.runner.finished():
                self.runner.restart()
            self.runner.step()

    def update(self, dt: float):
        self.runner.update(dt)

    def active_block(self) -> int | None:
        tick = self.runner.sim.tick
        if tick == 0 or self.runner.finished() and self.runner.sim.tick > len(self.program):
            return None
        return tick - 1 if tick - 1 < len(self.program) else None

    def draw(self, surface: pygame.Surface):
        self.board.draw(surface)
        self.runner.draw(surface, self.board, show_route=True)
        self.draw_phase(surface)
        for index, (label, color, _) in enumerate(PALETTE):
            rect = self.palette_rect(index)
            hovered = self.mouse is not None and rect.collidepoint(self.mouse)
            self.draw_block(surface, rect.move(0, -settings.TUTORIAL_BLOCK_LIFT if hovered else 0), label, settings.BLOCK_COLORS[color], hovered)
        active = self.active_block()
        for index in range(settings.TUTORIAL_PROGRAM_LIMIT):
            rect = self.slot_rect(index)
            if index < len(self.program):
                block = self.program[index]
                name = "wait" if block["type"] == blocks.WAIT else f"move-{settings.DIRECTION_NAMES[block['direction']]}"
                label = next(text for text, color, _ in PALETTE if color == name)
                self.draw_block(surface, rect, label, settings.BLOCK_COLORS[name], index == active)
            else:
                pygame.draw.polygon(surface, settings.MENU_GRAY, slanted_box(rect, settings.TUTORIAL_BLOCK_SKEW), settings.TUTORIAL_HOVER_WIDTH)
        self.draw_button(surface, settings.TUTORIAL_RUN_RECT, "RUN", True)
        self.draw_button(surface, settings.TUTORIAL_STEP_RECT, "STEP", False)

    def draw_block(self, surface: pygame.Surface, rect: pygame.Rect, label: str, color: tuple, lit: bool):
        box = slanted_box(rect, settings.TUTORIAL_BLOCK_SKEW)
        pygame.draw.polygon(surface, settings.MENU_WHITE if lit else settings.MENU_BLACK, shift_points(box, settings.TUTORIAL_BLOCK_SHADOW))
        pygame.draw.polygon(surface, color, box)
        if lit:
            pygame.draw.polygon(surface, settings.MENU_WHITE, box, settings.TUTORIAL_HOVER_WIDTH)
        text = load_font(settings.TUTORIAL_BLOCK_TEXT_SIZE).render(label, True, settings.BLOCK_TEXT_COLOR)
        surface.blit(text, text.get_rect(center=rect.center))

    def draw_button(self, surface: pygame.Surface, rect: tuple, label: str, filled: bool):
        rect = pygame.Rect(rect)
        hovered = self.mouse is not None and rect.collidepoint(self.mouse)
        box = slanted_box(rect, settings.TUTORIAL_BLOCK_SKEW)
        pygame.draw.polygon(surface, settings.MENU_BLUE, shift_points(box, settings.TUTORIAL_BLOCK_SHADOW))
        pygame.draw.polygon(surface, settings.MENU_BLUE if hovered else settings.MENU_WHITE if filled else settings.MENU_BLACK, box)
        pygame.draw.polygon(surface, settings.MENU_WHITE, box, settings.TUTORIAL_HOVER_WIDTH)
        ink = settings.MENU_BLACK if filled and not hovered else settings.MENU_WHITE
        text = load_font(settings.TUTORIAL_BLOCK_TEXT_SIZE).render(label, True, ink)
        surface.blit(text, text.get_rect(center=rect.center))

    def draw_phase(self, surface: pygame.Surface):
        sim = self.runner.sim
        if sim.tick == 0:
            text = "Pac-Man walks the green route"
        elif self.runner.finished():
            text = f"Tick {sim.tick}: round over"
        elif self.runner.ghosts_only():
            text = f"Tick {sim.tick}: 1. ghosts move"
        else:
            text = f"Tick {sim.tick}: 2. Pac-Man steps"
        tag = tag_surface(
            text,
            settings.TUTORIAL_PHASE_SIZE,
            settings.TUTORIAL_STAMP_DARK,
            settings.TUTORIAL_HEADER_PADDING,
            settings.TUTORIAL_TAG_SKEW,
            settings.TUTORIAL_TAG_SHADOW,
        )
        surface.blit(tag, settings.TUTORIAL_PHASE_POSITION)
