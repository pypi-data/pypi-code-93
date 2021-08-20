from firstimpression.scala import variables
from socketIO_client import SocketIO, LoggingNamespace

svars = variables()

class SocketClient:

    def __init__(self, name):
        self.name = name
        self.base_name = f'FI_{name}_'
        self.server = 'https://192.168.99.240'
        self.port = 443
        self.socket = SocketIO(self.server, self.port, LoggingNamespace, verify=False, wait_for_connection=False)
    
    def change_triggers(self, *args):
        for key in svars:
            if self.base_name in key:
                svars[key] = False
        
        if not args[0] == f'{self.base_name}01' and self.base_name in args[0]:
            svars[args[0]] = True

    def check_triggers(self):
        self.socket.on(self.name, self.change_triggers)

    def check_prices(self):
        self.socket.on('general', show_prices)
    
    def wait(self):
        self.socket.wait()

    @staticmethod
    def show_prices(*args):
        if args[0] == 'showprices':
            svars['showprices'] = True
    
        if args[0] == 'resetprices':
            svars['showprices'] = False



