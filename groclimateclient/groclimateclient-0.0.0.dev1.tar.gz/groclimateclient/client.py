from __future__ import division
from builtins import map
from builtins import zip
from datetime import datetime
# import numpy
# import pandas
from groclient import GroClient

class GroClimateClient(GroClient):
    def test(self):
        return self.lookup('regions', 1231)

