import time
import struct
import json
import logging
from . import mainnet_chain
from .setting import (MAX_NONCE,
    DEFAULT_TX_FEE,
    DEFAULT_FEE_SCALE,
    DEFAULT_LEASE_FEE,
    DEFAULT_CANCEL_LEASE_FEE,
    PAYMENT_TX_TYPE,
    LEASE_TX_TYPE,
    LEASE_CANCEL_TX_TYPE,
    CHECK_FEE_SCALE,
    MAX_ATTACHMENT_SIZE)
from .error import (InvalidAddressException,
    InvalidParameterException,
    InsufficientBalanceException,
    MissingPrivateKeyException,
    NetworkException,
    throw_error)
from .crypto import *
from ..wallet_cipher import WalletCipher

class Account(object):

    def __init__(self, chain=mainnet_chain(), address='', privateKey='', seed='', alias='', nonce=0):
        self.chain = chain
        self.wrapper = chain.apiWrapper
        self.publicKey = ''
        if nonce < 0 or nonce > MAX_NONCE:
            raise InvalidParameterException(f'Nonce must be between 0 and {MAX_NONCE}')

        if seed:
            self._generate(seed=seed, nonce=nonce)
        elif privateKey:
            self._generate(privateKey=privateKey)
        else:
            raise InvalidParameterException('Seed or private key not provided for account')

    def __str__(self):
        if not self.address:
            raise InvalidAddressException('No address')

        result = 'address = %s\npublicKey = %s\nprivateKey = %s\nseed = %s\nnonce = %d' % \
            (self.address, self.publicKey, self.privateKey, self.seed, self.nonce)

        try:
            balance = self.balance()
            result += f'\nbalance: {balance}'
        except NetworkException:
            logging.error('Failed to get balance')
        return result

    __repr__ = __str__

    def _generate(self, seed='', privateKey='', nonce=0):
        self.seed = seed
        self.nonce = nonce
        if seed:
            accInfo = WalletCipher.generate_account_info(seed=seed, net=self.chain.chainId, nonce=nonce)
            self.address = accInfo['addr']
            self.privateKey = bytes2str(base58.b58encode(accInfo['priv']))
            self.publicKey = bytes2str(base58.b58encode(accInfo['pub']))
        elif privateKey:
            privKey = base58.b58decode(privateKey)
            pubKey = curve.generatePublicKey(privKey)
            self.address = self.chain.public_key_to_address(pubKey).decode('utf-8')
            self.privateKey = privateKey
            self.publicKey = bytes2str(base58.b58encode(pubKey))

    def balance(self, confirmations=0):
        try:
            confirmationStr = '' if confirmations == 0 else f'/{confirmations}'
            resp = self.wrapper.request(f'/addresses/balance/{str(self.address)}{confirmationStr}')
            return resp['balance']
        except Exception as ex:
            msg = f'Failed to get balance. ({ex})'
            logging.error(msg)
            return 0

    def balance_detail(self):
        try:
            resp = self.wrapper.request(f'/addresses/balance/details/{str(self.address)}')
            return resp
        except Exception as ex:
            msg = f'Failed to get balance detail. ({ex})'
            logging.error(msg)
            return None

    def send_payment(self, recipient, amount, attachment='', txFee=DEFAULT_TX_FEE, feeScale=DEFAULT_FEE_SCALE, timestamp=0):
        self._check_parameter(recipient=recipient, amount=amount, attachment=attachment, txFee=txFee, feeScale=feeScale)
        if timestamp == 0:
            timestamp = int(time.time() * 1000000000)
        sData = struct.pack(">B", PAYMENT_TX_TYPE) + \
                struct.pack(">Q", timestamp) + \
                struct.pack(">Q", amount) + \
                struct.pack(">Q", txFee) + \
                struct.pack(">H", feeScale) + \
                base58.b58decode(recipient) + \
                struct.pack(">H", len(attachment)) + \
                str2bytes(attachment)
        signature = bytes2str(sign(self.privateKey, sData))
        attachmentStr = bytes2str(base58.b58encode(str2bytes(attachment)))
        data = json.dumps({
            'senderPublicKey': self.publicKey,
            'recipient': recipient,
            'amount': amount,
            'fee': txFee,
            'feeScale': feeScale,
            'timestamp': timestamp,
            'attachment': attachmentStr,
            'signature': signature
        })
        return self.wrapper.request('/vsys/broadcast/payment', data)

    def lease(self, recipient, amount, txFee=DEFAULT_LEASE_FEE, feeScale=DEFAULT_FEE_SCALE, timestamp=0):
        self._check_parameter(recipient=recipient, amount=amount, txFee=txFee, feeScale=feeScale)
        data = self._form_lease_data(recipient=recipient, amount=amount, txFee=txFee, feeScale=feeScale, isLeasing=True)
        return self.wrapper.request('/leasing/broadcast/lease', data)

    def lease_cancel(self, recipient, amount, txFee=DEFAULT_CANCEL_LEASE_FEE, feeScale=DEFAULT_FEE_SCALE, timestamp=0):
        self._check_parameter(recipient=recipient, amount=amount, txFee=txFee, feeScale=feeScale)
        data = self._form_lease_data(recipient=recipient, amount=amount, txFee=txFee, feeScale=feeScale, isLeasing=False)
        return self.wrapper.request('/leasing/broadcast/cancel', data)

    def _form_lease_data(self, recipient, amount, txFee, feeScale, isLeasing):
        txType = None

        timestamp = int(time.time() * 1000000000)

        if isLeasing:
            txType = LEASE_TX_TYPE
        else:
            txType = LEASE_CANCEL_TX_TYPE

        sData = struct.pack(">B", txType) + \
                struct.pack(">Q", amount) + \
                struct.pack(">Q", txFee) + \
                struct.pack(">H", feeScale) + \
                struct.pack(">Q", timestamp)
        signature = bytes2str(sign(self.privateKey, sData))
        data = json.dumps({
            'senderPublicKey': self.publicKey,
            'recipient': recipient,
            'fee': txFee,
            'feeScale': feeScale,
            'timestamp': timestamp,
            'signature': signature
        })
        return data

    def _check_parameter(self, recipient, amount, txFee, feeScale, attachment=''):
        if not self.privateKey:
            msg = 'Private key required'
            throw_error(msg, MissingPrivateKeyException)
        if not self.chain.validate_address(recipient):
            msg = 'Invalid recipient address'
            throw_error(msg, InvalidAddressException)
        elif amount <= 0:
            msg = 'Amount must be > 0'
            throw_error(msg, InvalidParameterException)
        elif txFee < DEFAULT_TX_FEE:
            msg = f'Transaction fee must be >= {DEFAULT_TX_FEE}'
            throw_error(msg, InvalidParameterException)
        elif len(attachment) > MAX_ATTACHMENT_SIZE:
            msg = f'Attachment length must be <= {MAX_ATTACHMENT_SIZE}'
            throw_error(msg, InvalidParameterException)
        elif CHECK_FEE_SCALE and feeScale != DEFAULT_FEE_SCALE:
            msg = f'Wrong fee scale (currently, fee scale must be {DEFAULT_FEE_SCALE})'
            throw_error(msg, InvalidParameterException)
        elif self.balance() < amount + txFee:
            msg = f'Insufficient VSYS balance'
            throw_error(msg, InsufficientBalanceException)
