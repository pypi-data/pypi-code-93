import base64 as bs64
from sys import path
path.append('..')
from sys import exit as tc
from e.__init__ import *
import platform,webbrowser
global mac
os=platform.system()
def bzc(time_num):
    print('当前系统或设备不支持，如想使用,请pip install ycc')
    print('下面将为您自动打开ycc在pypi上的地址')
    webbrowser.open('https://pypi.org/project/ycc/')
    exitings(time_num)
    tc('谢谢使用')
if os=='Windows':
    import uuid
    try:
        mac= uuid.UUID(int=uuid.getnode()).hex[-12:]
        mac= ':'.join([mac[e:e + 2] for e in range(0, 11, 2)])
        mac=str(bs64.b64encode(mac.encode('utf-8')),'utf-8')
        mac=mac+'\n'
    except:
        bzc(1.5)
elif os=='Linux':
    import uuid
    try:
        import netifaces
    except ImportError:
        import os
        os.system('pip install netifaces')
    net_list=netifaces.interfaces()
    if 'wlan0' in net_list:
        mac=netifaces.ifaddresses('wlan0')[netifaces.AF_LINK][0]['addr']
        mac=str(bs64.b64encode(mac.encode('utf-8')),'utf-8')
        mac='\n'+mac
    elif 'eth0' in net_list:
        mac=netifaces.ifaddresses('eth0')[netifaces.AF_LINK][0]['addr']
        mac=str(bs64.b64encode(mac.encode('utf-8')),'utf-8')
        mac='\n'+mac
    else:
        try:
            mac= uuid.UUID(int=uuid.getnode()).hex[-12:]
            mac= ':'.join([mac[e:e + 2] for e in range(0, 11, 2)])
            mac=str(bs64.b64encode(mac.encode('utf-8')),'utf-8')
            mac='\n'+mac
        except:
            bzc(2)
else:
    bzc(2)
