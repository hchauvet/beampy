# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo
"""

from beampy import document
from beampy.functions import gcs
from beampy.modules.figure import render_figure
import tempfile
import os

inkscapecmd='inkscape'
try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.formatters import SvgFormatter
    is_pigment = True
except:
    is_pigment = False
    
def code( codetext, x='center', y='auto', width=None, height=None, langage=None, size="14px"):
    """
        Color a given code using python pygment
        
        option
        ------
        
        langage[None]: try to infer the lexer from codetext
        
        size['9px']: size of the text
        
    """
    

    if width == None:
        width = str(document._width)
    if height == None:
        height = str(document._height)
            
    args = {"x":str(x), "y": str(y) , "width": width, "height": height,
            "langage": langage, 'font-size': size }
            
    codeout = {'type': 'code', 'content': codetext, 'args': args,
              "render": render_code}
    
    if is_pigment:
        document._contents[gcs()]['contents'] += [ codeout ]
    else:
        print("Python pygment is not installed, I can't translate code into svg...")
        
        
def render_code( codein, args ):
    """
        function to render figures
    """

    #Try to infer the lexer
    if args['langage'] == None:
        lexer = guess_lexer(codein)
    else:
        lexer = get_lexer_by_name(args['langage'], stripall=True)
        
    #Convert code to svgfile
    svgcode = highlight(codein, lexer, SvgFormatter(fontsize=args['font-size'],style='tango'))
    
    #Create a tmpfile
    tmpfile, tmpname = tempfile.mkstemp(prefix='beampytmp')
    #tmppath = tmpname.replace(os.path.basename(tmpname),'')
    
    with open( tmpname+'.svg', 'w' ) as f:
        f.write(svgcode)
        
    #Convert svgfile with inkscape to transform text to path
    cmd = inkscapecmd + ' -z -T -l=%s %s'%(tmpname+'_good.svg', tmpname+'.svg') 
    
    req = os.popen(cmd)
    req.close()
    
    #Read the good svg
    with open(tmpname+'_good.svg','r') as f:
        goodsvg = f.read()

    #remove files    
    os.remove(tmpname+'.svg')
    os.remove(tmpname+'_good.svg')
    
    #use the classic figure render
    args['ext'] = 'svg'
    tmpout, tmpw, tmph = render_figure(goodsvg, args)
    #print tmpw, tmph
    tmpout = '<g> %s </g>'%tmpout
    return tmpout, tmpw, tmph
