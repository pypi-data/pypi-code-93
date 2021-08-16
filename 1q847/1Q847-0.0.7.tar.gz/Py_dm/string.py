from Py_dm import mouse


class Str:
    def __init__(self, dx):
        self.__dx = dx

    def 设置字库(self, index, file):
        dm_ret = self.__dx.SetDict(index, file)

    def 找字(self, x1, y1, x2, y2, string, color_format, dic=0):
        self.__dx.UseDict(dic)
        dm_ret = self.__dx.FindStrE(x1, y1, x2, y2, string, color_format, 1.0)
        return dm_ret

    def 找字左击(self, x1, y1, x2, y2, string, color_format, dic=0):
        self.__dx.UseDict(dic)
        dm_ret = self.__dx.FindStrE(x1, y1, x2, y2, string, color_format, 1.0)
        pos = dm_ret.split('|')
        if pos[0] != '-1':
            mouse.Mouse(self.__dx).大漠移动单击(pos[1], pos[2])
            return 1
        else:
            return -1
