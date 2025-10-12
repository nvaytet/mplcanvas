# ipycanvas_plotting/artists/line.py
import numpy as np
from .base import Artist


class Line2D(Artist):
    """A line plot artist, similar to matplotlib.lines.Line2D"""

    def __init__(
        self,
        x,
        y,
        axes=None,
        color="blue",
        linewidth=1.5,
        linestyle="-",
        marker=None,
        markersize=6,
        **kwargs,
    ):
        super().__init__(axes)

        self.x = np.asarray(x)
        self.y = np.asarray(y)

        # Style properties
        self.color = color
        self.linewidth = linewidth
        self.linestyle = linestyle
        self.marker = marker
        self.markersize = markersize

        # Picking support
        self.picker = kwargs.get("picker", None)

    def set_data(self, x, y):
        """Update the line data"""
        self.x = np.asarray(x)
        self.y = np.asarray(y)
        if self.figure:
            self.figure.draw()

    def set_color(self, color):
        """Set line color"""
        self.color = color
        if self.figure:
            self.figure.draw()

    def draw(self):
        """Draw the line to canvas"""
        if not self.visible or len(self.x) == 0:
            return

        canvas = self.axes.canvas

        # Transform data to canvas coordinates
        canvas_x, canvas_y = self.axes.transData.transform(self.x, self.y)

        # Draw line
        if self.linestyle != "None" and self.linestyle != "":
            canvas.stroke_style = self.color
            canvas.line_width = self.linewidth

            # Use numpy array for efficient drawing
            points = np.column_stack([canvas_x, canvas_y])
            canvas.stroke_lines(points)

        # Draw markers if specified
        if self.marker is not None:
            self._draw_markers(canvas_x, canvas_y)

    def _draw_markers(self, canvas_x, canvas_y):
        """Draw markers at data points"""
        canvas = self.axes.canvas
        canvas.fill_style = self.color

        for x, y in zip(canvas_x, canvas_y):
            if self.marker == "o":
                canvas.begin_path()
                canvas.arc(x, y, self.markersize / 2, 0, 2 * np.pi)
                canvas.fill()
            # Add more marker types as needed
