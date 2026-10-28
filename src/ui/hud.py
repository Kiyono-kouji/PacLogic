import math

import pygame

from src.core import settings
from src.logic.sim import BLOCKED, CAUGHT, ESCAPED, RUNNING
from src.ui.component import Component
from src.ui.label import Label

STATUS_TEXT = {
    RUNNING: ("Running", settings.TEXT_COLOR),
    CAUGHT: ("Caught! Ghosts win", settings.ACCENT_COLOR),
    ESCAPED: ("Escaped! Pac-Man wins", settings.WARNING_COLOR),
    BLOCKED: ("Blocked: out of ticks", settings.TEXT_DIM_COLOR),
}


class HUD(Component):
    def __init__(self, position: tuple[int, int], pellet_mode: bool, seconds_left: float):
        super().__init__()
        self.pellet_mode = pellet_mode
        self.seconds_left = seconds_left
        self.status_label = Label("", position, settings.FONT_MEDIUM)
        names = ["Tick", "Planning left", "Algorithm", "Plans made", "Nodes expanded", "Last search"]
        if pellet_mode:
            names.insert(2, "Pellets left")
        x, y = position
        top = y + settings.HUD_STATUS_GAP
        self.value_labels = {
            name: Label("", (x, top + row * settings.HUD_LINE_HEIGHT), settings.FONT_SMALL)
            for row, name in enumerate(names)
        }

    def refresh(self, sim):
        text, color = STATUS_TEXT[sim.status]
        self.status_label.set_text(text, color)
        brain = sim.brain
        values = {
            "Tick": f"{sim.tick} / {sim.tick_cap}",
            "Planning left": f"{math.ceil(self.seconds_left)} s",
            "Pellets left": str(len(sim.pellets)),
            "Algorithm": f"{brain.algorithm} ({brain.difficulty})",
            "Plans made": str(brain.plans_made),
            "Nodes expanded": str(brain.nodes_expanded),
            "Last search": f"{brain.last_ms:.2f} ms",
        }
        for name, label in self.value_labels.items():
            label.set_text(f"{name}: {values[name]}")

    def draw(self, surface: pygame.Surface):
        self.status_label.draw(surface)
        for label in self.value_labels.values():
            label.draw(surface)
