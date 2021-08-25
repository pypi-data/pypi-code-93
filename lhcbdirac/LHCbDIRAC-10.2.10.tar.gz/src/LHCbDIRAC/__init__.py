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
"""
   LHCbDIRAC - LHCb extension of DIRAC

   References:
    DIRAC: https://github.com/DIRACGrid/DIRAC
    LHCbDIRAC: https://gitlab.cern.ch/lhcb-dirac/LHCbDIRAC

   The distributed data production and analysis system of LHCb.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)  # pylint: disable=redefined-builtin

import six

rootPath = os.path.dirname(os.path.realpath(__path__[0]))

# Define Version
if six.PY3:
  from pkg_resources import get_distribution, DistributionNotFound

  try:
    __version__ = get_distribution(__name__).version
    version = __version__
  except DistributionNotFound:
    # package is not installed
    version = "Unknown"
else:
  majorVersion = 10
  minorVersion = 2
  patchLevel = 10
  preVersion = 0

  version = "v%sr%s" % (majorVersion, minorVersion)
  __version__ = "%s.%s" % (majorVersion, minorVersion)
  buildVersion = "v%dr%d" % (majorVersion, minorVersion)
  if patchLevel:
    version = "%sp%s" % (version, patchLevel)
    __version__ += ".%s" % patchLevel
    buildVersion = "%s build %s" % (buildVersion, patchLevel)
  if preVersion:
    version = "%s-pre%s" % (version, preVersion)
    __version__ += "a%s" % preVersion
    buildVersion = "%s pre %s" % (buildVersion, preVersion)


def extension_metadata():
  return {
      "primary_extension": True,
      "priority": 100,
      "setups": {
          "LHCb-Production": "dips://lhcb-conf-dirac.cern.ch:9135/Configuration/Server",
          "LHCb-Certification": "dips://lhcb-cert-dirac.cern.ch:9135/Configuration/Server",
      },
      "default_setup": "LHCb-Production",
  }
