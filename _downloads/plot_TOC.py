"""
table of contents
=================

Create a table of content for your presentation. 

To create the structure of your presentation you could use the following function:
- section('Section title')
- subsection('Subsection title')
- subsubsection('Subsubsection title')

"""

from beampy import *

# Remove quiet=True to get Beampy render outputs
doc = document(quiet=True)

section('Introduction')
with slide('Table of content'):
    tableofcontents()
    
section('The main topic')
subsection('Argument 1')
with slide('Display only the current section'):
    tableofcontents(currentsection=True)
    
subsubsection('Demonstration 1')

with slide('Current subsection'):
    tableofcontents(currentsubsection=True)
    
subsection('Argument 2')
subsubsection('Demonstration 1')
subsubsection('Demonstration 2')

section('Conclusion')
with slide('Two columns table of contents'):
    with group(width='45%', x='auto', y='center') as t1:
        tableofcontents(x=0, y=0, sections=[1, 2],
                        section_style='square',
                        subsection_style='round')

    with group(width=t1.width, x='auto', y=t1.top+0) as t2:
        tableofcontents(x=0, y=0, sections=3,
                        section_style='square')

    t1.add_border()
    t2.add_border()
    
display_matplotlib('slide_0')
save('./examples_html_outputs/toc.html')

###############################################################
#
#HTML output
#===========
#
#.. raw:: html
#
#    <iframe src="../_static/examples_html_outputs/toc.html" width="100%" height="500px"></iframe>
#
#Module arguments
#================
#
#.. autoclass:: beampy.tableofcontents
#   :noindex:
