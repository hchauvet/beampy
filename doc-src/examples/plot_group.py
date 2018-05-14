"""
group
=====

Group Beampy modules to place them easily.

Grouping modules allows to create complex layout in your slide.

"""

from beampy import *

# Remove quiet=True to get Beampy render outputs
doc = document(quiet=True)

with slide('Grouping elements'):

    # Using with statement:
    with group(y=0.1, background='lightblue') as g1:
        text("I'm inside the first group", y=0)
        text('Me too!', y="+0.1")


    # Create two groups (g2 and g4) aligned on top 
    # and with automatic horizontal position
    with group(x='auto', y=0.3, width=400, height=200, background='lightgreen') as g2:
        text('At the group center', x='center', y='center')
    
        # Add child group to the parent group
        with group(width=400/2, background='red', x=g2.left+0, y=g2.bottom+bottom(0)) as g3:
            text('A group in a group')

        with group(width=400/2, background='violet', x=g3.right+0, y=g3.top+0) as g3:
            text('A group in a group')

    with group(x='auto', y=g2.top+0, height=300, width=300) as g4:
        text('''A last group with a bigger height and a lower width.
             The text inside this group has the group width!''')

    # Add a border to the last group
    g4.add_border()

display_matplotlib(gcs())

###################################################
#
#Module arguments
#================
#
#.. autoclass:: beampy.group
#   :noindex:
