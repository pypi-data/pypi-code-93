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
"""Add files to a transformation."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__RCSID__ = "$Id$"

from DIRAC.Core.Utilities.DIRACScript import DIRACScript


@DIRACScript()
def main():
  from LHCbDIRAC.TransformationSystem.Utilities.ScriptUtilities import getTransformations

  import os
  import DIRAC
  from DIRAC import gLogger
  from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript, Script

  dmScript = DMScript()
  dmScript.registerFileSwitches()

  Script.registerSwitch('', 'NoRunInfo', '   Use if no run information is required')
  Script.registerSwitch("", "Chown=", "   Give user/group for chown of the directories of files in the FC")

  Script.parseCommandLine(ignoreErrors=True)

  Script.setUsageMessage('\n'.join([__doc__,
                                    'Usage:',
                                    '  %s [option|cfgfile] ...' % Script.scriptName, ]))

  runInfo = True
  userGroup = None

  switches = Script.getUnprocessedSwitches()
  for opt, val in switches:
    if opt == 'NoRunInfo':
      runInfo = False
    elif opt == 'Chown':
      userGroup = val.split('/')
      if len(userGroup) != 2 or not userGroup[1].startswith('lhcb_'):
        gLogger.fatal("Wrong user/group")
        DIRAC.exit(2)

  if userGroup:
    from DIRAC.Core.Security.ProxyInfo import getProxyInfo
    res = getProxyInfo()
    if not res['OK']:
      gLogger.fatal("Can't get proxy info", res['Message'])
      DIRAC.exit(1)
    properties = res['Value'].get('groupProperties', [])
    if 'FileCatalogManagement' not in properties:
      gLogger.error("You need to use a proxy from a group with FileCatalogManagement")
      DIRAC.exit(5)

  from LHCbDIRAC.DataManagementSystem.Utilities.FCUtilities import chown
  from LHCbDIRAC.TransformationSystem.Utilities.PluginUtilities import addFilesToTransformation
  from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
  trClient = TransformationClient()
  transList = getTransformations(Script.getPositionalArgs())
  if not transList:
    DIRAC.exit(1)

  requestedLFNs = dmScript.getOption('LFNs')
  if not requestedLFNs:
    gLogger.always('No files to add')
    DIRAC.exit(0)

  if userGroup:
    directories = set([os.path.dirname(lfn) for lfn in requestedLFNs])
    res = chown(directories, user=userGroup[0], group=userGroup[1])
    if not res['OK']:
      gLogger.fatal("Error changing ownership", res['Message'])
      DIRAC.exit(3)
    gLogger.notice("Successfully changed owner/group for %d directories" % res['Value'])

  rc = 0
  for transID in transList:
    res = addFilesToTransformation(transID, requestedLFNs, addRunInfo=runInfo)
    if res['OK']:
      gLogger.always('Successfully added %d files to transformation %d' % (len(res['Value']), transID))
    else:
      gLogger.always('Failed to add %d files to transformation %d' % (len(requestedLFNs), transID), res['Message'])
      rc = 2
  DIRAC.exit(rc)


if __name__ == "__main__":
  main()
