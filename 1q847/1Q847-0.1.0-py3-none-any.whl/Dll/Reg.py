import ctypes, os
from comtypes.client import CreateObject


class RegDm:

    @classmethod
    def reg(cls):
        path = os.path.split(os.path.realpath(__file__))[0]
        reg_dm = ctypes.windll.LoadLibrary(path + '\DmReg.dll')
        reg_dm.SetDllPathW(path + '\dm.dll', 0)
        return CreateObject('dm.dmsoft')


    @classmethod
    def CreateDm(cls):
        dm = CreateObject('dm.dmsoft')
        return dm


if __name__ == '__main__':
    dm = RegDm.reg()
