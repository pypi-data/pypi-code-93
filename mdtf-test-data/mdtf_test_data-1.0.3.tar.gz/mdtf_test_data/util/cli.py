#!/usr/bin/python
""" mdtf_test_data cli utilties """

class cli_holder(object):
    "Object with command line info from argparse"
    def __init__(self, convention, startyear, nyears, dlat, dlon, unittest):
        self.convention = convention
        self.startyear = startyear
        self.nyears = nyears
        self.dlat = dlat
        self.dlon = dlon
        self.unittest = unittest