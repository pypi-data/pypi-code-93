import socket

class Server:
    def __init__(self, IP, PORT, SIZE, FORMAT,MESSAGE):
        self.IP = IP
        self.PORT = PORT
        self.SIZE = SIZE
        self.FORMAT = FORMAT
        self.MESSAGE = MESSAGE
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.IP, self.PORT))
        self.server.listen()
        
    def connect_client(self):
        self.conn, addr = self.server.accept()

    def recv(self):
        msg = self.conn.recv(self.SIZE).decode(self.FORMAT)
        print(msg)

    def send(self):
        self.conn.send(self.MESSAGE.encode(self.FORMAT))


class Client:
    def __init__(self, IP, PORT, SIZE, FORMAT, MESSAGE):
        self.IP = IP
        self.PORT = PORT
        self.SIZE = SIZE
        self.FORMAT = FORMAT
        self.MESSAGE = MESSAGE  
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def connect_server(self):
        self.client.connect((self.IP, self.PORT))

    def recv(self):
        msg = self.client.recv(self.SIZE).decode(self.FORMAT)
        print(msg)

    def send(self):
        self.client.send(self.MESSAGE.encode(self.FORMAT))
