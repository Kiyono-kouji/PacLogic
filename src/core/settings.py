from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
LEVELS_DIR = ASSETS_DIR / "levels"

DEFAULT_FONT = FONTS_DIR / "Jersey10-Regular.ttf"

MOVE_ORDER = ("U", "R", "D", "L")
SAFE_RADIUS = 3
MAX_GHOSTS = 4
MAX_PELLETS = 8
