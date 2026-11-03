from pathlib import Path

import pygame

from src.core import settings

SLIDE_CAPTIONS = (
    "Press Play to begin.",
    "Pick the maze, AI, ghosts, mode and time.",
    "Press Start.",
    "Study the maze first.",
    "Pac-Man runs to this exit.",
    "Ghosts can't enter the green safe zone.",
    "Press Start planning.",
    "Click a ghost to program it.",
    "Drag blocks from here...",
    "...and drop them here. Right-click deletes.",
    "At 0:00 your programs lock.",
    "Ready early? Press Lock & Run.",
    "Pac-Man uses A* to find the shortest route.",
    "Ghosts move first, then Pac-Man steps.",
    "Watch the stats. Space pauses.",
    "Caught: 1000+. Blocked: 500. Escaped: 0.",
)


def load_tutorial_slides() -> list:
    slides = []
    for i, caption in enumerate(SLIDE_CAPTIONS):
        path = settings.TUTORIAL_IMAGES_DIR / f"slide_{i + 1:02d}.png"
        image = pygame.image.load(path).convert_alpha()
        slides.append((caption, image))
    return slides