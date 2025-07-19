from beampy import *

doc = document(cache=False, optimize=False)

with slide():
    animatesvg("./svg_anims/*.svg", start=0, end=3, width="500", x='center', y='center')
    # with group(width=0.5)[1]:
    #       aa = animatesvg("./svg_anims/*.svg", width="0.5", end=4, x=10, y=10, autoplay=True)
    
"""
with slide('Animate with layers'):
    animatesvg("./svg_anims/*.svg", width="500", end=3, x='center', y='center')[0]
    animatesvg("./svg_anims/*.svg", width="100", end=3, x='0.1', y='0.1')[1]
"""

with slide('Animate with group recursion'):
    with group():
        animatesvg("./svg_anims/*.svg", end=3, width="500")
        with group():
            animatesvg("./svg_anims/*.svg", end=3, width="100")
            
save('./svg_animation.html')
