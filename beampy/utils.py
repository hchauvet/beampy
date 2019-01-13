"""
Store functions that needs all beampy module
"""
from beampy import *


def draw_axes(dx=100, dy=100, show_ticks=False, grid_color='lightgray'):
    """
    Function to draw Beampy axis with a grid
    """
    
    grid(dx=dx, dy=dy, color=grid_color)
    ax=arrow(5, 5, document._width-35, 0)
    ay=arrow(5, 5, 0, document._height-35)
    text('$x$', x=ax.right+5, y=ax.top+0)
    text('$y$', x=ay.left+0, y=ay.bottom+5)

    if show_ticks:
        # add the positions in pixels
        for xt in range(0, document._width, dx):
            text('$x=%ipx$' % xt, x=xt, y=15, size=10)

        for yt in range(0, document._height, dx):
            text('$y=%ipx$' % yt, x=15, y=yt, size=10)

def bounding_box(element):
    """
    Function to add a bounding-box (border + anchors) to the given element.

    Parameters
    ----------

    element : Beampy Module
        The Beampy module class of the element to add the bounding box

    """

    # Add the border
    element.add_border()

    # Create rectangles to show anchors of the text box
    rw, rh = 10, 10

    anchor_selected = element.positionner.x['anchor'] + element.positionner.y['anchor']

    corners = [('lefttop', element.left, element.top),
               ('righttop', element.right, element.top),
               ('leftbottom', element.left, element.bottom),
               ('rightbottom', element.right, element.bottom),
               ('leftmiddle', element.left, element.center),
               ('middletop', element.center, element.top),
               ('rightmiddle', element.right, element.center),
               ('middlebottom', element.center, element.bottom),
               ('middlemiddle', element.center, element.center)]

    for args in corners:
        label, ex, ey = args
        rc = 'gray'
        if anchor_selected == label:
            rc = 'red'

        rectangle(x=ex + center(0), y=ey + center(0), width=rw, height=rh,
                  color=rc, edgecolor=None)


