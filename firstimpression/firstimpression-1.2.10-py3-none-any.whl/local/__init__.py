from firstimpression.scala import variables
from firstimpression.constants import TEMP_FOLDER
from socketIO_client import SocketIO, LoggingNamespace
import socket
import os

svars = variables()

class SocketClient:

    def __init__(self, name, port=443):
        self.name = name
        self.base_name = f'FI_{name}_'
        self.server = 'https://192.168.99.240'
        self.port = port
        self.socket = SocketIO(self.server, self.port, LoggingNamespace, verify=False, wait_for_connection=False)
    
    def change_triggers(self, *args):
        for key in svars:
            if self.base_name in key:
                svars[key] = False

        if not args[0] == f'{self.base_name}01' and self.base_name in args[0]:
            svars[f'Channel.{args[0]}'] = True

    def check_triggers(self):
        self.socket.on(self.name, self.change_triggers)

    def check_prices(self):
        self.socket.on('general', SocketClient.show_prices)
    
    def wait(self):
        self.socket.wait()

    @staticmethod
    def show_prices(*args):
        if args[0] == 'showprices':
            svars['Channel.showprices'] = True
    
        if args[0] == 'resetprices':
            svars['Channel.showprices'] = False

class Socket:

    def __init__(self, name, port, triggers=True, alarm=False, prices=False):
        self.triggers = triggers
        self.alarm = alarm
        self.prices = prices
        self.name = name
        self.base_name = f'FI_{name}_'
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.buffer_size = 1024

        self.socket.bind((self.ip, self.port))

    def get_data(self):
        return self.socket.recvfrom(self.buffer_size)
    
    def check_data(self):
        data, addr = self.get_data()
        if self.triggers:
            self.check_triggers(data)
        if self.alarm:
            self.check_alarm(data)
        if self.prices:
            Socket.check_prices(data)

    def check_triggers(self, data):
        if self.base_name in data:
            for key in svars:
                if self.base_name in key:
                    svars[key] = False
            
            if not data == f'{self.base_name}01':
                svars[f'Channel.{data}'] = True
    
    def check_alarm(self, data):
        if data == 'alarm_on':
            svars[f'Channel.{self.base_name}off'] = True
        elif data == 'alarm_off':
            svars[f'Channel.{self.base_name}off'] = False
    
    @staticmethod
    def check_prices(data):
        if data == 'showprices':
            svars['Channel.showprices'] = True
    
        if data == 'resetprices':
            svars['Channel.showprices'] = False
            
            










