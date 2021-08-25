'''
This example was from e02_send_hello.py of IOTA Python workshop.
It creates a simple transaction with a custom message/tag
There is no value attached to this transaction.
'''

import json
import logging

from iota import Address, Iota, ProposedTransaction, Tag, TryteString
from iota.adapter import HttpAdapter
from iota.crypto.types import Seed
from iota.crypto.addresses import AddressGenerator


logger = logging.getLogger(__name__)


class NumbersIOTA():
    def __init__(self):
        self.seed = None
        self.address = None
        self.api = Iota(
            HttpAdapter('https://nodes.thetangle.org:443', timeout=20)
        )
        self.base_tangle_add = 'https://utils.iota.org/transaction/{}'

    def generate_seed(self):
        # Note that we don't need a seed to send 0 value transactions since
        # these transactions are not signed, we can publish to any address
        self.seed = Seed.random()

    def generate_address(self, security_level=2):
        # security level is defined during generator init
        if self.seed is None:
            self.generate_seed()

        try:
            generator = AddressGenerator(
                seed=self.seed, security_level=security_level
            )
            self.address = generator.get_addresses(0, 1)[0]  # index, count
            logger.info("New address generated.")
        except Exception as e:
            logger.error("Fail to generate new address")
            print(e)
            raise

    def get_transaction(self, trans_hash):
        """ Allow users to input a trans_hash hash and get one transaction"""

        return self.get_transactions(trans_hash)

    def get_transactions_by_add(self, _addresses):
        """ Allow users to input a address or a list of addresses """

        if isinstance(_addresses, str):
            addresses = [_addresses]
        else:
            addresses = _addresses
        response = self.api.find_transaction_objects(
            addresses=addresses)
        if len(response["transactions"]) == 1:
            return response["transactions"][0]
        else:
            return response["transactions"]

    def get_tranaction_by_tag(self, _tag):
        """ Allow users to input tag or a list of tags """
        if isinstance(_tag, str):
            tag = [_tag]
        else:
            tag = _tag
        response = self.api.find_transaction_objects(tags=tag)
        if len(response["transactions"]) == 1:
            return response["transactions"][0]
        else:
            return response["transactions"]

    def get_transactions(self, _trans_hashes):
        """ Allow users to input a trans_hash or a list of hashes """

        if isinstance(_trans_hashes, str):
            trans_hashes = [_trans_hashes]
        else:
            trans_hashes = _trans_hashes
        response = self.api.get_transaction_objects(trans_hashes)
        if len(response["transactions"]) == 1:
            return response["transactions"][0]
        else:
            return response["transactions"]

    def get_message(self, transaction, conv_to_dict=True):
        """ Retuen decoded message of a transaction """
        _message = transaction.signature_message_fragment.decode(
            errors='ignore')
        if conv_to_dict:
            try:
                return json.loads(_message)
            except Exception:
                self.logger.error('Fail to convert message to dict')
        return _message

    def propose_transaction(
            self,
            tag,
            _message,
            value=0,
            address=None,
            provider='NUMBERSPROTOCOL'):
        """ Send data to IOTA."""

        # If there is no specified address, it will use self.address
        # or generate a new one if self.address is also None
        if address is None:
            address = self.address
            if self.address is None:
                self.generate_address()
        else:
            self.address = address
        try:
            if isinstance(_message, dict):
                _message['provider'] = provider
                message = _message
            else:
                message = {
                    'provider': provider,
                    'content': _message
                }
            message = json.dumps(message)
        except Exception as e:
            logger.error("Fail to convert dict to json.")
            print(e)
            raise
        try:
            tx = ProposedTransaction(
                address=Address(self.address),
                message=TryteString.from_unicode(message),
                value=0,
                tag=Tag(tag),
            )
            response = self.api.send_transfer([tx])
            return self.base_tangle_add.format(response['bundle'][0].hash)

        except Exception as e:
            logger.error("Fail to propose and run transaction")
            print(e)
            raise
