import os
import json
from collections import namedtuple
from market_place_cli.v_cloud_market_cli_common.utils.vsyschain.error import throw_error
from market_place_cli.v_cloud_market_cli_common.utils.service_error import (
    WalletStorageLoadingException,
    WalletStorageSavingException)

WalletData = namedtuple("WalletData", ["seed", "accountSeeds", "nonce", "agent"])

class WalletStorage:

    def __init__(self, path = None):
        self.path = path

    def save(self, wallet_data, cipher=None):
        """
        :param wallet_data: a json dict
        :param cipher: an instance of cipher class for encrypting json data
        :return: None
        """
        try:
            parentPath = os.path.dirname(self.path)
            if not os.path.exists(parentPath):
                os.mkdir(parentPath)
            data = json.dumps(wallet_data._asdict())
            with open(self.path, "w") as wallet:
                if cipher:
                    wallet.write(cipher.encrypt(data))
                else:
                    wallet.write(data)
        except:
            msg = "Failed to save information to wallet file."
            throw_error(msg, WalletStorageSavingException)

    def load(self, cipher=None):
        """
        :param cipher: an instance of cipher class, default: None
        :return: a json dict, walletData, with keys: seed, accountSeeds, nonce, agent
        """
        try:
            with open(self.path, "r") as wallet:
                data = wallet.read()
                # cannot open wallet saved as plain text with cipher
                if cipher and not self.is_json(data):
                    return json.loads(cipher.decrypt(data), object_hook=self._wallet_data_decoder)
                else:
                    return json.loads(data, object_hook=self._wallet_data_decoder)
        except FileNotFoundError as e:
            return None
        except:
            msg = "Failed to load information from wallet file."
            throw_error(msg, WalletStorageLoadingException)

    def _wallet_data_decoder(self, walletDict):
        return namedtuple("WalletData", walletDict.keys())(*walletDict.values())

    def is_json(self,input):
        try:
            json.load(input)
            return True
        except:
            return False
