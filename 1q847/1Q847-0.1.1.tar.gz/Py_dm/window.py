class Windows:
    def __init__(self, dx):
        self.__dx = dx
    def 枚举窗口句柄(self, parent, title, class_name, filter):
        '''

        :param parent:整形数: 获得的窗口句柄是该窗口的子窗口的窗口句柄,取0时为获得桌面句柄

        :param title:字符串: 窗口标题. 此参数是模糊匹配.

        :param class_name:字符串: 窗口类名. 此参数是模糊匹配.

        :param filter:整形数: 取值定义如下
        1 : 匹配窗口标题,参数title有效

        2 : 匹配窗口类名,参数class_name有效.

        4 : 只匹配指定父窗口的第一层孩子窗口

        8 : 匹配所有者窗口为0的窗口,即顶级窗口

        16 : 匹配可见的窗口

        32 : 匹配出的窗口按照窗口打开顺序依次排列 <收费功能，具体详情点击查看>

        这些值可以相加,比如4+8+16就是类似于任务管理器中的窗口列表
        :return: 返回所有匹配的窗口句柄字符串,格式"hwnd1,hwnd2,hwnd3"
        '''
        hwnds = self.__dx.EnumWindow(parent, title, class_name, filter)
        return hwnds
    def 绑定窗口(self,hwnd,display,mouse,keypad,mode):
        dm_ret = self.__dx.BindWindow(hwnd,display,mouse,keypad,mode)
        return dm_ret
    def 绑定窗口EX(self,hwnd,display,mouse,keypad,public,mode):
        dm_ret = self.__dx.BindWindowEx(hwnd, display, mouse, keypad, public, mode)
        return dm_ret
    def 设置窗口大小(self,hwnd,width,height):
        dm_ret = self.__dx.SetWindowSize(hwnd,width,height)
    def 设置窗口位置(self,hwnd, x, y):
        dm_ret =self.__dx.MoveWindow(hwnd, x, y)
    def 设置窗口状态(self,hwnd,flag):
        dm_ret=self.__dx.SetWindowState(hwnd, flag)









