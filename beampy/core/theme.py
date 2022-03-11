#!/usr/bin/env python3

"""
Class to manage the Beampy Themes
"""
import importlib.util
from pathlib import Path
from beampy.core.store import Store

# The root folder of beampy
bproot = Path(__file__).parent.parent
# The theme folder of beampy
bptheme = bproot.joinpath('themes')


class Theme():
    """Beampy Theme are inside file (located in theme folder).
    This class contains methods and attributes to manage the defined theme of
    the presentation.
    """

    def __init__(self, theme_file=None, register=True):
        """Load a theme given by theme_file.

        Parameters:
        -----------

        - theme_file: str or None,
            The theme_file could be a full path to a .py file or the name of the
            theme. If None is given, the default theme is loaded.

            Theme file could be:
                - a full path to a .py file containing a THEME dictionnary
                - a name (like Simple), then load Simple_theme.py in theme
                  folder of beampy.
                - a file name without path like Simple_theme.py, then look for
                  this file in beampy theme folder.

        - register: boolean (optional),
            If True (default) add this Theme to the global Store so that it will
            be used by all beampy modules.
        """

        # Load the default theme
        default = self.load_theme(bproot.joinpath('statics', 'default_theme.py'))

        if theme_file is not None:
            abs_path_to_theme = self.parse_file(theme_file)
            theme = self.load_theme(abs_path_to_theme)

            self.theme = dict_deep_update(default, theme)
        else:
            self.theme = default

        if register:
            Store._theme = self.theme

    def load_theme(self, file_path: str) -> dict:
        """Load from a module from a source file directly

        References:
        -----------
        - https://docs.python.org/3.8/library/importlib.html#importing-a-source-file-directly
        """

        path = Path(file_path)
        theme_name = path.name.replace(''.join(path.suffixes), '')
        spec = importlib.util.spec_from_file_location(theme_name,
                                                      str(path.absolute()))
        modulevar = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulevar)

        if not hasattr(modulevar, 'THEME'):
            raise ImportError("Give theme file does not contains a THEME dictionary")

        return modulevar.THEME

    def parse_file(self, theme_file: str) -> Path:
        """Parse the impurt theme file and return an obsolute path to this
        theme.
        """

        infile = Path(theme_file)

        if infile.is_absolute():
            if infile.is_file():
                outfile = infile
            else:
                raise Exception("Not such theme file %s " % infile)
        else:
            # Case of a single name like (Simple or Simple_theme.py) is given
            # TODO: FIX THAT '.' for local theme
            if str(infile.parent) == '.':
                if '_theme.py' in str(infile):
                    tmpname = str(infile)
                else:
                    tmpname = f'{infile}_theme.py'

                tmp = bptheme.joinpath(tmpname)
                if tmp.is_file():
                    outfile = tmp.absolute()
                else:
                    print(f"No theme named {infile} in beampy theme folder {bptheme}")
                    print("Available themes")
                    print("-"*10)
                    for f in bptheme.glob('*_theme.py'):
                        print(f.name.replace('_theme.py', ''))
                    print("-"*10)
                    raise Exception('Not such theme file')

            else:
                tmp = infile.absolute()
                if tmp.is_file():
                    outfile = tmp
                else:
                    raise Exception(f'Not such theme file {tmp}')

        return outfile

    def __getitem__(self, value):
        return self.theme[value]


def dict_deep_update(original, update):
    """Recursively update a dict.
    Subdict's won't be overwritten but also updated.
    from http://stackoverflow.com/questions/38987/how-can-i-merge-two-python-dictionaries-in-a-single-expression/44512#44512
    """

    for key, value in original.items():
        if key not in update:
            update[key] = value
        elif isinstance(value, dict) and isinstance(update[key], dict):
            dict_deep_update(value, update[key])

    return update
