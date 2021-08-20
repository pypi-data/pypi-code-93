import os
import socket
import sys
import http.server
import socketserver
import ipaddress
import struct
import subprocess, platform


def get_ip():
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  try:
    # doesn't even have to be reachable
    s.connect(('8.8.8.8', 1))
    IP = s.getsockname()[0]
    print (s.getsockname())
  except:
    IP = '127.0.0.1'
  finally:
    s.close()
  return IP

    
def ping(host):
  # Ping parameters as function of OS
  DETACHED_PROCESS = 0x00000008
  ping_str = "-n 1" if  platform.system().lower()=="windows" else "-c 1"
  args = "ping " + " " + ping_str + " " + host
  need_sh = False if  platform.system().lower()=="windows" else True
  # Ping
  return subprocess.call(args, shell=need_sh, creationflags=DETACHED_PROCESS) == 0

def detect_network() :
  """
  Test if current network behind FW to then open internet
  replaced by is_on_open_network()
  return 
    
  """
  
  if ping('8.8.8.8'):
    return "OPEN"
  else :
    return "INTERNAL"

def is_on_open_network() :
  """
  Test if current network behind FW to then open internet
    
  """
  
  if test_port('8.8.8.8', 53) == True:
    return True
  else :
    return False



def test_port (host, port):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  result = sock.connect_ex((host,port))
  if result == 0: 
    return True # open
  return False

def http_server(port, web_path) :
  os.chdir(web_path)
  Handler = http.server.SimpleHTTPRequestHandler
  httpd = socketserver.TCPServer(("", port), Handler)
  print("HTTP Server started at port : ", port)
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    httpd.shutdown()
    sys.exit(0)
  sys.exit(0)  

def wake_on_lan(remote_host_mac):
  remote_host_mac = remote_host_mac.replace(":","")
  BROADCAST_IP = '192.168.1.255'
  DEFAULT_PORT = 9
  
  # Pad the synchronization stream
  data = b'FFFFFFFFFFFF' + (remote_host_mac * 16).encode()
  send_data = b''
  
  # Split up the hex values in pack
  for i in range(0, len(data), 2):
    send_data += struct.pack(b'B', int(data[i: i + 2], 16))

  packet = send_data
  print (packet)
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  sock.connect((BROADCAST_IP, DEFAULT_PORT))
  sock.send(packet)
  sock.close()

  
if __name__ == "__main__":
  wake_on_lan("48:5B:39:3E:02:07")
  """
  print(detect_network())
  while True:
    print (is_on_open_network())
  pass  
  """