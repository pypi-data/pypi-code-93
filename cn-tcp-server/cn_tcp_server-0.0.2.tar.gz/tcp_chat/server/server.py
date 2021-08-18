# -*- coding: utf-8 -*

import threading
import logging
import logging.handlers
from abc import ABC, abstractmethod
from socket import socket
import time
from typing import MutableSet


class LoopThread(ABC, threading.Thread):
    ''' LoopThread runs on a separate thread and includes an infinite loop that executes `main` and calls `final` upon completion. '''
    active = True
    def run(self):
        try:
            while self.active:
                self.main()
        finally:
            self.final()

    @abstractmethod
    def main(self):
        ''' The function to be called in the loop until the loop is stopped '''
        pass

    @abstractmethod
    def final(self):
        ''' Сalled after the end of the loop '''
        pass

    def stop(self):
        ''' Stops the loop '''
        self.active = False

class Chat:
    pass

class Connection(LoopThread):
    ''' Thread of user connection to server '''
    chat:Chat = None
    def __init__(connection, sock: socket, username:str, chat_id:str):
        super().__init__(daemon=True)
        connection.sock = sock
        connection.username = username
        connection.chat_id = chat_id
    
    def receive(connection) -> str:
        ''' Receives and decodes data '''
        try:
            return connection.sock.recv(1024).decode('utf-8')
        except OSError:
            return ''

    def send(connection, message: str):
        ''' Encode and send message to client '''
        connection.sock.send(message.encode('utf-8'))

class Server:
    ''' Server for multithreading TCP connections '''
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket:socket = socket()
        self.socket.bind((host, port))
        self.connections = {}

        self.logger = logging.getLogger('TCP_server')
        self.logger.setLevel('INFO')
        self.logger.addHandler(logging.handlers.SysLogHandler(address='/dev/log'))

        class Connection_(Connection):
            ''' Фn internal connection class that defines the logic for a specific server '''
            def main(connection):
                data = connection.receive()
                if len(data) > 0:
                    message = f'{connection.username}: {data}'
                    self.logger.info(message)
                    connection.chat.send(connection.username, data)
                else:
                    connection.stop()
                pass

            def final(connection):
                connection.send('/exit')
                connection.sock.close()
                del self.connections[connection.username]
                print(connection.username, 'disconnected')

        self.Connection = Connection_ 
        self.chats:dict[str, Connection_] = {}


    def receive(self, n:int = 1024, encoding:str = 'utf-8') -> str:
        ''' Receives and decrypts data from a socket '''
        return self.socket.recv(n).decode(encoding)

    def auth(self ,sock: socket, addr: str) -> Connection:
        ''' Attempts to authorize a user on this server. Sends one of three possible response codes to the client:
            * 200 - authorization is successful
            * 400 - invalid data
            * 403 - a user with this nickname is already logged in \n  
            Returns a connection object.'''
        data = sock.recv(1024).decode('utf-8')
        try:
            username, chat_id  = data.split('_')
        except ValueError:
            sock.send(b'400')
            sock.close()
            print('Authentificated error with', addr)
            return None
        if username and chat_id and username not in self.connections.keys():
            print("Connected to", addr, 'as', username)
            sock.send(b'200')
            connection = self.Connection(sock = sock, username = username, chat_id = chat_id)
            connection.start()
            self.connections[username] = connection
            print('Num of connections:', len(self.connections))
            return connection

        elif username in self.connections.keys():
            sock.send(b'403')
            sock.close()
            return None
        else:
            sock.send(b'400')
            sock.close()
            print('Authentificated error with', addr)
            return None

    def join_chat(self, chat_id, username):
        ''' Adds a user to the chat with the chat_id identifier. If there is no such chat, then creates it '''
        user = self.connections[username]
        if chat_id in self.chats.keys():
            self.chats[chat_id].join_user(user)
            user.chat = self.chats[chat_id]
        else:
            chat = Chat(chat_id)
            user.chat = chat
            self.chats[chat_id] = chat
            chat.start()
            chat.join_user(user)

    def start(self):
        ''' Starts mainloop of server '''
        print('Start server')
        self.socket.listen(5)
        try:
            while True:
                sock, addr = self.socket.accept()
                conn = self.auth(sock, addr)
                if conn:
                    self.join_chat(conn.chat_id, conn.username)
        except KeyboardInterrupt:
            print(' - you tab CTRL-C')
        finally:
            print('Stop server')
            for connection in self.connections.values():
                connection.stop()
            self.socket.close()


class Chat(LoopThread):
    ''' Class for implementing the logic for sending messages to groups '''
    active = True
    id: str = None
    def __init__(self, id:str):
        super(Chat, self).__init__(daemon=True)
        self.id = id
        self.members:MutableSet[Connection] = set()
        self.lock = threading.Lock()
    
    def join_user(self, conn: Connection):
        ''' Joins user to member set '''
        self.lock.acquire()
        self.members.add(conn)
        self.lock.release()
        print(self.id, '-', self.members)

    def send(self, sender, text):
        ''' Sends message to each member '''
        print(text,1213)
        self.lock.acquire()
        for member in self.members:
            member.send(f'{sender} - {text}')
        self.lock.release()

    def main(self):
        
        # for conn_sender in self.members:
        #     data = conn_sender.receive()
        #     if len(data):
        #         for conn_receiver in self.members:
        #             conn_receiver.send(f'{conn_sender.username}-{data}')
        time.sleep(1)

    def final(self):
        ''' Close all connections of this chat '''
        print('Chat closed')
        for conn in self.members:
            conn.stop()            
