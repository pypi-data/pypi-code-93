import socket


class AsteriskAMI:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, server_ip: str, server_port: int):
        """Connects with the asterisk AMI"""
        try:
            self.socket.connect((server_ip, server_port))
        except Exception as error:
            raise ConnectionError("Couldn't connect to asterisk. Error:", error)

    def login(self, username: str, password: str):
        """Login with asterisk AMI """
        self.send_command({
            "Action": "Login",
            "Username": username,
            "Secret": password,
            "Events": "OFF"})

        response = self.receive_response()
        if 'Response: Success' not in response:
            raise ConnectionRefusedError(response)
        print(response)

    def receive_response(self):
        response = ""
        while not response.endswith('\r\n\r\n'):
            buf = self.socket.recv(1024)
            if not len(buf) > 0:
                break
            response += buf.decode()
        return response


    def send_command(self, args: dict):
        """Sends the command to asterisk AMI"""
        command = ""
        for key, value in args.items():
            command += key + ": " + value + "\r\n"
        command += "\r\n"
        try:
            self.socket.send(command.encode())
        # except Exception as error:
        #     raise error
        # else:
        #     response = self.receive_response()
        # return response

    def originate(self, channel, exten=None, context=None, caller_id=None, priority="1", timeout="2000", variable=None):
        """* @param string $channel Channel name to call
        * @param string $exten Extension to use (requires 'Context' and 'Priority')
        * @param string $context Context to use (requires 'Exten' and 'Priority')
        * @param string $priority Priority to use (requires 'Exten' and 'Context')
        * @param string $application Application to use
        * @param string $data Data to use (requires 'Application')
        * @param integer $timeout How long to wait for call to be answered (in ms)
        * @param string $callerid Caller ID to be set on the outgoing channel
        * @param string $variable Channel variable to set (VAR1=value1|VAR2=value2)
        * @param string $account Account code
        * @param boolean $async true fast origination
        * @param string $actionid message matching variable
        """
        params = {
            "Action": "Originate",
            "Channel": channel,
            "Context": context,
            "Exten": exten,
            "Priority": priority,
            "Timeout": timeout,
            "CallerID": caller_id,
            "Variable": variable,
        }
        print("Calling apartment {extension}".format(extension=exten))
        self.send_command(params)
        response = self.receive_response()
        return response

    def sip_peer_status(self, extension: str):
        self.send_command(dict(Action="SIPpeerstatus", Peer=extension))
        response = ""
        while True:
            response += self.receive_response()
            if 'Event: SIPpeerstatusComplete' in response:
                break
        print(response)
        return response

    def disconnect(self):
        """Closes the connection to Asterisk AMI"""
        self.socket.close()
