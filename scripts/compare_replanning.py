import csv

from scripts.levels_for_evaluation import evaluation_levels
from scripts.sample_programs import controllers_for
from src.core import settings
from src.logic.brain import PacManBrain
from src.logic.grid import Level
from src.logic.sim import BLOCKED, CAUGHT, ESCAPED, Sim

RESULTS_FILE = settings.ROOT_DIR / "results" / "replanning.csv"
DIFFICULTY = "Hard"
OUTCOMES = (CAUGHT, ESCAPED, BLOCKED)


def run_round(level: Level, pellet_mode: bool, ghost_count: int, replan: bool) -> Sim:
    brain = PacManBrain(level, DIFFICULTY, pellet_mode)
    brain.config = {**brain.config, "replan": replan}
    sim = Sim(level, brain, pellet_mode, ghost_count, controllers_for(DIFFICULTY, ghost_count))
    sim.run()
    return sim


def summarize(replan: bool, level_name: str, mode: str, sims: list) -> dict:
    counts = {outcome: sum(sim.status == outcome for sim in sims) for outcome in OUTCOMES}
    rounds = len(sims)
    return {
        "replanning": "on" if replan else "off",
        "level": level_name,
        "mode": mode,
        **counts,
        "rounds": rounds,
        "catch_rate": round(counts[CAUGHT] / rounds, 3),
        "avg_ticks": round(sum(sim.tick for sim in sims) / rounds, 1),
        "avg_nodes_expanded": round(sum(sim.brain.nodes_expanded for sim in sims) / rounds, 1),
    }


def comparison_rows() -> list[dict]:
    rows = []
    for replan in (False, True):
        every_round = []
        for level, mode, pellet_mode in evaluation_levels():
            sims = [
                run_round(level, pellet_mode, ghost_count, replan)
                for ghost_count in range(1, min(settings.MAX_GHOSTS, len(level.ghosts)) + 1)
            ]
            every_round += sims
            rows.append(summarize(replan, level.name, mode, sims))
        rows.append(summarize(replan, "all", "all", every_round))
    return rows


def print_table(rows: list[dict]):
    print(f"{'Replan':<8}{'Level':<8}{'Mode':<9}{'Caught':>7}{'Escaped':>8}{'Blocked':>8}{'Catch rate':>11}{'Avg ticks':>10}{'Avg nodes':>11}")
    for row in rows:
        print(
            f"{row['replanning']:<8}{row['level']:<8}{row['mode']:<9}{row[CAUGHT]:>7}{row[ESCAPED]:>8}{row[BLOCKED]:>8}"
            f"{row['catch_rate']:>11.3f}{row['avg_ticks']:>10.1f}{row['avg_nodes_expanded']:>11.1f}"
        )


def main():
    rows = comparison_rows()
    RESULTS_FILE.parent.mkdir(exist_ok=True)
    with open(RESULTS_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{DIFFICULTY} rounds against the sample ghost programs, 1 to {settings.MAX_GHOSTS} ghosts per level and mode\n")
    print_table(rows)
    print(f"\nSaved {RESULTS_FILE}")


if __name__ == "__main__":
    main()
