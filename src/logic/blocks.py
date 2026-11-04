from typing import Iterator

from src.core import settings
from src.logic.sim import idle

MOVE = "MOVE"
WAIT = "WAIT"
REPEAT = "REPEAT"

PALETTE = tuple({"type": MOVE, "direction": direction} for direction in settings.MOVE_ORDER) + (
    {"type": WAIT, "count": settings.WAIT_MIN},
    {"type": REPEAT, "count": settings.REPEAT_MIN},
)

COUNT_RANGES = {
    WAIT: (settings.WAIT_MIN, settings.WAIT_MAX),
    REPEAT: (settings.REPEAT_MIN, settings.REPEAT_MAX),
}


def new_block(template: dict, depth: int) -> dict:
    return {**template, "depth": depth}


def can_add(program: list, limit: int) -> bool:
    return len(program) < limit


# The program is a flat list; "inside a loop" just means a bigger depth.
# Returns (start, stop) of a block, including the whole body for a Repeat.
def block_span(program: list, index: int) -> tuple[int, int]:
    head = program[index]
    stop = index + 1
    if head["type"] == REPEAT:
        # The body is every block right after the Repeat that is deeper than it.
        while stop < len(program) and program[stop]["depth"] > head["depth"]:
            stop += 1
    return index, stop


# Which depths a block dropped at index may have.
def depth_range(program: list, index: int) -> tuple[int, int]:
    above = program[index - 1] if index > 0 else None
    # Deepest: the block above's depth, +1 only if it is a Repeat (True counts as 1).
    highest = above["depth"] + (above["type"] == REPEAT) if above else 0
    # Shallowest: the block below's depth, so a loop body is never cut in half.
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
            levels[depth].append({"type": MOVE, "direction": block["direction"]})
        elif kind == WAIT:
            levels[depth].append({"type": WAIT, "count": _clamp_count(WAIT, block["count"])})
        elif kind == REPEAT:
            node = {"type": REPEAT, "count": _clamp_count(REPEAT, block["count"]), "body": []}
            levels[depth].append(node)
            levels.append(node["body"])
    return root


# A generator: every yield is one action (a direction, or None to stand still).
# The Sim calls next() once per tick, so the program pauses at each yield until the next tick.
def _execute(nodes: list, steps_without_action: list) -> Iterator[str | None]:
    for node in nodes:
        # Safety net: Repeats with nothing inside would never yield, so force a None.
        steps_without_action[0] += 1
        if steps_without_action[0] >= settings.MAX_STEPS_WITHOUT_ACTION:
            steps_without_action[0] = 0
            yield None
        kind = node["type"]
        if kind == MOVE:
            steps_without_action[0] = 0
            yield node["direction"]
        elif kind == WAIT:
            steps_without_action[0] = 0
            # Wait n = n ticks of standing still (ticks, not seconds).
            for _ in range(node["count"]):
                yield None
        elif kind == REPEAT:
            for _ in range(node["count"]):
                # yield from passes on every action of the loop body, count times.
                yield from _execute(node["body"], steps_without_action)


# Runs the program once, then idle() stands the ghost still forever.
def run(tree: list) -> Iterator[str | None]:
    yield from _execute(tree, [0])
    yield from idle()
