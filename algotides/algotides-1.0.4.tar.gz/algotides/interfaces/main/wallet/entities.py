# Tides
from algosdk.wallet import Wallet as AlgosdkWallet


class Wallet:
    """
    This class represents a wallet inside this program memory. Not to be confused with algosdk.wallet.Wallet.

    It just holds 2 properties:
        1. The dict returned from algosdk call
        2. algosdk.wallet.Wallet for when the wallet is unlocked with its password
    """
    def __init__(self, info: dict):
        self.info = info
        self.algo_wallet = None

    def unlock(self, algo_wallet: AlgosdkWallet):
        self.algo_wallet = algo_wallet

    def lock(self):
        self.algo_wallet = None
