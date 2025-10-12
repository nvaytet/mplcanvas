# ipycanvas_plotting/axes.py
import numpy as np
from typing import List, Tuple, Any
from .artists.line import Line2D

# from .artists.scatter import PathCollection
from .transforms.transforms import DataTransform
from .events.mouse import MouseEventMixin


class Axes(MouseEventMixin):
    """
    An Axes object represents one plot area within a figure.
    Similar to matplotlib.axes.Axes but optimized for ipycanvas.
    """

    def __init__(self, figure, rect: Tuple[int, int, int, int]):
        self.figure = figure
        self.canvas = figure.canvas  # Direct reference for drawing

        # Position within figure (x, y, width, height)
        self.x, self.y, self.width, self.height = rect

        # Data limits
        self._xlim = [0, 1]
        self._ylim = [0, 1]
        self._autoscale_x = True
        self._autoscale_y = True

        # Collections of artists
        self.lines: List[Line2D] = []
        self.collections: List[Any] = []  # For scatter plots, etc.

        # Coordinate transformer
        self.transData = DataTransform(self)

        # Styling
        self.facecolor = "white"
        self.grid_enabled = False

        # Initialize mouse event handling
        super().__init__()
        self._setup_mouse_events()

    # Plotting methods
    def plot(self, *args, **kwargs) -> List[Line2D]:
        """
        Plot y versus x as lines and/or markers.

        Parameters similar to matplotlib:
        - plot(y)
        - plot(x, y)
        - plot(x, y, format_string)
        """
        lines = []

        # Parse arguments (simplified for prototype)
        if len(args) == 1:
            # plot(y)
            y = np.asarray(args[0])
            x = np.arange(len(y))
        elif len(args) == 2:
            # plot(x, y)
            x = np.asarray(args[0])
            y = np.asarray(args[1])
        else:
            raise ValueError("Invalid number of arguments")

        # Create Line2D artist
        line = Line2D(x, y, axes=self, **kwargs)
        self.lines.append(line)
        lines.append(line)

        # Auto-scale if needed
        if self._autoscale_x or self._autoscale_y:
            self._update_datalim(x, y)
            if self._autoscale_x:
                self._xlim = [np.min(x), np.max(x)]
            if self._autoscale_y:
                self._ylim = [np.min(y), np.max(y)]

        # Trigger redraw
        self.figure.draw()

        return lines[0] if len(lines) == 1 else lines

    def scatter(self, x, y, s=None, c=None, **kwargs):
        """Create a scatter plot"""
        collection = PathCollection(x, y, s=s, c=c, axes=self, **kwargs)
        self.collections.append(collection)

        if self._autoscale_x or self._autoscale_y:
            self._update_datalim(x, y)

        self.figure.draw()
        return collection

    # Limit methods
    def set_xlim(self, left: float = None, right: float = None):
        """Set x-axis limits"""
        if left is not None:
            self._xlim[0] = left
        if right is not None:
            self._xlim[1] = right
        self._autoscale_x = False
        self.figure.draw()

    def set_ylim(self, bottom: float = None, top: float = None):
        """Set y-axis limits"""
        if bottom is not None:
            self._ylim[0] = bottom
        if top is not None:
            self._ylim[1] = top
        self._autoscale_y = False
        self.figure.draw()

    def get_xlim(self) -> Tuple[float, float]:
        return tuple(self._xlim)

    def get_ylim(self) -> Tuple[float, float]:
        return tuple(self._ylim)

    # Internal methods
    def _update_datalim(self, x, y):
        """Update data limits for autoscaling"""
        if len(self.lines) == 0 and len(self.collections) == 0:
            # First data
            self._xlim = [np.min(x), np.max(x)]
            self._ylim = [np.min(y), np.max(y)]
        else:
            if self._autoscale_x:
                self._xlim[0] = min(self._xlim[0], np.min(x))
                self._xlim[1] = max(self._xlim[1], np.max(x))
            if self._autoscale_y:
                self._ylim[0] = min(self._ylim[0], np.min(y))
                self._ylim[1] = max(self._ylim[1], np.max(y))

    def draw(self):
        """Render this axes and all its artists"""
        from ipycanvas import hold_canvas

        with hold_canvas(self.canvas):
            # Draw axes background
            self.canvas.fill_style = self.facecolor
            self.canvas.fill_rect(self.x, self.y, self.width, self.height)

            # Set clipping region to axes area
            self.canvas.save()
            self.canvas.begin_path()
            self.canvas.rect(self.x, self.y, self.width, self.height)
            self.canvas.clip()

            # Draw all line artists
            for line in self.lines:
                line.draw()

            # Draw all collections (scatter, etc.)
            for collection in self.collections:
                collection.draw()

            # Restore canvas state (remove clipping)
            self.canvas.restore()

            # Draw axes frame and ticks
            self._draw_frame()

    def _draw_frame(self):
        """Draw the axes frame and ticks"""
        # Simple frame for now
        self.canvas.stroke_style = "black"
        self.canvas.line_width = 1
        self.canvas.stroke_rect(self.x, self.y, self.width, self.height)
