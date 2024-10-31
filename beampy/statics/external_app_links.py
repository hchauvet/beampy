#!/usr/bin/env python3

"""
Create a dictionnay with the external links for executables used by Beampy.
"""
import os
from pathlib import Path

# Format is
#
# 'app_name': [('exec_name', 'alt_exec_name'),
#               'path/to/the/app',
#                mendatory]
#
# with mendatory a boolean to tels beampy if the application is optional or not.
# If the path is given as 'auto' -> then the executable will be automatically
# with an equivalent of the'which' command.

beampy_path = Path(os.path.dirname(__file__)).parent
__APPS__ = {
    'inkscape': ['inkscape', 'auto', False],
    'latex': ['latex', 'auto', True],
    'dvisvgm': ['dvisvgm', 'auto', True],
    'pdfjoin': ['pdfjoin', str(beampy_path/'external_tools'/'pdfjoin'), True],
    'video_encoder': [('ffmpeg', 'avconv'), 'auto', False],
    'pdf2svg': ['pdf2svg', 'auto', False],
    'epstopdf': ['epstopdf', 'auto', False]
}
