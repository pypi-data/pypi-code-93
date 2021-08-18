import socket
import threading
from time import sleep

class Client:
    ''' A class that implements the logic of connecting, authorizing, and exchanging messages with the server '''
    host = None
    port = None
    connected = False
    def __init__(self, username, chat_id):
        self.socket = socket.socket()
        self.username = username
        self.chat_id = chat_id

    def connect(self, host, port):
        ''' Sends authorization information to the server and responds to the returned code. Starts listen thread. '''
        self.host = host
        self.port = port
        try:
            self.socket.connect((host,port))
            self.send(f'{self.username}_{self.chat_id}')
            answer = self.receive()
            assert answer == '200'
            self.connected = True
            listen_thread = threading.Thread(target=self.listen, daemon=True)
            listen_thread.start()
        except AssertionError:
            if answer == '403':
                print('The user with such name already connect')
                self.socket.close()
            elif answer == '401':
                print('Authorization error')
                self.socket.close()
        except:
            print('Connection error')
            self.socket.close()
        else:
            print('Connected!')

    def shell(self):
        ''' A shell for reading messages from the console and sending them to the server '''
        try:
            while self.connected:
                sleep(0.2)
                message = input('>> ')
                if not message:
                    print('I can`t send empty message')
                elif message == '/exit':
                    print('Exit!')
                    break
                elif message == '/down':
                    self.socket.shutdown(socket.SHUT_RDWR)
                    break
                else:
                    self.send(message)
        except KeyboardInterrupt:
            print(' - you tab CTRL-C')
        finally:
            print('Closing...')
            self.close()
    
    def listen(self):
        ''' Listens to the socket and outputs messages '''
        try:
            while self.connected:
                data = self.socket.recv(1024)
                if len(data) > 0:
                    message = data.decode("utf-8")
                    if message=='/exit':
                        self.connected = False
                    elif message.startswith(self.username):
                        print(message)
                    else:
                        print('\n',message)
                else:
                    self.connected = False
        finally:
            print('\nStop listening...')
            self.close()
            exit()

    def send(self, message: str):
        ''' Encodes and send message'''
        self.socket.send(message.encode('utf-8'))
    
    def receive(self):
        ''' Receives and returns message '''
        data = self.socket.recv(1024)
        return data.decode('utf-8')
    

    def close(self):
        ''' Close connection and stops listen and shell loops '''
        self.connected = False
        self.socket.close()


