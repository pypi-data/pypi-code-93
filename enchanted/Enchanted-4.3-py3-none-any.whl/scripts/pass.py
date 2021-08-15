import os,sys,subprocess,requests,random,time
from colorama import *
init(autoreset=True)

os.system("cls")
if sys.argv[1] == "create":
    if sys.argv[3]:
        print(f"{Fore.RED}be aware that the url is public! so make a good url!{Fore.WHITE} ")
        os.system("color")
        time.sleep(2.5)
        print(sys.argv[2])
        payload = sys.argv[2]
        payload2 = sys.argv[3]
        randomxd = random.random
        os.system(f"rentry.py new -p random -u {payload2} {payload}")
        url2 = input("pls enter the url : ")
        os.system(f"rentry.py raw -u {url2}")
if sys.argv[1] == "del":
    loadxd = input("pls enter the url : ")
    os.system(f"rentry.py edit -p random -u {loadxd} be_sure_to_use_enchanted_sniper_!")
