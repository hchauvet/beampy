# Manually list modules we want to use in beampy
from .figure import figure 
from .video import video 
from .itemize import itemize
from .rectangle import rectangle
from .svg import svg
from .text import text
from .title import title
from .maketitle import maketitle
from .box import box

__all__ = [
    'text',
    'title',
    'figure',
    'video',
    'itemize',
    'rectangle',
    'svg',
    'maketitle',
    'box'
]