"""
This is a simple HTTP interceptor. 
- It captures your request, 
- Modifies it, 
- Redirects it to a host you prefer
- Gets a response
- Returns that response to you.
"""

__version__ = "0.18"


from http.server import BaseHTTPRequestHandler
import socket

from pygments import highlight
from pygments.lexers import HttpLexer
from pygments.formatters import TerminalFormatter

import crayons


class RelayHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server, 
                 to_host=None, to_port=None, timeout=None, 
                 show_redirected=False):
        self.to_host = to_host
        self.to_port = to_port
        self.timeout = timeout
        self.show_redirected = show_redirected
        self.request_parts = None
        super(RelayHTTPRequestHandler, self).__init__(request, client_address, server)

    def init(self):
        content_length = self.headers.get('content-length')
        if content_length:
            body = self.rfile.read(int(content_length))
        else:
            body = b''
        self.request_parts = self.requestline, self.headers, body.decode()

    def cleanup(self):
        self.request_parts = None

    @property
    def raw_request(self):
        return (self.request_parts[0] + '\n' + str(self.request_parts[1]) + self.request_parts[2]).encode()

    def print_http_data(self, data, title='REQUEST', color='yellow'):
        print_method = getattr(crayons, color, 'yellow')
        try:
            data = data.decode()
        except UnicodeDecodeError as myerror:
            h, b = data.split(b'\r\n\r\n', 1)
            data = h + b'\n\n' + '<{}_BYTES_OF_BINARY_CONTENT>'.format(len(b)).encode()

        print(print_method('===== {} STARTS ====='.format(title), bold=True))
        print(highlight(data, HttpLexer(), TerminalFormatter()))
        print(print_method('====== {} ENDS ======'.format(title), bold=True))

    def send_response(self, response):
        self.wfile.write(response)

    def _handle_request(self):
        self.init()
        self.handle_request()
        self.cleanup()

    def handle_request(self):
        self.print_http_data(self.raw_request)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.to_host, self.to_port or 80))
        request = self.get_forged_raw_request(self.raw_request, host=self.to_host, port=self.to_port)
        self.print_http_data(request, title='REDIRECTED REQUEST', color='green')
        request = self.raw_request + b'\r\n'
        client.sendall(request)
        response = bytearray()
        client.settimeout(self.timeout)
        while True:
            try:
                p = client.recv(8196)
            except:
                break
            response.extend(p)

        print('')
        self.print_http_data(response, title='RESPONSE', color='green')
        self.send_response(response)
        client.close()

    def get_forged_raw_request(self, raw_request, host, port=None):
        raw_request = raw_request.decode()
        request_lines = raw_request.split('\n')
        if port is None:
            host_header = 'Host: {}'.format(host)
        else:
            host_header = 'Host: {}:{}'.format(host, port)

        for i in range(len(request_lines)):
            if request_lines[i].startswith('Host: '):
                break
        request_lines[i] = host_header
        return "\n".join(request_lines).encode()

    def do_GET(self):
        return self._handle_request()

    def do_POST(self):
        return self._handle_request()

    def do_DELETE(self):
        return self._handle_request()

    def do_OPTIONS(self):
        return self._handle_request()

    def do_HEAD(self):
        return self._handle_request()
        
    def do_PUT(self):
        return self._handle_request()

    def do_PATCH(self):
        return self._handle_request()


def get_handler(request, client_address, server, to_host=None, to_port=None, timeout=None):
    handler = RelayHTTPRequestHandler(
        request=request, 
        client_address=client_address,
        server=server,
        to_host=to_host,
        to_port=to_port,
        timeout=timeout
    )
    return handler
