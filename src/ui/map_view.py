import pygame

from src.core import settings
from src.core.resource_loader import load_font, load_sprite
from src.logic.grid import Level
from src.ui.component import Component


def fit_tile_size(level: Level, area: pygame.Rect) -> int:
    return max(1, min(area.width // level.width, area.height // level.height))


class MapView(Component):
    def __init__(self, level: Level, area: pygame.Rect):
        super().__init__()
        self.level = level
        self.tile = fit_tile_size(level, area)
        size = (level.width * self.tile, level.height * self.tile)
        self.rect = pygame.Rect((0, 0), size)
        self.rect.center = area.center
        self.background = self.render_background(size)
        self.route_tile = pygame.Surface((self.tile, self.tile), pygame.SRCALPHA)
        self.route_tile.fill(settings.ROUTE_COLOR)

    def render_background(self, size: tuple) -> pygame.Surface:
        background = pygame.Surface(size)
        background.fill(settings.MAP_FLOOR_COLOR)
        corner = int(self.tile * settings.WALL_CORNER)
        for wall in self.level.walls:
            pygame.draw.rect(background, settings.MAP_WALL_COLOR, self.local_rect(wall), border_radius=corner)
        safe_zone = pygame.Surface(size, pygame.SRCALPHA)
        for tile in self.level.safe_zone:
            safe_zone.fill(settings.SAFE_ZONE_COLOR, self.local_rect(tile))
        background.blit(safe_zone, (0, 0))
        inset = int(self.tile * settings.EXIT_INSET)
        pygame.draw.rect(background, settings.EXIT_COLOR, self.local_rect(self.level.goal).inflate(-2 * inset, -2 * inset), border_radius=corner)
        return background

    def local_rect(self, tile: tuple) -> pygame.Rect:
        return pygame.Rect(tile[0] * self.tile, tile[1] * self.tile, self.tile, self.tile)

    def tile_topleft(self, tile: tuple) -> tuple:
        return self.rect.x + tile[0] * self.tile, self.rect.y + tile[1] * self.tile

    def tile_center(self, tile: tuple) -> tuple:
        x, y = self.tile_topleft(tile)
        return x + self.tile // 2, y + self.tile // 2

    def tile_at(self, mouse_position: tuple) -> tuple | None:
        if not self.rect.collidepoint(mouse_position):
            return None
        return (mouse_position[0] - self.rect.x) // self.tile, (mouse_position[1] - self.rect.y) // self.tile

    def draw(self, surface: pygame.Surface, pellets=None, route=()):
        pellets = self.level.pellets if pellets is None else pellets
        surface.blit(self.background, self.rect)
        for tile in route:
            surface.blit(self.route_tile, self.tile_topleft(tile))
        sprite = load_sprite("items/pellet/pellet.png", self.tile)
        for pellet in pellets:
            surface.blit(sprite, sprite.get_rect(center=self.tile_center(pellet)))

    def cost_font(self, costs) -> pygame.font.Font | None:
        widest = max((str(value) for _, g, h in costs for value in (g, h)), key=len)
        room = self.tile - 2 * int(self.tile * settings.COST_PADDING)
        for size in settings.COST_FONT_SIZES:
            font = load_font(size)
            if font.size(widest)[0] <= room and 2 * font.get_linesize() <= room:
                return font
        return None

    def draw_costs(self, surface: pygame.Surface, costs):
        costs = list(costs)
        font = self.cost_font(costs) if costs else None
        if font is None:
            return
        padding = int(self.tile * settings.COST_PADDING)
        for tile, g, h in costs:
            rect = pygame.Rect(self.tile_topleft(tile), (self.tile, self.tile))
            surface.fill(settings.COST_TILE_COLOR, rect.inflate(-2, -2))
            surface.blit(font.render(str(g), True, settings.COST_G_COLOR), (rect.x + padding, rect.y + padding))
            h_text = font.render(str(h), True, settings.COST_H_COLOR)
            surface.blit(h_text, h_text.get_rect(bottomright=(rect.right - padding, rect.bottom - padding)))
