class Key:
    def __init__(self,dx):
        self.__dx=dx
    def KeyDown(self,a):
        self.__dx.KeyDown(a)
    def KeyDownChar(self,a):
        self.__dx.KeyDownChar(a)
    def KeyPress(self, a):
        self.__dx.KeyPress(a)

    def KeyPressChar(self, a):
        self.__dx.KeyPressChar(a)

    def KeyPressStr(self, a):
        self.__dx.KeyPressStr(a)
    def KeyUp(self, a):
        self.__dx.KeyUp(a)
    def KeyUpChar(self, a):
        self.__dx.KeyUpChar(a)