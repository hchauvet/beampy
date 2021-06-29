# -*- coding: utf-8 -*-
"""
@author: hugo

Here we define commands used to create elements in beampy

"""
#Core commands (slides, begingroup etc..)
from beampy.core.module import beampy_module
from beampy.core.group import group
from beampy.core.slide import slide
from beampy.core.document import (document, section,
                                  subsection, subsubsection)

#Specific commands with their renders
from beampy.modules.biblio import cite
from beampy.modules.text import *
from beampy.modules.title import *
from beampy.modules.figure import *
from beampy.modules.animatesvg import *
from beampy.modules.video import *
from beampy.modules.tikz import *
from beampy.modules.code import *
from beampy.modules.svg import *
from beampy.modules.box import *
from beampy.modules.toc import tableofcontents
from beampy.modules.iframe import iframe

#Small functions
from beampy.modules.arrow import arrow
from beampy.modules.itemize import itemize
from beampy.modules.maketitle import *

# Minor classes
from beampy.modules.biblio import bibliography
