import pytest
from beampy import *

# import logging
# logging.basicConfig(level=logging.DEBUG)

test_name = 'test_box'

@pytest.fixture
def make_presentation():
    doc = document(cache=False, optimize=False)

    with slide('Add nice boxes to group'):

        with box(title='Very very very long box title', width=300, height=500, x=20, y='center') as g:
            text('Box text')

        with box(title='Change color and drop-shadow', title_align='center', color='Crimson',
                 shadow=True, width=450, x=g.right+10, y=g.top+0) as g2:
            tt = text('Box text, with a centered title', y=10, x='center')
            tt = text('tutututu tutut tutuu', y=tt.bottom+5)

            with group(width='50%', y=tt.bottom+10):
                rectangle(height=20, width='100%')


        with box(title='right title', title_align='right', width=450, x=g2.left+0,
                 y=g2.bottom+20, height=200, color='RoyalBlue') as g3:

            text('Test with auto placed elements')
            text('With a given height to the group')

        with box(color='darkorange', rounded=70, background_color='lightgray', linewidth=4,
                 width=450, x=g.right+10, y=g3.bottom+20) as g4:

            text('''
                Without title for the box, more rounded angle, bigger
                linewidth, and a background color
                ''', align='center', width="80%")
    return doc


def test_html(make_presentation):
    doc = make_presentation
    save('./html_out/%s.html' % test_name)


def test_pdf(make_presentation):
    doc = make_presentation
    save('./pdf_out/%s.pdf' % test_name)
