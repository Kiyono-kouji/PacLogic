import pygame

from src.core import settings
from src.core.resource_loader import load_font
from src.logic.blocks import MOVE, REPEAT, WAIT

START = "START"
MOVE_KINDS = {"U": "move-up", "R": "move-right", "D": "move-down", "L": "move-left"}
KINDS = {WAIT: "wait", REPEAT: "repeat", START: "when-start"}


def block_kind(block: dict) -> str:
    if block["type"] == MOVE:
        return MOVE_KINDS[block["dir"]]
    return KINDS[block["type"]]


def block_rect(position: tuple[int, int]) -> pygame.Rect:
    return pygame.Rect(position, (settings.BLOCK_WIDTH, settings.BLOCK_HEIGHT))


def draw_block(surface: pygame.Surface, block: dict, position: tuple[int, int], typing: str | None = None):
    kind = block_kind(block)
    color = settings.BLOCK_COLORS[kind]
    rect = block_rect(position)
    tab = pygame.Rect(
        rect.left + settings.BLOCK_TAB_OFFSET,
        rect.bottom,
        settings.BLOCK_TAB_WIDTH,
        settings.BLOCK_TAB_HEIGHT,
    )
    pygame.draw.rect(surface, color, tab)
    pygame.draw.rect(surface, color, rect, border_radius=settings.BLOCK_RADIUS)
    font = load_font(settings.BLOCK_FONT_SIZE)
    label = font.render(settings.BLOCK_LABELS[kind], True, settings.BLOCK_TEXT_COLOR)
    surface.blit(label, label.get_rect(midleft=(rect.left + settings.BLOCK_TEXT_PADDING, rect.centery)))
    if typing is None and "n" not in block:
        return
    count = font.render(
        str(block["n"]) if typing is None else typing,
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
    for index in reversed(range(len(program))):
        block = program[index]
        position = (origin[0] + block["depth"] * settings.INDENT, origin[1] + index * settings.BLOCK_HEIGHT)
        draw_block(surface, block, position, typing if index == typing_index else None)
