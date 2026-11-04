import pygame

from src.core import settings
from src.core.resource_loader import load_font
from src.logic.grid import load_level
from src.ui.component import Component
from src.ui.effects import ease_out_back
from src.ui.menu_shapes import draw_lines, outlined_text, progress, shift_points, slanted_box, tag_surface, wrap_text
from src.ui.slash_menu import CONFIRM_KEYS
from src.ui.tutorial_lessons import (
    ROUND_CARDS,
    SCORE_CARDS,
    CardsLesson,
    ExitLesson,
    RouteLesson,
    SafeZoneLesson,
)
from src.ui.tutorial_program_lesson import ProgramLesson

PREVIOUS_KEYS = (pygame.K_LEFT, pygame.K_a)
NEXT_KEYS = (pygame.K_RIGHT, pygame.K_d)


class TutorialPanel(Component):
    def __init__(self):
        super().__init__()
        self.visible = False
        self.lessons: list = []
        self.index = 0
        self.elapsed = 0.0
        self.swap_elapsed = 0.0
        self.mouse: tuple | None = None
        self.stage_rect = pygame.Rect(settings.TUTORIAL_STAGE_RECT)
        self.stage = pygame.Surface(self.stage_rect.size)
        self.dim_layer = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.dim_layer.fill(settings.TUTORIAL_DIM_COLOR)
        self.header = pygame.transform.rotate(
            tag_surface(
                settings.TUTORIAL_HEADER_TEXT,
                settings.TUTORIAL_HEADER_SIZE,
                (settings.MENU_BLUE, settings.MENU_WHITE, settings.MENU_BLACK),
                settings.TUTORIAL_HEADER_PADDING,
                settings.TUTORIAL_TAG_SKEW,
                settings.TUTORIAL_TAG_SHADOW,
            ),
            settings.TUTORIAL_HEADER_TILT,
        )
        self.speaker = pygame.transform.rotate(
            tag_surface(
                settings.TUTORIAL_SPEAKER_TEXT,
                settings.TUTORIAL_SPEAKER_SIZE,
                (settings.MENU_WHITE, settings.MENU_BLACK, settings.MENU_BLUE),
                settings.TUTORIAL_HEADER_PADDING,
                settings.TUTORIAL_TAG_SKEW,
                settings.TUTORIAL_TAG_SHADOW,
            ),
            settings.TUTORIAL_SPEAKER_TILT,
        )
        self.hint_tag = tag_surface(
            settings.TUTORIAL_HINT_TAG,
            settings.TUTORIAL_HINT_TAG_SIZE,
            (settings.MENU_BLACK, settings.MENU_WHITE, settings.MENU_WHITE),
            settings.TUTORIAL_HEADER_PADDING,
            settings.TUTORIAL_TAG_SKEW,
            (0, 0),
        )

    def build_lessons(self) -> list:
        level = load_level(settings.LEVELS_DIR / settings.TUTORIAL_LEVEL_FILE)
        return [
            CardsLesson(
                "THE ROUND",
                "You never steer the ghosts. You write their orders before the round, then watch them hunt Pac-Man on their own.",
                "Click each card to see what happens in that part of a round.",
                ROUND_CARDS,
            ),
            ExitLesson(level),
            RouteLesson(level),
            SafeZoneLesson(level),
            ProgramLesson(level),
            CardsLesson(
                "SCORING",
                "How the round ends decides your score. A ghost on Pac-Man's tile is a catch. If the tick cap runs out first, he is blocked.",
                "Click an outcome to see how its points are counted.",
                SCORE_CARDS,
            ),
        ]

    def open(self):
        if not self.lessons:
            self.lessons = self.build_lessons()
        self.visible = True
        self.elapsed = 0.0
        self.show(0)

    def close(self):
        self.visible = False

    def lesson(self):
        return self.lessons[self.index]

    def show(self, index: int):
        self.index = index
        self.swap_elapsed = 0.0
        self.lesson().reset()

    def previous(self):
        if self.index > 0:
            self.show(self.index - 1)

    def next(self):
        if self.index == len(self.lessons) - 1:
            self.close()
        else:
            self.show(self.index + 1)

    def typed_characters(self) -> int:
        return int(self.swap_elapsed * settings.TUTORIAL_TYPE_SPEED)

    def typing(self) -> bool:
        return self.typed_characters() < len(self.lesson().text)

    def finish_typing(self):
        self.swap_elapsed = max(self.swap_elapsed, len(self.lesson().text) / settings.TUTORIAL_TYPE_SPEED)

    def tab_rect(self, index: int) -> pygame.Rect:
        width, height = settings.TUTORIAL_TAB_SIZE
        left = settings.TUTORIAL_TAB_LEFT + index * (width + settings.TUTORIAL_TAB_GAP)
        return pygame.Rect(left, settings.TUTORIAL_NAV_TOP, width, height)

    def local(self, position: tuple) -> tuple | None:
        if not self.stage_rect.collidepoint(position):
            return None
        return position[0] - self.stage_rect.left, position[1] - self.stage_rect.top

    def update(self, dt: float):
        if not self.visible:
            return
        self.elapsed += dt
        self.swap_elapsed += dt
        self.lesson().update(dt)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN:
            self.handle_key(event.key)
        elif event.type == pygame.MOUSEMOTION:
            self.mouse = event.pos
            self.lesson().handle_event(event, self.local(event.pos))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.click(event.pos)
        return True

    def handle_key(self, key: int):
        if key == pygame.K_ESCAPE:
            self.close()
        elif key in PREVIOUS_KEYS:
            self.previous()
        elif key in NEXT_KEYS:
            self.next()
        elif key in CONFIRM_KEYS:
            if self.typing():
                self.finish_typing()
            else:
                self.next()

    def click(self, position: tuple):
        if pygame.Rect(settings.TUTORIAL_CLOSE_RECT).collidepoint(position):
            self.close()
        elif self.index > 0 and pygame.Rect(settings.TUTORIAL_PREVIOUS_RECT).collidepoint(position):
            self.previous()
        elif pygame.Rect(settings.TUTORIAL_NEXT_RECT).collidepoint(position):
            self.next()
        elif self.lesson().resettable and pygame.Rect(settings.TUTORIAL_RESET_RECT).collidepoint(position):
            self.lesson().reset()
        elif pygame.Rect(settings.TUTORIAL_DIALOG_RECT).collidepoint(position):
            self.finish_typing()
        else:
            for index in range(len(self.lessons)):
                if self.tab_rect(index).collidepoint(position):
                    self.show(index)
                    return
            local = self.local(position)
            if local is not None:
                self.lesson().handle_event(
                    pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=local, button=1),
                    local,
                )

    def slide(self) -> float:
        linear = progress(self.swap_elapsed, 0.0, settings.TUTORIAL_SWAP_SECONDS)
        return (1 - ease_out_back(linear, settings.MENU_OVERSHOOT)) * settings.TUTORIAL_SWAP_SLIDE

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return
        self.dim_layer.set_alpha(round(255 * progress(self.elapsed, 0.0, settings.TUTORIAL_OPEN_SECONDS)))
        surface.blit(self.dim_layer, (0, 0))
        surface.blit(self.header, settings.TUTORIAL_HEADER_POSITION)
        self.draw_button(surface, settings.TUTORIAL_CLOSE_RECT, "ESC  X", False)
        slide = self.slide()
        self.draw_stage(surface, slide)
        self.draw_title(surface, slide)
        self.draw_dialog(surface, slide)
        self.draw_hint(surface, slide)
        self.draw_nav(surface)

    def draw_stage(self, surface: pygame.Surface, slide: float):
        rect = self.stage_rect.move(-slide, 0)
        border = rect.inflate(2 * settings.TUTORIAL_STAGE_BORDER, 2 * settings.TUTORIAL_STAGE_BORDER)
        pygame.draw.rect(surface, settings.MENU_BLUE, border.move(settings.TUTORIAL_STAGE_SHADOW))
        pygame.draw.rect(surface, settings.MENU_WHITE, border)
        self.stage.fill(settings.MENU_BLACK)
        self.lesson().draw(self.stage)
        surface.blit(self.stage, rect)
        if self.lesson().resettable:
            self.draw_button(surface, pygame.Rect(settings.TUTORIAL_RESET_RECT).move(-slide, 0), "RESET", False)

    def draw_title(self, surface: pygame.Surface, slide: float):
        left, top = settings.TUTORIAL_TITLE_POSITION
        left += slide
        number = tag_surface(
            f"{self.index + 1:02d}",
            settings.TUTORIAL_NUMBER_SIZE,
            (settings.MENU_WHITE, settings.MENU_BLACK, settings.MENU_BLUE),
            settings.TUTORIAL_HEADER_PADDING,
            settings.TUTORIAL_TAG_SKEW,
            settings.TUTORIAL_TAG_SHADOW,
        )
        number = pygame.transform.rotate(number, settings.TUTORIAL_HEADER_TILT)
        surface.blit(number, (left, top))
        title = outlined_text(self.lesson().title, settings.TUTORIAL_TITLE_SIZE, settings.MENU_WHITE, settings.MENU_BLUE, settings.TUTORIAL_TITLE_OUTLINE)
        surface.blit(title, title.get_rect(midleft=(left + number.get_width() + settings.TUTORIAL_TITLE_GAP, top + number.get_height() // 2)))

    def draw_dialog(self, surface: pygame.Surface, slide: float):
        rect = pygame.Rect(settings.TUTORIAL_DIALOG_RECT).move(slide, 0)
        skew = settings.TUTORIAL_DIALOG_SKEW
        border = slanted_box(rect.inflate(2 * settings.TUTORIAL_DIALOG_BORDER, 2 * settings.TUTORIAL_DIALOG_BORDER), skew)
        pygame.draw.polygon(surface, settings.MENU_BLUE, shift_points(border, settings.TUTORIAL_DIALOG_SHADOW))
        pygame.draw.polygon(surface, settings.MENU_WHITE, border)
        pygame.draw.polygon(surface, settings.MENU_BLACK, slanted_box(rect, skew))
        surface.blit(self.speaker, (rect.left + settings.TUTORIAL_SPEAKER_OFFSET[0], rect.top + settings.TUTORIAL_SPEAKER_OFFSET[1]))
        font = load_font(settings.TUTORIAL_TEXT_SIZE)
        padding = settings.TUTORIAL_DIALOG_PADDING
        lines = wrap_text(self.lesson().text, font, rect.width - 2 * padding - skew)
        top = rect.top + settings.TUTORIAL_DIALOG_TEXT_TOP
        draw_lines(surface, lines, font, settings.MENU_WHITE, (rect.left + padding, top), settings.TUTORIAL_TEXT_LINE, self.typed_characters())

    def draw_hint(self, surface: pygame.Surface, slide: float):
        rect = pygame.Rect(settings.TUTORIAL_HINT_RECT).move(slide, 0)
        skew = settings.TUTORIAL_DIALOG_SKEW
        pygame.draw.polygon(surface, settings.MENU_BLACK, shift_points(slanted_box(rect, skew), settings.TUTORIAL_TAG_SHADOW))
        pygame.draw.polygon(surface, settings.MENU_BLUE, slanted_box(rect, skew))
        surface.blit(self.hint_tag, (rect.left + settings.TUTORIAL_HINT_TAG_OFFSET[0], rect.top + settings.TUTORIAL_HINT_TAG_OFFSET[1]))
        font = load_font(settings.TUTORIAL_HINT_SIZE)
        padding = settings.TUTORIAL_DIALOG_PADDING
        lines = wrap_text(self.lesson().hint, font, rect.width - 2 * padding - skew)
        draw_lines(surface, lines, font, settings.MENU_WHITE, (rect.left + padding, rect.top + settings.TUTORIAL_HINT_TOP), settings.TUTORIAL_HINT_LINE)

    def draw_nav(self, surface: pygame.Surface):
        for index in range(len(self.lessons)):
            self.draw_button(surface, self.tab_rect(index), str(index + 1), index == self.index)
        if self.index > 0:
            self.draw_button(surface, settings.TUTORIAL_PREVIOUS_RECT, "< BACK", False)
        last = self.index == len(self.lessons) - 1
        self.draw_button(surface, settings.TUTORIAL_NEXT_RECT, "DONE" if last else "NEXT >", True)

    def draw_button(self, surface: pygame.Surface, rect: tuple, label: str, chosen: bool):
        rect = pygame.Rect(rect)
        hovered = self.mouse is not None and rect.collidepoint(self.mouse)
        box = slanted_box(rect, settings.TUTORIAL_BUTTON_SKEW)
        pygame.draw.polygon(surface, settings.MENU_BLUE if chosen else settings.MENU_BLACK, shift_points(box, settings.TUTORIAL_BUTTON_SHADOW))
        if chosen and not hovered:
            fill, ink = settings.MENU_WHITE, settings.MENU_BLACK
        elif hovered:
            fill, ink = settings.MENU_BLUE, settings.MENU_WHITE
        else:
            fill, ink = settings.MENU_BLACK, settings.MENU_WHITE
        pygame.draw.polygon(surface, fill, box)
        pygame.draw.polygon(surface, settings.MENU_WHITE, box, settings.TUTORIAL_HOVER_WIDTH)
        text = load_font(settings.TUTORIAL_BUTTON_TEXT_SIZE).render(label, True, ink)
        surface.blit(text, text.get_rect(center=rect.center))
