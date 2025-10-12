# mplcanvas/figure.py
from ipycanvas import Canvas, hold_canvas
import ipywidgets as widgets
from typing import List, Tuple

from .axes import Axes


class Figure(widgets.HBox):
    """
    Top-level container for all plot elements.

    Inherits from VBox so it can be composed with other widgets,
    and implements _repr_mimebundle_ for automatic Jupyter display.
    """

    def __init__(
        self,
        figsize: Tuple[float, float] = (8, 6),
        dpi: int = 100,
        facecolor: str = "white",
        toolbar: bool = True,
        **kwargs,
    ):
        # Convert figsize from inches to pixels
        self.figsize = figsize
        self.dpi = dpi
        self.width = int(figsize[0] * dpi)
        self.height = int(figsize[1] * dpi)

        layout = widgets.Layout(width=f"{self.width}px", height=f"{self.height}px")

        # Create the canvas
        self.canvas = Canvas(width=self.width, height=self.height, layout=layout)

        # Create toolbar if requested
        self.toolbar = None
        if toolbar:
            # We'll create the toolbar after adding the first axes
            self._toolbar_enabled = True
        else:
            self._toolbar_enabled = False

        # Initialize as VBox with canvas as child
        super().__init__(children=[self.canvas], **kwargs)

        # Container for all axes
        self.axes: List[Axes] = []

        # Figure-level properties
        self.facecolor = facecolor

        # Auto-draw on creation
        self._auto_draw = True

    def add_subplot(self, nrows: int, ncols: int, index: int, **kwargs) -> "Axes":
        """Add a subplot to the figure"""
        from .axes import Axes  # Import here to avoid circular imports

        # For now, only support single subplot
        if nrows == 1 and ncols == 1 and index == 1:
            # Calculate axes position (leave margin for labels)
            margin_left = 80
            margin_right = 20
            margin_top = 20
            margin_bottom = 60

            ax_x = margin_left
            ax_y = margin_top
            ax_width = self.width - margin_left - margin_right
            ax_height = self.height - margin_top - margin_bottom

            ax = Axes(self, (ax_x, ax_y, ax_width, ax_height))
            self.axes.append(ax)

            # If toolbar exists, register this new axes with it
            if self.toolbar is not None:
                self.toolbar.add_axes(ax)

            # Create toolbar if this is the first axes
            if self._toolbar_enabled and self.toolbar is None:
                self._create_toolbar()
                # Register this axes with the new toolbar
                self.toolbar.add_axes(ax)
            return ax
        else:
            raise NotImplementedError("Multiple subplots not yet supported")

    # Update the _create_toolbar method in mplcanvas/figure.py

    def _create_toolbar(self, axes=None):
        """Create and add the toolbar"""
        from .widgets.toolbar import NavigationToolbar

        # Toolbar operates on the entire figure, not a single axes
        self.toolbar = NavigationToolbar(self)

        # Update children to include toolbar on the left
        self.children = [self.toolbar, self.canvas]

        # # def add_subplot(self, nrows: int, ncols: int, index: int, **kwargs) -> 'Axes':
        # #     """Add a subplot to the figure"""
        # #     from .axes import Axes

        # # ... existing subplot creation code ...

        # ax = Axes(self, (ax_x, ax_y, ax_width, ax_height))
        # self.axes.append(ax)

        # # If toolbar exists, register this new axes with it
        # if self.toolbar is not None:
        #     self.toolbar.add_axes(ax)

        # # Create toolbar if this is the first axes
        # if self._toolbar_enabled and self.toolbar is None:
        #     self._create_toolbar()
        #     # Register this axes with the new toolbar
        #     self.toolbar.add_axes(ax)

        # return ax

    def draw(self):
        """Render the entire figure"""
        with hold_canvas(self.canvas):
            # Clear canvas
            self.canvas.clear()

            # Draw background
            self.canvas.fill_style = self.facecolor
            self.canvas.fill_rect(0, 0, self.width, self.height)

            # Draw all axes
            for ax in self.axes:
                ax.draw()

    def show(self):
        """
        Display the figure in Jupyter.

        Note: This is mainly for backward compatibility.
        The preferred way is to just have the figure as the last
        line in a cell, which will use _repr_mimebundle_.
        """
        # Ensure we're drawn
        if self._auto_draw:
            self.draw()

        # Return self so Jupyter displays it
        return self

    # def _repr_mimebundle_(self, include=None, exclude=None):
    #     """
    #     Jupyter representation - this makes the figure display automatically
    #     when it's the result of a cell.
    #     """
    #     # Ensure we're drawn
    #     if self._auto_draw:
    #         self.draw()

    #     # Let the parent VBox handle the representation
    #     return super()._repr_mimebundle_(include=include, exclude=exclude)

    def clf(self):
        """Clear the figure"""
        self.axes.clear()
        self.draw()

    # def add_child_widget(self, widget):
    #     """
    #     Add an additional widget to the figure (like a toolbar, slider, etc.)

    #     This allows composing figures with other widgets easily.
    #     """
    #     self.children = list(self.children) + [widget]

    # def insert_child_widget(self, index, widget):
    #     """Insert a widget at a specific position"""
    #     children = list(self.children)
    #     children.insert(index, widget)
    #     self.children = children

    # Properties to make it more matplotlib-like
    @property
    def number(self):
        """Figure number (for matplotlib compatibility)"""
        return id(self)  # Use object id as figure number

    def set_facecolor(self, color):
        """Set the figure face color"""
        self.facecolor = color
        if self._auto_draw:
            self.draw()

    def set_size_inches(self, w, h=None, forward=True):
        """
        Set the figure size in inches.

        If forward=True, also update the canvas size.
        """
        if h is None:
            w, h = w  # Assume w is a tuple

        self.figsize = (w, h)

        if forward:
            new_width = int(w * self.dpi)
            new_height = int(h * self.dpi)

            # Update canvas size
            self.canvas.width = new_width
            self.canvas.height = new_height
            self.width = new_width
            self.height = new_height

            # Reposition axes
            for ax in self.axes:
                # Recalculate axes dimensions
                margin_left = 80
                margin_right = 20
                margin_top = 20
                margin_bottom = 60

                ax.x = margin_left
                ax.y = margin_top
                ax.width = self.width - margin_left - margin_right
                ax.height = self.height - margin_top - margin_bottom

            if self._auto_draw:
                self.draw()

    # Toolbar management methods
    def hide_toolbar(self):
        """Hide the toolbar"""
        if self.toolbar is not None:
            self.children = [self.canvas]

    def show_toolbar(self):
        """Show the toolbar"""
        if self.toolbar is not None:
            self.children = [self.toolbar, self.canvas]
        elif self._toolbar_enabled and self.axes:
            self._create_toolbar(self.axes[0])

    def toggle_toolbar(self):
        """Toggle toolbar visibility"""
        if self.toolbar is not None and self.toolbar in self.children:
            self.hide_toolbar()
        else:
            self.show_toolbar()
