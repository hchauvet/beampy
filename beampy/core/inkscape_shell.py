#!/usr/bin/env python3

"""
Interact with the inkscape --shell mode from python

TODO: Create a Python interface to inkscape --shell mode

"""
from beampy.core.store import Store
import subprocess as sp

class Inkscape():

    def __init__(self):
        """
        Create an inkscape object to interact with inkscape --shell
        """

        # Check if a session is already open in Beampy
        if Store._inkscape_session is None:
            self.shell = sp.Popen('inkscape --shell', stdin=sp.PIPE,
                                  stdout=sp.PIPE, stderr=sp.PIPE,
                                  shell=True,
                                  universal_newlines=True)
            Store._inkscape_session = self.shell
        else:
            self.shell = Store._inkscape_session

    def close(self):
        self.shell.communicate('quit\n')

    def version(self):
        return self.shell.communicate('version\n')
