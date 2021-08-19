from .transports.smtp import SmtpTransport


class TransportManager:
    def create_smtp_driver(self, host: str, port: str,
                           username: str = None, password: str = None,
                           from_address: str = 'test@mail.com', from_name: str = 'Test',
                           encryption: bool = False,
                           **kwargs):
        transport = SmtpTransport(host, int(port))
        if username is not None or password is not None:
            transport.username = username
            transport.password = password
        transport.default_from_addr = from_address or 'test@mail.com'
        transport.default_from_name = from_name or 'Test'
        transport.encryption = encryption
        return transport
