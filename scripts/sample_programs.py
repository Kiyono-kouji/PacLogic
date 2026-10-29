from src.core import settings
from src.core.session import Session
from src.logic import blocks


def _move(direction: str, depth: int = 0) -> dict:
    return {"type": blocks.MOVE, "dir": direction, "depth": depth}


def _wait(count: int, depth: int = 0) -> dict:
    return {"type": blocks.WAIT, "n": count, "depth": depth}


def _repeat(count: int, depth: int = 0) -> dict:
    return {"type": blocks.REPEAT, "n": count, "depth": depth}


EXIT_GUARD = [_repeat(9), _move("R", 1), _move("D", 1)]
CHASER = [_repeat(9), _move("U", 1), _move("L", 1)]
PATROLLER = [_repeat(9), _move("R", 1), _move("R", 1), _move("L", 1), _move("L", 1)]
CORRIDOR_BLOCKER = [_move("L"), _move("L"), _move("U"), _wait(9), _repeat(9), _move("U", 1), _move("D", 1)]

SMART_EXIT_GUARD = [_repeat(9), _move("D", 1), _move("R", 1), _move("D", 1), _repeat(9), _move("R", 1), _wait(1, 1)]
SMART_CHASER = [_repeat(9), _move("L", 1), _move("U", 1), _move("L", 1), _repeat(9), _move("U", 1), _move("L", 1)]
SWEEPER = [
    _repeat(9),
    _repeat(3, 1),
    _move("L", 2),
    _repeat(3, 1),
    _move("U", 2),
    _repeat(3, 1),
    _move("R", 2),
    _repeat(3, 1),
    _move("D", 2),
]
AMBUSHER = [_wait(3), _repeat(9), _move("U", 1), _move("L", 1), _move("U", 1), _wait(1, 1), _move("L", 1)]

SAMPLE_PROGRAMS = {
    "Easy": [EXIT_GUARD, CHASER, PATROLLER, CORRIDOR_BLOCKER],
    "Medium": [SMART_EXIT_GUARD, SMART_CHASER, PATROLLER, CORRIDOR_BLOCKER],
    "Hard": [SMART_EXIT_GUARD, SMART_CHASER, SWEEPER, AMBUSHER],
}


def programs_for(difficulty: str, ghost_count: int) -> list:
    return [[dict(block) for block in program] for program in SAMPLE_PROGRAMS[difficulty][:ghost_count]]


def controllers_for(difficulty: str, ghost_count: int) -> list:
    return [blocks.run(blocks.parse(program), None, index) for index, program in enumerate(programs_for(difficulty, ghost_count))]


def check_programs():
    for difficulty, programs in SAMPLE_PROGRAMS.items():
        limit = settings.DIFFICULTIES[difficulty]["block_limit"]
        assert len(programs) == settings.MAX_GHOSTS, difficulty
        for program in programs:
            assert len(program) <= limit, (difficulty, len(program))
            for index, block in enumerate(program):
                low, high = blocks.depth_range(program[:index], index)
                assert low <= block["depth"] <= high, (difficulty, index)
                if "n" in block:
                    assert blocks.valid_count(block["type"], block["n"]), (difficulty, block)
            assert blocks.parse(program), difficulty


def play_rounds():
    for difficulty_index, difficulty in enumerate(settings.DIFFICULTIES):
        for level_index, level_file in enumerate(settings.LEVEL_FILES):
            session = Session()
            session.options.update(level=level_index, ai=difficulty_index, ghosts=settings.MAX_GHOSTS - 1)
            session.prepare()
            sim = session.new_sim(controllers_for(difficulty, session.ghost_count))
            print(f"{difficulty:<7}{level_file:<12}{sim.run():<9}tick {sim.tick}/{sim.tick_cap}")


if __name__ == "__main__":
    check_programs()
    play_rounds()
