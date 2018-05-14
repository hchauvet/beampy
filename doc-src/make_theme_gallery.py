"""
Script to loop over all theme to create a gallery for Beampy documentation.

"""

from beampy import *
import glob
import os

available_theme = glob.glob('../beampy/themes/*_theme.py')

def create_beampy_slides(theme, output_dir):

    doc = document(theme = theme)

    with slide():
        maketitle('Beampy with ``%s" theme' % theme,
                  date='now', subtitle='The subtitle goes here',
                  author=['Authors','goes','here'])


    with slide('Load this theme'):
        code('''
        from beampy import *
        doc = document(theme='%s')

        with slide():
            pass
        ''' % theme,
        language='python', width=500)

    with slide('Theme slide'):
        figure('./examples/ressources/test_0.svg', width=500)
        text('Test default positioning of this theme')

    save(output_dir+'theme_%s.html'%theme)


for theme in available_theme:
    theme_name = os.path.basename(theme).replace('_theme.py', '')
    print("Create slide for theme %s"%theme_name)

    create_beampy_slides(theme_name, './_static/theme_html_outputs/')
    
