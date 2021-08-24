from rich.console import Console
from rich.prompt import Prompt


class WalletRequest:

    def __init__(self, console: Console):
        self.console = console

    def get_num_address(self) -> int:
        msg = '[green]Please enter number of address in wallet (1-10): '
        num = self._get_num(msg)
        return num

    def get_payment_address(self) -> int:
        msg = 'Please enter the index of address that you want to use: '
        return self._get_num(msg) - 1

    def get_password(self) -> str:
        msg = '[green]Please enter password for encrypting wallet (Press ENTER for no encryption): '
        return Prompt.ask(msg, password=True)

    def get_seed(self) -> str:
        msg = '[green]Please enter your wallet seed: '
        return self._get_input(msg)

    def save_to_csv(self) -> bool:
        msg = '[green]Save generated addresses to a csv file (default n) [Y/n]: '
        choice = self._get_input(msg)
        return self.get_yes_no(choice)

    def display_detail_balance(self) -> bool:
        msg = '[green]Display detailed balance info (default n) [Y/n]: '
        choice = self._get_input(msg)
        return self.get_yes_no(choice)

    def get_to_append(self) -> bool:
        msg = '[green]Append new generated addresses to wallet (default n) [Y/n]: '
        choice = self._get_input(msg)
        return self.get_yes_no(choice)

    def get_recipient_address(self) -> str:
        msg = '[green]Please enter recipient address: '
        return self._get_input(msg)

    def get_amount(self) -> int:
        msg = '[green]Please enter amount: '
        amt = self._get_input(msg)
        if not amt.isnumeric() or int(amt) < 0:
            self.console.print('[bright_red]Invalid input amount !')
            return -1
        return int(amt)

    def get_attachment(self) -> str:
        msg = '[green]Please enter attachment for this payment[/] [optional]: '
        return self._get_input(msg)

    def get_yes_no(self, choice: str) -> bool:
        if choice.lower() not in ['y', 'n', '']:
            choice = 'n'
        if choice == '':
            choice = 'n'
        return choice.lower() == 'y'

    def _get_num(self, msg) -> int:
        num = 1
        while True:
            try:
                num = int(self.console.input(msg))
                if num < 1 or num > 10:
                    raise ValueError
            except ValueError:
                self.console.print('[bold bright_red]!!! Invalid Input Number !!!')
                continue
            break
        return num

    def _get_input(self, msg: str) -> str:
        return self.console.input(msg)

