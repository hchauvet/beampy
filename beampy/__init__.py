#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Beampy main file to manage imports
"""
from beampy._version import __version__

__all__ = ['__version__']

# from beampy.commands import *
from beampy.modules import *
from beampy.modules import __all__ as modules_all 
__all__ += modules_all

from beampy.core import *
from beampy.core import __all__ as core_all
__all__ += core_all
