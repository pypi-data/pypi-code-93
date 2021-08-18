#!/usr/bin/env python

#
# Generated  by generateDS.py.
# Python 3.8.11 (default, Aug  3 2021, 15:09:35)  [GCC 7.5.0]
#
# Command line options:
#   ('--no-dates', '')
#   ('--no-versions', '')
#   ('--disable-xml', '')
#   ('--disable-generatedssuper-lookup', '')
#   ('--member-specs', 'list')
#   ('-f', '')
#   ('-a', 'xsd:')
#   ('-o', 'tests/disable_xml_super2_sup.py')
#   ('-s', 'tests/disable_xml_super2_sub.py')
#   ('--super', 'disable_xml_super2_sup')
#   ('--no-warnings', '')
#
# Command line arguments:
#   tests/disable_xml_super.xsd
#
# Command line:
#   generateDS.py --no-dates --no-versions --disable-xml --disable-generatedssuper-lookup --member-specs="list" -f -a "xsd:" -o "tests/disable_xml_super2_sup.py" -s "tests/disable_xml_super2_sub.py" --super="disable_xml_super2_sup" --no-warnings tests/disable_xml_super.xsd
#
# Current working directory (os.getcwd()):
#   generateds
#

import os
import sys
## from lxml import etree as etree_

import disable_xml_super2_sup as supermod

## def parsexml_(infile, parser=None, **kwargs):
##     if parser is None:
##         # Use the lxml ElementTree compatible parser so that, e.g.,
##         #   we ignore comments.
##         parser = etree_.ETCompatXMLParser()
##     try:
##         if isinstance(infile, os.PathLike):
##             infile = os.path.join(infile)
##     except AttributeError:
##         pass
##     doc = etree_.parse(infile, parser=parser, **kwargs)
##     return doc

## def parsexmlstring_(instring, parser=None, **kwargs):
##     if parser is None:
##         # Use the lxml ElementTree compatible parser so that, e.g.,
##         #   we ignore comments.
##         try:
##             parser = etree_.ETCompatXMLParser()
##         except AttributeError:
##             # fallback to xml.etree
##             parser = etree_.XMLParser()
##     element = etree_.fromstring(instring, parser=parser, **kwargs)
##     return element

#
# Globals
#

ExternalEncoding = ''
SaveElementTreeNode = True

#
# Data representation classes
#


class PackageTypeSub(supermod.PackageType):
    def __init__(self, Address=None, **kwargs_):
        super(PackageTypeSub, self).__init__(Address,  **kwargs_)
supermod.PackageType.subclass = PackageTypeSub
# end class PackageTypeSub


