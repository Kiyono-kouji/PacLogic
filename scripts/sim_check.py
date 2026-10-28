from src.core import settings
from src.logic.grid import parse_level
from src.logic.sim import (
    BLOCKED,
    CAUGHT,
    ESCAPED,
    Sim,
    score_breakdown,
    total_score,
)


class TestBrain:
    def __init__(self, moves: list[str]):
        self.moves: list[str] = list(moves)
        self.optimal_cost: int = len(moves)

    def next_move(
        self, position: tuple[int, int], pellets: frozenset, ghosts: tuple
    ) -> str | None:
        if self.moves:
            return self.moves.pop(0)
        return None


def ghost_controller(moves: list[str]):
    for move in moves:
        yield move
    while True:
        yield None


def check_corridor_same_tile():
    text = (settings.LEVELS_DIR / "easy.txt").read_text()
    level = parse_level(text, "easy")
    brain = TestBrain(["R"])
    sim = Sim(level, brain, False, 1, [ghost_controller([])])
    sim.ghosts[0] = (level.start[0] + 1, level.start[1])
    sim.step()
    assert sim.status == CAUGHT
    assert sim.is_caught()


def check_corridor_tile_swap():
    text = (settings.LEVELS_DIR / "easy.txt").read_text()
    level = parse_level(text, "easy")
    brain = TestBrain(["R"])
    sim = Sim(level, brain, False, 1, [ghost_controller(["L"])])
    sim.ghosts[0] = (level.start[0] + 1, level.start[1])
    sim.step()
    assert sim.status == CAUGHT
    assert sim.is_caught()


def check_headless_run():
    text = (settings.LEVELS_DIR / "easy.txt").read_text()
    level = parse_level(text, "easy")
    moves = [
        "R", "R", "R", "R", "D", "D", "R", "R",
        "U", "U", "R", "R", "R", "R", "R", "R",
        "D", "D", "D", "D", "D", "D", "D", "D",
    ]
    brain = TestBrain(moves)
    sim = Sim(level, brain, False, len(level.ghosts))
    outcome = sim.run()
    assert outcome == ESCAPED
    assert sim.status == ESCAPED


def check_scoring():
    text = (settings.LEVELS_DIR / "easy.txt").read_text()
    level = parse_level(text, "easy")
    brain = TestBrain(["R"])
    sim = Sim(level, brain, False, 1)

    sim.status = CAUGHT
    sim.tick = 10
    sim.tick_cap = 50
    caught_breakdown = score_breakdown(sim, 15.0)
    assert total_score(caught_breakdown) == 1000 + 10 * 15 + 5 * 40

    sim.status = BLOCKED
    blocked_breakdown = score_breakdown(sim, 0.0)
    assert total_score(blocked_breakdown) == 500

    sim.status = ESCAPED
    escaped_breakdown = score_breakdown(sim, 0.0)
    assert total_score(escaped_breakdown) == 0


def main():
    check_corridor_same_tile()
    check_corridor_tile_swap()
    check_headless_run()
    check_scoring()
    print("All checks including scoring passed successfully.")


if __name__ == "__main__":
    main()
