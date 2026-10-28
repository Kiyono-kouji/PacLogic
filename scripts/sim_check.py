from src.core import settings
from src.logic.grid import parse_level
from src.logic.sim import CAUGHT, ESCAPED, Sim


class TestBrain:
    def __init__(self, moves: list[str]):
        self.moves: list[str] = list(moves)
        self.optimal_cost: int = len(moves)

    def next_move(self, position: tuple[int, int], pellets: frozenset, ghosts: tuple) -> str | None:
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


def main():
    check_corridor_same_tile()
    check_corridor_tile_swap()
    check_headless_run()
    print("All K04 checks passed successfully: same-tile catch, tile-swap catch, and headless run.")


if __name__ == "__main__":
    main()
