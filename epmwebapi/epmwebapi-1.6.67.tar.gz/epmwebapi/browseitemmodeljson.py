"""
Elipse Plant Manager - EPM Web API
Copyright (C) 2018 Elipse Software.
Distributed under the MIT License.
(See accompanying file LICENSE.txt or copy at http://opensource.org/licenses/MIT)
"""

class BrowseItemModelJSON(object):
  
  def __init__(self, path, nodeClassMask, referenceTypes):
    self._path = path
    self._nodeClassMask = nodeClassMask
    self._referenceTypes = referenceTypes

  def toDict(self):

    referenceTypes = []
    for item in self._referenceTypes:
        referenceTypes.append(item);

    return { 'path': self._path.toDict(), 
             'nodeClassMask': self._nodeClassMask, 
             'referenceTypes': referenceTypes }

