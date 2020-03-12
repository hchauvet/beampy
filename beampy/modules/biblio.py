#-*- coding:utf-8 -*-

import bibtexparser
from warnings import warn
from glob import glob

from beampy import document
from beampy.modules.text import text
from beampy.functions import check_function_args, gcs
import sys

import logging
_log = logging.getLogger(__name__)

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


class bibliography:

    def __init__(self, bibtex_source=None, **bibtex_style):

        '''
        Bibliography object for Beampy.

        Arguments:
            bibtex_file_name (str) : BibTeX file
            bibtex_style (dict, optional) : style parameters, updates
            default_bibtex_style.
        '''

        self.references = {}

        if bibtex_source is not None:
            self.add_from_source(bibtex_source)

        if bibtex_style is None:
            bibtex_style = {}

        self.bibtex_style = check_function_args(bibliography,
                                                bibtex_style)

    def add_from_source(self, bibtex_source):
        '''
        Add source to bibliography.

        Arguments:
            bibtex_source (str, or list) : bibtex string, bibtex file
            name, path to bibtex file, or list of such arguments.
        '''

        if isinstance(bibtex_source, str):
            bibtex_sources = [bibtex_source]
        else:
            bibtex_sources = bibtex_source

        for bibtex_source in bibtex_sources:

            new_references = bibtexparser_to_references(bibtexparser.loads(bibtex_source))

            if len(new_references) == 0:
                try:
                    with open(bibtex_source) as source_file:
                        new_references = bibtexparser_to_references(bibtexparser.load(source_file))
                except Exception as e:
                    _log.warning(e)

                if len(new_references) == 0:

                    for source_file_name in glob(bibtex_source + '*.bib'):

                        with open(source_file_name) as source_file:
                            new_references = bibtexparser_to_references(bibtexparser.load(source_file))


            if len(new_references) > 0:
                self.references.update(new_references)

            else:
                warn('Cannot load bibliography.')
                _log.warning('Bibliography source %s not found' % bibtex_source)
                sys.exit(1)

    def cite(self, reference, **kwargs):

        '''
        Add reference on slide

        Arguments:
            reference (str or list) : either a bibtex ID, or the
            reference itself
        '''

        cite_kwargs = self.bibtex_style.copy()
        cite_kwargs.update(kwargs)

        if isinstance(reference, str):
            references = [reference]

        else:
            references = reference

        refs_str_list = []

        for i, reference in enumerate(references):
            refs_str_list += [bibtex_to_str(self.get_reference(reference),
                                            bibtex_style=cite_kwargs)]

        return cite(refs_str_list, **cite_kwargs)

    def get_reference(self, ID):

        '''
        Finds a reference in bibliogray.

        Arguments :
            ID (str) : the bibtex label

        Returns :
            Entire entry with corresponding ID
        '''

        try:
            return self.references[ID]
        except Exception as e:
            warn('Could not find reference.')
            _log.warning('Missing reference: ' + ID)
            _log.warning(e)
            # return ID  # (error when try to formating authors)
            sys.exit(1)

##########################
#
# USEFUL FUNCTIONS
#
##########################


class cite(text):
    """
    Add citation on slide.

    Parameters
    ----------

    reference : str or list
        Either a string with what you want to cite or a list of citations.

    x : int or float or {'center', 'auto'} or str, optional
        Horizontal position for the text container (the default is 'center').
        See positioning system of Beampy.

    y : int or float or {'center', 'auto'} or str, optional
        Vertical position for the text container (the default is 'auto'). See
        positioning system of Beampy.

    width : int or float or None, optional
       Width of the text container (the default is None, which implies that the
       width is the parent group with).

    size : int, optional
        The font size (the default theme sets this value to 20).

    font : str, optional
        The Tex font (the default theme sets this value to
        'CMR'). **THIS IS NOT YET IMPLEMENTED!**

    color : str, optional
        The text color (the default theme set this value to '#000000'). Color
        could be html hex values or SVG-COLOR-NAMES.

    usetex : bool, optional
        Use latex to render text (the default value is true). Latex render
        could be turned off using `usetex`=False, then the text is rendered as
        svg.

    va : {'','baseline'}, optional
       Vertical text alignment (the default value is '', which implies that the
       alignment reference is the top-left corner of text). When
       `va`='baseline', the base-line of the first text row is computed and
       used as alignment reference (baseline-left).

    extra_packages : list of string, optional
        Add latex packages to render the text, like
        ['\\usepackage{name1}', '\\usepackage{name2}']

    reference_delimiter: string, optional
        Add a delimiter between citations (default theme sets this to ';')

    brackets: list of two string, optional
        Set the starting and closing brakets (default theme set this
        to ('[',']')).

    Example
    -------

    >>> cite('Einstein 1935', x='20', y='20')

    See Also
    --------

    bibliography class to manage citation from bibtex.
    """

    def __init__(self, reference, **kwargs):

        self.type = 'text'
        self.check_args_from_theme(kwargs, lenient=True)
        # self.check_args_from_theme(kwargs)
        self.load_extra_args('text')
        self.svgtext = ''  # To store the svg produced by latex

        if isinstance(reference, str):
            references = [reference]
        else:
            references = reference

        cite_str = self.brackets[0]

        for i, reference in enumerate(references):

            cite_str += reference

            if i < len(references) - 1:
                cite_str += ' ' + self.reference_delimiter + ' '
            else:
                cite_str += self.brackets[1]

        self.content = cite_str

        self.height = None
        # Check width
        if self.width is None:
            self.width = document._slides[gcs()].curwidth

        # Add special args for cache id
        # Cite need to be re-rendered from latex if with, color, size,  are changed
        self.initial_width = self.width
        self.args_for_cache_id = ['initial_width', 'color', 'size',
                                  'align', 'opacity']


        # Initialise the global store on document._content to store letter
        if 'svg_glyphs' not in document._contents:
            document._contents['svg_glyphs'] = {}

        self.register()


def bibtexparser_to_references(bib_database):

    references = {}

    for entry in bib_database.entries:
        references.update({entry['ID']: entry})

    return references

def parse_author_str(author_str):
    '''
    Gets firstnames and lastnames from BibTeX authors list.
    '''

    authors = []

    for author in author_str.split(' and '):
        author = author.split(',')

        authors += [{'firstname': author[1].strip(),
                     'lastname': author[0].strip()}]

    return authors

def firstname_to_initials(firstname, delimiter='.'):
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
