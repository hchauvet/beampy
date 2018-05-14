from beampy import *

doc = document()

with slide("My first slide"):
    grid(50, 50, color="lightgray", linewidth=0.5)
    e = text('Hello Beampy!', x='50', y='50')
    e.add_border()


save('hello.html')
