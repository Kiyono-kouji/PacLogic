import pygame

from src.core import settings
from src.core.resource_loader import load_font
from src.ui.button import Button


class TutorialButton(Button):
    def __init__(self, on_click):
        super().__init__(settings.TUTORIAL_BUTTON_RECT, on_click, settings.TUTORIAL_BUTTON_TEXT)

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return
        pygame.draw.rect(surface, self.color(), self.rect.inflate(-2 * settings.BUTTON_STEP, 0))
        pygame.draw.rect(surface, self.color(), self.rect.inflate(0, -2 * settings.BUTTON_STEP))
        font = load_font(settings.BUTTON_FONT_SIZE)
        radius = settings.TUTORIAL_ICON_RADIUS
        text = font.render(self.text, True, settings.BUTTON_TEXT_COLOR)
        total_width = text.get_width() + settings.TUTORIAL_ICON_GAP + 2 * radius
        left = self.rect.centerx - total_width // 2
        surface.blit(text, text.get_rect(midleft=(left, self.rect.centery)))
        icon_center = (left + total_width - radius, self.rect.centery)
        pygame.draw.circle(surface, settings.BUTTON_TEXT_COLOR, icon_center, radius, settings.TUTORIAL_ICON_LINE_WIDTH)
        mark = font.render("?", True, settings.BUTTON_TEXT_COLOR)
        surface.blit(mark, mark.get_rect(center=icon_center))
