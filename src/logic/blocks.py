from typing import Iterator

from src.core import settings
from src.logic.sim import Sim, idle

MOVE = "MOVE"
WAIT = "WAIT"
REPEAT = "REPEAT"

PALETTE = tuple({"type": MOVE, "dir": direction} for direction in settings.MOVE_ORDER) + (
    {"type": WAIT, "n": settings.WAIT_MIN},
    {"type": REPEAT, "n": settings.REPEAT_MIN},
)

COUNT_RANGES = {
    WAIT: (settings.WAIT_MIN, settings.WAIT_MAX),
    REPEAT: (settings.REPEAT_MIN, settings.REPEAT_MAX),
}


def new_block(template: dict, depth: int) -> dict:
    return {**template, "depth": depth}


def can_add(program: list, limit: int) -> bool:
    return len(program) < limit


def block_span(program: list, index: int) -> tuple[int, int]:
    head = program[index]
    stop = index + 1
    if head["type"] == REPEAT:
        while stop < len(program) and program[stop]["depth"] > head["depth"]:
            stop += 1
    return index, stop


def depth_range(program: list, index: int) -> tuple[int, int]:
    above = program[index - 1] if index > 0 else None
    highest = above["depth"] + (above["type"] == REPEAT) if above else 0
    lowest = program[index]["depth"] if index < len(program) else 0
    return min(lowest, highest), highest


def valid_count(kind: str, value: int) -> bool:
    low, high = COUNT_RANGES[kind]
    return low <= value <= high


def _clamp_count(kind: str, value: int) -> int:
    low, high = COUNT_RANGES[kind]
    return max(low, min(high, int(value)))


def parse(program: list) -> list:
    root = []
    levels = [root]
    for block in program:
        depth = max(0, min(block["depth"], len(levels) - 1))
        del levels[depth + 1:]
        kind = block["type"]
        if kind == MOVE:
            levels[depth].append({"type": MOVE, "dir": block["dir"]})
        elif kind == WAIT:
            levels[depth].append({"type": WAIT, "n": _clamp_count(WAIT, block["n"])})
        elif kind == REPEAT:
            node = {"type": REPEAT, "n": _clamp_count(REPEAT, block["n"]), "body": []}
            levels[depth].append(node)
            levels.append(node["body"])
    return root


def _execute(nodes: list, ops: list) -> Iterator[str | None]:
    for node in nodes:
        ops[0] += 1
        if ops[0] >= settings.OP_CAP:
            ops[0] = 0
            yield None
        kind = node["type"]
        if kind == MOVE:
            ops[0] = 0
            yield node["dir"]
        elif kind == WAIT:
            ops[0] = 0
            for _ in range(node["n"]):
                yield None
        elif kind == REPEAT:
            for _ in range(node["n"]):
                yield from _execute(node["body"], ops)


def run(tree: list, sim: Sim | None, ghost_index: int) -> Iterator[str | None]:
    yield from _execute(tree, [0])
    yield from idle(sim, ghost_index)
