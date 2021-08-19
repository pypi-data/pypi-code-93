"""This module contains the Proxy class.

Although the Proxy class has a simple API, the module as a whole is quite 
confusing.  Here are the logical entities involved:

proxy client - This is the client of the proxy.
proxied host - This is the host being proxied.
proxy - This is the proxy as a whole.

The proxy itself is devided into three parts:

proxy server - This is the server portion of the proxy.  It listens for 
connections from proxy clients.

proxy server backend - this is backend of the proxy server.  it handles a 
connection from a proxy client.

proxied host client - This is the portion of the proxy that connects to the 
proxied host.

Notice that proxy server backend and proxied host client are similar in that 
they each have a single connection.  In fact, I call them peers.

Consider the following usage scenario.  The proxy client wishes to connect to 
the proxied host.  The proxy client connects to the proxy server.  The proxy
server creates a proxy server backend.  The proxy server backend start the 
creation of a proxy host client.  If everything is successful, the proxy client
can send data to the proxy server backend.  The proxy server backend forwards
the data to the proxy host client.  The proxy host client forwards the data
to the proxied host.  The data flow above can be generalized to the following:
A proxy server backend or proxied host client receives data, fowards it to 
its peer, who fowards it to its associated proxied host or proxy client 
respectively.

The API is simple in that the user only has to worry about instantiating the 
Proxy class, catching socket.error exceptions, and calling asyncore.loop.
By the way, due to the way the code flows, the Proxy class is actually just a
pseudonym for the ProxyServer class.

Concerning line endings, the standard is "\r\n", but we need to be prepared to
receive "\n" as well.  Hence, look for "\n", and if there's a "\r" in front of
it, that's fine too.

"""

import asyncore
from asynchat import async_chat
import socket
from io import StringIO


class ProxyServer(asyncore.dispatcher):

    """This is the server portion of the proxy.  
    
    It listens for connections from proxy clients.  It is also the entry point
    into this module.  Thus it goes by the pseudonym Proxy.

    The following private variables are used: 

    _proxiedHost, _proxiedPort - These are host and port that are being 
    proxied.

    _encrypt, _decrypt - These are the encrypt and decrypt functions to use.
    
    """

    def __init__(self, proxiedHost, proxiedPort, listeningPort, encrypt, 
        decrypt):
        """Start listening on listeningPort."""
        LISTEN = 5
        self._proxiedHost = proxiedHost
        self._proxiedPort = proxiedPort
        self._encrypt = encrypt
        self._decrypt = decrypt
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(("", listeningPort))
        self.listen(LISTEN)

    def handle_accept(self):
        """Accept a connection.
        
        Create a _ProxyServerBackend and a _ProxiedHostClient.  Let the
        _ProxiedHostClient instance take over processing since we now need to
        connect to the proxied host.

        """
        (socket, address) = self.accept()
        proxiedHostClient = _ProxiedHostClient(self, self._decrypt)
        proxyServerBackend = _ProxyServerBackend(socket, self._encrypt, 
                proxiedHostClient )
        proxiedHostClient.peer = proxyServerBackend 

Proxy = ProxyServer


class _Peer(async_chat):

    """This is the base class for _ProxyServerBackend and _ProxiedHostClient.

    It provides common behavior concerning data flow.

    The following attributes are provided:

    peer - This is the peer of this _Peer.  Remember that instances of
    _ProxyServerBackend and _ProxiedHostClient are peers of each other.
    
    The following private variables are used: 

    _translator - Apply this to the data before transfering the data to this
    _Peer's peer.

    _buf - This is a StringIO buffer for incoming data.
    
    """

    def __init__(self, socket, translator, peer):
        """Initialize the async_chat class."""
        async_chat.__init__(self, socket)
        self.set_terminator("\n")
        self.shutdown = False
        self.peer = peer
        self._translator = translator
        self._buf = StringIO()

    def collect_incoming_data(self, data):
        """Just buffer the data."""
        self._buf.write(data)

    def found_terminator(self):
        """Forward _translator(_buf) to peer and reset _buf."""
        line = self._translator(self._buf.getvalue() + "\n")
        self.peer.push(line)
        self._buf = StringIO()


class _ProxyServerBackend(_Peer):

    """This is backend of the proxy server.

    It handles a connection from a proxy client.

    It turns out that the baseclass is doing all the work.  However, I'll keep
    this class just in case I end up needing to do something here.  More 
    importantly, it's helpful to maintain the terminology.

    """

    pass


class _ProxiedHostClient(_Peer):

    """This is the portion of the proxy that connects to the proxied host."""

    def __init__(self, proxyServer, translator):
        """Start a connection to the proxied host."""
        _Peer.__init__(self, None, translator, None)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((proxyServer._proxiedHost, proxyServer._proxiedPort))

    def handle_connect(self):
        """Do nothing.  This must be defined."""
        pass
