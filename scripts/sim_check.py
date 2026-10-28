from pathlib import Path

from src.core import settings
from src.logic.grid import parse_level
from src.logic.sim import RUNNING, Sim


class TestBrain:
    def __init__(self, moves: list[str]):
        self.moves: list[str] = list(moves)
        self.optimal_cost: int = len(moves)

    def next_move(self, position: tuple[int, int], pellets: frozenset, ghosts: tuple) -> str | None:
        if self.moves:
            return self.moves.pop(0)
        return None


def main():
    level_path = settings.LEVELS_DIR / "easy.txt"
    text = level_path.read_text()
    level = parse_level(text, "easy")
    moves = [
        "R", "R", "R", "R", "D", "D", "R", "R",
        "U", "U", "R", "R", "R", "R", "R", "R",
        "D", "D", "D", "D", "D", "D", "D", "D",
    ]
    brain = TestBrain(moves)
    sim = Sim(level, brain, pellet_mode=False, ghost_count=len(level.ghosts))
    while sim.status == RUNNING:
        sim.step()
    print(f"Simulation completed at tick {sim.tick} with status: {sim.status}")


if __name__ == "__main__":
    main()
