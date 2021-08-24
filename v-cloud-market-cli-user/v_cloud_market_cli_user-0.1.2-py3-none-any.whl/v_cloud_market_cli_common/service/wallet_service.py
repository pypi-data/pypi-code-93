from base58 import b58encode
from market_place_cli.v_cloud_market_cli_common.service_display.wallet_service_display import WalletServiceDisplay
from market_place_cli.v_cloud_market_cli_common.utils.wallet_storage import WalletStorage, WalletData
from market_place_cli.v_cloud_market_cli_common.utils.vsyschain.account import *
from market_place_cli.v_cloud_market_cli_common.utils.vsyschain import testnet_chain
from market_place_cli.v_cloud_market_cli_common.config.wallet_config import (
    WALLET_FILENAME,
    AGENT_STRING,
    ADDRESS_CSV_FILENAME)

NO_DISPLAY = 0
DISPLAY_BALANCE = 1
DISPLAY_BALANCE_DETAIL = 2


class WalletService:

    def __init__(self, wsd: WalletServiceDisplay, net: str, password: str, walletFile=None):
        self.display = wsd
        self.accounts = []
        self.net = net
        self.password = password
        self.cipher = None if not password else WalletCipher(password)
        if walletFile:
            self.walletFile = walletFile
        else:
            self.walletFile = WALLET_FILENAME
        self.wallet_data = self.load_wallet_file()

    def load_wallet_file(self):
        wallet_storage = WalletStorage(self.walletFile)
        try:
            wallet_data = wallet_storage.load(self.cipher)
            if not wallet_data or len(wallet_data) == 0:
                return None
        except Exception as e:
            return None
        self._load_accounts(seed=wallet_data.seed, nonce=wallet_data.nonce)
        return wallet_data

    def save_wallet_file(self, walletData):
        wallet_storage = WalletStorage('./' + WALLET_FILENAME)
        wallet_storage.save(walletData, self.cipher)

    def set_wallet_cipher(self, new_password: str):
        self.cipher = None if not new_password else WalletCipher(new_password)

    def decrypt_wallet_file(self):
        data = self.load_wallet_file()
        if data:
            self.save_wallet_file(data)

    def show_address(self, toCSV, balanceFlag):
        if not self.wallet_data:
            self.display.console.print('[orange]No seed information or wallet data file.')
            return
        seed = self.wallet_data.seed
        accInfoList = []
        for i in range(0, len(self.wallet_data.accountSeeds)):
            accInfo = WalletCipher.generate_account_info(seed, self.net, i)
            if balanceFlag == DISPLAY_BALANCE:
                accInfo['balance'] = self._load_account(seed, i).balance()
            elif balanceFlag == DISPLAY_BALANCE_DETAIL:
                accInfo['balanceDetail'] = self._load_account(seed, i).balance_detail()
            accInfoList.append(accInfo)
            if toCSV:
                accInfo['seed'] = self.wallet_data.seed
                self._save_to_csv(accInfo)
        self.display.show_address(accInfoList)

    def fetch_wallet_info(self, index: int, field: str):
        if not self.wallet_data:
            self.display.console.print('[orange]No seed information or wallet data file.')
            return
        account = self.accounts[index]

        pub = base58.b58decode(str2bytes(account.publicKey))
        # priv = base58.b58decode(str2bytes(account.privateKey))
        address = WalletCipher.generate_address(pub, self.net).decode('utf-8')
        if field == 'priv':
            return account.privateKey
        elif field == 'pub':
            return account.publicKey
        elif field == 'add':
            return address

    def recover_wallet(self, seed, count, toCSV, balanceFlag=DISPLAY_BALANCE_DETAIL):
        accSeeds = set()
        accInfoList = []
        for i in range(0, count):
            accInfo = WalletCipher.generate_account_info(seed, self.net, i)
            accInfo['seed'] = seed
            if balanceFlag == DISPLAY_BALANCE:
                accInfo['balance'] = self._load_account(seed, i).balance()
            elif balanceFlag == DISPLAY_BALANCE_DETAIL:
                accInfo['balanceDetail'] = self._load_account(seed, i).balance_detail()
            accInfoList.append(accInfo)
            accSeedDisplay = b58encode(accInfo['accSeed']).decode('utf-8')
            accSeeds.add(accSeedDisplay)
            if toCSV:
                self._save_to_csv(accInfo)
        data = WalletData(seed, list(accSeeds), count, AGENT_STRING)
        self.save_wallet_file(data)
        self.display.show_address(accInfoList)

    def seed_generate(self, toCSV, balanceFlag, count=1):
        seed = WalletCipher.generate_phrase()
        self._protect_local_wallet()
        self.display.show_seed(seed)
        self.recover_wallet(seed=seed, count=count, toCSV=toCSV, balanceFlag=balanceFlag)

    def address_generate(self, count, toCSV, toAppend, balanceFlag):
        if not self.wallet_data:
            self.seed_generate(count, toCSV)
            self.load_wallet_file()

        n = self.wallet_data.nonce - 1
        seed = self.wallet_data.seed
        oldAccSeeds = self.wallet_data.accountSeeds
        newAcc = set()
        accInfoList = []
        for i in range(n, n + count):
            accInfo = WalletCipher.generate_account_info(seed, self.net, i)
            accInfo['seed'] = seed
            accSeedDisplay = b58encode(accInfo['accSeed']).decode('utf-8')
            newAcc.add(accSeedDisplay)
            accInfoList.append(accInfo)
            if balanceFlag == DISPLAY_BALANCE:
                accInfo['balance'] = self._load_account(seed, i).balance()
            elif balanceFlag == DISPLAY_BALANCE_DETAIL:
                accInfo['balanceDetail'] = self._load_account(seed, i).balance_detail()
            if toCSV:
                self._save_to_csv(accInfo)
        if toAppend:
            oldAccSeeds += list(newAcc)
            data = WalletData(seed, oldAccSeeds, count + n, AGENT_STRING)
            self.save_wallet_file(data)
        self.display.show_address(accInfoList)

    def account_pay(self, accountNonce, recipient, amount, attachment=''):
        account = self.accounts[accountNonce]
        resp = account.send_payment(recipient, amount * 10**8, attachment=attachment)
        self.display.show_account_pay(recipient, resp['amount'] / 10 ** 8)

    def _protect_local_wallet(self):
        if os.path.exists(WALLET_FILENAME):
            input('> press ENTER to continue.')

    def _save_to_csv(self, jsonData):
        with open(ADDRESS_CSV_FILENAME, 'w+') as file:
            file.write(str(jsonData['nonce']) + ',' +
                       jsonData['addr'] + ',' +
                       b58encode(jsonData['pub']).decode('utf-8') + ',' +
                       b58encode(jsonData['priv']).decode('utf-8') + ',' +
                       b58encode(jsonData['accSeed']).decode('utf-8') + ',' +
                       jsonData['seed']
                       )

    def _load_accounts(self, seed, nonce):
        for i in range(0, nonce):
            self.accounts.append(self._load_account(seed, i))

    def _load_account(self, seed, nonce):
        if self.net == 'M':
            return Account(chain=mainnet_chain(), seed=seed, nonce=nonce)
        else:
            return Account(chain=testnet_chain(), seed=seed, nonce=nonce)
