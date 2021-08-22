#!/usr/bin/env python3

###
# This module allows to make a single path::``MD`` file from several single 
# ones (using or not an "automatic" merging).
###


from typing import *

from pathlib import Path

from natsort import natsorted

from .toc import *


# ------------------------------------ #
# -- SINGLE MD FROM MULTI SINGLE MD -- #
# ------------------------------------ #

###
# This class finds all the single path::``MD`` files and then builds a final
# single one.
###

class Builder():

###
# prototype::
#     output  = ; // See Python typing...
#               the path of the single final path::``MD`` file.
#     content = ; // See Python typing...
#               the path of the directory with the path::``MD`` files.
###
    def __init__(
        self,
        output : Path,
        content: Path,
    ) -> None:
        self.output  = output
        self.content = content
        
        self._lof: List[Path] = []


###
# This method is the great bandleader building the final path::``MD`` file
# from several single ones.
###
    def build(self) -> None:
        for name in [
            'build_lof',
            'merge',
        ]:
            getattr(self, name)()


###
# This method builds the list of the single path::``MD`` files.
###
    def build_lof(self) -> None:
# Do we have an about.peuf file?
        if (self.content / ABOUT_NAME).is_file():
            self._lof = TOC(self.content).extract()

            return

# Find all the MD files.
        self._lof = []

        for fileordir in self.content.iterdir():
            if not fileordir.is_file():
                continue

            if fileordir.suffix == MD_FILE_SUFFIX:
                self._lof.append(fileordir)

        self._lof = natsorted(self._lof)


###
# This method simply merges all the ¨md codes in a sigle path::``MD`` file.
###
    def merge(self) -> None:
# All the MD code.
        mdcode = []

        for onefile in self._lof:
            with onefile.open(
                encoding = 'utf-8',
                mode     = 'r',
            ) as f:
                mdcode.append(f.read().strip())

        mdcode = ('\n'*3).join(mdcode)

# We can build the file.
        with self.output.open(
            encoding = 'utf-8',
            mode     = 'w',
        ) as f:
            f.write(mdcode)