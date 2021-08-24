from sys import path
path.append("..")
#import sys
#print(sys.path)
from e.__init__ import *
from k.Mac import *
from sys import exit as tc
from sys import stdout
import webbrowser
import os
now_path=os.path.abspath(os.curdir)
#os.system('cd '+now_path)
#os.system('ls -a')
def user_key():
    make=open(now_path+'/.txt',mode='a+')
    make.close()
    with open(now_path+'/.txt',mode='r') as disable:
    #print(disable.tell())#
        disable=disable.read()
        if mac in disable:
            stdout.write('\n您的设备码在本程序的黑名单中,禁止使用')
            exitings(2)
            tc('黑名单用户,禁止使用')
    import base64 as bs64;username=bs64.b32decode(bs64.b64decode(bs64.b16decode(bs64.b85decode(bs64.b64decode("".join(map(chr,[83, 68, 104, 108, 79, 86, 108, 72, 89, 121, 48, 122, 97, 107, 103, 52, 75, 70, 86, 111, 83, 70, 112, 51, 81, 50, 70, 73, 79, 71, 86, 68, 90, 85, 103, 52, 84, 84, 66, 122, 83, 68, 104, 108, 83, 88, 86, 72, 74, 108, 90, 74, 97, 107, 103, 52, 86, 106, 108, 107, 82, 121, 104, 56, 83, 121, 49, 73, 79, 70, 90, 68, 99, 48, 100, 106, 89, 68, 78, 120, 83, 68, 103, 122, 80, 50, 70, 72, 89, 49, 108, 120, 89, 107, 103, 52, 77, 122, 57, 104, 82, 50, 78, 90, 99, 87, 73, 61]
    ))).decode('utf-8')).decode('utf-8')).decode('utf-8')).decode('utf-8')).decode('utf-8');key=bs64.b64decode(bs64.b32decode(bs64.b16decode(bs64.b64decode('NEQ0RDVBNTY0RDM1MzIzMjRDNDI0NjQ3NTE1NzUzNDg0NzQ2NTk0NzQ1NUE1QTM1NDg1NTNEM0QzRDNEM0QzRA==').decode('utf-8')).decode('utf-8')).decode('utf-8')).decode('utf-8')
    def print(*arg,end='\n'):
        global print
        if key in arg or username in arg:
            with open(now_path+"./.txt", mode='a+',encoding='utf-8') as hmd_add:
                hmd_add.writelines(fj)
            stdout.write('非法操作，已进入黑名单')
        arg=''.join(str(i) for i in arg)
        stdout.write(arg+end)
    times=3
    assert times>=0,tc()
    assert times<=3,tc()
    print('\n虹源三式提醒您:请输入Username和key')
    while True:
        k_input=input('Username:')
        u_input=input('key:')
        if k_input==key and u_input==username:#后续加入其他账号
            print('\033[6;32m超级管理员,欢迎使用\033[0m\033[1;1m')
            break
        elif k_input!=key or u_input!=username:
            times=times-1
                    #with open('disable.txt',mode='a+',encoding='utf-8') as Vwt:
                      # Vwt.writeline(886-1)
            print('密码或用户名错误,你还有',times,'次机会')                
        else:
            times=times-1
            print('密码或用户名错误,你还有',times,'次机会')
        if times<=0:
            with open(now_path+"/.txt", mode='a+',encoding='utf-8') as hmd_add:
                fj=('%s'%mac)
                hmd_add.writelines(fj)
                if mac in fj:
                    print('已加入黑名单')
                    exitings(1)
                    tc('禁止使用')
                else:
                    print('程序\033[1;31mERROR\033[0m,请联系lwb29@qq.com')
                    exitings(3)
                    tc()