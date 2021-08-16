from Py_dm.window import Windows


def 绑定雷电模拟器(dx):
    parentHwd = Windows(dx).枚举窗口句柄(0, '', 'LDPlayerMainFrame', 2)
    childHwd = Windows(dx).枚举窗口句柄(0, '', 'RenderWindow', 2)
    print('游戏窗口句柄:%s' % childHwd)
    print('父窗口句柄:%s' % parentHwd)
    ret = Windows(dx).绑定窗口EX(int(childHwd), "dx.graphic.opengl", "windows", "windows", "", 0)
    print("绑定成功") if ret == 1 else print("绑定失败")
