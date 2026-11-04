from dataclasses import replace

import pygame

from src.core import settings
from src.core.resource_loader import load_font
from src.logic.grid import Level
from src.logic.route import route_costs
from src.logic.search import plan
from src.ui.menu_shapes import approach, draw_lines, outlined_text, shift_points, slanted_box, wrap_text
from src.ui.tutorial_board import Stamp, TutorialBoard, pac_man_sprite
from src.ui.tutorial_runner import SimRunner

STAGE_AREA = (0, 0, settings.TUTORIAL_STAGE_RECT[2], settings.TUTORIAL_STAGE_RECT[3])

ROUND_CARDS = (
    ("1", "SET UP", "Choose a level or a random maze, the AI, how many ghosts, Exit or Pellets mode, and the planning time."),
    ("2", "STUDY", "Look over the maze first. Find the exit, the green safe zone and where your ghosts start."),
    ("3", "PLAN", "Click a ghost and drag blocks into its program. At 0:00 the programs lock. Done early? Press Lock & Run."),
    ("4", "RUN", "The programs run on their own. Every tick the ghosts move first, then Pac-Man takes one step. Space pauses."),
    ("5", "SCORE", "Catch him for big points. If he escapes you get nothing. Lesson 6 has the numbers."),
)

SCORE_CARDS = (
    (
        f"{settings.SCORE['caught']}+",
        "CAUGHT",
        f"{settings.SCORE['caught']} points, plus {settings.SCORE['time_factor']} for every second of planning time "
        f"you didn't use, plus {settings.SCORE['ticks_factor']} for every tick left before the cap.",
    ),
    (
        str(settings.SCORE["blocked"]),
        "BLOCKED",
        f"{settings.SCORE['blocked']} points. Pac-Man couldn't reach the exit before the tick cap ran out.",
    ),
    (
        str(settings.SCORE["escaped"]),
        "ESCAPED",
        "No points. Pac-Man reached the exit. On Hard he even plans a new route around your ghosts every tick.",
    ),
)


class Lesson:
    title = ""
    text = ""
    hint = ""
    resettable = False

    def __init__(self):
        self.mouse: tuple | None = None

    def reset(self):
        pass

    def click(self, position: tuple):
        pass

    def handle_event(self, event: pygame.event.Event, position: tuple | None):
        if event.type == pygame.MOUSEMOTION:
            self.mouse = position
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and position is not None:
            self.click(position)

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface):
        raise NotImplementedError


class CardsLesson(Lesson):
    def __init__(self, title: str, text: str, hint: str, cards: tuple):
        super().__init__()
        self.title = title
        self.text = text
        self.hint = hint
        self.cards = cards
        self.selected = 0
        self.lifts = [0.0] * len(cards)
        self.detail_elapsed = 0.0

    def reset(self):
        self.selected = 0
        self.detail_elapsed = 0.0

    def card_rect(self, index: int) -> pygame.Rect:
        count = len(self.cards)
        margin = settings.TUTORIAL_CARD_MARGIN
        gap = settings.TUTORIAL_CARD_GAP
        width = (STAGE_AREA[2] - 2 * margin - (count - 1) * gap) // count
        return pygame.Rect(margin + index * (width + gap), settings.TUTORIAL_CARD_TOP, width, settings.TUTORIAL_CARD_HEIGHT)

    def card_at(self, position: tuple | None) -> int | None:
        if position is None:
            return None
        for index in range(len(self.cards)):
            if self.card_rect(index).collidepoint(position):
                return index
        return None

    def click(self, position: tuple):
        index = self.card_at(position)
        if index is not None and index != self.selected:
            self.selected = index
            self.detail_elapsed = 0.0

    def update(self, dt: float):
        self.detail_elapsed += dt
        hovered = self.card_at(self.mouse)
        for index in range(len(self.cards)):
            target = 1.0 if index == self.selected else 0.5 if index == hovered else 0.0
            self.lifts[index] = approach(self.lifts[index], target, settings.TUTORIAL_CARD_FOLLOW, dt)

    def draw(self, surface: pygame.Surface):
        hovered = self.card_at(self.mouse)
        for index, (big, title, _) in enumerate(self.cards):
            rect = self.card_rect(index).move(0, -round(self.lifts[index] * settings.TUTORIAL_CARD_LIFT))
            box = slanted_box(rect, settings.TUTORIAL_CARD_SKEW)
            if index == self.selected:
                pygame.draw.polygon(surface, settings.MENU_BLUE, shift_points(box, settings.TUTORIAL_TAG_SHADOW))
                pygame.draw.polygon(surface, settings.MENU_WHITE, box)
                ink = settings.MENU_BLACK
            else:
                pygame.draw.polygon(surface, settings.MENU_WHITE, slanted_box(rect.inflate(2 * settings.TUTORIAL_CARD_BORDER, 2 * settings.TUTORIAL_CARD_BORDER), settings.TUTORIAL_CARD_SKEW))
                pygame.draw.polygon(surface, settings.MENU_BLUE if index == hovered else settings.MENU_BLACK, box)
                ink = settings.MENU_WHITE
            big_text = load_font(settings.TUTORIAL_CARD_BIG_SIZE).render(big, True, settings.MENU_BLUE if index == self.selected else ink)
            title_text = load_font(settings.TUTORIAL_CARD_TITLE_SIZE).render(title, True, ink)
            surface.blit(big_text, big_text.get_rect(center=(rect.centerx, rect.top + rect.height * settings.TUTORIAL_CARD_BIG_Y)))
            surface.blit(title_text, title_text.get_rect(center=(rect.centerx, rect.top + rect.height * settings.TUTORIAL_CARD_TITLE_Y)))
        self.draw_detail(surface)

    def draw_detail(self, surface: pygame.Surface):
        rect = pygame.Rect(settings.TUTORIAL_DETAIL_RECT)
        box = slanted_box(rect, settings.TUTORIAL_CARD_SKEW)
        pygame.draw.polygon(surface, settings.MENU_BLUE, box)
        font = load_font(settings.TUTORIAL_DETAIL_SIZE)
        padding = settings.TUTORIAL_DETAIL_PADDING
        lines = wrap_text(self.cards[self.selected][2], font, rect.width - 2 * padding - settings.TUTORIAL_CARD_SKEW)
        characters = int(self.detail_elapsed * settings.TUTORIAL_TYPE_SPEED)
        draw_lines(surface, lines, font, settings.MENU_WHITE, (rect.left + padding + settings.TUTORIAL_CARD_SKEW, rect.top + padding), settings.TUTORIAL_DETAIL_LINE, characters)


class ExitLesson(Lesson):
    title = "THE TARGET"
    text = "Pac-Man is the AI. He searches for the shortest route to the exit and walks it one tile per tick. You play the ghosts."
    hint = "Click any floor tile to move the exit and watch him plan a new route."
    resettable = True

    def __init__(self, level: Level):
        super().__init__()
        self.base = replace(level, ghosts=())
        self.board = TutorialBoard(STAGE_AREA)
        self.runner = SimRunner(loop=True)
        self.reset()

    def reset(self):
        self.use(self.base)

    def use(self, level: Level):
        self.level = level
        self.board.fit(level)
        self.runner.start(level, list, running=True)

    def click(self, position: tuple):
        tile = self.board.tile_at(position)
        if tile is None or tile in self.level.walls or tile == self.level.start or tile == self.level.goal:
            return
        self.use(replace(self.level, goal=tile))

    def update(self, dt: float):
        self.runner.update(dt)

    def draw(self, surface: pygame.Surface):
        self.board.draw(surface)
        hovered = self.board.tile_at(self.mouse)
        if hovered is not None and hovered not in self.level.walls:
            self.board.draw_hover(surface, hovered, settings.MENU_WHITE)
        self.runner.draw(surface, self.board, show_route=True)


class RouteLesson(Lesson):
    title = "A* SEARCH"
    text = "He finds that route with A* search. g(n) counts the steps he has walked. h(n) guesses the steps left. A* always tries the lowest g + h first."
    hint = "Click floor to build a wall, click a wall to remove it. Hover the route to read g and h."
    resettable = True

    def __init__(self, level: Level):
        super().__init__()
        self.base = replace(level, ghosts=())
        self.board = TutorialBoard(STAGE_AREA)
        self.stamp = Stamp()
        self.reset()

    def reset(self):
        self.use(self.base)

    def use(self, level: Level):
        self.level = level
        self.board.fit(level)
        result = plan(level, level.start, frozenset(), False)
        self.costs = [] if result.cost is None else route_costs(level, level.start, (), False, result.path)
        if result.cost is None:
            self.stamp.show("NO ROUTE!", settings.TUTORIAL_STAMP_DARK)

    def editable(self, tile: tuple | None) -> bool:
        if tile is None or tile in (self.level.start, self.level.goal):
            return False
        x, y = tile
        return 0 < x < self.level.width - 1 and 0 < y < self.level.height - 1

    def click(self, position: tuple):
        tile = self.board.tile_at(position)
        if not self.editable(tile):
            return
        walls = self.level.walls - {tile} if tile in self.level.walls else self.level.walls | {tile}
        self.use(replace(self.level, walls=walls))

    def update(self, dt: float):
        self.stamp.update(dt)

    def readout(self) -> str:
        hovered = self.board.tile_at(self.mouse)
        for tile, g, h in self.costs:
            if tile == hovered:
                return f"g = {g}   h = {h}   f = g + h = {g + h}"
        if not self.costs:
            return "No route: the exit is walled off"
        return f"Route length: {len(self.costs)} steps"

    def draw(self, surface: pygame.Surface):
        self.board.draw(surface)
        self.board.draw_route(surface, [tile for tile, _, _ in self.costs])
        self.board.draw_costs(surface, self.costs)
        hovered = self.board.tile_at(self.mouse)
        if self.editable(hovered):
            self.board.draw_hover(surface, hovered, settings.MENU_WHITE)
        self.board.draw_sprite(surface, pac_man_sprite("R"), self.level.start)
        text = outlined_text(self.readout(), settings.TUTORIAL_READOUT_SIZE, settings.MENU_WHITE, settings.MENU_BLACK, settings.TUTORIAL_TITLE_OUTLINE)
        surface.blit(text, settings.TUTORIAL_READOUT_POSITION)
        self.stamp.draw(surface, self.board.stamp_center())


class SafeZoneLesson(Lesson):
    title = "SAFE ZONE"
    text = (
        f"Every tile within {settings.SAFE_RADIUS} steps of the exit is the green safe zone. "
        "Ghosts can never enter it, so catch him before he gets there."
    )
    hint = "Click a tile to place the ghost. Put it on his route to catch him."
    resettable = True

    def __init__(self, level: Level):
        super().__init__()
        self.base = level
        self.board = TutorialBoard(STAGE_AREA)
        self.board.fit(level)
        self.runner = SimRunner(loop=True)
        self.reset()

    def reset(self):
        self.use(self.base.ghosts[0])

    def use(self, ghost: tuple):
        self.ghost = ghost
        self.runner.start(replace(self.base, ghosts=(ghost,)), lambda: [None], running=True)

    def allowed(self, tile: tuple) -> bool:
        return tile not in self.base.walls and tile not in self.base.safe_zone and tile != self.base.start

    def click(self, position: tuple):
        tile = self.board.tile_at(position)
        if tile is None or tile in self.base.walls:
            return
        if not self.allowed(tile):
            self.runner.stamp.show("NO ENTRY!", settings.TUTORIAL_STAMP_LIGHT)
            return
        self.use(tile)

    def update(self, dt: float):
        self.runner.update(dt)

    def draw(self, surface: pygame.Surface):
        self.board.draw(surface)
        hovered = self.board.tile_at(self.mouse)
        if hovered is not None and hovered not in self.base.walls:
            self.board.draw_hover(surface, hovered, settings.MENU_WHITE if self.allowed(hovered) else settings.WARNING_COLOR)
        self.runner.draw(surface, self.board, show_route=True)
