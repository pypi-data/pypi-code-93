from colorama import init
from time import sleep as dd
from sys import exit as tc
import platform as pd1
from sys import platform as pd2
os1=pd1.system()#大写
os2=pd2#
def pdios():
    print('正在判断系统')
    dd(0.4)
    print('\r检测到您的系统为',os1)
    if (os1=='Windows') or (os2=='windows'):
        print('*^_^* 欢迎Windows用户\n')
        init(autoreset=True)
    elif (os1=='Linux') or (os2=='linux'):
        print('$欢迎Linux用户\n')
        init(autoreset=False)
    else:
        print('虹源三式提醒您:不支持该系统,请联系lwb29@qq.com')
        dd(2)
        tc('exit')