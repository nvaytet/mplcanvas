# mplcanvas/events/mouse.py
"""
Mouse event handling for mplcanvas axes
"""

from typing import Callable, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MouseEvent:
    """
    Mouse event data structure, similar to matplotlib.backend_bases.MouseEvent
    """

    name: str  # 'button_press_event', 'button_release_event', 'motion_notify_event'
    canvas_x: float  # Canvas pixel coordinates
    canvas_y: float
    data_x: float  # Data coordinates
    data_y: float
    button: Optional[int] = None  # 1=left, 2=middle, 3=right
    key: Optional[str] = None  # Modifier keys
    dblclick: bool = False
    inaxes: Optional["Axes"] = None  # Which axes the event occurred in


class MouseEventMixin:
    """
    Mixin class to add mouse event handling to Axes.

    This provides matplotlib-compatible mouse event handling using ipycanvas events.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Event callback lists
        self._mouse_press_callbacks: List[Callable] = []
        self._mouse_release_callbacks: List[Callable] = []
        self._mouse_motion_callbacks: List[Callable] = []
        self._pick_callbacks: List[Callable] = []

        # Mouse state tracking
        self._mouse_pressed = False
        self._last_click_time = 0
        self._last_click_pos = (0, 0)
        self._double_click_threshold = 0.3  # seconds
        self._pick_tolerance = 5  # pixels

        # Current mouse position (for cursor display)
        self._current_mouse_pos = None

    def _setup_mouse_events(self):
        """Setup mouse event handlers on the canvas"""
        if hasattr(self, "canvas"):
            self.canvas.on_mouse_down(self._on_canvas_mouse_down)
            self.canvas.on_mouse_up(self._on_canvas_mouse_up)
            self.canvas.on_mouse_move(self._on_canvas_mouse_move)

    def _on_canvas_mouse_down(self, x: float, y: float):
        """Handle canvas mouse down events"""
        import time

        # Check if this is in our axes
        if not self._point_in_axes(x, y):
            return

        # Convert to data coordinates
        data_x, data_y = self.transData.inverse_transform(x, y)

        # Check for double click
        current_time = time.time()
        dblclick = False
        if (
            current_time - self._last_click_time < self._double_click_threshold
            and abs(x - self._last_click_pos[0]) < 5
            and abs(y - self._last_click_pos[1]) < 5
        ):
            dblclick = True

        self._last_click_time = current_time
        self._last_click_pos = (x, y)
        self._mouse_pressed = True

        # Create mouse event
        event = MouseEvent(
            name="button_press_event",
            canvas_x=x,
            canvas_y=y,
            data_x=data_x,
            data_y=data_y,
            button=1,  # Left click for now (ipycanvas doesn't distinguish)
            dblclick=dblclick,
            inaxes=self,
        )

        # Call registered callbacks
        for callback in self._mouse_press_callbacks:
            callback(event)

        # Check for picking
        self._check_picking(event)

    def _on_canvas_mouse_up(self, x: float, y: float):
        """Handle canvas mouse up events"""
        if not self._point_in_axes(x, y):
            return

        data_x, data_y = self.transData.inverse_transform(x, y)
        self._mouse_pressed = False

        event = MouseEvent(
            name="button_release_event",
            canvas_x=x,
            canvas_y=y,
            data_x=data_x,
            data_y=data_y,
            button=1,
            inaxes=self,
        )

        for callback in self._mouse_release_callbacks:
            callback(event)

    def _on_canvas_mouse_move(self, x: float, y: float):
        """Handle canvas mouse move events"""
        # Always track mouse position for cursor display
        self._current_mouse_pos = (x, y)

        if not self._point_in_axes(x, y):
            return

        data_x, data_y = self.transData.inverse_transform(x, y)

        event = MouseEvent(
            name="motion_notify_event",
            canvas_x=x,
            canvas_y=y,
            data_x=data_x,
            data_y=data_y,
            inaxes=self,
        )

        for callback in self._mouse_motion_callbacks:
            callback(event)

    def _point_in_axes(self, canvas_x: float, canvas_y: float) -> bool:
        """Check if a canvas point is within this axes"""
        return (
            self.x <= canvas_x <= self.x + self.width
            and self.y <= canvas_y <= self.y + self.height
        )

    def _check_picking(self, event: MouseEvent):
        """Check if any artists can be picked at this location"""
        from .pick import PickEvent

        picked_artists = []

        # Check lines
        for line in self.lines:
            if hasattr(line, "picker") and line.picker is not None:
                if line.contains_point(event.canvas_x, event.canvas_y):
                    picked_artists.append(line)

        # Check collections (scatter plots, etc.)
        for collection in getattr(self, "collections", []):
            if hasattr(collection, "picker") and collection.picker is not None:
                if collection.contains_point(event.canvas_x, event.canvas_y):
                    picked_artists.append(collection)

        # Fire pick events
        for artist in picked_artists:
            pick_event = PickEvent(name="pick_event", artist=artist, mouseevent=event)

            for callback in self._pick_callbacks:
                callback(pick_event)

    # Public API for registering event handlers (matplotlib-compatible)
    def mpl_connect(self, event_type: str, callback: Callable) -> int:
        """
        Connect a callback to a mouse event.

        Parameters:
        -----------
        event_type : str
            'button_press_event', 'button_release_event', 'motion_notify_event', 'pick_event'
        callback : callable
            Function to call when event occurs

        Returns:
        --------
        int : Connection id (for disconnecting later)
        """
        if event_type == "button_press_event":
            self._mouse_press_callbacks.append(callback)
            return len(self._mouse_press_callbacks) - 1
        elif event_type == "button_release_event":
            self._mouse_release_callbacks.append(callback)
            return len(self._mouse_release_callbacks) - 1
        elif event_type == "motion_notify_event":
            self._mouse_motion_callbacks.append(callback)
            return len(self._mouse_motion_callbacks) - 1
        elif event_type == "pick_event":
            self._pick_callbacks.append(callback)
            return len(self._pick_callbacks) - 1
        else:
            raise ValueError(f"Unknown event type: {event_type}")

    def mpl_disconnect(self, cid: int):
        """Disconnect a callback (simplified implementation)"""
        # TODO: Implement proper connection tracking
        pass

    # Convenience methods
    def add_mouse_callback(self, callback: Callable):
        """Add a callback for mouse motion events (for cursor position display)"""
        self._mouse_motion_callbacks.append(callback)

    def add_click_callback(self, callback: Callable):
        """Add a callback for mouse click events"""
        self._mouse_press_callbacks.append(callback)

    def add_pick_callback(self, callback: Callable):
        """Add a callback for artist picking events"""
        self._pick_callbacks.append(callback)

    def get_cursor_position(self) -> Optional[Tuple[float, float]]:
        """
        Get current cursor position in data coordinates.
        Returns None if cursor is not over the axes.
        """
        if self._current_mouse_pos is None:
            return None

        x, y = self._current_mouse_pos
        if self._point_in_axes(x, y):
            return self.transData.inverse_transform(x, y)
        return None
