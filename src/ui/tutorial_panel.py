import pygame

from src.core import settings
from src.ui.button import Button
from src.ui.component import Component
from src.ui.label import Label
from src.ui.panel import Panel


def highlighted_screenshot(screenshot: pygame.Surface, highlight: pygame.Rect) -> pygame.Surface:
    image_rect = pygame.Rect(settings.TUTORIAL_IMAGE_RECT)
    scale = image_rect.width / screenshot.get_width()
    image = pygame.transform.smoothscale(screenshot, image_rect.size)
    padding = settings.TUTORIAL_HIGHLIGHT_PADDING
    box = pygame.Rect(
        round(highlight.x * scale) - padding,
        round(highlight.y * scale) - padding,
        round(highlight.width * scale) + 2 * padding,
        round(highlight.height * scale) + 2 * padding,
    )
    shade = pygame.Surface(image_rect.size, pygame.SRCALPHA)
    shade.fill(settings.TUTORIAL_SHOT_DIM_COLOR)
    shade.fill((0, 0, 0, 0), box)
    image.blit(shade, (0, 0))
    pygame.draw.rect(image, settings.TUTORIAL_HIGHLIGHT_COLOR, box, settings.TUTORIAL_HIGHLIGHT_WIDTH)
    return image


class TutorialPanel(Component):
    def __init__(self, make_slides):
        super().__init__()
        self.visible = False
        self.make_slides = make_slides
        self.slides: list = []
        self.index = 0
        self.dim_layer = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.dim_layer.fill(settings.TUTORIAL_DIM_COLOR)
        self.panel = Panel(settings.TUTORIAL_PANEL_RECT)
        self.step_label = Label("", settings.TUTORIAL_STEP_POSITION, settings.FONT_SMALL, settings.TEXT_DIM_COLOR)
        self.text_label = Label("", settings.TUTORIAL_TEXT_POSITION, settings.FONT_MEDIUM, anchor="center")
        self.previous_button = Button(settings.TUTORIAL_PREVIOUS_RECT, self.previous, "< Previous")
        self.next_button = Button(settings.TUTORIAL_NEXT_RECT, self.next, "Next >")
        self.close_button = Button(settings.TUTORIAL_CLOSE_RECT, self.close, "X")
        self.buttons = [self.previous_button, self.next_button, self.close_button]

    def open(self):
        if not self.slides:
            self.slides = [(text, highlighted_screenshot(shot, area)) for text, shot, area in self.make_slides()]
        self.visible = True
        self.show(0)

    def close(self):
        self.visible = False

    def show(self, index: int):
        self.index = index
        last = len(self.slides) - 1
        self.step_label.set_text(f"Step {index + 1} of {last + 1}")
        self.text_label.set_text(self.slides[index][0])
        self.previous_button.visible = index > 0
        self.next_button.text = "Done" if index == last else "Next >"

    def previous(self):
        if self.index > 0:
            self.show(self.index - 1)

    def next(self):
        if self.index == len(self.slides) - 1:
            self.close()
        else:
            self.show(self.index + 1)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
            elif event.key == pygame.K_LEFT:
                self.previous()
            elif event.key == pygame.K_RIGHT:
                self.next()
            return True
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return True

    def draw_dots(self, surface: pygame.Surface):
        gap = settings.TUTORIAL_DOT_GAP
        left = settings.SCREEN_WIDTH // 2 - (len(self.slides) - 1) * gap // 2
        for index in range(len(self.slides)):
            color = settings.ACCENT_COLOR if index == self.index else settings.TEXT_DIM_COLOR
            pygame.draw.circle(surface, color, (left + index * gap, settings.TUTORIAL_DOTS_Y), settings.TUTORIAL_DOT_RADIUS)

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return
        surface.blit(self.dim_layer, (0, 0))
        self.panel.draw(surface)
        self.step_label.draw(surface)
        self.text_label.draw(surface)
        image_rect = pygame.Rect(settings.TUTORIAL_IMAGE_RECT)
        surface.blit(self.slides[self.index][1], image_rect)
        pygame.draw.rect(surface, settings.PANEL_BORDER_COLOR, image_rect, settings.PANEL_BORDER_WIDTH)
        self.draw_dots(surface)
        for button in self.buttons:
            button.draw(surface)
