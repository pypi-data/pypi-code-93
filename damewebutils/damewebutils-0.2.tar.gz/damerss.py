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

# This program returns a list of broken links in an url

import requests
from lxml import html
import os
import re
import xml.etree.ElementTree as ET
import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument("url", help="url to download rss files")
parser.add_argument("-n", "--number", type=int, default=5)
parser.add_argument("-f", "--file", help="file with rss downloaded")
args = parser.parse_args()

r = requests.get(args.url)
fo = open("/tmp/rss.xml", "w")
fo.write(r.text)
fo.close()

tree = ET.parse('/tmp/rss.xml')
root = tree.getroot()

for elem in tree.iter():
    if (elem.tag == "title"):
        print("----------------------------------------------------")
        print(elem.text)
    if (elem.tag == "link"):
        print(elem.text)
        print("----------------------------------------------------")
