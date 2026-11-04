import pygame

from src.core import settings
from src.core.resource_loader import animation_frame, load_character_sprite, load_font
from src.logic.grid import Level
from src.ui.effects import ease_out_back
from src.ui.menu_shapes import tag_surface


def pac_man_sprite(direction: str) -> str:
    name = settings.DIRECTION_NAMES[direction]
    frame = animation_frame(settings.PACMAN_FRAME_COUNT, settings.PACMAN_FRAME_MS) + 1
    return f"pacman/eat-{name}/eat-{name}-{frame}.png"


def ghost_sprite(index: int, direction: str) -> str:
    folder = settings.GHOST_SPRITES[index % len(settings.GHOST_SPRITES)]
    name = settings.DIRECTION_NAMES[direction]
    frame = animation_frame(settings.GHOST_FRAME_COUNT, settings.GHOST_FRAME_MS) + 1
    return f"ghosts/{folder}/move-{name}/move-{name}-{frame}.png"


class TutorialBoard:
    def __init__(self, area: tuple):
        self.area = pygame.Rect(area).inflate(-2 * settings.TUTORIAL_BOARD_MARGIN, -2 * settings.TUTORIAL_BOARD_MARGIN)
        self.level: Level | None = None
        self.layer: pygame.Surface | None = None
        self.tile = 1
        self.rect = pygame.Rect(self.area)

    def fit(self, level: Level):
        if level is self.level:
            return
        self.level = level
        self.tile = max(1, min(self.area.width // level.width, self.area.height // level.height))
        self.rect = pygame.Rect(0, 0, self.tile * level.width, self.tile * level.height)
        self.rect.center = self.area.center
        self.layer = self.static_layer()

    def static_layer(self) -> pygame.Surface:
        tile = self.tile
        layer = pygame.Surface(self.rect.size)
        layer.fill(settings.TUTORIAL_FLOOR_COLOR)
        safe = pygame.Surface((tile, tile), pygame.SRCALPHA)
        safe.fill(settings.SAFE_ZONE_COLOR)
        wall_inset = round(tile * settings.TUTORIAL_WALL_INSET)
        exit_inset = round(tile * settings.TUTORIAL_EXIT_INSET)
        for y in range(self.level.height):
            for x in range(self.level.width):
                rect = pygame.Rect(x * tile, y * tile, tile, tile)
                if (x, y) in self.level.walls:
                    pygame.draw.rect(layer, settings.MENU_BLUE_DARK, rect)
                    pygame.draw.rect(layer, settings.MENU_BLUE, rect.inflate(-2 * wall_inset, -2 * wall_inset))
                elif (x, y) in self.level.safe_zone:
                    layer.blit(safe, rect)
        goal = pygame.Rect(self.level.goal[0] * tile, self.level.goal[1] * tile, tile, tile)
        pygame.draw.rect(layer, settings.EXIT_COLOR, goal.inflate(-2 * exit_inset, -2 * exit_inset))
        pygame.draw.rect(layer, settings.EXIT_CORE_COLOR, goal.inflate(-4 * exit_inset, -4 * exit_inset))
        return layer

    def tile_rect(self, tile: tuple) -> pygame.Rect:
        return pygame.Rect(self.rect.left + tile[0] * self.tile, self.rect.top + tile[1] * self.tile, self.tile, self.tile)

    def tile_at(self, position: tuple | None) -> tuple | None:
        if position is None or not self.rect.collidepoint(position):
            return None
        return (position[0] - self.rect.left) // self.tile, (position[1] - self.rect.top) // self.tile

    def stamp_center(self) -> tuple:
        return self.rect.centerx, self.rect.top + self.tile // 2

    def draw(self, surface: pygame.Surface):
        surface.blit(self.layer, self.rect)

    def draw_route(self, surface: pygame.Surface, tiles):
        inset = round(self.tile * settings.TUTORIAL_ROUTE_INSET)
        for tile in tiles:
            pygame.draw.rect(surface, settings.ROUTE_COLOR, self.tile_rect(tile).inflate(-2 * inset, -2 * inset))

    def draw_hover(self, surface: pygame.Surface, tile: tuple | None, color: tuple):
        if tile is not None:
            pygame.draw.rect(surface, color, self.tile_rect(tile), settings.TUTORIAL_HOVER_WIDTH)

    def draw_sprite(self, surface: pygame.Surface, name: str, tile: tuple):
        sprite = load_character_sprite(name, self.tile)
        surface.blit(sprite, sprite.get_rect(center=self.tile_rect(tile).center))

    def draw_costs(self, surface: pygame.Surface, costs: list):
        font = load_font(settings.TUTORIAL_COST_SIZE)
        inset = settings.TUTORIAL_COST_INSET
        for tile, g, h in costs:
            rect = self.tile_rect(tile)
            g_text = font.render(str(g), True, settings.COST_G_COLOR)
            h_text = font.render(str(h), True, settings.COST_H_COLOR)
            surface.blit(g_text, (rect.left + inset, rect.top))
            surface.blit(h_text, h_text.get_rect(bottomright=(rect.right - inset, rect.bottom)))


class Stamp:
    def __init__(self):
        self.image: pygame.Surface | None = None
        self.elapsed = 0.0

    def show(self, text: str, colors: tuple):
        surface = tag_surface(
            text,
            settings.TUTORIAL_STAMP_SIZE,
            colors,
            settings.TUTORIAL_STAMP_PADDING,
            settings.TUTORIAL_TAG_SKEW,
            settings.TUTORIAL_STAMP_SHADOW,
        )
        self.image = pygame.transform.rotate(surface, settings.TUTORIAL_STAMP_TILT)
        self.elapsed = 0.0

    def clear(self):
        self.image = None

    def update(self, dt: float):
        if self.image is None:
            return
        self.elapsed += dt
        if self.elapsed >= settings.TUTORIAL_STAMP_SECONDS:
            self.image = None

    def draw(self, surface: pygame.Surface, center: tuple):
        if self.image is None:
            return
        linear = min(1.0, self.elapsed / settings.TUTORIAL_STAMP_POP_SECONDS)
        scale = max(0.01, 2 - ease_out_back(linear, settings.MENU_OVERSHOOT))
        image = pygame.transform.rotozoom(self.image, 0, scale)
        surface.blit(image, image.get_rect(center=center))
