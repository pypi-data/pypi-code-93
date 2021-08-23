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
#   ('-o', 'tests/ipo2_sup.py')
#   ('-s', 'tests/ipo2_sub.py')
#   ('--super', 'ipo2_sup')
#
# Command line arguments:
#   tests/ipo.xsd
#
# Command line:
#   generateDS.py --no-dates --no-versions --member-specs="list" -f -o "tests/ipo2_sup.py" -s "tests/ipo2_sub.py" --super="ipo2_sup" tests/ipo.xsd
#
# Current working directory (os.getcwd()):
#   generateds
#

import os
import sys
from lxml import etree as etree_

import ipo2_sup as supermod

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

ExternalEncoding = ''
SaveElementTreeNode = True

#
# Data representation classes
#


class PurchaseOrderTypeSub(supermod.PurchaseOrderType):
    def __init__(self, orderDate=None, shipTo=None, billTo=None, comment=None, items=None, **kwargs_):
        super(PurchaseOrderTypeSub, self).__init__(orderDate, shipTo, billTo, comment, items,  **kwargs_)
supermod.PurchaseOrderType.subclass = PurchaseOrderTypeSub
# end class PurchaseOrderTypeSub


class ItemsSub(supermod.Items):
    def __init__(self, item=None, **kwargs_):
        super(ItemsSub, self).__init__(item,  **kwargs_)
supermod.Items.subclass = ItemsSub
# end class ItemsSub


class AddressSub(supermod.Address):
    def __init__(self, name=None, street=None, city=None, extensiontype_=None, **kwargs_):
        super(AddressSub, self).__init__(name, street, city, extensiontype_,  **kwargs_)
supermod.Address.subclass = AddressSub
# end class AddressSub


class USAddressSub(supermod.USAddress):
    def __init__(self, name=None, street=None, city=None, state=None, zip=None, **kwargs_):
        super(USAddressSub, self).__init__(name, street, city, state, zip,  **kwargs_)
supermod.USAddress.subclass = USAddressSub
# end class USAddressSub


class UKAddressSub(supermod.UKAddress):
    def __init__(self, name=None, street=None, city=None, exportCode=1, postcode=None, **kwargs_):
        super(UKAddressSub, self).__init__(name, street, city, exportCode, postcode,  **kwargs_)
supermod.UKAddress.subclass = UKAddressSub
# end class UKAddressSub


class itemTypeSub(supermod.itemType):
    def __init__(self, partNum=None, productName=None, quantity=None, USPrice=None, comment=None, shipDate=None, **kwargs_):
        super(itemTypeSub, self).__init__(partNum, productName, quantity, USPrice, comment, shipDate,  **kwargs_)
supermod.itemType.subclass = itemTypeSub
# end class itemTypeSub


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
        rootTag = 'PurchaseOrderType'
        rootClass = supermod.PurchaseOrderType
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
            namespacedef_='xmlns:ipo="http://www.example.com/IPO"',
            pretty_print=True)
    return rootObj


def parseEtree(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'PurchaseOrderType'
        rootClass = supermod.PurchaseOrderType
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
        rootTag = 'PurchaseOrderType'
        rootClass = supermod.PurchaseOrderType
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        rootNode = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_='xmlns:ipo="http://www.example.com/IPO"')
    return rootObj


def parseLiteral(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'PurchaseOrderType'
        rootClass = supermod.PurchaseOrderType
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
    if not silence:
        sys.stdout.write('#from ipo2_sup import *\n\n')
        sys.stdout.write('import ipo2_sup as model_\n\n')
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
