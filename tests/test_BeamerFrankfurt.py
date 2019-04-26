import pytest
from beampy import *

test_name = 'test_theme_beamerFrankfurt'

@pytest.fixture
def make_presentation():
    doc = document(cache=True,
                   theme='BeamerFrankfurt',
                   source_filename = __name__)

    with slide():
        maketitle('Beampy a tool to make simple or complex presentation from python to SVG/HTML',
                  ['Alexandra A.$^1$', 'Bob B.$^2$', ' Pierre P.$^3$', 'Hugo C.$^4$', 'Gabin~G.$^2$'], lead_author=3,
                  affiliation=['$^1$University of Python, France', '$^2$University of Beamer, Germany',
                               '$^3$University with a very very long affiliation, United State of America',
                               '$^4$Test university, Japan', '$^5$SVG University, Russia'],
                  meeting='Conference on nice program for presentation', date='now')

    section('Introduction')
    subsection('Test of box in BeamerFrankfurt Theme')
    with slide('Table of content'):
        aa = tableofcontents(currentsection=False, subsection=True)


    with slide('Box'):
        with box(title='Lorem Ipsum:', width='90%'):
            text('Lorem ipsum sapientem ne neque dolor erat,eros solet invidunt duo Quisque aliquid leo. Pretium patrioque sociis eu nihil Cum enim ad, ipsum alii vidisse justo id. Option porttitor diam voluptua. Cu Eam augue dolor dolores quis, Nam aliquando elitr Etiam consetetur. Fringilla lucilius mel adipiscing rebum. Sit nulla Integer ad volumus, dicta scriptorem viderer lobortis est Utinam, enim commune corrumpit Aenean erat tellus. Metus sed amet dolore justo, gubergren sed. ',
                 width='90%')

    section('The second section is about important things!')
    with slide('The second section'):
        itemize(['Item 1', 'Item 2', 'Item 3'])

    subsection('The thing number 1')
    subsection('The second thind')

    with slide('The second subsection'):
        pass

    subsection('The last one')

    section('The final section about the presentation')
    subsection('The thing number 1')
    subsection('The second thind')
    subsection('The last one')

    with slide('CAPITAL TITLE'):
        pass

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
