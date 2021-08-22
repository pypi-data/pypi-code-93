from pymodels import *

class FixedBondVal:
    def __init__(self):
        pass

    @property
    def bond_info(self):
        return self.__bond_info

    @bond_info.setter
    def bond_info(self, bond_info):
        self.__bond_info = bond_info
        