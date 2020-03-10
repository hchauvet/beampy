import sys
sys.path.append('./../')

from beampy import *

doc = document()

bib = bibliography('biblio.bib')

slide('Quantum mechanics')

text('Any serious consideration of a physical theory must take into account the distinction between the objective reality, which is independent of any theory, and the physical concepts with which the theory operates.', y = '+1cm')

cite('Einstein 1935', y = '+1cm')
bib.cite('einstein1935can', y = '+1cm' )
bib.cite('einstein1935can', y = '+1cm', initials = True )
bib.cite('einstein1935can', y = '+1cm', max_author = 1, journal = True )
bib.cite(['einstein1935can']*3, y = '+1cm', max_author = 1)

save( 'biblio_test.html')
