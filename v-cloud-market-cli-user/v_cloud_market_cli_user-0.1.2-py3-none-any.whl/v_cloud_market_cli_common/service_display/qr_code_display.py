# rfcs/0007-wallet-interaction-specification-4
from rich.console import Console
import json
import pyqrcode


class QRCodeDisplay:

    def __init__(self):
        pass

    def show_export_seed(self, seed: str):
        payload = {
            'protocol': 'v.systems',
            'api': 1,
            'opc': 'seed',
            'seed': seed
        }
        self._display_qr_code(payload)

    def show_account_of_wallet(self, address: str, public_key: str = '', amt: float = 0, invoice: str = ''):
        '''
        api: if it has invoice, api should be 2. Otherwise, it's 1
        amount: should not be specified when monitoring cold wallet account in hot wallet
        publicKey: is required for monitoring cold wallet but optional for receiving coin
        '''
        payload = {
            'protocol': 'v.systems',
            'opc': 'account',
            'address': address
        }

        if invoice:
            payload['invoice'] = invoice
            payload['api'] = 2
        else:
            payload['api'] = 1

        if amt and amt > 0:
            payload['amount'] = int(amt * 10**8)

        if public_key:
            payload['publicKey'] = public_key
        self._display_qr_code(payload)

    def _display_qr_code(self, payload: dict):
        text = pyqrcode.create(json.dumps(payload), error='L')
        print(text.terminal(quiet_zone=1))