import csv

from scripts.levels_for_evaluation import evaluation_levels
from scripts.sample_programs import controllers_for
from src.core import settings
from src.logic.brain import PacManBrain
from src.logic.grid import Level
from src.logic.sim import BLOCKED, CAUGHT, ESCAPED, Sim

RESULTS_FILE = settings.ROOT_DIR / "results" / "catch_rate.csv"
OUTCOMES = (CAUGHT, ESCAPED, BLOCKED)


def run_round(level: Level, difficulty: str, pellet_mode: bool) -> str:
    ghost_count = min(settings.MAX_GHOSTS, len(level.ghosts))
    brain = PacManBrain(level, difficulty, pellet_mode)
    return Sim(level, brain, pellet_mode, ghost_count, controllers_for(difficulty, ghost_count)).run()


def catch_rates() -> list[dict]:
    rows = []
    for difficulty in settings.DIFFICULTIES:
        counts = dict.fromkeys(OUTCOMES, 0)
        for level, mode, pellet_mode in evaluation_levels():
            counts[run_round(level, difficulty, pellet_mode)] += 1
        rounds = sum(counts.values())
        rows.append({"difficulty": difficulty, **counts, "rounds": rounds, "catch_rate": round(counts[CAUGHT] / rounds, 3)})
    return rows


def main():
    rows = catch_rates()
    RESULTS_FILE.parent.mkdir(exist_ok=True)
    with open(RESULTS_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(row)
    print(f"Saved {RESULTS_FILE}")


if __name__ == "__main__":
    main()
