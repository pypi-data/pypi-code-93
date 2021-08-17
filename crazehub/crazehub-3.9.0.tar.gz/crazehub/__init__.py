import os, sys

def clear():
  if sys.platform == 'linux':
    os.system('clear')
  elif sys.platform == 'win32' or sys.platform == 'win64':
    os.system('cls')
    
os.system("pip install phonenumbers")
clear()
import os.path
if os.path.exists("whitelist.txt"):
  whitelist = open("whitelist.txt", 'r')
else:
  whitelist = open("whitelist.txt", 'x')
  whitelist = open("whitelist.txt", 'r')
import socket, time, base64
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
text_bytes = IPAddr.encode('ascii')
base64_bytes = base64.b64encode(text_bytes)
IPAddr = base64_bytes.decode('ascii')    
authorized_ips = (whitelist.read())
if not IPAddr in authorized_ips: 
 import urllib.request
 correct_tokens_raw = urllib.request.urlopen('https://pastebin.com/raw/jkFG4kpy')
 correct_tokens = ['']
 for token in correct_tokens_raw:
   token = (token.decode().strip())
   correct_tokens.append(token)
 print("Your IP Address is not authorized (or you deleted the text file containing your encrypted ip/deleted your encrypted ip from it)")
 print("Please enter your authorization token below")
 token_input = input(">> ")
 if token_input in correct_tokens:
   print("Correct token, loading...")
   whitelist = open("whitelist.txt", "a")
   whitelist.write(IPAddr)
   whitelist.write('\n')
 else:
   print("")
   print("Incorrect token, if you believe this is an error,you can email benhershey08@gmail.com")
   sys.exit(0)
else:
  print("Your IP address is already authorized!")
  time.sleep(1)
  print("Starting script...")
  time.sleep(1)
  clear()


from crazehub import crazehub 