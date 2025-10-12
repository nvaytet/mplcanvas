# ipycanvas_plotting/transforms/transforms.py
import numpy as np


class DataTransform:
    """Transform between data coordinates and canvas pixels"""

    def __init__(self, axes):
        self.axes = axes

    def transform(self, x, y):
        """Transform data coordinates to canvas coordinates"""
        x = np.asarray(x)
        y = np.asarray(y)

        # Get data limits
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()

        # Scale to [0, 1]
        x_norm = (x - xlim[0]) / (xlim[1] - xlim[0])
        y_norm = (y - ylim[0]) / (ylim[1] - ylim[0])

        # Scale to canvas coordinates
        canvas_x = self.axes.x + x_norm * self.axes.width
        canvas_y = self.axes.y + (1 - y_norm) * self.axes.height  # Flip Y

        return canvas_x, canvas_y

    def inverse_transform(self, canvas_x, canvas_y):
        """Transform canvas coordinates to data coordinates"""
        # Normalize to [0, 1]
        x_norm = (canvas_x - self.axes.x) / self.axes.width
        y_norm = 1 - (canvas_y - self.axes.y) / self.axes.height  # Flip Y

        # Scale to data coordinates
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()

        x = xlim[0] + x_norm * (xlim[1] - xlim[0])
        y = ylim[0] + y_norm * (ylim[1] - ylim[0])

        return x, y
