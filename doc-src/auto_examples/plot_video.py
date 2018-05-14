"""
video
=====

Add video to your slide.

"""

from beampy import *

# Remove quiet=True to get beampy compilation outputs
doc = document(quiet=True)

with slide('Video module'):
    video('./ressources/test.webm', still_image_time=5.5)

display_matplotlib(gcs())
save('./examples_html_outputs/video.html')


##########################################################
#
#HTML output
#===========
#
#.. raw:: html
#
#    <iframe src="../_static/examples_html_outputs/video.html" width="100%" height="500px"></iframe>
#
#
#Module arguments
#================
#
#.. autoclass:: beampy.video
#   :noindex:
#
