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
    This module implements the default behavior for the FTS3Agent for TPC and source SE selection
"""
import random
from DIRAC import S_OK, S_ERROR
from DIRAC.DataManagementSystem.Utilities.DMSHelpers import DMSHelpers
from DIRAC.DataManagementSystem.private.FTS3Plugins.DefaultFTS3Plugin import DefaultFTS3Plugin


class LHCbFTS3Plugin(DefaultFTS3Plugin):

  def selectTPCProtocols(self, ftsJob=None, sourceSEName=None, destSEName=None, **kwargs):
    # For the time being, just return the default.
    # Later, we may specialize some links
    # like EOS -> CTA
    return super(
        LHCbFTS3Plugin,
        self).selectTPCProtocols(
        ftsJob=ftsJob,
        sourceSEName=sourceSEName,
        destSEName=destSEName,
        **kwargs)

  def selectSourceSE(self, ftsFile, replicaDict, allowedSources):
    """
      This is basically a copy/paste of the parent method, with the exception
      of not staging between CTA and Echo....
    """

    allowedSourcesSet = set(allowedSources) if allowedSources else set()
    # Only consider the allowed sources

    # If we have a restriction, apply it, otherwise take all the replicas
    allowedReplicaSource = (set(replicaDict) & allowedSourcesSet) if allowedSourcesSet else replicaDict

    # If we have CTA and RAL as a tape source, choose RAL.
    if 'CERN-RAW' in allowedReplicaSource and 'RAL-RAW' in allowedReplicaSource:
      allowedReplicaSource = {'RAL-RAW': True}
    # pick a random source

    randSource = random.choice(list(allowedReplicaSource))  # one has to convert to list
    return randSource
