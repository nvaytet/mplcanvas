# ipycanvas_plotting/axes.py
import numpy as np
from typing import List, Tuple, Any
from matplotlib.figure import Figure as MplFigure
from .artists.line import Line2D

# from .artists.scatter import PathCollection
from .transforms.transforms import DataTransform
from .events.mouse import MouseEventMixin


# class Axes:

#     def __init__(self):


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

        # Create minimal shadow matplotlib axes for tick calculations
        self._shadow_fig = MplFigure(figsize=(1, 1))
        self._shadow_ax = self._shadow_fig.add_subplot(111)
        self._shadow_ax.set_xlim(self._xlim)
        self._shadow_ax.set_ylim(self._ylim)

        # Spine properties
        self._spines_visible = True
        self._spine_color = "black"
        self._spine_linewidth = 0.8

        # Tick properties
        self._ticks_visible = True
        self._tick_color = "black"
        self._tick_length = 4
        self._tick_width = 0.8

        # Label properties
        self._labels_visible = True
        self._label_color = "black"
        self._label_fontsize = 10
        self._label_fontfamily = "sans-serif"

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

    # # Limit methods
    # # mplcanvas/axes.py
    # def set_xlim(self, left: float = None, right: float = None):
    #     """Set x-axis limits"""
    #     if left is not None:
    #         self._xlim[0] = left
    #     if right is not None:
    #         self._xlim[1] = right
    #     self._autoscale_x = False

    # def set_ylim(self, bottom: float = None, top: float = None):
    #     """Set y-axis limits"""
    #     if bottom is not None:
    #         self._ylim[0] = bottom
    #     if top is not None:
    #         self._ylim[1] = top
    #     self._autoscale_y = False

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

    def set_xlim(self, left: float = None, right: float = None):
        """Set x-axis limits and update shadow axes"""
        if left is not None:
            self._xlim[0] = left
        if right is not None:
            self._xlim[1] = right
        self._autoscale_x = False

        # Update shadow axes
        self._shadow_ax.set_xlim(self._xlim)

    def set_ylim(self, bottom: float = None, top: float = None):
        """Set y-axis limits and update shadow axes"""
        if bottom is not None:
            self._ylim[0] = bottom
        if top is not None:
            self._ylim[1] = top
        self._autoscale_y = False

        # Update shadow axes
        self._shadow_ax.set_ylim(self._ylim)

    def _get_tick_info(self):
        """Get tick positions and labels from shadow matplotlib axes"""
        # Force matplotlib to update ticks
        self._shadow_fig.canvas.draw()

        # Get X ticks
        x_major_locs = self._shadow_ax.xaxis.get_majorticklocs()
        x_major_labels = [
            tick.get_text() for tick in self._shadow_ax.xaxis.get_majorticklabels()
        ]
        x_minor_locs = self._shadow_ax.xaxis.get_minorticklocs()

        # Get Y ticks
        y_major_locs = self._shadow_ax.yaxis.get_majorticklocs()
        y_major_labels = [
            tick.get_text() for tick in self._shadow_ax.yaxis.get_majorticklabels()
        ]
        y_minor_locs = self._shadow_ax.yaxis.get_minorticklocs()

        return {
            "x_major_locs": x_major_locs,
            "x_major_labels": x_major_labels,
            "x_minor_locs": x_minor_locs,
            "y_major_locs": y_major_locs,
            "y_major_labels": y_major_labels,
            "y_minor_locs": y_minor_locs,
        }

    def _data_to_canvas(self, x_data, y_data):
        """Convert data coordinates to canvas coordinates"""
        # Scale to axes coordinate system
        x_norm = (x_data - self._xlim[0]) / (self._xlim[1] - self._xlim[0])
        y_norm = (y_data - self._ylim[0]) / (self._ylim[1] - self._ylim[0])

        # Convert to canvas coordinates
        x_canvas = self.x + x_norm * self.width
        y_canvas = self.y + (1 - y_norm) * self.height  # Flip Y axis

        return x_canvas, y_canvas

    def _draw_spines(self):
        """Draw the axes spines (borders)"""
        if not self._spines_visible:
            return

        self.canvas.stroke_style = self._spine_color
        self.canvas.line_width = self._spine_linewidth

        # Draw rectangle around axes
        self.canvas.stroke_rect(self.x, self.y, self.width, self.height)

    def _draw_ticks_and_labels(self):
        """Draw ticks and labels using matplotlib calculations"""
        if not self._ticks_visible:
            return

        tick_info = self._get_tick_info()

        self.canvas.stroke_style = self._tick_color
        self.canvas.line_width = self._tick_width
        self.canvas.font = f"{self._label_fontsize}px {self._label_fontfamily}"
        self.canvas.fill_style = self._label_color
        self.canvas.text_align = "center"
        self.canvas.text_baseline = "top"

        # Draw X ticks and labels
        for i, x_val in enumerate(tick_info["x_major_locs"]):
            if self._xlim[0] <= x_val <= self._xlim[1]:  # Only draw visible ticks
                x_canvas, _ = self._data_to_canvas(x_val, 0)

                # Draw major tick line
                self.canvas.begin_path()
                self.canvas.move_to(x_canvas, self.y + self.height)
                self.canvas.line_to(x_canvas, self.y + self.height + self._tick_length)
                self.canvas.stroke()

                # Draw tick label
                if self._labels_visible and i < len(tick_info["x_major_labels"]):
                    label_text = tick_info["x_major_labels"][i]
                    if label_text.strip():  # Only draw non-empty labels
                        self.canvas.fill_text(
                            label_text,
                            x_canvas,
                            self.y + self.height + self._tick_length + 2,
                        )

        # Draw X minor ticks
        for x_val in tick_info["x_minor_locs"]:
            if self._xlim[0] <= x_val <= self._xlim[1]:
                x_canvas, _ = self._data_to_canvas(x_val, 0)

                # Draw minor tick line (shorter)
                self.canvas.begin_path()
                self.canvas.move_to(x_canvas, self.y + self.height)
                self.canvas.line_to(
                    x_canvas, self.y + self.height + self._tick_length // 2
                )
                self.canvas.stroke()

        # Draw Y ticks and labels
        self.canvas.text_align = "right"
        self.canvas.text_baseline = "middle"

        for i, y_val in enumerate(tick_info["y_major_locs"]):
            if self._ylim[0] <= y_val <= self._ylim[1]:  # Only draw visible ticks
                _, y_canvas = self._data_to_canvas(0, y_val)

                # Draw major tick line
                self.canvas.begin_path()
                self.canvas.move_to(self.x - self._tick_length, y_canvas)
                self.canvas.line_to(self.x, y_canvas)
                self.canvas.stroke()

                # Draw tick label
                if self._labels_visible and i < len(tick_info["y_major_labels"]):
                    label_text = tick_info["y_major_labels"][i]
                    if label_text.strip():  # Only draw non-empty labels
                        self.canvas.fill_text(
                            label_text, self.x - self._tick_length - 4, y_canvas
                        )

        # Draw Y minor ticks
        for y_val in tick_info["y_minor_locs"]:
            if self._ylim[0] <= y_val <= self._ylim[1]:
                _, y_canvas = self._data_to_canvas(0, y_val)

                # Draw minor tick line (shorter)
                self.canvas.begin_path()
                self.canvas.move_to(self.x - self._tick_length // 2, y_canvas)
                self.canvas.line_to(self.x, y_canvas)
                self.canvas.stroke()

    def draw(self):
        """Render this axes and all its artists"""
        # from ipycanvas import hold_canvas

        # with hold_canvas(self.canvas):
        # Draw axes background
        self.canvas.fill_style = self.facecolor
        self.canvas.fill_rect(self.x, self.y, self.width, self.height)

        # Set clipping region to axes area
        self.canvas.save()
        self.canvas.begin_path()
        self.canvas.rect(self.x, self.y, self.width, self.height)
        self.canvas.clip()

        # Draw spines first
        self._draw_spines()

        # Draw all line artists
        for line in self.lines:
            line.draw()

        # Draw all collections (scatter, etc.)
        for collection in self.collections:
            collection.draw()

        # Restore canvas state (remove clipping)
        self.canvas.restore()

        # Draw ticks and labels on top
        self._draw_ticks_and_labels()

        # # Draw axes frame and ticks
        # self._draw_frame()

    def _draw_frame(self):
        """Draw the axes frame and ticks"""
        # Simple frame for now
        self.canvas.stroke_style = "black"
        self.canvas.line_width = 1
        self.canvas.stroke_rect(self.x, self.y, self.width, self.height)

    def set_xlabel(self, label: str):
        """Set X axis label"""
        self._xlabel = label
        self._shadow_ax.set_xlabel(label)  # Keep shadow in sync

    def set_ylabel(self, label: str):
        """Set Y axis label"""
        self._ylabel = label
        self._shadow_ax.set_ylabel(label)  # Keep shadow in sync

    def set_title(self, title: str):
        """Set axes title"""
        self._title = title
        self._shadow_ax.set_title(title)  # Keep shadow in sync

    def grid(self, visible: bool = True, **kwargs):
        """Enable/disable grid"""
        self._grid_visible = visible
        self._shadow_ax.grid(visible, **kwargs)  # Keep shadow in sync

    # Cleanup method
    def __del__(self):
        """Clean up shadow matplotlib figure"""
        try:
            plt.close(self._shadow_fig)
        except:
            pass
