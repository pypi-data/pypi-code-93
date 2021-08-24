import base58
import logging
from .crypto import hashChain, bytes2str, str2bytes
from .setting import ADDRESS_LENGTH, ADDRESS_CHECKSUM_LENGTH

class Chain(object):

    def __init__(self, chainName, chainId, addressVersion, apiWrapper):
        self.chainName = chainName
        self.chainId = chainId
        self.addressVersion = addressVersion
        self.apiWrapper = apiWrapper

    def get_connected_peers(self):
        response = self.apiWrapper.request('/peers/connected')
        if not response.get('peers'):
            return []
        else:
            return [peer['address'] for peer in response.get('peers')]

    def tx(self, id):
        return self.apiWrapper.request(f'/transactions/info/{id}')

    def unconfirmed_tx(self, id):
        return self.apiWrapper.request(f'/transactions/unconfirmed/info/{id}')

    def validate_address(self, address):
        addr = bytes2str(base58.b58decode(address.encode('utf-8'))) #bytes2str(base58.b58decode(address))
        if addr[0] != chr(self.addressVersion):
            logging.error("Wrong address version")
        elif addr[1] != self.chainId:
            logging.error("Wrong chain id")
        elif len(addr) != ADDRESS_LENGTH:
            logging.error("Wrong address length")
        elif addr[-ADDRESS_CHECKSUM_LENGTH:] != hashChain(str2bytes(addr[:-ADDRESS_CHECKSUM_LENGTH]))[:ADDRESS_CHECKSUM_LENGTH]:
            logging.error("Wrong address checksum")
        else:
            return True
        return False

    def public_key_to_address(self, publicKey):
        unhashedAddress = chr(self.addressVersion) + \
            str(self.chainId) + hashChain(publicKey)[0:20]
        addressHash = hashChain(str2bytes(unhashedAddress))[0:4]
        address = bytes2str(base58.b58encode(
            str2bytes(unhashedAddress + addressHash)))
        return address
