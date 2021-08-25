import hashlib
import json
import logging

from .core import NumbersIOTA


logger = logging.getLogger(__name__)


class NumbersVerify():
    def __init__(self, logger):
        self.niota = NumbersIOTA()

    def verify(
            self, trans_hash, verify_json, keys=['timestamp'],
            verify_hash=True, verify_provider=True, verify_sig=True):
        """
        Thie verify module will get the transaction message from IOTA and
        compare the following
            1. if the provider is NUMBERSPROTOCOL
            2. if the hash of the JSON data matches
            3. if the data specified by keys matches
            4. if the signature is valid

        Please SORT verify_json before sending it to the verify module.
        """

        transaction = self.niota.get_transaction(trans_hash)
        if isinstance(transaction, list) and len(transaction) == 0:
            logger.error('No transaction found')
            raise
        message = self.niota.get_message(transaction)

        if verify_provider:
            try:
                provider = message['provider']
            except KeyError:
                logger.warning('No provider found')
                return False
            if provider != 'NUMBERSPROTOCOL':
                logger.error('provider verification fails.')
                return False

        if verify_hash:
            try:
                registered_hash = message['data_hash']
            except KeyError:
                logger.warning('No data_hash found')
                return False
            logger.info('Registered hash = %s' % registered_hash)

            encoded_data = json.dumps(
                verify_json, sort_keys=True).encode('utf-8')
            verify_hash = hashlib.sha256(encoded_data).hexdigest()
            logger.info('Verify hash = %s' % verify_hash)

            if verify_hash != registered_hash:
                logger.error('data_hash verification fails.')
                return False

        if verify_sig:
            # TODO
            pass

        for verify_key in keys:
            try:
                ledger_data = message[verify_key]
            except KeyError:
                logger.warning(
                    'No %s found in ledger message' % verify_key)
                return False
            try:
                verify_data = verify_json[verify_key]
            except KeyError:
                logger.warning(
                    'No %s found in input JSON data' % verify_key)
                return False
            if ledger_data != verify_data:
                logger.error('%s verification fails.' % verify_key)
                return False
        logger.info('Numbers NIota Verification passed!')
        return True
