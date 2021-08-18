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
# along with damewebutils; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA,

import requests
from lxml import html
import os
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("url", help="url to analize broken links")
args = parser.parse_args()

start_url = args.url + '/'
response = requests.get(start_url)
tree = html.fromstring(response.text)
imgs = tree.cssselect('img')  # or tree.xpath('//a')

out = []
for i in imgs:
    # we use this if just in case some <a> tags lack an href attribute
    if 'src' in i.attrib:
        out.append(i.attrib['src'])

absoluteurls = []
for o in out:
    if 'http' in o:
        absoluteurls.append(o)
    else:
        o = start_url + o
        absoluteurls.append(o)

buggyurls = []
for i in absoluteurls:
    print(i)
    r = requests.get(i)
    r.raise_for_status()
    print(r.status_code)
    if (r.status_code != 200):
        buggyurls.append(i)

nbuggyurls = len(buggyurls)
if (nbuggyurls == 1):
    print("%s images with troubles:" % str(nbuggyurls))
else:
    print("%s images with troubles:" % str(nbuggyurls))

print(buggyurls)
nurls = len(imgs) - len(buggyurls)
if (nurls == 1):
    print(str(nurls) + " good images")
else:
    print(str(nurls) + " good images")
