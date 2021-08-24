from rich.console import Console
from rich.panel import Panel

from market_place_cli.v_cloud_market_cli_common.service.wallet_service import WalletService, WalletCipher
from market_place_cli.v_cloud_market_cli_common.service_display.main_interface import MainInterface
from market_place_cli.v_cloud_market_cli_common.service_display.user_service_display import UserServiceDisplay
from market_place_cli.v_cloud_market_cli_common.service_display.market_service_display import MarketServiceDisplay
from market_place_cli.v_cloud_market_cli_common.service.user_service import UserService
from market_place_cli.v_cloud_market_cli_common.service.market_service import MarketService
from market_place_cli.service_interface_request.wallet_service_request import WalletRequest
from market_place_cli.service_interface_request.user_service_request import UserServiceRequest
from market_place_cli.service_interface_request.common_request import get_table_choice
from market_place_cli.service_interface_logic.common import get_net, wallet_has_password
from market_place_cli.v_cloud_market_cli_common.utils.message_decipher import decrypt_message


class UserServiceLogic:

    def __init__(self):
        self.title = 'UserService'
        self.console = None
        self.ur = None  # User Request
        self.ud = None  # User Display
        self.net_type = 'M'
        self.main_functions = ['Show Running User Service', 'Show Usable User Service', 'Show Past User Service', 'Show Abort User Service']

    @property
    def Name(self):
        return self.title

    def StartLogic(self, console: Console, isTestnet: bool):
        self.console = console
        self.net_type = get_net(isTestnet)
        self.ur = UserServiceRequest(self.console)
        self.ud = UserServiceDisplay(self.console)
        console.clear()
        while True:
            choice = MainInterface.display_service_choice(console, self.title, self.main_functions, True)
            if choice == '1':
                self.show_current_user_service_logic()
            elif choice == '2':
                self.show_usable_user_service_logic()
            elif choice == '3':
                self.show_past_user_service_logic()
            elif choice == '4':
                self.show_abort_user_service_logic()
            elif choice.lower() == 'b':
                break

    def show_current_user_service_logic(self):
        self.show_user_service_page('ServiceRunning')

    def show_usable_user_service_logic(self):
        self.show_user_service_page('ServiceUsable')

    def show_past_user_service_logic(self):
        self.show_user_service_page('ServiceDone')

    def show_abort_user_service_logic(self):
        self.show_user_service_page('ServiceAbort')

    def access_provider_api_logic(self, us: UserService, user_service_id: str, user_service_info: dict, index: int):
        # get decryption private key
        wr = WalletRequest(self.console)
        password = ''
        if wallet_has_password(self.net_type):
            password = wr.get_password()
        private_key = WalletService(None, self.net_type, password).fetch_wallet_info(index, "priv")

        # get provider host
        ms = MarketService(self.net_type, password)
        provider_host = ms.get_provider_host(user_service_info['provider'])

        info = us.get_user_service_info(provider_host, user_service_id)
        magic = info["magic"]
        cipher = decrypt_message(private_key, magic)
        p = Panel.fit(cipher)
        p.title = 'Service Login Information'
        p.title_align = 'center'
        self.console.print(p)
        self.console.input('Press ENTER to continue...')

    def access_user_service_api_logic(self, us: UserService, user_service_id: str, password: str, index: int):
        md = MarketServiceDisplay(self.console)
        ms = MarketService(self.net_type, password, index)
        info = us.get_user_service_info(user_service_id)
        service_info = ms.get_service_info(info['serviceID'])

        self.console.print(md.form_service_api(service_info['serviceAPI']))
        is_secret, api_func = self.ur.get_api_func(service_info['serviceAPI'])
        if is_secret:
            msg = us.access_user_api_get(user_service_id, 'secret', api_func)
        else:
            msg = us.access_user_api_get(user_service_id, 'normal', api_func)
        p = Panel.fit(msg)
        p.title = '[]User Service API Service Response'
        p.title_align = 'center'
        self.console.print(p)
        self.console.input('Press ENTER to continue...')

    def show_user_service_page(self, status: str):
        wr = WalletRequest(self.console)
        password = ''
        if wallet_has_password(self.net_type):
            password = wr.get_password()
        index = wr.get_payment_address()
        us = UserService(self.net_type, password, index)

        cur = 1
        page_size = 10
        title, extra = self._construct_page_title(status)
        while True:
            display_result, has_next = self._construct_user_service_page(us, cur, status)
            w = self.ud.show_user_service_page(title, display_result['list'])
            has_next = len(display_result['list']) >= page_size
            choice = get_table_choice(self.console, w, has_next,
                                      extra=extra)
            if choice == 'p' and cur > 1:
                cur -= 1
            elif choice == 'n' and has_next:
                cur += 1
            elif choice == 'd':
                user_service_id = self.ur.get_user_service_id()
                u, ok = self.validate_user_service(display_result, user_service_id)
                if ok:
                    self.ud.show_user_service_detail(u)
            elif status == 'ServiceUsable' and choice == 'u':
                user_service_id = self.ur.get_user_service_id()
                user_service_info_list = [item for item in display_result['list'] if item['id'] == user_service_id]
                if len(user_service_info_list) == 0:
                    continue
                self.access_provider_api_logic(us, user_service_id, user_service_info_list[0], index)
            elif choice == 'a':
                user_service_id = self.ur.get_user_service_id()
                self.access_user_service_api_logic(us, user_service_id, password, index)
            elif choice == 'e':
                break

    def validate_user_service(self, result: dict, user_service_id: str) -> (dict, bool):
        found = False
        for u in result['list']:
            if u['id'] == user_service_id:
                found = True
                return u, found
        if not found:
            self.console.input('[bright_red]User Service ID Not Found.[/] Press ENTER to continue...')
            return None, found

    def _construct_user_service_page(self, us: UserService, cur_page: int, status: str):
        if status == 'ServiceUsable':
            display_result = us.get_user_service_page(
                current=cur_page,
                page_size=10,
                statuses=['ServicePending', 'ServiceRunning'])
        else:
            display_result = us.get_user_service_page(
                current=cur_page,
                page_size=10,
                statuses=status)

        has_next = False if len(display_result['list']) < 10 else True
        return display_result, has_next

    def _construct_page_title(self, status: str):
        extra = {}
        title = 'User Service Information Table'
        if status == 'ServiceRunning':
            title = 'Running ' + title
            extra = {'d': '[D]User Service Detail', 'a': '[A]User Service API Access'}
        elif status == 'ServiceUsable':
            title = 'Usable ' + title
            extra = {'d': '[D]User Service Detail', 'u': '[U]User Service Usage Info'}
        elif status == 'ServiceDone':
            title = 'Past ' + title
        return title, extra

