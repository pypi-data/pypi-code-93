from colorama import init
from time import sleep as dd
from sys import exit as tc
import platform
#import emoji
os=platform.system()
def pdios():
    print('正在判断系统')
    dd(0.4)
    print('\r检测到您的系统为',os)
    if (os=='Windows'):
        print('*^_^* 欢迎Windows用户\n')
        init(autoreset=True)
    elif (os=='Linux'):
        print('$欢迎Linux用户\n')
        init(autoreset=False)
    elif (os=='Unix'):
        print('^欢迎Unix用户\n')
        init(autoreset=False)
    elif (os=='Darwin'):
        print('欢迎Mac用户,以下显示可能出现异常')
        init(autoreset=False)
    elif os=='ios':
    	print('欢迎ios用户')
    	init(autoreset=False)
    else:
        print('无法您的判断系统,请更换设备或向lwb29@qq.com报告')
        print('你现在可以选择1.退出\n2.我能忍受，开始\n3.输入其他字符退出')
        choose_exit=input('请选择:')
        if choose_exit=='1':
            tc('goodbye')
        elif choose_exit=='2':
            pass
        else:
            tc('goodbye')