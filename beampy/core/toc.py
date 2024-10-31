#!/usr/bin/env python3

"""
Function to manage TOC in beampy
"""
from beampy.core import Store


def section(title: str):
    """
    Function to add a section in the TOC.

    Parameters
    ----------

    title : str,
        The title of the section.   
    """

    Store.add_toc(title=title, level=0)


def subsection(title: str):
    """
    Function to add a subsection in the TOC.

    Parameters
    ----------

    title : str,
        The title of the subsection.
    """
    
    Store.add_toc(title, level=1)
    
    
def subsubsection(title: str):
    """
    Function to add a subsubsection in the TOC.

    Parameters
    ----------

    title : str,
        The title of the subsubsection.
    """

    Store.add_toc(title, level=1)