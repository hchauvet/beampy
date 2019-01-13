from beampy import *


doc = document(cache=False)

with slide():
    arrow(x=10, y=0.1, dx=780, dy=0, lw=6, color='Crimson')

save('./html_out/arrow.html')
