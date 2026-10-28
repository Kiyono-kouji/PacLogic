from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
LEVELS_DIR = ASSETS_DIR / "levels"

DEFAULT_FONT = FONTS_DIR / "Jersey10-Regular.ttf"

TITLE = "PacLogic"
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
MAX_DT = 0.05
BG_COLOR = (10, 10, 20)
