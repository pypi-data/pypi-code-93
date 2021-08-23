from winreg import *
import os, sys, win32gui, win32con

class WindowsEnv:
    """     Usage:
            windowsEnv = WindowsEnv()
            subprocess.call(["cmd"], shell=True)
    """
    def __init__(self):
        try:
            path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
            reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
            key = OpenKey(reg, path, 0, KEY_ALL_ACCESS)
            
            # if len(sys.argv) == 1:
            #     self.show(key)
            # else:
            #     name, value = sys.argv[1].split('=')
            #     if name.upper() == 'PATH':
            #         value = self.queryValue(key, name) + ';' + value
            #     if value:
            #         SetValueEx(key, name, 0, REG_EXPAND_SZ, value)
            #     else:
            #         DeleteValue(key, name)

            #self.show("VBOX_MSI_INSTALL_PATH")
            #self.show(key)

            #SetValueEx(key, "XXX_JUNIOR", 0, REG_EXPAND_SZ, "UALTER")
                
            win32gui.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')
                                
        except Exception as e:
            raise e
    
    def show(self, key):
        for i in range(1024):                                           
            try:
                n,v,t = EnumValue(key, i)
                print('%s=%s' % (n, v))
            except EnvironmentError:
                break 
    
    def queryValue(self, key, name):       
        value, type_id = QueryValueEx(key, name)
        return value