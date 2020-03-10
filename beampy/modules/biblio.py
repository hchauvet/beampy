#-*- coding:utf-8 -*-

import bibtexparser
from warnings import warn
from glob import glob

from beampy import document
from beampy.modules.text import text
from beampy.functions import check_function_args

# default_bibtex_style = {
#     "max_author" : 3,
#     "initials" : False,
#     "journal" : False,
#     "and" : r'\&',
#     'et_al' : 'et al.',
#     'initial_delimiter' : '.',
# }

##########################
#
# BIBLIOGRAPHY CLASS
#
##########################

class bibliography :

    def __init__( self, bibtex_source = None, bibtex_style = None ) :

        '''
        Bibliography object for Beampy.

        Arguments:
            bibtex_file_name (str) : BibTeX file
            bibtex_style (dict, optional) : style parameters, updates default_bibtex_style.
        '''

        self.references = {}

        if not bibtex_source is None :
            self.add_from_source( bibtex_source )

        if bibtex_style is None :
            bibtex_style = {}

        self.bibtex_style = check_function_args( bibliography, bibtex_style, lenient = False )

    def add_from_source( self, bibtex_source ) :
        '''
        Add source to bibliography.

        Arguments:
            bibtex_source (str, or list) : bibtex string, bibtex file name, path to bibtex file, or list of such arguments.
        '''

        if type(bibtex_source) is type('') :
            bibtex_sources = [ bibtex_source ]
        else :
            bibtex_sources = bibtex_source


        for bibtex_source in bibtex_sources :

            new_references = bibtexparser_to_references( bibtexparser.loads( bibtex_source ) )

            if len( new_references ) == 0 :
                try :
                    with open( bibtex_source ) as source_file :
                        new_references = bibtexparser_to_references( bibtexparser.load( source_file ) )
                except :
                    pass

                if len( new_references )  == 0 :

                    for source_file_name in glob( bibtex_source + '*.bib' ) :

                        with open( source_file_name ) as source_file :
                            new_references = bibtexparser_to_references( bibtexparser.load( source_file )  )


            if len(new_references) > 0 :
                self.references.update( new_references )

            else :
                warn( 'Cannot load bibliography.' )
                print( 'Bibliography source : ' + bibtex_source   )


    def cite( self, reference, **kwargs ):

        '''
        Add reference on slide

        Arguments:
            reference (str or list) : either a bibtex ID, or the reference itself
        '''

        cite_kwargs = self.bibtex_style.copy()
        cite_kwargs.update( kwargs )

        if type(reference) is type('') :
            references = [ reference ]

        else :
            references = reference

        refs_str_list = []

        for i, reference in enumerate( references ) :
            refs_str_list += [ bibtex_to_str( self.get_reference( reference ), bibtex_style = cite_kwargs ) ]

        cite( refs_str_list, **cite_kwargs )


    def get_reference( self, ID ) :

        '''
        Finds a reference in bibliogray.

        Arguments :
            ID (str) : the bibtex label

        Returns :
            Entire entry with corresponding ID
        '''

        try :
            return self.references[ID]

        except :
            warn( 'Could not find reference.')
            print( 'Missing reference: ' + reference )
            return ID

##########################
#
# USEFUL FUNCTIONS
#
##########################

def cite( reference, **kwargs ):

    """
    Add citation on slide.

    Arguments :
        reference (str or list): python list of authors
    """

    kwargs = check_function_args( cite, kwargs, lenient = True )

    if type(reference) == type( 'this_is_a_string' ) :
        references = [ reference ]
    else :
        references = reference

    cite_str = kwargs['brackets'][0]

    for i, reference in enumerate( references ) :

        cite_str += reference

        if i < len( references ) - 1 :
            cite_str += ' ' + kwargs['reference_delimiter'] + ' '
        else :
            cite_str += kwargs['brackets'][1]

    text( cite_str, **check_function_args( text, kwargs, lenient = True ) )


def bibtexparser_to_references( bib_database ) :

    references = {}

    for entry in bib_database.entries :
        references.update( { entry['ID'] : entry } )

    return references

def parse_author_str( author_str ) :
    '''
    Gets firstnames and lastnames from BibTeX authors list.
    '''

    authors = []

    for author in author_str.split(' and ') :
        author = author.split(',')

        authors += [ {'firstname' : author[1].strip(), 'lastname' : author[0].strip() } ]

    return authors

def firstname_to_initials( firstname, delimiter = '.' ) :
    '''
    Guess initials from firstname string based on uppercase letters.
    '''

    initials = ''

    for letter in firstname :
        if letter.isupper() :
            initials += letter + delimiter

    if initials is '' :
        try :
            initials += firstname.upper() + delimiter
        except :
            pass

    return initials

def bibtex_to_str( entry, bibtex_style = None ) :
    '''
    Converts bibtex entry to short reference string suited for Beampy.

    Arguments:
        entry (str) : the ID used in bibtex
        bibtex_style (dict) : style parameters, updates default_bibtex_style.
    '''

    if bibtex_style is None :
        bibtex_style = default_bibtex_style

    bib_str = ''

    authors = parse_author_str( entry['author'] )

    if len( authors ) > bibtex_style["max_author"]:
        authors = authors[:bibtex_style["max_author"]]
        et_al = True

    else :
        et_al = False

    for i, author in enumerate( authors ) :

        if bibtex_style['initials'] :
            bib_str += firstname_to_initials( author['firstname'] ) + ' '

        bib_str += author['lastname']

        if not et_al and i == len( authors ) - 2 :
            bib_str += ' ' + bibtex_style['and'] + ' '
        else :
            bib_str += ', '

    if et_al :
        bib_str = bib_str[:-2] + ' ' + bibtex_style['et_al']
    else :
        bib_str = bib_str[:-2] + ''
        bib_str

    if bibtex_style["journal"] :
        bib_str += ', ' + entry['journal']

    bib_str += ' (' + entry['year'] + ')'

    return bib_str
