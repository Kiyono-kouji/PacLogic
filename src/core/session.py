from src.core import settings
from src.logic.brain import PacManBrain
from src.logic.grid import Level, load_level
from src.logic.route import route_costs
from src.logic.sim import Sim

OPTIONS = ("level", "difficulty", "ghosts", "mode", "time")
DIFFICULTY_NAMES = tuple(settings.DIFFICULTIES)


class Session:
    def __init__(self):
        self.options = dict(settings.OPTION_DEFAULTS)
        self.loaded_levels: dict = {}
        self.level: Level | None = None
        self.planned_route_costs: list = []
        self.programs: list = []
        self.parsed_programs: list = []
        self.seconds_left: float = 0.0

    def chosen_level(self) -> Level:
        name = settings.LEVEL_FILES[self.options["level"]]
        if name not in self.loaded_levels:
            self.loaded_levels[name] = load_level(settings.LEVELS_DIR / name)
        return self.loaded_levels[name]

    def max_ghosts(self) -> int:
        return len(self.chosen_level().ghosts)

    def option_count(self, option: str) -> int:
        if option == "level":
            return len(settings.LEVEL_FILES)
        if option == "difficulty":
            return len(DIFFICULTY_NAMES)
        if option == "ghosts":
            return self.max_ghosts()
        if option == "mode":
            return len(settings.WIN_MODES)
        return len(settings.PLANNING_TIMES)

    def cycle(self, option: str, delta: int):
        self.options[option] = (self.options[option] + delta) % self.option_count(option)
        self.options["ghosts"] = min(self.options["ghosts"], self.max_ghosts() - 1)

    def option_text(self, option: str) -> str:
        if option == "level":
            return self.chosen_level().name.capitalize()
        if option == "difficulty":
            return self.difficulty
        if option == "ghosts":
            return str(self.ghost_count)
        if option == "mode":
            return settings.WIN_MODES[self.options["mode"]][0]
        minutes, seconds = divmod(self.planning_time, 60)
        return f"{minutes}:{seconds:02d}"

    @property
    def difficulty(self) -> str:
        return DIFFICULTY_NAMES[self.options["difficulty"]]

    @property
    def config(self) -> dict:
        return settings.DIFFICULTIES[self.difficulty]

    @property
    def pellet_mode(self) -> bool:
        return settings.WIN_MODES[self.options["mode"]][1]

    @property
    def pellets_in_play(self) -> frozenset:
        return self.level.pellets if self.pellet_mode else frozenset()

    @property
    def planning_time(self) -> int:
        return settings.PLANNING_TIMES[self.options["time"]]

    @property
    def ghost_count(self) -> int:
        return min(self.options["ghosts"], self.max_ghosts() - 1) + 1

    def prepare(self):
        self.level = self.chosen_level()
        self.clear_programs()
        brain = PacManBrain(self.level, self.difficulty, self.pellet_mode)
        self.planned_route_costs = route_costs(
            self.level, self.level.start, self.level.pellets, self.pellet_mode, brain.planned_route
        )

    def clear_programs(self):
        self.programs = [[] for _ in range(self.ghost_count)]
        self.parsed_programs = [[] for _ in range(self.ghost_count)]
        self.seconds_left = float(self.planning_time)

    def new_sim(self, controllers: list | None = None) -> Sim:
        brain = PacManBrain(self.level, self.difficulty, self.pellet_mode)
        return Sim(self.level, brain, self.pellet_mode, self.ghost_count, controllers)
