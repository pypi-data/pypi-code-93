__Author__='神秘的·'
__Project__='虹源三式'
__version__='定制版'#2.6.5.2
link='https://pypi.org/project/sycc/'
from time import sleep as dd
from sys import path
path.append('..')
import sys as s, time as t
def A():#作者&运算符相关
    print('\033[1;5;44m作者:' ,__Author__,'\033[0m')  
    print('\033[1;5;44m版本:',__version__ ,'\033[0m')
    print('\033[1;5;44mname:',__Project__,'\033[0m')
    print('\033[1;5;44mInformation',link,'\033[0m')
    dd(0.5)
    print('\033[1;44m支持\033[0m','输入运算符(选项除外),\033[0m(使用英文字符)')
    dd(0.2)
pai2='π' #下面要用到，提前放上来 
def dw():#单位
    print('请自行换算单位并保持单位一致')
from math import pi as pai1
def aboutpi():
    print('''
    选择π的大小
    1.输入1,π为3.14
    2.输入2,π为''',pai1,
    '''
    3.输入3,保留π(π不换成数字)
    4.输入4,π为自定义大小(大于3 ,小于3.2)
    其他选项:
    5.输入5,切换模式
    6.输入不是1~5中的数,直接退出''')
#A()#test