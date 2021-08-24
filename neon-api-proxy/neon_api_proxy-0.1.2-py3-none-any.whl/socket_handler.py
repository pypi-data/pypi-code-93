import socketserver
import json
import base64

from neon_utils import LOG
from neon_utils.socket_utils import *
from neon_api_proxy.controller import NeonAPIProxyController


class NeonAPITCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        received_message = get_packet_data(self.request)
        received_message_decoded = b64_to_dict(received_message)
        LOG.debug(f"Received request from '{self.client_address[0]}' : {received_message_decoded}")
        response = self.server.controller.resolve_query(received_message_decoded)
        LOG.debug(f'Received response from controller: {response}')
        encoded_response = dict_to_b64(response)
        LOG.debug(f'Encoded response from controller: {encoded_response}')
        self.request.sendall(encoded_response)
