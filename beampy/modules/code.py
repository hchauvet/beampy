# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo
"""
from beampy.core.store import Store
from beampy.core.document import document
from beampy.core.module import beampy_module
from beampy.modules.figure import figure
import tempfile
import os
from textwrap import dedent

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.formatters import SvgFormatter
    is_pigment = True
except Exception:
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

    def __init__(self, codetext, x=None, y=None, width=None, height=None, margin=None,
                 language=None, font_size=None, code_style=None, *args, **knwargs):
        
        # dedent code
        codetext = dedent(codetext)

        if width is None:
            width = Store.current_width()
        
        super().__init__(x, y, width, height, margin, 'svg', **knwargs)
        
        # Update the signature
        self.update_signature()
        
        self.set(content=codetext, language=language, 
                 font_size=font_size, code_style=code_style)
        
        self.apply_theme(exclude=['language'])
        
        if is_pigment:
            # This command trigger the render
            self.add_content(codetext, 'svg')
        else:
            print("Python pygment is not installed, I can't translate code into svg...")
            
    def code2svg(self):
        """
            function to render code to svg
        """

        inkscapecmd = Store.get_exec('inkscape')
        codein = self.content

        # Try to infer the lexer
        if self.language is None:
            lexer = guess_lexer(codein)
        else:
            lexer = get_lexer_by_name(self.language, stripall=True)

        # Convert code to svgfile
        svgcode = highlight(codein, lexer, 
                            SvgFormatter(fontsize=self.font_size, 
                                         style=self.code_style))

        # Use tempfile.NamedTemporaryFile, that automaticly delete the file on close by default
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', prefix='beampytmp_CODE') as f:
            tmpname, tmpext = os.path.splitext(f.name)
            f.write(svgcode)

            # Need to flush the file to write it to disk
            f.file.flush()
            
            # Convert svgfile with inkscape to transform text to path
            cmd = inkscapecmd + f' --export-text-to-path --export-filename={tmpname + "_good.svg"} {f.name}'
            
            req = os.popen(cmd)
            req.close()

        f = figure(tmpname + '_good.svg', 
                   x=0, y=0,
                   width=None, 
                   height=None,
                   add_to_slide=False,
                   add_to_group=False)

        self.svgdef = f.svgdef
        self.content_width = f.content_width
        self.content_height = f.content_height
        self.width = f.content_width
        self.height = f.content_height
        
        # remove files
        os.remove(tmpname + '_good.svg')
        
    def render(self):
        self.code2svg()
        self.rendered = True
