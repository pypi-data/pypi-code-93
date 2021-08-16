from Py_dm.mouse import Mouse
class Pic:
    def __init__(self, dx):
        self.__dx = dx

    def 大漠找图(self, x1, y1, x2, y2, name):
        '''
        找到返回字符串，没找到返回-1
        '''

        dm_ret = self.__dx.FindPicE(x1, y1, x2, y2, name, '050505', 0.9, 0 )
        if dm_ret != '-1|-1|-1':
            return 1
        else:
            return -1
    def 等待图片出现(self,x1, y1, x2, y2, name):

        while self.大漠找图(x1, y1, x2, y2, name) ==-1:
            self.__dx.Delay(1000)
        print('找到图片',name)





    def 大漠找图单击(self, x1, y1, x2, y2, name):
        dm_ret = self.__dx.FindPicE(x1, y1, x2, y2, name, '050505', 0.9, 0 )
        pos = dm_ret.split('|')
        if pos[0]!='-1':
            Mouse(self.__dx).大漠移动单击(pos[1], pos[2])
            return 1
        else:

            return -1

    def 大漠找图偏移单击(self, x1, y1, x2, y2, name,x3,y3):
        dm_ret = self.__dx.FindPicE(x1, y1, x2, y2, name, '050505', 0.9, 0)
        pos = dm_ret.split('|')
        if pos[0] != '-1':
            Mouse(self.__dx).大漠移动单击(x3, y3)
            return 1
        else:

            return -1

    def 大漠找图偏移单击EX(self, x1, y1, x2, y2, name, x3, y3):
        dm_ret = self.__dx.FindPicE(x1, y1, x2, y2, name, '050505', 0.9, 0)
        pos = dm_ret.split('|')
        if pos[0] != '-1':
            Mouse(self.__dx).大漠移动单击(pos[1], pos[2])
            self.__dx.MoveR(x3,y3)
            return 1
        else:

            return -1
    def 大漠找图双击(self, x1, y1, x2, y2, name):
        dm_ret = self.__dx.FindPicE(x1, y1, x2, y2, name, '050505', 0.9, 0)
        pos = dm_ret.split('|')

        if pos[0]!='-1':
            Mouse(self.__dx).大漠移动双击(pos[1], pos[2])
            return 1
        else:
            return -1