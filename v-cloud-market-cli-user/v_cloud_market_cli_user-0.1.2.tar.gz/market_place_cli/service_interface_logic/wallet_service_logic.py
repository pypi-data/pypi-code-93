from rich.console import Console
from rich.prompt import Prompt

from market_place_cli.v_cloud_market_cli_common.service_display.wallet_service_display import WalletServiceDisplay
from market_place_cli.v_cloud_market_cli_common.service_display.main_interface import MainInterface
from market_place_cli.v_cloud_market_cli_common.service.wallet_service import WalletService
from market_place_cli.v_cloud_market_cli_common.utils.service_error import WalletStorageLoadingException
from market_place_cli.service_interface_request.wallet_service_request import WalletRequest
from market_place_cli.service_interface_logic.common import get_net, wallet_has_password


class WalletServiceLogic(object):

    def __init__(self):
        self.title = 'WalletService'
        self.console = None
        self.netType = 'M'
        self.main_functions = ['Show Address', 'Make Payment to An Address', 'Generate New Address',
                               'Reset Current Wallet', 'Set Wallet Password']

    @property
    def Name(self):
        return self.title

    def StartLogic(self, console: Console, isTestnet: bool):
        self.console = console
        self.netType = get_net(isTestnet)
        console.clear()
        while True:
            choice = MainInterface.display_service_choice(console, self.title, self.main_functions, True)
            if choice == '1':
                self.show_address_logic()
            elif choice == '2':
                self.make_payment_logic()
            elif choice == '3':
                self.generate_new_address_logic()
            elif choice == '4':
                self.reset_wallet_logic()
            elif choice == '5':
                self.set_wallet_password_logic()
            elif choice.lower() == 'b':
                break

    def show_address_logic(self):
        wr = WalletRequest(self.console)
        MainInterface.display_title(self.console, self.title)
        password = wr.get_password()
        wsd = WalletServiceDisplay(self.console)
        ws = WalletService(wsd, self.netType, password)
        ws.show_address(wr.save_to_csv(),
                        wr.display_detail_balance())

    def reset_wallet_logic(self):
        wr = WalletRequest(self.console)
        MainInterface.display_title(self.console, self.title)
        seed = wr.get_seed()
        password = wr.get_password()
        numAddr = wr.get_num_address()
        wsd = WalletServiceDisplay(self.console)
        ws = WalletService(wsd, self.netType, password)
        ws.recover_wallet(seed, numAddr, wr.save_to_csv())

    def generate_new_address_logic(self):
        wr = WalletRequest(self.console)
        numAddr = wr.get_num_address()
        password = wr.get_password()

        wsd = WalletServiceDisplay(self.console)
        ws = WalletService(wsd, self.netType, password)
        ws.address_generate(numAddr, wr.save_to_csv(), wr.get_to_append(), 2)

    def make_payment_logic(self):
        wr = WalletRequest(self.console)
        password = wr.get_password()
        addrIndex = wr.get_payment_address()
        amt = wr.get_amount() * 10**8
        if amt < 0:
            return
        recipient = wr.get_recipient_address()
        attach = wr.get_attachment()

        wsd = WalletServiceDisplay(self.console)
        ws = WalletService(wsd, self.netType, password)
        ws.account_pay(addrIndex, recipient, amt, attach)

    def set_wallet_password_logic(self):
        wr = WalletRequest(self.console)
        wsd = WalletServiceDisplay(self.console)

        if wallet_has_password(self.netType):
            # has password encrypted
            old_wallet = None
            while not old_wallet:
                password = Prompt.ask('[bright_green]Please enter old password: ', password=True)
                try:
                    ws_old = WalletService(wsd, self.netType, password)
                    old_wallet = ws_old.load_wallet_file()
                except WalletStorageLoadingException:
                    self.console.print('[bright_red]Invalid Password !!!')
                    continue
                if not old_wallet:
                    self.console.print('[bright_red]Invalid password for the wallet !')
                else:
                    break
            new_password = Prompt.ask('[bright_green]Please enter new password: ', password=True)
            password_again = Prompt.ask('[bright_green]Please enter new password AGAIN: ', password=True)
            if not new_password == password_again:
                self.console.input('[red]The two new password does not match!')
                return
            ws_old.set_wallet_cipher(new_password)
            ws_old.save_wallet_file(old_wallet)
        else:
            # no encryption
            password = Prompt.ask('[bright_green]Please enter new password: ', password=True)
            ws_new = WalletService(wsd, self.netType, '')
            ws_new.set_wallet_cipher(password)
            old_wallet = ws_new.load_wallet_file()
            ws_new.save_wallet_file(old_wallet)
        self.console.print('[bold green]Successfully Updated !!')

