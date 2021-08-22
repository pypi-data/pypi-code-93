#!/usr/bin/env python3

###
# This module is for extracting paths inside the peuf::``toc`` block of 
# an existing path::``about.peuf`` file of one directory.
###


from typing import *

from pathlib import Path

from orpyste.data      import ReadBlock
from orpyste.parse.ast import ASTError


# ----------- #
# -- ABOUT -- #
# ----------- #

ABOUT_NAME      = "about.peuf"
TOC_TAG         = "toc"
PLACEHOLDER     = "+"
ABOUT_PEUF_MODE = {"verbatim": TOC_TAG}

MD_FILE_EXT    = "md"
MD_FILE_SUFFIX = f'.{MD_FILE_EXT}'


# -------------------------------------------------- #
# -- LOOK FOR A TOC INSIDE AN EXISTING ABOUT FILE -- #
# -------------------------------------------------- #

###
# This class extracts the list of paths from an existing path::``about.peuf``
# file of one directory.
#
# warning::
#     This is not the responsability of this class to test the existence 
#     of the path::``about.peuf`` file.
###

class TOC():

###
# prototype::
#     onedir = ; // See Python typing...
#              the path of the directory with the path::``about.peuf`` file.
###
    def __init__(
        self,
        onedir: Path,
    ) -> None:
        self.onedir = onedir

        self._lines: List[str] = []


###
# prototype::
#     :return: = ; // See Python typing...
#                the list of paths found in the peuf::``toc`` block.
###
    def extract(self) -> List[Path]:
# Lines in the TOC block.
        self.readlines()

# Paths from the lines of the TOC block.
        pathsfound: List[str] = []

        for nbline, oneline in enumerate(self._lines[TOC_TAG], 1):
            path = self.pathfound(nbline, oneline)

# Empty line?
            if not path:
                continue

# Complete short names.
            if not '.' in path:
                path = f'{path}.{MD_FILE_EXT}'

# A new path found.
            pathsfound.append(self.onedir / path)

# Everything seems ok.
        return pathsfound


###
# prototype::
#     nbline  = ; // See Python typing...
#               the relative number of the line read (for message error).
#     oneline = ; // See Python typing...
#               one line to analyze.
#
#     :return: = ; // See Python typing...
#                the stripped text after the placeholder peuf::``+`` 
#                or an empty string for an empty line.
###
    def pathfound(
        self, 
        nbline : int, 
        oneline: str,
    ) -> str:
        oneline = oneline.strip()

        if not oneline:
            return ""
        
# We are lazzy... :-)
        if len(oneline) == 1:
            oneline += " "

        firstchar, otherchars = oneline[0], oneline[1:].lstrip()

        if firstchar != PLACEHOLDER:
            raise ValueError(
                f'missing ``{PLACEHOLDER}`` to indicate a path. '
                f'See line {nbline} (number relative to the block).'
            )

        if otherchars == "":
            raise ValueError(
                f'an empty path after ``{PLACEHOLDER}``. '
                f'See line {nbline} (number relative to the block).'
            )
            
        return otherchars


###
# This method builds ``self._lines`` the list of lines stored in 
# the path::``about.peuf`` file.
###
    def readlines(self) -> None:
        try:
            with ReadBlock(
                content = self.onedir / ABOUT_NAME,
                mode    = ABOUT_PEUF_MODE
            ) as datas:
                self._lines = datas.mydict("std nosep nonb")
    
        except ASTError:
            raise ValueError(
                f'invalid ``{ABOUT_NAME}`` found ine the following dir:'
                 '\n'
                f'{self.onedir}'
            )
