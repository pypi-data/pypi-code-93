#!/usr/bin/env python
###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import re
import fileinput
import json
from diraccfg import parseVersion, CFG


def linePrepend(filename, line):
  with open(filename, 'r+') as f:
    content = f.read()
    f.seek(0, 0)
    f.write(line.rstrip('\r\n') + '\n' + content)


def lineReplace(filename, lineToReplace, newLine):
  for line in fileinput.input(filename, inplace=True):
    if lineToReplace == 0:
      print(newLine)
    else:
      print(line, end="")
    lineToReplace -= 1


# Load version from last release and get last version
LATEST_RELEASE = os.environ.get('LATEST_RELEASE')

# Read in the releases.cfg as JSON
res = CFG().loadFromFile("releases.cfg").getAsDict()

# From the releases.cfg look up the versions of DIRAC, LHCbWebDIRAC, LHCbDIRACOS used in last version
LAST_DIRAC = res['Releases'][LATEST_RELEASE]['Depends'].split(':', 1)[-1]
LAST_LHCbDIRACOS = res['Releases'][LATEST_RELEASE]['DIRACOS'].split(':', 1)[-1]
LAST_LHCbWebDIRAC = res['Releases'][LATEST_RELEASE]['Modules'].split(':', 2)[-1]

# Read env variables defined by user or use version from previous release
DIRAC = os.getenv('DIRAC', LAST_DIRAC)
LHCbDIRACOS = os.getenv('LHCbDIRACOS', LAST_LHCbDIRACOS)
LHCbWebDIRAC = os.getenv('LHCbWebDIRAC', LAST_LHCbWebDIRAC)

# Check if user specified version for next release
NEXT_RELEASE = os.environ.get('NEXT_RELEASE')

# If the user did not specify a release increment the current version by 1
version = None
versionString = None
versionStringPy3 = None
preRelease = None
if not NEXT_RELEASE:
  version = parseVersion(LATEST_RELEASE)
  if version[3] is None:
    # Increment patch version for 1
    version = (version[0], version[1], version[2] + 1, version[3])
    versionString = "v%sr%sp%s" % (version[0], version[1], version[2])
    versionStringPy3 = "v%s.%s.%s" % (version[0], version[1], version[2])
    preRelease = False
    print("Automatically increment current release %s to %s" % (LATEST_RELEASE, versionString))
  else:
    # Increment pre version for 1
    version = (version[0], version[1], version[2], version[3] + 1)
    versionString = "v%sr%s-pre%s" % (version[0], version[1], version[3])
    versionStringPy3 = "v%s.%s.0a%s" % (version[0], version[1], version[3])
    preRelease = True
    print("Automatically increment current release %s to %s" % (LATEST_RELEASE, versionString))
else:
  # Use the version specified by NEXT_RELEASE
  version = parseVersion(NEXT_RELEASE)
  print("Preparing files for release %s" % NEXT_RELEASE)
  if version[3] is None:
    preRelease = False
  else:
    preRelease = True

# Construct the new releases section
newCFG = "\n  %s\n  {\n    Modules = LHCbDIRAC:%s, LHCbWebDIRAC:%s\n    " \
    "Depends = DIRAC:%s\n    DIRACOS = LHCb:%s\n  }\n" % \
    (versionString, versionString, LHCbWebDIRAC, DIRAC, LHCbDIRACOS)
print("I am adding the following section to releases.cfg")
print(newCFG)

# Insert into releases.cfg the new release
lineReplace("releases.cfg", 22, newCFG)

# Add information about version to release notes
linePrepend("../notes.txt", "LHCbDIRACOS %s" % LHCbDIRACOS)
linePrepend("../notes.txt", "LHCbWebDIRAC %s" % LHCbWebDIRAC)
linePrepend("../notes.txt", "Based on DIRAC %s" % DIRAC)
linePrepend("../notes.txt", versionString)


# store into artifact the version and series for later usage in tagging process
with open('version.txt', 'a') as fver:
  fver.write(versionString)
if versionStringPy3:
  with open('versionPy3.txt', 'a') as fver:
    fver.write(versionStringPy3)
with open('series.txt', 'a') as fser:
  fser.write("v%sr%s" % (version[0], version[1]))

# change the __init__.py
# Currently master and devel have different layout
if not preRelease:
  lineReplace("src/LHCbDIRAC/__init__.py", 43, "  majorVersion = %s" % version[0])
  lineReplace("src/LHCbDIRAC/__init__.py", 44, "  minorVersion = %s" % version[1])
  lineReplace("src/LHCbDIRAC/__init__.py", 45, "  patchLevel = %s" % version[2])
  lineReplace("src/LHCbDIRAC/__init__.py", 46, "  preVersion = %s" % 0)
else:
  lineReplace("src/LHCbDIRAC/__init__.py", 43, "  majorVersion = %s" % version[0])
  lineReplace("src/LHCbDIRAC/__init__.py", 44, "  minorVersion = %s" % version[1])
  lineReplace("src/LHCbDIRAC/__init__.py", 45, "  patchLevel = %s" % 0)
  lineReplace("src/LHCbDIRAC/__init__.py", 46, "  preVersion = %s" % version[3])
