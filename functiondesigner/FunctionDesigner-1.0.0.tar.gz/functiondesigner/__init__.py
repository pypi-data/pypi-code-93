import sys
sys.path.append('{0}\\Lib\\site-packages\\functiondesigner'.format(sys.executable.strip('python.exe')))
import setting

def cleanCache():
    cache = open(setting.InstallationDirectory,'w')
    cache.write('')
    cache.close()

