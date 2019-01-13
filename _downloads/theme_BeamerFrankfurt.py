"""
BeamerFrankfurt
===============

Port of the Beamer frankfurt theme to Beampy (with an headerbar that display TOC).

"""

from beampy import *

doc = document(theme="BeamerFrankfurt", quiet=True)

with slide():
    maketitle('''Beampy theme ``BeamerFrankfurt" inspired by it's Beamer version''',
              author=['Author 1$^1$', 'Author 2$^2$'],
              lead_author=1,
              meeting='Beampy Users Meeting (BUM 2018)',
              affiliation=['$^1$From Univ. of Python', '$^2$From university of HTML5, Paris'],
              date='now')

section('Introduction')
with slide('Table of content'):
    tableofcontents()

section('Main talk topic')
subsection('Subtopic 1')
subsection('Subtopic 2')
with slide('Subtopic2: Nice box'):
    with box(title='Lorem Ipsum:', width='90%'):
        text('''Lorem ipsum sapientem ne neque dolor erat,eros solet
        invidunt duo Quisque aliquid leo. Pretium patrioque sociis eu
        nihil Cum enim ad, ipsum alii vidisse justo id. Option
        porttitor diam voluptua. Cu Eam augue dolor dolores quis, Nam
        aliquando elitr Etiam consetetur. Fringilla lucilius mel
        adipiscing rebum. Sit nulla Integer ad volumus, dicta
        scriptorem viderer lobortis est Utinam, enim commune corrumpit
        Aenean erat tellus. Metus sed amet dolore justo, gubergren
        sed. ''', width='90%')
        
subsection('Subtopic 3')

section('Conclusion')
with slide('Last slide'):
    pass

for sl in range(4):
    display_matplotlib('slide_%i' % sl)
