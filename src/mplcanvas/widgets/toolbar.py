# mplcanvas/widgets/toolbar.py
"""
Navigation toolbar for mplcanvas - operates on any axes in the figure
"""

import ipywidgets as widgets


class NavigationToolbar(widgets.VBox):
    """
    Navigation toolbar that can operate on any axes in the figure.

    Similar to matplotlib's NavigationToolbar2 - activates tools that work
    on whichever axes the user interacts with.
    """

    def __init__(self, figure, **kwargs):
        self.figure = figure

        # Tool state
        self._active_tool = None  # 'zoom', 'pan', or None
        self._zoom_rect_start = None
        self._pan_start = None
        self._pan_start_limits = None
        self._active_axes = None  # Which axes is currently being interacted with
        self._tools_lock = False

        # Store home views for all axes (will be populated as axes are added)
        self._home_views = {}  # {axes_id: (xlim, ylim)}

        # Create toolbar buttons
        self._create_buttons()

        # Set up event connections - we'll connect to all axes
        self._setup_event_connections()

        # Initialize as VBox
        super().__init__(
            children=[self.button_box], layout=widgets.Layout(width="auto"), **kwargs
        )

    def _create_buttons(self):
        """Create toolbar buttons"""
        # Button styling
        button_style = widgets.ButtonStyle()
        button_layout = widgets.Layout(width="37px", padding="0px 0px 0px 0px")

        # Home button
        self.home_button = widgets.Button(
            # description="🏠",
            icon="fa-home",
            tooltip="Reset all axes to home view",
            style=button_style,
            layout=button_layout,
        )
        self.home_button.on_click(self._on_home_clicked)

        # Pan button
        self.pan_button = widgets.ToggleButton(
            icon="fa-arrows",
            tooltip="Pan tool - drag to move any plot",
            style=button_style,
            layout=button_layout,
        )
        self.pan_button.observe(self._on_pan_clicked, names="value")

        # Zoom button
        self.zoom_button = widgets.ToggleButton(
            icon="fa-square-o",
            tooltip="Zoom tool - drag to select zoom region on any plot",
            style=button_style,
            layout=button_layout,
        )
        self.zoom_button.observe(self._on_zoom_clicked, names="value")

        # # Status label
        # self.status_label = widgets.Label(
        #     value="Ready", layout=widgets.Layout(margin="10px 5px")
        # )

        # Arrange buttons vertically
        self.button_box = widgets.VBox(
            [self.home_button, self.pan_button, self.zoom_button],
            layout=widgets.Layout(align_items="center"),
        )

    def add_axes(self, axes):
        """
        Add an axes to be managed by this toolbar.
        Called when new axes are created in the figure.
        """
        # Store home view for this axes
        self._store_home_view(axes)

        # Connect to this axes' mouse events
        axes.add_mouse_callback(self._on_mouse_move)
        axes.add_click_callback(self._on_mouse_press)
        axes._mouse_release_callbacks.append(self._on_mouse_release)

    def _store_home_view(self, axes):
        """Store the current view of an axes as its home view"""
        axes_id = id(axes)
        self._home_views[axes_id] = (axes.get_xlim(), axes.get_ylim())

    def _setup_event_connections(self):
        """Connect to all existing axes in the figure"""
        for axes in self.figure.axes:
            self.add_axes(axes)

    def _update_button_states(self):
        """Update button appearance based on active tool"""
        # Reset all button styles
        normal_style = widgets.ButtonStyle()
        active_style = widgets.ButtonStyle(button_color="lightblue")

        self.home_button.style = normal_style
        self.pan_button.style = (
            active_style if self._active_tool == "pan" else normal_style
        )
        self.zoom_button.style = (
            active_style if self._active_tool == "zoom" else normal_style
        )

    def _determine_active_axes(self, event):
        """
        Determine which axes this mouse event belongs to.
        This is key - we work on whichever axes the user is interacting with.
        """
        # The event should have inaxes set by the axes' mouse handler
        if hasattr(event, "inaxes") and event.inaxes is not None:
            return event.inaxes

        # Fallback: check all axes to see which one contains the event
        for axes in self.figure.axes:
            if axes._point_in_axes(event.canvas_x, event.canvas_y):
                return axes

        return None

    # Button event handlers
    def _on_home_clicked(self, button):
        """Reset all axes to home view"""
        for axes in self.figure.axes:
            axes_id = id(axes)
            if axes_id in self._home_views:
                xlim, ylim = self._home_views[axes_id]
                axes.set_xlim(*xlim)
                axes.set_ylim(*ylim)

        # self.status_label.value = "Reset all axes to home view"
        self._active_tool = None
        # self._update_button_states()

    def _on_pan_clicked(self, change):
        """Activate/deactivate pan tool"""
        if self._tools_lock:
            return
        if self._active_tool == "pan":
            self._active_tool = None
            # self.status_label.value = "Pan tool deactivated"
        else:
            self._active_tool = "pan"
            # self.status_label.value = "Pan tool active - drag on any plot to move it"
        self._update_button_states()

    def _on_zoom_clicked(self, button):
        """Activate/deactivate zoom tool"""
        if self._tools_lock:
            return
        if self._active_tool == "zoom":
            self._active_tool = None
            # self.status_label.value = "Zoom tool deactivated"
        else:
            self._active_tool = "zoom"
            # self.status_label.value = (
            #     "Zoom tool active - drag on any plot to select region"
            # )
        self._update_button_states()

    # Mouse event handlers
    def _on_mouse_move(self, event):
        """Handle mouse movement for active tools"""
        if self._active_tool == "pan" and self._pan_start is not None:
            # Continue pan on the same axes we started on
            if self._active_axes == event.inaxes:
                self._do_pan(event)
        elif self._active_tool == "zoom" and self._zoom_rect_start is not None:
            # Continue zoom on the same axes we started on
            if self._active_axes == event.inaxes:
                self._update_zoom_preview(event)

    def _on_mouse_press(self, event):
        """Handle mouse press for active tools"""
        if self._active_tool == "pan":
            self._active_axes = self._determine_active_axes(event)
            if self._active_axes:
                self._start_pan(event)
        elif self._active_tool == "zoom":
            self._active_axes = self._determine_active_axes(event)
            if self._active_axes:
                self._start_zoom(event)

    def _on_mouse_release(self, event):
        """Handle mouse release for active tools"""
        if self._active_tool == "pan" and self._pan_start is not None:
            if self._active_axes == self._determine_active_axes(event):
                self._end_pan()
        elif self._active_tool == "zoom" and self._zoom_rect_start is not None:
            if self._active_axes == self._determine_active_axes(event):
                self._end_zoom(event)

    # Pan implementation (now works on self._active_axes)
    def _start_pan(self, event):
        """Start panning operation on the active axes"""
        self._pan_start = (event.data_x, event.data_y)
        self._pan_start_limits = (
            self._active_axes.get_xlim(),
            self._active_axes.get_ylim(),
        )
        # self.status_label.value = "Panning axes..."

    def _do_pan(self, event):
        """Perform panning on the active axes"""
        if (
            self._pan_start is None
            or self._pan_start_limits is None
            or self._active_axes is None
        ):
            return

        # Calculate delta in data coordinates
        dx = event.data_x - self._pan_start[0]
        dy = event.data_y - self._pan_start[1]

        # Apply pan (move in opposite direction)
        start_xlim, start_ylim = self._pan_start_limits
        new_xlim = (start_xlim[0] - dx, start_xlim[1] - dx)
        new_ylim = (start_ylim[0] - dy, start_ylim[1] - dy)

        self._active_axes.set_xlim(*new_xlim)
        self._active_axes.set_ylim(*new_ylim)

    def _end_pan(self):
        """End panning operation"""
        self._pan_start = None
        self._pan_start_limits = None
        self._active_axes = None
        # self.status_label.value = "Pan complete"

    # Zoom implementation (now works on self._active_axes)
    def _start_zoom(self, event):
        """Start zoom selection on the active axes"""
        self._zoom_rect_start = (event.data_x, event.data_y)
        # self.status_label.value = "Selecting zoom region..."

    def _update_zoom_preview(self, event):
        """Update zoom rectangle preview"""
        if self._zoom_rect_start is not None and self._active_axes is not None:
            x0, y0 = self._zoom_rect_start
            x1, y1 = event.data_x, event.data_y
            width = abs(x1 - x0)
            height = abs(y1 - y0)
            # self.status_label.value = f"Zoom region: {width:.2f} × {height:.2f}"

    def _end_zoom(self, event):
        """Complete zoom operation on the active axes"""
        if self._zoom_rect_start is None or self._active_axes is None:
            return

        x0, y0 = self._zoom_rect_start
        x1, y1 = event.data_x, event.data_y

        # Ensure we have a proper rectangle (not just a click)
        min_size = 0.01  # Minimum zoom region size
        if abs(x1 - x0) < min_size or abs(y1 - y0) < min_size:
            # self.status_label.value = "Zoom region too small"
            self._zoom_rect_start = None
            self._active_axes = None
            return

        # Set new limits on the active axes
        new_xlim = (min(x0, x1), max(x0, x1))
        new_ylim = (min(y0, y1), max(y0, y1))

        self._active_axes.set_xlim(*new_xlim)
        self._active_axes.set_ylim(*new_ylim)

        self._zoom_rect_start = None
        self._active_axes = None
        # self.status_label.value = "Zoomed"
