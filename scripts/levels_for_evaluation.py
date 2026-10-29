from src.core import settings
from src.logic.grid import Level, load_level


def evaluation_levels() -> list[tuple[Level, str, bool]]:
    levels = [load_level(settings.LEVELS_DIR / name) for name in settings.LEVEL_FILES]
    return [(level, mode, pellet_mode) for level in levels for mode, pellet_mode in settings.WIN_MODES]


def main():
    for level, mode, pellet_mode in evaluation_levels():
        print(f"{level.name:<8} {mode:<8} {len(level.ghosts)} ghosts, {len(level.pellets)} pellets")


if __name__ == "__main__":
    main()
