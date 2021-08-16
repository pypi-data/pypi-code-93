from win32com.client import Dispatch
def 创建大漠对象():
    dm =Dispatch('dm.dmsoft')
    return dm
def 注册收费功能(dx,zcm,fjm):
    ret = dx.Reg(zcm,fjm)
    if ret == 1 :
        print('收费功能注册成功')