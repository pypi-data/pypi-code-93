#!/usr/bin/env python

#
# Generated  by generateDS.py.
# Python 3.8.11 (default, Aug  3 2021, 15:09:35)  [GCC 7.5.0]
#
# Command line options:
#   ('--no-dates', '')
#   ('--no-versions', '')
#   ('--member-specs', 'list')
#   ('-f', '')
#   ('-o', 'tests/validate_simpletypes2_sup.py')
#   ('-s', 'tests/validate_simpletypes2_sub.py')
#   ('--super', 'validate_simpletypes2_sup')
#   ('--external-encoding', 'utf-8')
#   ('--export', 'write validate')
#
# Command line arguments:
#   tests/validate_simpletypes.xsd
#
# Command line:
#   generateDS.py --no-dates --no-versions --member-specs="list" -f -o "tests/validate_simpletypes2_sup.py" -s "tests/validate_simpletypes2_sub.py" --super="validate_simpletypes2_sup" --external-encoding="utf-8" --export="write validate" tests/validate_simpletypes.xsd
#
# Current working directory (os.getcwd()):
#   generateds
#

import os
import sys
from lxml import etree as etree_

import validate_simpletypes2_sup as supermod

def parsexml_(infile, parser=None, **kwargs):
    if parser is None:
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        parser = etree_.ETCompatXMLParser()
    try:
        if isinstance(infile, os.PathLike):
            infile = os.path.join(infile)
    except AttributeError:
        pass
    doc = etree_.parse(infile, parser=parser, **kwargs)
    return doc

def parsexmlstring_(instring, parser=None, **kwargs):
    if parser is None:
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        try:
            parser = etree_.ETCompatXMLParser()
        except AttributeError:
            # fallback to xml.etree
            parser = etree_.XMLParser()
    element = etree_.fromstring(instring, parser=parser, **kwargs)
    return element

#
# Globals
#

ExternalEncoding = 'utf-8'
SaveElementTreeNode = True

#
# Data representation classes
#


class containerTypeSub(supermod.containerType):
    def __init__(self, sample1=None, sample2_bad=None, sample3_bad=None, sample4_bad=None, sample2=None, **kwargs_):
        super(containerTypeSub, self).__init__(sample1, sample2_bad, sample3_bad, sample4_bad, sample2,  **kwargs_)
supermod.containerType.subclass = containerTypeSub
# end class containerTypeSub


class simpleOneTypeSub(supermod.simpleOneType):
    def __init__(self, integer_range_1_value_with_default='6', integer_range_1_value=5, pattern_value=None, token_enum_value=None, integer_range_incl_value=None, integer_range_excl_value=None, min_max_length_value=None, length_value=None, totalDigits_value=None, date_minincl_value=None, date_maxincl_value=None, date_minexcl_value=None, date_maxexcl_value=None, time_minincl_value=None, time_maxincl_value=None, time_minexcl_value=None, time_maxexcl_value=None, datetime_minincl_value=None, datetime_maxincl_value=None, datetime_minexcl_value=None, datetime_maxexcl_value=None, vbar_pattern_value=None, unicode_pattern_value=None, gyear_minincl_value=None, gyearmonth_minincl_value=None, simpletype0=None, simpletype1=None, simpletype2=None, simpletype0a=None, simpletype1a=None, simpletype2a=None, hexbinary_simple_value1=None, hexbinary_simple_value2=None, decimal_enumeration_simple_value1=None, decimal_enumeration_simple_value2=None, anonymous_float_value=None, primative_integer=None, primative_float=None, **kwargs_):
        super(simpleOneTypeSub, self).__init__(integer_range_1_value_with_default, integer_range_1_value, pattern_value, token_enum_value, integer_range_incl_value, integer_range_excl_value, min_max_length_value, length_value, totalDigits_value, date_minincl_value, date_maxincl_value, date_minexcl_value, date_maxexcl_value, time_minincl_value, time_maxincl_value, time_minexcl_value, time_maxexcl_value, datetime_minincl_value, datetime_maxincl_value, datetime_minexcl_value, datetime_maxexcl_value, vbar_pattern_value, unicode_pattern_value, gyear_minincl_value, gyearmonth_minincl_value, simpletype0, simpletype1, simpletype2, simpletype0a, simpletype1a, simpletype2a, hexbinary_simple_value1, hexbinary_simple_value2, decimal_enumeration_simple_value1, decimal_enumeration_simple_value2, anonymous_float_value, primative_integer, primative_float,  **kwargs_)
supermod.simpleOneType.subclass = simpleOneTypeSub
# end class simpleOneTypeSub


class simpleTwoTypeSub(supermod.simpleTwoType):
    def __init__(self, simpleTwoElementOne=None, **kwargs_):
        super(simpleTwoTypeSub, self).__init__(simpleTwoElementOne,  **kwargs_)
supermod.simpleTwoType.subclass = simpleTwoTypeSub
# end class simpleTwoTypeSub


class simpleTwoElementOneTypeSub(supermod.simpleTwoElementOneType):
    def __init__(self, simpleTwoElementTwo=None, **kwargs_):
        super(simpleTwoElementOneTypeSub, self).__init__(simpleTwoElementTwo,  **kwargs_)
supermod.simpleTwoElementOneType.subclass = simpleTwoElementOneTypeSub
# end class simpleTwoElementOneTypeSub


def get_root_tag(node):
    tag = supermod.Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = None
    rootClass = supermod.GDSClassesMapping.get(tag)
    if rootClass is None and hasattr(supermod, tag):
        rootClass = getattr(supermod, tag)
    return tag, rootClass


def parse(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'containerType'
        rootClass = supermod.containerType
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_='',
            pretty_print=True)
    return rootObj


def parseEtree(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'containerType'
        rootClass = supermod.containerType
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    mapping = {}
    rootElement = rootObj.to_etree(None, name_=rootTag, mapping_=mapping)
    reverse_mapping = rootObj.gds_reverse_node_mapping(mapping)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
    if not silence:
        content = etree_.tostring(
            rootElement, pretty_print=True,
            xml_declaration=True, encoding="utf-8")
        sys.stdout.write(content)
        sys.stdout.write('\n')
    return rootObj, rootElement, mapping, reverse_mapping


def parseString(inString, silence=False):
    if sys.version_info.major == 2:
        from StringIO import StringIO
    else:
        from io import BytesIO as StringIO
    parser = None
    rootNode= parsexmlstring_(inString, parser)
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'containerType'
        rootClass = supermod.containerType
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        rootNode = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_='')
    return rootObj


def parseLiteral(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'containerType'
        rootClass = supermod.containerType
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
    if not silence:
        sys.stdout.write('#from validate_simpletypes2_sup import *\n\n')
        sys.stdout.write('import validate_simpletypes2_sup as model_\n\n')
        sys.stdout.write('rootObj = model_.rootClass(\n')
        rootObj.exportLiteral(sys.stdout, 0, name_=rootTag)
        sys.stdout.write(')\n')
    return rootObj


USAGE_TEXT = """
Usage: python ???.py <infilename>
"""


def usage():
    print(USAGE_TEXT)
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
    infilename = args[0]
    parse(infilename)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    main()
