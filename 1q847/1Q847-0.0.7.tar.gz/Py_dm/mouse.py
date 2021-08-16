class Mouse:
    '''
    模块为dm鼠标类模块。
    例子：mouse = Mouse(dm)
    mouse.大漠移动(100,200)
    '''
    def __init__(self,dx):
        self.__dx = dx
    def 大漠移动(self,x,y):
        self.__dx.MoveTo(int(x),int(y))
    def 大漠鼠标左单击(self):
        self.__dx.LeftClick()
    def 大漠鼠标左双击(self):
        self.__dx.LeftDoubleClick()
    def 大漠鼠标左键按下(self):
        self.__dx.LeftDown()
    def 大漠鼠标左键弹起(self):
        self.__dx.LeftUp()
    def 大漠移动单击(self,x,y):
        self.大漠移动(x,y)
        self.大漠鼠标左单击()
    def 大漠移动双击(self,x,y):
        self.大漠移动(x,y)
        self.大漠鼠标左双击()

    def 拖动(self,x1,y1,x2,y2):
        self.大漠移动(x1,y1)
        self.大漠鼠标左键按下()
        self.大漠移动(x2,y2)
        self.大漠鼠标左键弹起()







