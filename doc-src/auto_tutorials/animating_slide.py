"""
How to animate apparition of Beampy modules in your slide
=========================================================

Beampy allows to fragment the apparition of modules in your slide.
The syntax uses the python "iterable" notation, with index:

- [0]: the module only appears on the first layer
- [:]: the module appears on all layers 
- [1:]: the module appears from second layer and until the last

Ok, let's stats some real life examples with squares.

Animate 3 colored squares
-------------------------

We create 3 squares with 3 different colors (stored in C list), and add each one to a given layer.
This is done in the loop with `[i]` at the end of the rectangle command. 

Without the for loop this could also be written:

- `rectangle(width=100, height=100, color=C[0])[0]`
- `rectangle(width=100, height=100, color=C[1])[1]`
- `rectangle(width=100, height=100, color=C[2])[2]`
"""

from beampy import *

doc = document(quiet=True, cache=False)

C = ['dodgerblue', 'crimson', 'forestgreen']

with slide('The 3 rectangles apparition'):

    for i in range(3):
        rectangle(width=100, height=100, color=C[i])[i]

save('./tuto_html_outputs/animation.html')

################################################
#
#Click on the iframe and use the arrows (left and right) to make the
#two other squares appear.
#
#.. raw:: html
#
#   <iframe src="../_static/tuto_html_outputs/animation.html" width="100%" height="500px"></iframe>
#
#Keep the squares on the screen!
#-------------------------------
#
#Now we want that each time a square appears it stays on the next layer of the slide.
#To do so, we only need to add ":" to "[i]"
#

doc = document(quiet=True, cache=False)

C = ['dodgerblue', 'crimson', 'forestgreen']

with slide('The 3 rectangles appears and stay'):

    for i in range(3):
        rectangle(width=100, height=100, color=C[i])[i:]

save('./tuto_html_outputs/animation2.html')

#####################################################
#.. raw:: html
#
#   <iframe src="../_static/tuto_html_outputs/animation2.html" width="100%" height="500px"></iframe>
#
#Remove the two first square at the end
#--------------------------------------
#
#Now for the last layer we want the two first squares to disappear and to keep only the last one remains 

doc = document(quiet=True, cache=False)

C = ['dodgerblue', 'crimson', 'forestgreen']

with slide('The 3 rectangles appear and stay until last'):

    rectangle(width=100, height=100, color=C[0])[0:1]
    rectangle(width=100, height=100, color=C[1])[1]
    rectangle(width=100, height=100, color=C[2])[2]
    
save('./tuto_html_outputs/animation3.html')

#####################################################
#.. raw:: html
#
#   <iframe src="../_static/tuto_html_outputs/animation3.html" width="100%" height="500px"></iframe>
#
#Add more layers than the number of modules
#------------------------------------------
#
#Now lets add an additional layer where only the first and the last squares are displayed

doc = document(quiet=True, cache=False)

C = ['dodgerblue', 'crimson', 'forestgreen']

with slide('Add more layers than modules in the slide'):

    rectangle(width=100, height=100, color=C[0])[0,1,3]
    rectangle(width=100, height=100, color=C[1])[1]
    rectangle(width=100, height=100, color=C[2])[2,3]
    
save('./tuto_html_outputs/animation4.html')

#####################################################
#.. raw:: html
#
#   <iframe src="../_static/tuto_html_outputs/animation4.html" width="100%" height="500px"></iframe>
#
#Animation also works on groups
#------------------------------
#
#We now create two groups with squares inside them and make this two groups appears one by one.
#

doc = document(quiet=True, cache=False)

C = ['dodgerblue', 'crimson', 'forestgreen']

with slide('Group rectangles on different layers'):

    with group(height=150)[0]:
        for i in range(3):
            rectangle(width=100, height=100, x='auto', y='center', color=C[i])

    with group(height=150)[1]:
        for i in range(3):
            rectangle(width=100, height=100, x='auto', y='center', color=C[i], opacity=0.5)
    
save('./tuto_html_outputs/animation5.html')

#####################################################
#.. raw:: html
#
#   <iframe src="../_static/tuto_html_outputs/animation5.html" width="100%" height="500px"></iframe>
#
#How to animate slide titles?
#----------------------------
#
#Let's make changed the slide title for each layers
#


doc = document(quiet=True, cache=False)

C = ['dodgerblue', 'crimson', 'forestgreen']

with slide():
    title('The first layer title')[0]
    title('The second layer title')[1]
    title('The third layer title')[2]
    title('The last layer with all squares')[3]
    
    for i in range(3):
        rectangle(width=100, height=100, color=C[i])[i,3]

save('./tuto_html_outputs/animation6.html')

#####################################################
#.. raw:: html
#
#   <iframe src="../_static/tuto_html_outputs/animation6.html" width="100%" height="500px"></iframe>
#
#How to animate elements in itemize
#----------------------------------
#
#The itemize module has a special way to create animation of each
#item. The "iterable" parameters (int, ':', '0:', '1:2', etc...) are
#passed inside a list to the item_layers parameter of the itemize
#function.
#
doc = document(quiet=True, cache=False)

with slide():
    itemize(['item1 on all layers',
             'item2 on layer 1',
             'item3 on layer 3'],
            item_layers=[':', 1, 2])

save('./tuto_html_outputs/animation7.html')

#####################################################
#.. raw:: html
#
#   <iframe src="../_static/tuto_html_outputs/animation7.html" width="100%" height="500px"></iframe>
#
