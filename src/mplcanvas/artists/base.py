# ipycanvas_plotting/artists/base.py
from abc import ABC, abstractmethod


class Artist(ABC):
    """Base class for all plot artists"""

    def __init__(self, axes=None):
        self.axes = axes
        self.figure = axes.figure if axes else None
        self.visible = True
        self.zorder = 0

    @abstractmethod
    def draw(self):
        """Draw this artist to the canvas"""
        pass

    def set_visible(self, visible: bool):
        """Set visibility of this artist"""
        self.visible = visible
        if self.figure:
            self.figure.draw()

    def remove(self):
        """Remove this artist from its axes"""
        if self.axes:
            if hasattr(self.axes, "lines") and self in self.axes.lines:
                self.axes.lines.remove(self)
            if hasattr(self.axes, "collections") and self in self.axes.collections:
                self.axes.collections.remove(self)
            self.figure.draw()
