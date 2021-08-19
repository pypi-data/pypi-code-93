from quickstats._version import __version__

import os
import sys
import pathlib

import ROOT
ROOT.gROOT.SetBatch(True) 
ROOT.PyConfig.IgnoreCommandLineOptions = True
macro_path = pathlib.Path(__file__).parent.absolute()
"""
try:
    ROOT.gSystem.Load(os.path.join(macro_path, 'macros', 'RooTwoSidedCBShape_cxx'))
    from ROOT import RooTwoSidedCBShape
except Exception:
    pass
"""
MAX_WORKERS = 8