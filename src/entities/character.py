import pygame


def lerp_tile(
    previous: tuple[int, int], tile: tuple[int, int], progress: float
) -> tuple[float, float]:
    clamped = max(0.0, min(1.0, progress))
    x = previous[0] + (tile[0] - previous[0]) * clamped
    y = previous[1] + (tile[1] - previous[1]) * clamped
    return x, y


class Character:
    def __init__(self, tile: tuple[int, int] = (0, 0), direction: str = "R"):
        self.tile: tuple[int, int] = tile
        self.previous_tile: tuple[int, int] = tile
        self.direction: str = direction
        self.position: tuple[float, float] = (0.0, 0.0)
        self.tile_size: int = 32
        self.time: float = 0.0

    def update(self, dt: float):
        self.time += dt

    def follow(
        self,
        previous_tile: tuple[int, int],
        tile: tuple[int, int],
        direction: str,
        progress: float,
        map_view,
    ):
        self.previous_tile = previous_tile
        self.tile = tile
        if direction:
            self.direction = direction
        self.tile_size = map_view.tile
        interp = lerp_tile(previous_tile, tile, progress)
        self.position = (
            map_view.rect.x + interp[0] * map_view.tile,
            map_view.rect.y + interp[1] * map_view.tile,
        )

    def draw(self, surface: pygame.Surface):
        raise NotImplementedError
