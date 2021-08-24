import os
import time
from rich.console import Console

from market_place_cli.service_interface_request.wallet_service_request import WalletRequest
from market_place_cli.v_cloud_market_cli_common.config.wallet_config import WALLET_FILENAME
from market_place_cli.v_cloud_market_cli_common.service.wallet_service import WalletService
from market_place_cli.v_cloud_market_cli_common.service_display.main_interface import MainInterface
from market_place_cli.v_cloud_market_cli_common.service_display.wallet_service_display import WalletServiceDisplay


class InitializationLogic(object):

    def __init__(self):
        # TODO use wallet storage
        self.title = 'Wallet Initialize'
        self.console = None
        self.isTestnet = False
        self.main_functions = ['Recover Wallet From Seed', 'Generate New Wallet']

    @property
    def Name(self):
        return self.title

    def StartLogic(self, console: Console, isTestnet: bool):
        # This should be executed once if no wallet file detected
        self.console = console
        self.isTestnet = isTestnet
        console.clear()
        if os.path.isfile(WALLET_FILENAME):
            return
        MainInterface.display_title(console, self.title)
        console.print('[red]System does not detect wallet in your local environment.[/]')
        time.sleep(2)
        while True:
            choice = MainInterface.display_service_choice(console, self.title, self.main_functions)
            if choice not in ['1', '2']:
                console.print('[red] !!! Invalid Choice !!!')
                time.sleep(2)
                continue
            break
        if choice == '1':
            self._recover_from_seed()
        elif choice == '2':
            self._generate_new_wallet()

    def _recover_from_seed(self):
        wr = WalletRequest(self.console)
        numAddr = wr.get_num_address()
        net = 'T' if self.isTestnet else 'M'
        password = wr.get_password()
        wsd = WalletServiceDisplay(self.console)
        ws = WalletService(wsd, net, password)
        seed = wr.get_seed()
        ws.recover_wallet(seed, numAddr, wr.save_to_csv())

    def _generate_new_wallet(self):
        wr = WalletRequest(self.console)
        numAddr = wr.get_num_address()
        net = 'T' if self.isTestnet else 'M'
        password = wr.get_password()
        wsd = WalletServiceDisplay(self.console)
        ws = WalletService(wsd, net, password)
        ws.seed_generate(wr.save_to_csv(),
                         wr.display_detail_balance(),
                         numAddr)
