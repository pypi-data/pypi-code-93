# Natural Language Toolkit: Inference
#
# Copyright (C) 2001-2021 NLTK Project
# Author: Dan Garrette <dhgarrette@gmail.com>
#         Ewan Klein <ewan@inf.ed.ac.uk>
#
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT

"""
Classes and interfaces for theorem proving and model building.
"""

from nltkma.inference.api import ParallelProverBuilder, ParallelProverBuilderCommand
from nltkma.inference.mace import Mace, MaceCommand
from nltkma.inference.prover9 import Prover9, Prover9Command
from nltkma.inference.resolution import ResolutionProver, ResolutionProverCommand
from nltkma.inference.tableau import TableauProver, TableauProverCommand
from nltkma.inference.discourse import (
    ReadingCommand,
    CfgReadingCommand,
    DrtGlueReadingCommand,
    DiscourseTester,
)
