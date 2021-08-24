from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.measure import Measurement
from rich import box
from base58 import b58encode


class WalletServiceDisplay:

    def __init__(self, console: Console):
        self.console = console

    def show_address(self, accInfoList: [dict]) -> None:
        self.console.clear()
        table = Table()
        table.title = 'Wallet Address Information'
        table.add_column('Address', justify='center')
        table.add_column('Account Seed', justify='center')
        table.add_column('Private Key', justify='center')
        table.add_column('Public Key', justify='center')
        table.columns[0].style = 'green'
        table.columns[0].header_style = 'bold green'
        table.columns[1].style = 'magenta'
        table.columns[1].header_style = 'bold magenta'
        table.columns[2].style = 'red'
        table.columns[2].header_style = 'bold red'
        table.columns[3].style = 'bright_yellow'
        table.columns[3].header_style = 'bold bright_yellow'
        table.row_styles = ['none', 'dim']
        rows = self._form_address_rows(accInfoList)
        for row in rows:
            table.add_row(*row)

        balanceTable = Table()
        balanceTable.row_styles = ['none', 'dim']
        balanceTable.title = 'Wallet Address Balance Information'
        balanceTable.add_column('Address', justify='center')
        balanceTable.columns[0].style = 'dark_sea_green4'
        balanceTable.columns[0].header_style = 'bold dark_sea_green4'
        if 'balance' in accInfoList[0]:
            balanceTable.add_column('Balance', '[u]412,000,000 VSYS', justify='right')
            balanceTable.columns[1].style = 'bright_green'
            balanceTable.columns[1].header_style = 'bold bright_green'
        elif 'balanceDetail' in accInfoList[0]:
            balanceTable.add_column('Regular Balance', '[u]412,000,000', justify='right')
            balanceTable.add_column('Minting Average', '[u]412,000,000', justify='right')
            balanceTable.add_column('Available Balance', '[u]412,000,000', justify='right')
            balanceTable.add_column('Effective Balance', '[u]412,000,000', justify='right')
            balanceTable.columns[1].style = 'bright_yellow'
            balanceTable.columns[1].header_style = 'bold bright_yellow'
            balanceTable.columns[2].style = 'bright_red'
            balanceTable.columns[2].header_style = 'bold bright_red'
            balanceTable.columns[3].style = 'bright_green'
            balanceTable.columns[3].header_style = 'bold bright_green'
            balanceTable.columns[4].style = 'cyan'
            balanceTable.columns[4].header_style = 'bold cyan'

        bRows = self._form_balance_rows(accInfoList)
        for row in bRows:
            balanceTable.add_row(*row)

        table.box = box.SIMPLE_HEAD
        balanceTable.box = box.SIMPLE_HEAD
        table_w = Measurement.get(self.console, table).maximum
        balanceTable.width = table_w
        self.console.print(table, justify='left')
        self.console.print(balanceTable, justify='left')
        self.console.input('Press ENTER to continue...')

    def show_wallet(self, wallet_data: dict) -> None:
        self.console.clear()
        if not wallet_data or len(wallet_data) == 0:
            self.console.print('[dark_red]! No Wallet Data File ![/]')
            return
        table = Table()
        table.add_column('Agent', no_wrap=True, justify='center')
        table.add_column('Seed', justify='center')
        table.add_column('Last Nonce #', justify='center')
        row = [wallet_data.agent, wallet_data.seed, str(wallet_data.nonce)]
        table.add_row(*row)
        self.console.print(table, justify='center')

        accSeedTable = Table()
        accSeedTable.add_column('Account Seed', no_wrap=True, justify='left')
        for accSeed in wallet_data.accountSeeds:
            accSeedTable.add_row(accSeed)
        self.console.print(accSeedTable, justify='center')

    def show_account_pay(self, recipient: str, amount: float) -> None:
        self.console.clear()
        self.console.print('[dark_sea_green4]=[/]' * 25)
        self.console.print('[dark_sea_green4]+[/] Successfully Payment! [dark_sea_green4]+[/]')
        self.console.print('[dark_sea_green4]=[/]' * 25)
        self.console.print('Recipient:        : ' + recipient)
        self.console.print('Amount            : ' + str(amount))
        self.console.input('Press ENTER to continue...')

    def show_seed(self, seed: str) -> None:
        self.console.clear()
        msg = '[bright_red]IMPORTANT - COPY OR MEMORIZE THE SEED PHRASE BELOW FOR KEY RECOVERY!!!\n'
        msg += '[bright_green]seed              :' + seed
        p = Panel(msg, box=box.DOUBLE_EDGE, expand=False)
        self.console.print(p)
        self.console.input('Press ENTER to continue...')

    def _form_address_rows(self, accInfoList: [dict]) -> [[str]]:
        rows = []
        for accInfo in accInfoList:
            row = []
            row.append(accInfo['addr'])
            row.append(b58encode(accInfo['accSeed']).decode('utf-8'))
            row.append(b58encode(accInfo['priv']).decode('utf-8'))
            row.append(b58encode(accInfo['pub']).decode('utf-8'))
            rows.append(row)
        return rows

    def _form_balance_rows(self, accInfoList: [dict]) -> [[str]]:
        rows = []
        for accInfo in accInfoList:
            row = []
            row.append(accInfo['addr'])
            rows.append(self._add_balance_info(accInfo, row))
        return rows

    def _add_balance_info(self, accInfo: dict, row: [str]) -> [str]:
        if 'balance' in accInfo:
            row.append(str(accInfo['balance']))
        elif 'balanceDetail' in accInfo:
            d = accInfo['balanceDetail']
            row.append(str(d['regular']))
            row.append(str(d['mintingAverage']))
            row.append(str(d['available']))
            row.append(str(d['effective']))
        return row


