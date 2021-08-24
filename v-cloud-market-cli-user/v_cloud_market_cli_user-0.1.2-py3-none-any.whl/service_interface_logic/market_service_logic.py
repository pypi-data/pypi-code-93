import math
from rich.console import Console

from market_place_cli.v_cloud_market_cli_common.service.wallet_service import WalletService
from market_place_cli.v_cloud_market_cli_common.service_display.market_service_display import MarketServiceDisplay
from market_place_cli.v_cloud_market_cli_common.service_display.qr_code_display import QRCodeDisplay
from market_place_cli.v_cloud_market_cli_common.service_display.main_interface import MainInterface
from market_place_cli.v_cloud_market_cli_common.service.market_service import MarketService
from market_place_cli.service_interface_request.wallet_service_request import WalletRequest
from market_place_cli.service_interface_request.market_service_request import MarketServiceRequest
from market_place_cli.service_interface_request.common_request import get_table_choice
from market_place_cli.service_interface_logic.common import get_net, wallet_has_password
from market_place_cli.v_cloud_market_cli_common.service_display.wallet_service_display import WalletServiceDisplay


class MarketServiceLogic(object):

    def __init__(self):
        self.title = 'MarketService'
        self.console = None
        self.mr = None
        self.md = None
        self.net_type = 'M'
        self.nonce = 2
        self.password = ''
        self.main_functions = ['Get Service Provider Information', 'Make An Order']

    @property
    def Name(self):
        return self.title

    def StartLogic(self, console: Console, isTestnet: bool):
        console.clear()
        self.console = console
        self.net_type = get_net(isTestnet)
        self.mr = MarketServiceRequest(self.console)
        self.md = MarketServiceDisplay(self.console)
        if wallet_has_password(self.net_type):
            wr = WalletRequest(self.console)
            self.password = wr.get_password()
        while True:
            choice = MainInterface.display_service_choice(console, self.title, self.main_functions, True)
            if choice == '1':
                # request provider
                self.provider_logic()
            elif choice == '2':
                self.make_order_logic()
            elif choice.lower() == 'b':
                break

    def provider_logic(self):
        ms = MarketService(self.net_type, self.password)

        cur = 1
        page_size = 10
        while True:
            result = ms.get_provider_info_page(current=cur,opt={}, page_size=page_size)
            w = self.md.display_provider_page(result)
            has_next = len(result['list']) >= page_size
            choice = get_table_choice(self.console, w, has_next, {'c': '[C]ategory Search In Provider'})
            if choice == 'p' and cur > 1:
                cur -= 1
            elif choice == 'n' and has_next:
                cur += 1
            elif choice == 'c':
                provider = self.mr.get_provider_name()
                self.category_logic(provider)
            elif choice == 'e':
                break

    def category_logic(self, provider: str):
        ms = MarketService(self.net_type, self.password)

        cur = 1
        page_size = 10
        while True:
            result = ms.get_category_info_page({'provider':provider}, cur, page_size)
            w = self.md.display_category_page(result)
            has_next = len(result['list']) >= page_size
            choice = get_table_choice(self.console, w, has_next, {'t': '[T]Service Type Search In Category'})
            if choice == 'p' and cur > 1:
                cur -= 1
            elif choice == 'n' and has_next:
                cur += 1
            elif choice == 't':
                category = self.mr.get_category_name()
                self.service_type_logic(provider, category)
            elif choice == 'e':
                break

    def service_type_logic(self, provider: str, category: str):
        ms = MarketService(self.net_type, self.password)

        cur = 1
        page_size = 10
        opt = {
            'provider': provider,
            'category': category
        }
        while True:
            result = ms.get_service_info_page(opt, cur, page_size)
            w = self.md.display_service_page(result)
            has_next = len(result['list']) >= page_size
            choice = get_table_choice(self.console, w, has_next)
            if choice == 'p' and cur > 1:
                cur -= 1
            elif choice == 'n' and has_next:
                cur += 1
            elif choice == 'e':
                break

    def make_order_logic(self):
        wr = WalletRequest(self.console)
        index = wr.get_payment_address()

        wsd = WalletServiceDisplay(self.console)
        ws = WalletService(wsd, self.net_type, self.password)
        pub_key = ws.fetch_wallet_info(index, 'pub')

        ms = MarketService(self.net_type, self.password, index)
        mr = MarketServiceRequest(self.console)
        qr_display = QRCodeDisplay()

        service_id = self.mr.get_service_id()
        service_info = ms.get_service_info(service_id)
        opts = self.mr.user_choose_options(service_info['serviceOptions'])
        price_set = ms.find_price_set(service_info['durationToPrice'], opts)
        time_period = self.mr.user_choose_duration(price_set)
        amt = self.calculate_amount(price_set, time_period['time'])

        if not ms.enough_balance(amt):
            self.console.print(f'[bright_red]Your balance in address index {self.nonce + 1} is not enough.')
            self.console.input('[bright_red]Order Creation Aborted...')
            return
        expired_date = time_period['expiredDate'] if 'expiredDate' in time_period else ''
        order_brief = ms.make_order(
            service_id,
            amt,
            opts,
            time_period['time'],
            expired_date)
        display_qr = mr.get_display_qr_code()
        self.md.display_order_brief(order_brief)

        if display_qr:
            qr_display.show_account_of_wallet(
                address=order_brief['recipient'],
                amt=order_brief['amount'],
                invoice=order_brief['id']+'-'+pub_key)
            self.console.input('Press ENTER to continue...')

    def calculate_amount(self, price_set: dict, duration: int) -> int:
        time_units = []
        index = 0
        for k in price_set['duration']:
            time_units.append(int(k))
        time_units.sort(reverse=True)
        total_len = len(time_units)

        while index < total_len - 1 and duration < time_units[index]:
            index += 1
        amt = price_set['price'] * price_set['duration'][str(time_units[index])] * duration
        return math.ceil(amt)
