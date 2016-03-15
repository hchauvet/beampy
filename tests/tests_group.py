#!/usr/bin/env python
#-*- coding:utf-8 -*-

from beampy import *

doc = document(cache=False)

slide('TEST')

begingroup(width=200,height=400, background='#888')
eg0 = text('totaaaao', x=0.1, y=0.1)
for i in range(2):
    text('tata', x=eg0.left+0.1, y=eg0.bottom+(0.1+i/5.))
endgroup()

eg1 = text('tututu', x=0.1, y=0.1)
others = []
for i in range(2):
    others += [text('tata', x=eg1.left+0.1, y=eg1.bottom+(0.1+i/5.))]
group([eg1]+others, x=0.1, y=0.1, width=200, height=400)

with group(x=0.6,y=0.1, width=200, height=400):
    eg4 = text('toaao', x=0.1, y=0.1)
    for i in range(2):
        text('tjtj', x=eg4.left+0.1, y=eg4.bottom+(0.1+i/5.))


    with group(x=eg4.left+0.1, y="+1cm", background="forestgreen"):
        egg = text('inside',x=0,y=0)
        for i in range(2):
            text("%i"%i, x=egg.left+0.1, y="+0.5cm")
#e3 = text('tutu', x=e0.left+0.1, y=e0.bottom+0.2)

#Buggy test
#e4 = text('youpt', x=0.4, y=eg0.bottom+{"align":"bottom","shift":0.0})

#text('youpt', x=e0.left+0.0, y=e0.bottom+0)
#print(doc._contents[gcs()]['element_keys'].index(e4.left.element_id))

display_matplotlib(gcs())
