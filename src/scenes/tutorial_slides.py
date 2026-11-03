import pygame

from src.core import settings
from src.core.session import OPTIONS, Session
from src.logic import blocks
from src.logic.sim import score_breakdown
from src.scenes.menu_scene import MenuScene
from src.scenes.plan_scene import PlanScene
from src.scenes.play_scene import PlayScene
from src.scenes.preview_scene import PreviewScene
from src.scenes.result_scene import ResultScene

SAMPLE_PROGRAM = [
    {"type": blocks.REPEAT, "count": 3, "depth": 0},
    {"type": blocks.MOVE, "direction": "R", "depth": 1},
    {"type": blocks.MOVE, "direction": "D", "depth": 1},
]


def _screenshot(scene) -> pygame.Surface:
    surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    scene.draw(surface)
    return surface


def _around_tile(map_view, tile: tuple, tiles_wide: int) -> pygame.Rect:
    size = map_view.tile_size * tiles_wide
    area = pygame.Rect(0, 0, size, size)
    area.center = map_view.tile_center(tile)
    return area


def _setup_rows() -> pygame.Rect:
    right = settings.SETUP_RIGHT_ARROW_X + settings.SETUP_ARROW_SIZE
    height = (len(OPTIONS) - 1) * settings.SETUP_ROW_HEIGHT + settings.SETUP_ARROW_SIZE
    return pygame.Rect(settings.SETUP_NAME_X, settings.SETUP_ROW_TOP, right - settings.SETUP_NAME_X, height)


def _result_scores(row_count: int) -> pygame.Rect:
    width = settings.RESULT_VALUE_X - settings.RESULT_NAME_X
    height = (row_count - 1) * settings.RESULT_ROW_HEIGHT + settings.FONT_MEDIUM
    return pygame.Rect(settings.RESULT_NAME_X, settings.RESULT_ROW_TOP, width, height)


def make_slides(game) -> list:
    session = Session()
    session.prepare()
    level = session.level

    menu = MenuScene(game, session)
    menu_shot = _screenshot(menu)
    menu.open_setup()
    setup_shot = _screenshot(menu)

    preview = PreviewScene(game, session)
    preview_shot = _screenshot(preview)
    preview_map = preview.map_view

    plan = PlanScene(game, session)
    plan.update(0)
    overview_shot = _screenshot(plan)
    ghost_area = _around_tile(plan.overview.map_view, level.ghosts[0], 2)
    session.programs[0] = [dict(block) for block in SAMPLE_PROGRAM]
    plan.select(0)
    plan.update(0)
    editor_shot = _screenshot(plan)

    session.parsed_programs = [blocks.parse(program) for program in session.programs]
    play = PlayScene(game, session)
    for _ in range(settings.TUTORIAL_PLAY_TICKS):
        play.sim.step()
    play.board.show_sim(play.sim)
    play.show_status()
    play_shot = _screenshot(play)
    pac_area = _around_tile(play.board.map_view, play.sim.pac_tile, 2)

    finished = session.new_sim([blocks.run(program) for program in session.parsed_programs])
    finished.run()
    result_shot = _screenshot(ResultScene(game, session, finished))
    result_rows = len(score_breakdown(finished, session.seconds_left)) + 1

    return [
        ("Press Play to begin.", menu_shot, pygame.Rect(settings.MENU_PLAY_RECT)),
        ("Pick the maze, AI, ghosts, mode and time.", setup_shot, _setup_rows()),
        ("Press Start.", setup_shot, pygame.Rect(settings.SETUP_START_RECT)),
        ("Study the maze first.", preview_shot, preview_map.rect),
        ("Pac-Man runs to this exit.", preview_shot, _around_tile(preview_map, level.goal, 1)),
        ("Ghosts can't enter the green safe zone.", preview_shot, _around_tile(preview_map, level.goal, 2 * settings.SAFE_RADIUS + 1)),
        ("Press Start planning.", preview_shot, pygame.Rect(settings.PREVIEW_START_RECT)),
        ("Click a ghost to program it.", overview_shot, ghost_area),
        ("Drag blocks from here...", editor_shot, pygame.Rect(settings.PALETTE_RECT)),
        ("...and drop them here. Right-click deletes.", editor_shot, pygame.Rect(settings.PROGRAM_RECT)),
        ("At 0:00 your programs lock.", editor_shot, plan.timer.rect),
        ("Ready early? Press Lock & Run.", editor_shot, pygame.Rect(settings.PLAN_LOCK_RECT)),
        ("Pac-Man uses A* to find the shortest route.", play_shot, pac_area),
        ("Ghosts move first, then Pac-Man steps.", play_shot, play.board.map_view.rect),
        ("Watch the stats. Space pauses.", play_shot, pygame.Rect(settings.PLAY_PANEL_RECT)),
        ("Caught: 1000+. Blocked: 500. Escaped: 0.", result_shot, _result_scores(result_rows)),
    ]
