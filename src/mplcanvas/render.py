import numpy as np


def flip_y(y, canvas):
    """Flip y coordinate for canvas (top-left origin)"""
    return canvas.height - y


def draw_line(line, ax, canvas):
    # Get data coordinates
    xdata = line.get_xdata()
    ydata = line.get_ydata()

    if len(xdata) == 0 or len(ydata) == 0:
        return

    x, y = ax.transData.transform(np.array((xdata, ydata)).T).T
    y = flip_y(y, canvas)

    canvas.stroke_style = line.get_color()
    canvas.line_width = line.get_linewidth()
    # Use numpy array for efficient drawing
    points = np.column_stack([x, y])
    canvas.stroke_lines(points)


def draw_axes(ax, canvas):
    # Draw frame

    # Apparently need to ask the axis limits for them to be set correctly
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    # (xmin_disp, ymin_disp), (xmax_disp, ymax_disp) = ax.transData.transform(
    #     ((xmin, ymin), (xmax, ymax))
    # )
    # width = xmax_disp - xmin_disp
    # height = ymax_disp - ymin_disp
    # print(f"Drawing axes at {xmin_disp},{ymin_disp} size {width}x{height}")

    # # Set clipping region to axes area
    # canvas.save()
    # canvas.begin_path()
    # canvas.rect(xmin_disp, ymin_disp, width, height)
    # canvas.clip()

    # Draw all line artists
    for line in ax.lines:
        draw_line(line, ax, canvas)

    # # Draw frame
    # xmin, xmax = ax.get_xlim()
    # ymin, ymax = ax.get_ylim()
    (xmin_disp, ymin_disp), (xmax_disp, ymax_disp) = ax.transData.transform(
        ((xmin, ymin), (xmax, ymax))
    )
    width = xmax_disp - xmin_disp
    height = ymax_disp - ymin_disp
    print(f"Drawing axes at {xmin_disp},{ymin_disp} size {width}x{height}")

    canvas.stroke_style = "black"
    canvas.line_width = 1.0
    canvas.stroke_rect(xmin_disp, ymin_disp, width, height)
