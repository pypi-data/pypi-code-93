import socket



class UsrR16:
    def __init__(self, host: str, port: int = 8899, password: str = 'admin'):
        self.host = host
        self.port = port

        self.sock = socket.socket()
        self.sock.connect((host, port))

        self.auth(password=password)

        if self.sock.recv(1024) != b'OK':
            raise ConnectionError("Password incorrect")

    def auth(self, password: str):
        self.sock.send(password.encode() + b'\x0d' + b'\x0a')

    @staticmethod
    def req_gen(relay: int, command: int):
        """
        Generate byte-command
        0x55 0xaa 0x00 %s 0x00 %s %s %s

        :param relay: Relay number 0-16 (0 - all)
        :param command: 1 - off, 2 - on, 3 - invert
        :return: bytearray
        """
        if relay < 0 or relay > 16:
            raise ValueError(f"Relay value out of range, expected 1-16, got {relay}")

        return bytearray([0x55, 0xAA, 0x00, 3, 0x00, command, relay, 3])

    def send(self):
        pass

    def turn_off(self, relay: int):
        """
        Turn off relay

        :param relay: relay's id
        :return:
        """
        self.sock.send(self.req_gen(relay=relay, command=1))

    def turn_on(self, relay: int):
        """
        Turn on relay

        :param relay: relay's id
        :return:
        """
        self.sock.send(self.req_gen(relay=relay, command=2))

    def invert(self, relay: int):
        """
        Invert relay's status

        :param relay: relay's id
        :return:
        """
        self.sock.send(self.req_gen(relay=relay, command=3))

    def turn_off_all(self):
        """
        Invert relay's status

        :param relay: relay's id
        :return:
        """
        self.sock.send(self.req_gen(relay=0, command=5))

