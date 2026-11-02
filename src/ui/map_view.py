import pygame

from src.core import settings
from src.core.resource_loader import load_font, load_sprite, sprite_size
from src.logic.grid import DIRECTIONS, Level, move
from src.ui.component import Component

CORNERS = ((-1, -1, "U", "L"), (1, -1, "U", "R"), (-1, 1, "D", "L"), (1, 1, "D", "R"))


def fit_tile_size(level: Level, area: pygame.Rect) -> int:
    return max(1, min(area.width // level.width, area.height // level.height))


def _stepped_fill(surface: pygame.Surface, color: tuple, rect: pygame.Rect, step: int):
    pygame.draw.rect(surface, color, rect.inflate(-2 * step, 0))
    pygame.draw.rect(surface, color, rect.inflate(0, -2 * step))


def _stepped_outline(surface: pygame.Surface, color: tuple, rect: pygame.Rect, step: int):
    pygame.draw.rect(surface, color, (rect.left + step, rect.top, rect.width - 2 * step, step))
    pygame.draw.rect(surface, color, (rect.left + step, rect.bottom - step, rect.width - 2 * step, step))
    pygame.draw.rect(surface, color, (rect.left, rect.top + step, step, rect.height - 2 * step))
    pygame.draw.rect(surface, color, (rect.right - step, rect.top + step, step, rect.height - 2 * step))


class MapView(Component):
    def __init__(self, level: Level, area: pygame.Rect):
        super().__init__()
        self.level = level
        self.tile = fit_tile_size(level, area)
        self.pixel = max(1, sprite_size(self.tile) // settings.SPRITE_PIXELS)
        size = (level.width * self.tile, level.height * self.tile)
        self.rect = pygame.Rect((0, 0), size)
        self.rect.center = area.center
        self.background = self.render_background(size)
        self.route_tile = self.render_route_tile()

    def render_route_tile(self) -> pygame.Surface:
        marker = pygame.Surface((self.tile, self.tile), pygame.SRCALPHA)
        inset = settings.ROUTE_INSET_PIXELS * self.pixel
        _stepped_outline(marker, settings.ROUTE_COLOR, marker.get_rect().inflate(-2 * inset, -2 * inset), self.pixel)
        return marker

    def render_background(self, size: tuple) -> pygame.Surface:
        background = pygame.Surface(size)
        background.fill(settings.MAP_FLOOR_COLOR)
        for wall in self.level.walls:
            self.draw_wall(background, wall)
        dither = pygame.Surface(size, pygame.SRCALPHA)
        for tile in self.level.safe_zone:
            self.draw_dither(dither, self.local_rect(tile))
        background.blit(dither, (0, 0))
        inset = settings.EXIT_INSET_PIXELS * self.pixel
        pad = self.local_rect(self.level.goal).inflate(-2 * inset, -2 * inset)
        _stepped_fill(background, settings.EXIT_COLOR, pad, self.pixel)
        _stepped_fill(background, settings.EXIT_CORE_COLOR, pad.inflate(-4 * self.pixel, -4 * self.pixel), self.pixel)
        return background

    def is_wall(self, tile: tuple) -> bool:
        return not self.level.in_bounds(tile) or tile in self.level.walls

    def draw_wall(self, surface: pygame.Surface, tile: tuple):
        rect, step = self.local_rect(tile), self.pixel
        pygame.draw.rect(surface, settings.MAP_WALL_COLOR, rect)
        open_side = {direction: not self.is_wall(move(tile, direction)) for direction in DIRECTIONS}
        edges = {
            "U": (rect.left, rect.top, rect.width, step),
            "D": (rect.left, rect.bottom - step, rect.width, step),
            "L": (rect.left, rect.top, step, rect.height),
            "R": (rect.right - step, rect.top, step, rect.height),
        }
        for direction, edge in edges.items():
            if open_side[direction]:
                pygame.draw.rect(surface, settings.MAP_WALL_EDGE_COLOR, edge)
        for dx, dy, vertical, horizontal in CORNERS:
            corner_x = rect.left if dx < 0 else rect.right - step
            corner_y = rect.top if dy < 0 else rect.bottom - step
            if open_side[vertical] and open_side[horizontal]:
                pygame.draw.rect(surface, settings.MAP_FLOOR_COLOR, (corner_x, corner_y, step, step))
                pygame.draw.rect(surface, settings.MAP_WALL_EDGE_COLOR, (corner_x - dx * step, corner_y - dy * step, step, step))
            elif not open_side[vertical] and not open_side[horizontal] and not self.is_wall((tile[0] + dx, tile[1] + dy)):
                pygame.draw.rect(surface, settings.MAP_WALL_EDGE_COLOR, (corner_x, corner_y, step, step))

    def draw_dither(self, surface: pygame.Surface, rect: pygame.Rect):
        step = self.pixel
        for y in range(rect.top, rect.bottom, step):
            for x in range(rect.left, rect.right, step):
                if (x // step + y // step) % 2 == 0:
                    surface.fill(settings.SAFE_ZONE_COLOR, pygame.Rect(x, y, step, step).clip(rect))

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

    def cost_inset(self) -> int:
        return (settings.ROUTE_INSET_PIXELS + 1) * self.pixel + int(self.tile * settings.COST_PADDING)

    def cost_font(self, costs) -> pygame.font.Font | None:
        widest = max((str(value) for _, g, h in costs for value in (g, h)), key=len)
        room = self.tile - 2 * self.cost_inset()
        for size in settings.COST_FONT_SIZES:
            font = load_font(size)
            if font.size(widest)[0] <= room and 2 * font.get_linesize() <= room:
                return font
        return None

    def draw_costs(self, surface: pygame.Surface, costs):
        costs = list({tile: (tile, g, h) for tile, g, h in costs}.values())
        font = self.cost_font(costs) if costs else None
        if font is None:
            return
        for tile, g, h in costs:
            inner = pygame.Rect(self.tile_topleft(tile), (self.tile, self.tile)).inflate(-2 * self.cost_inset(), -2 * self.cost_inset())
            surface.blit(font.render(str(g), True, settings.COST_G_COLOR), inner.topleft)
            h_text = font.render(str(h), True, settings.COST_H_COLOR)
            surface.blit(h_text, h_text.get_rect(bottomright=inner.bottomright))
