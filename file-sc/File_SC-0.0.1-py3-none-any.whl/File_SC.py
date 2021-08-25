import socket



class Server:
    def __init__(self, IP, PORT, SIZE, FORMAT):
        self.IP = IP
        self.PORT = PORT
        self.SIZE = SIZE
        self.FORMAT = FORMAT
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.IP, self.PORT))
        self.server.listen()
        
    def connect_client(self):
        self.conn, addr = self.server.accept()
        

    def recv(self):
        msg = self.conn.recv(self.SIZE).decode(self.FORMAT)
        print(msg)

    def send(self, MESSAGE):
        self.conn.send(MESSAGE.encode(self.FORMAT))

    def recv_file(self, FILEPATH):        
        msg = self.conn.recv(self.SIZE).decode(self.FORMAT)
        msg = msg.split("@")
        PATH = msg[1]
        content = msg[0]
        PATH = PATH.split("\\")
        PATH = PATH[-1]
        PATH = f'{FILEPATH}\\{PATH}'
        with open(PATH, 'w') as f:
            f.write(content)
            f.close

    def send_file(self, PATH):
        with open(PATH, 'r') as f:
            content = f.read()
            content = f'{content}@{PATH}'
            self.conn.send(content.encode(self.FORMAT))




class Client:
    def __init__(self, IP, PORT, SIZE, FORMAT):
        self.IP = IP
        self.PORT = PORT
        self.SIZE = SIZE
        self.FORMAT = FORMAT  
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def connect_server(self):
        self.client.connect((self.IP, self.PORT))

    def recv(self):
        msg = self.client.recv(self.SIZE).decode(self.FORMAT)
        print(msg)

    def send(self, MESSAGE):
        self.client.send(MESSAGE.encode(self.FORMAT))
    
    def send_file(self, PATH):
        with open(PATH, 'r') as f:
            content = f.read()
            content = f'{content}@{PATH}'
            self.client.send(content.encode(self.FORMAT))

    def recv_file(self, FILEPATH):
        msg = self.client.recv(self.SIZE).decode(self.FORMAT)
        msg = msg.split("@")
        PATH = msg[1]
        content = msg[0]
        PATH = PATH.split("\\")
        PATH = PATH[-1]
        PATH = f'{FILEPATH}\\{PATH}'
        with open(PATH, 'w') as f:
            f.write(content)
            f.close
