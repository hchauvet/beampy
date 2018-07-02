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
    rw, rh = 5, 5

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


def box(group_object, title=None, rounded=10, linewidth=1,
        color='red', head_height=30, shadow=False,
        background_color='white', title_color='white',
        title_align='left', title_xoffset=10):
    """
    Draw a box around a group.

    Parameters
    ----------
    
    group_object : beampy.group object
        The beampy group to apply the box 

    title : str or None, optional
        The title of the box (the default value is None, which implies
        no title).
    
    rounded : int, optional
        The number of pixel for rounded borders (the default value is
        10).

    linewidth : int, optional
        The linewidth of the border in pt (the default value is 1).

    color : svg color name as string, optional
        The color of the contour line of the box (the default value is
        'red').

    head_height : int, optional
        The height in pixel of the background under the title (the
        default is 30, which corresponds of a one line title). You
        need to adjust this value for multi-lines titles.

    shadow : boolean, optional
        Draw a shadow under the box (the default value is False, which
        means no shadow).

    background_color : svg color name as string, optional
        The color of the background of the box (the default values is
        'white').

    title_color : svg color name as string, optional
        The color of the title (the default value is 'white').

    title_align : {'left','right','center'}, optional
        The horizontal alignment of the title (the default value is
        'left').

    title_xoffset : int, optional
        The horizontal offset in pixel from the box border of the
        title (the default value is 10).
    """
    if shadow:
        svg_shadow = 'filter="url(#drop-shadow)"'
    else:
        svg_shadow = ''

    # Add filter and clip-path to the svg </defs> tag of the slide
    cslide = document._slides[gcs()]
    cslide.svgdefout += [
        '''
        <filter id="drop-shadow"> <feGaussianBlur in="SourceAlpha"
        stdDeviation="3"/> <feOffset dx="4" dy="4" result="offsetblur"/>
        <feMerge> <feMergeNode/> <feMergeNode in="SourceGraphic"/> </feMerge>
        </filter>

        <clipPath id="boxborder_{id}">
        <rect width="{width}" height="{height}"
        rx="{rounded}" ry="{rounded}" stroke="{color}" stroke-width="{lw}"/>
        </clipPath>
        '''.format(width=group_object.width,
                   height=group_object.height,
                   rounded=rounded,
                   color=color,
                   id=group_object.id,
                   lw=linewidth)
    ]


    svg('''
    <rect width="{width}" height="{height}"
    stroke="{color}" fill="{bgcolor}" stroke-width="{lw}"
    rx="{rounded}" ry="{rounded}" {filter}/>
    '''.format(width=group_object.width,
               height=group_object.height,
               rounded=rounded,
               color=color,
               lw=linewidth,
               bgcolor=background_color,
               filter=svg_shadow),
    x=group_object.center+center(0),
    y=group_object.center+center(0))

    if title is not None:
        s = svg('''
               <rect x="0" y="0" width="{width}" height="{height}"
               fill="{color}" stroke-width="{lw}" stroke="{color}"
               clip-path="url(#boxborder_{id})"/>'''.format(width=group_object.width,
                                                            height=head_height,
                                                            color=color, lw=linewidth,
                                                            id=group_object.id),
                x=group_object.left-'%fpx' % (linewidth/2.),
                y=group_object.top-"%fpx" % (linewidth/2.))

        xpos = title_xoffset
        
        if title_align == 'center':
            xpos = 'center'

        if title_align == 'right':
            xpos = {'anchor':'right', 'shift':xpos, 'align':'right'}
            
        t = text(title, x=xpos, y=5, color=title_color,
                 width=group_object.width-20)

        # Add y offset to the group (the height taken by the title)
        group_object.yoffset = head_height
