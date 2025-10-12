# mplcanvas/events/pick.py
"""
Artist picking events
"""

from dataclasses import dataclass
from typing import Any
from .mouse import MouseEvent


@dataclass
class PickEvent:
    """
    Pick event data structure, similar to matplotlib.backend_bases.PickEvent
    """

    name: str  # 'pick_event'
    artist: Any  # The picked artist
    mouseevent: MouseEvent  # The mouse event that triggered the pick
