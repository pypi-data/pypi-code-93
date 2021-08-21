
# MacSpoof 
# Copyright (C) 2020-2021 M.Anish <aneesh25861@gmail.com>

''' 
This is a simple Project to Randomize MAC Address of a Linux PC using Network Manager.
'''

import argparse
import os
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--status",action="store_true",help="Display status of MacSpoof tool.")
    parser.add_argument("--on",action="store_true",help="Start Spoofing MAC ADDRESS .")
    parser.add_argument("--off",action="store_true",help="Stop Spoofing MAC ADDRESS .")
    args = parser.parse_args()

    def spoofcheck():
        output=subprocess.run(['ip','a'], capture_output = True)
        if 'permaddr' in output.stdout.decode().split():
            print('MAC SPOOFING is currently enabled.')

    def status():
        if os.path.exists("/etc/NetworkManager/conf.d/spoof.conf") is False:
            print('MacSpoof is Not Active.')
    
        else:
            spoofcheck()

    def on():
        try:
            with open('spoof.conf','w') as f:
                for i in '[device-mac-randomization] wifi.scan-rand-mac-address=yes [connection-mac-randomization] ethernet.cloned-mac-address=random wifi.cloned-mac-address=random'.split() :
                    f.write(i+"\n")
            z=subprocess.run(['sudo','mv','spoof.conf','/etc/NetworkManager/conf.d/'])
            z=subprocess.run(['sudo','systemctl','restart','NetworkManager'])
            if z.returncode != 0:
                print("MAC SPOOFING failed :(")
                sys.exit(1)

        except Exception as e:
            print("MAC SPOOFING failed :( ")
            sys.exit(1)

        spoofcheck()

    def off():
        if os.path.exists('/etc/NetworkManager/conf.d/spoof.conf'):
            z=subprocess.run(['sudo','rm','/etc/NetworkManager/conf.d/spoof.conf'])
            z=subprocess.run(['sudo','systemctl','restart','NetworkManager'])
            if z.returncode != 0:
                print("Task Failed...")
                sys.exit(1)
        print('status: MacSpoof off.')    

    if args.status is True:
        status()

    elif args.on is True:
        on()

    elif args.off is True:
        off()

    else:
        print("""  
 MacSpoof : A simple tool to Randomize MAC Address of a Linux PC .
 Copyright (C) 2020-2021 M.Anish <aneesh25861@gmail.com>
 
 visit: https://github.com/anish-m-code/macspoof for more details.
""")