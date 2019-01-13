# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo
"""

from beampy import document
from beampy.modules.figure import figure
from beampy.modules.core import beampy_module
import tempfile
import os
from textwrap import dedent

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.formatters import SvgFormatter
    is_pigment = True
except:
    is_pigment = False

class code(beampy_module):
    """
    Add highlighted code syntax to your presentation. This module require pygments.

    Parameters
    ----------

    codetext : string
        Text of the code source to include.

    x : int or float or {'center', 'auto'} or str, optional
        Horizontal position for the code (the default is 'center'). See
        positioning system of Beampy.

    y : int or float or {'center', 'auto'} or str, optional
        Vertical position for the code (the default is 'auto'). See positioning
        system of Beampy.

    width : string, optional
        Width of the code (the default is :py:mod:`document._width`). The value
        is given as string with a unit accepted by svg syntax.

    language : string or None, optional
        Language of the source code (the default value is None, which implies
        that the language is guessed by pygments). See pygments language for
        available ones.

    size : string, optional
        Font size used to render the source code (the default is '14px').


    .. note::
       This module is in very draft stage !!!

    """

    def __init__(self, codetext, x='center', y='auto', width=None, language=None, size="14px"):
        #Transform the code to svg using pigment and then use the classic render for figure

        self.type = 'svg'
        self.content = dedent(codetext)

        self.x = x
        self.y = y

        if width is None:
            self.width = document._width
        else:
            self.width = width

        self.args = {"language": language, 'font_size': size }
        self.language = language
        self.font_size = size

        #TODO: Move this function to pre-render to be managed by cache
        #and not run at each beampy run
        # self.code2svg()

        if is_pigment:
            self.register()
        else:
            print("Python pygment is not installed, I can't translate code into svg...")

    def code2svg(self):
        """
            function to render code to svg
        """

        inkscapecmd = document._external_cmd['inkscape']
        codein = self.content


        #Try to infer the lexer
        if self.language is None:
            lexer = guess_lexer(codein)
        else:
            lexer = get_lexer_by_name(self.language, stripall=True)

        #Convert code to svgfile
        svgcode = highlight(codein, lexer, SvgFormatter(fontsize=self.font_size, style='tango'))

        #Create a tmpfile
        tmpfile, tmpname = tempfile.mkstemp(prefix='beampytmp_CODE')
        #tmppath = tmpname.replace(os.path.basename(tmpname),'')

        with open( tmpname+'.svg', 'w' ) as f:
            f.write(svgcode)

        #Convert svgfile with inkscape to transform text to path
        cmd = inkscapecmd + ' -z -T -l=%s %s'%(tmpname+'_good.svg', tmpname+'.svg')

        req = os.popen(cmd)
        req.close()

        f = figure(tmpname+'_good.svg', width=self.width.value, height=self.height.value)
        f.positionner = self.positionner
        f.render()
        self.svgout = f.svgout
        self.positionner = f.positionner
        self.width = f.width
        self.height = f.height

        self.update_size(self.width, self.height)
        f.delete()

        #remove files
        os.remove(tmpname+'.svg')
        os.remove(tmpname+'_good.svg')
        os.remove(tmpname)

    def render(self):
        self.code2svg()
        self.rendered = True
