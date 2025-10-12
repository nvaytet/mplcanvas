"""
mplcanvas: A matplotlib-compatible plotting library using ipycanvas
"""

__version__ = "0.1.0"

# Import key components for direct access
from . import pyplot
from .figure import Figure
from .axes import Axes

# For matplotlib compatibility
import matplotlib.rcsetup as _rcsetup

rcParams = _rcsetup.defaultParams.copy()

# Re-export pyplot functions at package level (like matplotlib)
from .pyplot import (
    subplots,
    figure,
)
