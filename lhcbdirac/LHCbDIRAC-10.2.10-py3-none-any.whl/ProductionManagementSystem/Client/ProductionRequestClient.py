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
"""Module holding ProductionRequestClient class."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from DIRAC.Core.Base.Client import Client, createClient

__RCSID__ = "$Id$"


@createClient('ProductionManagement/ProductionRequest')
class ProductionRequestClient(Client):
  """This class expose the methods of the Production Request Service."""

  def __init__(self, url=None, **kwargs):
    """c'tor.

    :param str url: can specify a specific URL
    """
    super(ProductionRequestClient, self).__init__(**kwargs)
    self.setServer('ProductionManagement/ProductionRequest')
    if url:
      self.setServer(url)
