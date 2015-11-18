# -*- coding: utf-8 -*-
"""
@author: hugo

Here we define commands used to create elements in beampy

"""
import glob
import os
bppath = os.path.dirname(__file__) + '/'

#Core commands (slides, begingroup etc..)
from beampy.modules.core import *

#Specific commands with their renders
from beampy.modules.text import *
from beampy.modules.title import *
from beampy.modules.figure import *
from beampy.modules.animatesvg import *
from beampy.modules.video import *
from beampy.modules.tikz import *
from beampy.modules.maketitle import *
from beampy.modules.code import *

#Small functions 
#from beampy.modules.biblio import cite
from beampy.modules.arrow import arrow
from beampy.modules.itemize import itemize

