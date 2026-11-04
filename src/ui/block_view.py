import pygame

from src.core import settings
from src.core.resource_loader import load_font
from src.logic.blocks import MOVE, REPEAT, WAIT

START = "START"
MOVE_KINDS = {"U": "move-up", "R": "move-right", "D": "move-down", "L": "move-left"}
KINDS = {WAIT: "wait", REPEAT: "repeat", START: "when-start"}


def block_kind(block: dict) -> str:
    if block["type"] == MOVE:
        return MOVE_KINDS[block["direction"]]
    return KINDS[block["type"]]


def block_rect(position: tuple[int, int]) -> pygame.Rect:
    return pygame.Rect(position, (settings.BLOCK_WIDTH, settings.BLOCK_HEIGHT))


# Works out the y of every block (tops) and every Repeat foot (feet), plus the total height.
# The editor uses the same numbers for clicking, dropping and scrolling.
def program_layout(program: list) -> tuple[list[int], dict[int, int], int]:
    # open_loops: a stack of Repeats whose C shape is still open.
    tops, feet, open_loops, y = [], {}, [], 0
    for index, block in enumerate(program):
        tops.append(y)
        y += settings.BLOCK_HEIGHT
        if block["type"] == REPEAT:
            open_loops.append(index)
        # -1 after the last block closes every open loop.
        next_depth = program[index + 1]["depth"] if index + 1 < len(program) else -1
        # A loop closes when the next block is not deeper than it; innermost closes first.
        while open_loops and program[open_loops[-1]]["depth"] >= next_depth:
            # Empty Repeat: leave an open gap to drop into.
            if open_loops[-1] == index:
                y += settings.BLOCK_FOOT_HEIGHT
            feet[open_loops.pop()] = y
            y += settings.BLOCK_FOOT_HEIGHT
    return tops, feet, y


def draw_shape(surface: pygame.Surface, color: tuple, rect: pygame.Rect):
    pygame.draw.rect(surface, color, rect.inflate(-2 * settings.BLOCK_STEP, 0))
    pygame.draw.rect(surface, color, rect.inflate(0, -2 * settings.BLOCK_STEP))


def draw_tab(surface: pygame.Surface, color: tuple, left: int, top: int):
    pygame.draw.rect(surface, color, (left + settings.BLOCK_TAB_OFFSET, top, settings.BLOCK_TAB_WIDTH, settings.BLOCK_TAB_HEIGHT))


# The rest of the C: the arm and the foot, in the same colour as the Repeat head so they merge.
def draw_loop_frame(surface: pygame.Surface, position: tuple[int, int], foot_top: int):
    color = settings.BLOCK_COLORS[KINDS[REPEAT]]
    head = block_rect(position)
    foot = pygame.Rect(head.left, foot_top, settings.BLOCK_WIDTH, settings.BLOCK_FOOT_HEIGHT)
    # Arm: INDENT wide, from the middle of the head to the middle of the foot, so there's no gap.
    # It grows on its own: more blocks inside push foot_top down.
    pygame.draw.rect(surface, color, (head.left, head.centery, settings.INDENT, foot.centery - head.centery))
    draw_shape(surface, color, foot)
    draw_tab(surface, color, foot.left, foot.bottom)


def draw_block(surface: pygame.Surface, block: dict, position: tuple[int, int], typing: str | None = None):
    kind = block_kind(block)
    color = settings.BLOCK_COLORS[kind]
    rect = block_rect(position)
    draw_tab(surface, color, rect.left + (settings.INDENT if block["type"] == REPEAT else 0), rect.bottom)
    draw_shape(surface, color, rect)
    font = load_font(settings.BLOCK_FONT_SIZE)
    label = font.render(settings.BLOCK_LABELS[kind], True, settings.BLOCK_TEXT_COLOR)
    surface.blit(label, label.get_rect(midleft=(rect.left + settings.BLOCK_TEXT_PADDING, rect.centery)))
    if typing is None and "count" not in block:
        return
    count = font.render(
        str(block["count"]) if typing is None else typing + "_",
        True,
        settings.BLOCK_TEXT_COLOR if typing is None else settings.BLOCK_TYPING_COLOR,
    )
    surface.blit(count, count.get_rect(midright=(rect.right - settings.BLOCK_TEXT_PADDING, rect.centery)))


def draw_program(
    surface: pygame.Surface,
    program: list,
    origin: tuple[int, int],
    typing_index: int | None = None,
    typing: str | None = None,
):
    tops, feet, _ = program_layout(program)
    # Bottom-up, so each block's tab is drawn on top of the block below it.
    for index in reversed(range(len(program))):
        block = program[index]
        position = (origin[0] + block["depth"] * settings.INDENT, origin[1] + tops[index])
        if index in feet:
            draw_loop_frame(surface, position, origin[1] + feet[index])
        draw_block(surface, block, position, typing if index == typing_index else None)
