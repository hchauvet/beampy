import pytest
from beampy import *

import logging
logging.basicConfig(level=logging.DEBUG)

test_name = 'test_TOC'

@pytest.fixture
def make_presentation():
    print(__name__)
    doc = document(source_filename=__name__)

    with slide():
        maketitle('Test Table of Contents')

    section('test')
    subsection('totot')
    with slide('toto'):
        aa = tableofcontents(currentsection=True, subsection=True, subsubsection=False)

    subsubsection('tatata')

    with slide('tata'):
        c1 = circle(x='center', y='center', r=10, linewidth="1px",
                   edgecolor="red")
        c = circle(x='center', y='center', r=10, linewidth="5px",
                   edgecolor="yellow", opacity=0.7)
        c1.add_border()

    section('The second section is about important things!')
    with slide('The second section'):
        c1 = rectangle(x='center', y='center', width=100, height=100, linewidth="1px",
                   edgecolor="red")
        c1.add_border()

        c = rectangle(x='center', y='center', width=c1.width, height=c1.height, linewidth="5px",
                      edgecolor="yellow", opacity=0.5)[1]
        c.add_border()


    subsection('The thing number 1')
    with slide('sub 1'):
        pass

    subsection('The second thind')
    with slide('sub 2'):
        pass

    subsubsection('Argument A')

    with slide('tutu'):
        tableofcontents(currentsubsection=True, hideothersubsection=True, section_style='square')

    subsubsection('Argument B')
    subsubsection('Argument C')

    subsection('The last one')
    with slide():
        pass

    section('The final section about the presentation')
    subsection('The thing number 1')
    subsection('The second thind')
    subsection('The last one')

    with slide('jksqlfjkqs sldjfmlqsj'):
        aa=tableofcontents(subsection=True, currentsection=True, sections=[1,2], width=350)[:]
        bb=tableofcontents(subsection=True, currentsection=True, sections=[3,4], width=350,
                           x=aa.right+5, y=aa.top+0)[1]
        aa.add_border()
        bb.add_border()

    with slide('Test'):
        pass

    with slide('CAPITAL TITLE'):
        pass
    # print(doc._TOC)

    section('Conclusion')
    with slide('Conclusion'):
        pass

    return doc


def test_html(make_presentation):
    doc = make_presentation
    save('./html_out/%s.html' % test_name)


def test_pdf(make_presentation):
    doc = make_presentation
    save('./pdf_out/%s.pdf' % test_name)
