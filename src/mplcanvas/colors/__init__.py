# mplcanvas/colors/__init__.py
"""
Color handling - initially delegate to matplotlib.colors
"""

try:
    # Import everything from matplotlib.colors
    from matplotlib.colors import *
    from matplotlib import colors as _mpl_colors

    # Re-export the module for full compatibility
    __all__ = _mpl_colors.__all__

except ImportError:
    # Fallback implementations if matplotlib not available
    # TODO: Implement basic color handling
    pass
