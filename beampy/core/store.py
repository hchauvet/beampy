#!/usr/bin/env python3

"""
The beampy store is used to store beampy slideshow content using the class
variable conservation in python
"""
import logging
from .._version import __version__
_log = logging.getLogger(__name__)

class StoreMetaclass(type):
    """
    Define a metaclass for store to let define some usefull properties for the
    Store class, such as it's length with len(Store) etc...
    """

    def __len__(self):
        return len(self._slides)

    def get_number_of_groups(self):
        """Count the number of groups in the Store
        """
        n = 0
        for c in self._contents.values():
            if hasattr(c, 'data') and 'svgdef' in c.data and isinstance(c.data['svgdef'], list):
                n += 1

        return n

    def __repr__(self):
        ngroups = self.get_number_of_groups()
        out = "Beampy Store:\n"
        out += "- %i slides\n" % (len(self))
        out += "- %i modules [%i group]\n" % (len(self._contents), ngroups)
        out += f"- current slide: {self._current_slide}\n"
        out += f"- current group: {self.group()}\n"

        return out


class Store(metaclass=StoreMetaclass):
    """
    Main store class to save data of the slideshow
    """

    # Store beampy slide objects
    _slides = dict()
    _current_slide = None

    # Store beampy content (text, figure, etc...) objects
    _contents = dict()

    # Store data (the output of render function that could be independant of width, height)
    _data = dict()

    # Store the table of content
    _TOC = list()

    # Store slideshow options (like cache, rasterised, other global properties)
    _options = None

    # Store slideshow theme
    _theme = dict()

    # The cache class
    _cache = None

    # Store the slideshow layout (previously denominated document in Beampy < 1.0)
    _layout = None

    # Store the current group
    _current_group = None

    # Store the glyphs
    _glyphs = dict()

    # Beampy version
    _version = __version__

    # Inkscape session
    _inkscape_session = None

    # UID counter for svg
    _svg_id = 0

    @classmethod
    def __repr__(cls):
        return '%s' % str(cls._slides)

    @classmethod
    def add_slide(cls, newslide: object):
        """
        Add a slide to the store

        Store.add_slide(beampy_slide)
        """

        # Add the slide object to the slides dict
        cls._slides[newslide.id] = newslide

        #update the current slide
        cls._current_slide = newslide.id

    @classmethod
    def get_current_slide(cls):
        """
        Get the current slide
        """

        return cls._slides[cls._current_slide]

    @classmethod
    def get_slide(cls, slide_id):
        """
        Return a given slide in the store
        """

        return cls._slides[slide_id]

    @classmethod
    def get_current_slide_id(cls):
        """
        return the content of _current_slide
        """

        return cls._current_slide

    @classmethod
    def get_current_slide_pos(cls):
        """
        Return the index of the current slide
        """

        if cls._current_slide is None:
            out = -1
        else:
            out = list(cls._slides.keys()).index(cls._current_slide)

        return out

    @classmethod
    def add_data(cls, data: dict, data_id: str):
        """Add data to the Store. Data are hashed to get a unique ID
        """
        if data_id not in cls._data:
            cls._data[data_id] = data
        else:
            _log.info('Data already in store %s' % data_id)

    @classmethod
    def is_data(cls, data_id: str):
        """Check if data is in store
        """

        if data_id in cls._data:
            return True

        return False

    @classmethod
    def get_data(cls, data_id: str):
        if data_id in cls._data:
            return cls._data[data_id]
        else:
            raise IndexError("No data with id: %s" % data_id)

    @classmethod
    def get_content(cls, content_id):
        """
        Return the beampy module stored in _contents[content_id]
        """
        if content_id in cls._contents:
            out = cls._contents[content_id]
        else:
            _log.error('Module %s does not exist in Store' % content_id)
            out = None
            sys.exit(1)

        return out

    @classmethod
    def is_content(cls, module_id):
        """
        Return if a module is present in the store or not
        """
        if module_id in cls._contents:
            return True
        else:
            return False

    @classmethod
    def add_content(cls, bp_content: object):
        """
        Add a beampy module to the content Store.
        """

        if bp_content.id not in cls._contents:
            cls._contents[bp_content.id] = bp_content
        else:
            print('Beampy module %s(%s) is already in the Store, I will use the one in the Store!' % (bp_content.name,
                                                                                                      bp_content.id))

    @classmethod
    def update_content_data_id(cls, content_id: str, data_id: str):
        """Update the content in the Store
        """

        # TODO: implement save_cache if needed!!!
        cls._contents[content_id]._data_id = data_id

    @classmethod
    def update_content_size(cls, bp_content: object, dim='both'):
        # TODO: implement save_cache if needed!!!
        if dim in ['both', 'width']:
            cls._contents[bp_content.id]._width = bp_content._width
        if dim in ['both', 'height']:
            cls._contents[bp_content.id]._height = bp_content._height

    @classmethod
    def remove_content(cls, content_id):
        """
        Remove the given element id from Store
        """

        if content_id in cls._contents:
            cls._contents.pop(content_id)
        else:
            _log.error('No module id %s in Store to delete' % content_id)

    @classmethod
    def get_layout(cls):
        """
        Return the layout object defined for the presentation.
        """

        return cls._layout

    @classmethod
    def add_layout(cls, newlayout: object):
        """
        Add a layout class to the Store
        """

        cls._layout = newlayout

    @classmethod
    def group(cls):
        return cls._current_group

    @classmethod
    def set_group(cls, new_group):
        cls._current_group = new_group

    @classmethod
    def isgroup(cls):
        if cls.group() is None:
            return False

        return True

    @classmethod
    def theme(cls, module_name):
        if module_name in cls._theme:
            return cls._theme[module_name]
        else:
            raise KeyError(f'Not such module {module_name} defined in theme {cls._theme.keys()}')

    @classmethod
    def cache(cls):
        return cls._cache

    @classmethod
    def get_glyph(cls, unique_id: str):
        """Get the glyph from the store base on it's unique_id obtain from the
        hash of the svg path content "d"
        """
        if unique_id in cls._glyphs:
            return cls._glyphs[unique_id]
        else:
            raise KeyError('No glyphs %s in Store' % unique_id)

    @classmethod
    def add_glyph(cls, new_glyph: dict):
        """Add a new glyph to the Store.

        Parameter:
        ----------

        - new_glyph, dict:
            The new glyph to add, the dict should contains keys:
            - "uid", the unique id of the glyph
            - "id", the new id (based on the length of _glyphs)
            - "dvisvgm_id", the orginal dvisvgm_id
            - "svg", the svg (path or use) of the glyph
        """

        assert 'id' in new_glyph
        assert 'uid' in new_glyph
        assert 'dvisvgm_id' in new_glyph
        assert 'svg' in new_glyph

        if new_glyph['uid'] not in cls._glyphs:
            cls._glyphs[new_glyph['uid']] = new_glyph
        else:
            _log.debug('Glyph already in Store %s ' % str(new_glyph))

    @classmethod
    def is_glyph(cls, glyph_id: str):
        if glyph_id in cls._glyphs:
            return True

        return False

    @classmethod
    def get_all_glyphs(cls):
        """Export all glyphs in Store
        """

        return cls._glyphs

    @classmethod
    def load_all_glyphs(cls, glyphs):
        """Replace _glpyhs with incomming glyphs attribute
        """

        cls._glyphs = glyphs

    @classmethod
    def svg_id(cls):
        """
        Return the current id to make unique id for svg
        """
        return cls._svg_id

    @classmethod
    def update_svg_id(cls):
        """
        Add one to the svg_id
        """
        cls._svg_id += 1

    @classmethod
    def clear_all(cls):
        """
        Clear all data of the Store
        """

        cls._slides = dict()
        cls._current_slide = None
        cls._contents = dict()
        cls._TOC = list()
        cls._options = dict()
        cls._theme = dict()
        cls._layout = None
        cls._cache = None
        cls._current_group = None
        cls._glyphs = dict()
        cls._svg_id = 0

# Some functions to easily manipulate the store
def get_module_position(content_id, slide_id=None):
    """
    Get the position of the beampy module defined by `content_id` in the slide
    index list.

    Arguments:
    ----------

    content_id : str,
        The id of the beampy module used to look for its position.

    slide_id : str or None,
        The slide id where to search for the beampy module inside its index. If
        None (default) the last created slide is used.

    return the position in Slide.index of the content_id
    """

    if slide_id is None:
        slide_id = Store.get_current_slide_id()

    try:
        slide = Store._slides[slide_id]
    except KeyError:
        print('Slide %s is not in the Store' % (str(slide_id)))

    try:
        return slide.content_keys.index(content_id)
    except KeyError:
        print('Module %s is not referenced in slide %s', (str(content_id), str(slide_id)))


def get_previous_module_id(content_id, slide_id=None):
    """
    Return the Beampy module stored before the one defined by `content_id`
    inside the given slide.

    Arguments:
    ----------

    content_id : str,
        The id of the beampy module of reference

    slide_id : str or None,
        The id of the slide where the module is registered. If None (default),
        use the last slide in the store.

    return the id of the previous module
    """

    if slide_id is None:
        slide_id = Store.get_current_slide_id()

    module_position = get_module_position(content_id, slide_id)

    try:
        return Store._slides[slide_id].content_keys[module_position-1]
    except IndexError:
        print('No previous module ! Module %s is the first one in slide %s' % (str(content_id), str(slide_id)))
