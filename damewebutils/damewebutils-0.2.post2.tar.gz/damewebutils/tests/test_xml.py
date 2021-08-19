#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2019  David Arroyo Menéndez

# Author: David Arroyo Menéndez <davidam@gnu.org>
# Maintainer: David Arroyo Menéndez <davidam@gnu.org>

# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.

# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with damewebutils; see the file LICENSE.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA,

from unittest import TestCase
from xml.dom import minidom
import xml.etree.ElementTree as ET

class TestXml(TestCase):

    def test_minidom(self):
        xmldoc = minidom.parse('files/items.xml')
        itemlist = xmldoc.getElementsByTagName('item')
        self.assertEqual(len(itemlist), 4)
        l = []
        for s in itemlist:
            l.append(s.attributes['name'].value)
        self.assertEqual(l, ['item1', 'item2', 'item3', 'item4'])

    def test_et(self):
        tree = ET.parse('files/rss.xml')
        l = []
        for elem in tree.iter():
            l.append(elem)
        self.assertEqual(len(l), 855)

    def test_et_modify(self):
        tree = ET.parse('files/index.xhtml')
        p = tree.find("body/p")
        links = list(p.iter("a"))
        self.assertEqual(2, len(links))
        for i in links:
            i.attrib["target"] = "blank"
        tree.write("files/output.xhtml")
        self.assertNotEqual("files/index.xhtml", "files/output.xhtml")

    def test_et_tags_text_attrib(self):
        tree = ET.parse('files/rss.xml')
        item = tree.find("channel/item")
        links = list(item.iter("link"))
        self.assertEqual(1, len(links))
        # root = tree.getroot()
        # rtitle = root.find("channel/item")
        # rtitles = list(rtitle.iter("title"))
        # self.assertEqual(1, len(titles))
#        self.assertEqual(2, len(titles))

    def test_et_modify(self):
        tree = ET.parse('files/index.xhtml')
        p = tree.find("body/p")
        links = list(p.iter("a"))
        self.assertEqual(2, len(links))
        for i in links:
            i.attrib["target"] = "blank"
        tree.write("files/output.xhtml")
        self.assertNotEqual("files/index.xhtml", "files/output.xhtml")

    def test_build_xml(self):
        a = ET.Element('elem')
        c = ET.SubElement(a, 'child1')
        c.text = "some text"
        d = ET.SubElement(a, 'child2')
        b = ET.Element('elem_b')
        root = ET.Element('root')
        root.extend((a, b))
        tree = ET.ElementTree(root)
        tree.write("files/tree_created.xml")
        fo = open("files/tree_created.xml", "r+")
        lines = fo.readlines()
        self.assertEqual(['<root><elem><child1>some text</child1><child2 /></elem><elem_b /></root>'], lines)

    def test_include_xml(self):
        from xml.etree import ElementTree, ElementInclude
        tree = ElementTree.parse("files/document.xml")
        root = tree.getroot()
        ElementInclude.include(root)
        tree.write("files/tree_created.xml")
        fo = open("files/tree_created.xml", "r+")
        lines = fo.readlines()
        self.assertEqual(['<document>\n', '  <document>\n', '  <para>This is a paragraph.</para>\n', '</document>\n', '</document>'], lines)

    def test_foaf(self):
        import rdflib
        g = rdflib.Graph()
        # ... add some triples to g somehow ...
        g.parse("files/foaf.rdf")
        qres = g.query(
            """SELECT DISTINCT ?aname ?bname
            WHERE {
            ?a foaf:knows ?b .
            ?a foaf:name ?aname .
            ?b foaf:name ?bname .
            }""")
        cnt = 0
        for row in qres:
            cnt = cnt +1
        self.assertEqual(cnt, 1)

