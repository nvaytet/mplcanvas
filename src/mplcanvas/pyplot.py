# mplcanvas/pyplot.py
"""
mplcanvas.pyplot: Matplotlib-compatible plotting interface using ipycanvas

This module provides a matplotlib.pyplot compatible API that renders
to ipycanvas for better performance in Jupyter notebooks.

Usage:
    import mplcanvas.pyplot as plt

    x = [1, 2, 3, 4]
    y = [1, 4, 2, 3]
    plt.plot(x, y)
    plt.show()
"""

from typing import Optional
from .figure import Figure
from .axes import Axes

# Global state (like matplotlib.pyplot)
_current_figure: Optional[Figure] = None
_current_axes: Optional[Axes] = None


# Figure management
def figure(num=None, figsize=(8, 6), dpi=100, facecolor="white", **kwargs) -> Figure:
    """
    Create a new figure or retrieve an existing figure.

    Parameters match matplotlib.pyplot.figure()
    """
    global _current_figure, _current_axes

    fig = Figure(figsize=figsize, dpi=dpi, facecolor=facecolor, **kwargs)
    _current_figure = fig
    _current_axes = None  # Reset current axes

    return fig


def subplots(nrows=1, ncols=1, figsize=(8, 6), **kwargs):
    """
    Create a figure and subplots.

    Returns (fig, ax) or (fig, axes_array) to match matplotlib exactly.
    """
    global _current_figure, _current_axes

    fig = figure(figsize=figsize, **kwargs)

    if nrows == 1 and ncols == 1:
        ax = fig.add_subplot(1, 1, 1)
        _current_axes = ax
        return fig, ax
    else:
        # TODO: Implement multiple subplots
        raise NotImplementedError("Multiple subplots not yet implemented")
