#!/usr/bin/env python
#-*- coding:utf-8 -*-

from beampy import *

doc = document(cache=False)

slide('TEST')
e0 = text('toto', x=0.1, y=0.1)

begingroup(width=200,height=400, background='#888')
eg0 = text('totaaaao', x=0.1, y=0.1)
for i in range(2):
    print i
    text('tata', x=eg0.left+0.1, y=eg0.bottom+(0.1+i/5.))
endgroup()

#e3 = text('tutu', x=e0.left+0.1, y=e0.bottom+0.2)

#Buggy test
#e4 = text('youpt', x=0.4, y=eg0.bottom+{"align":"bottom","shift":0.0})

#text('youpt', x=e0.left+0.0, y=e0.bottom+0)
#print(doc._contents[gcs()]['element_keys'].index(e4.left.element_id))

display_matplotlib(gcs())
