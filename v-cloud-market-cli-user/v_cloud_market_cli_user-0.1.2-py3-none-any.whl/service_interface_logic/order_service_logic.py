from rich.console import Console
from rich.panel import Panel

from market_place_cli.v_cloud_market_cli_common.service.market_service import MarketService
from market_place_cli.v_cloud_market_cli_common.service.order_service import OrderService
from market_place_cli.v_cloud_market_cli_common.service.wallet_service import WalletService
from market_place_cli.v_cloud_market_cli_common.service_display.main_interface import MainInterface
from market_place_cli.v_cloud_market_cli_common.service_display.order_service_display import OrderServiceDisplay
from market_place_cli.v_cloud_market_cli_common.service_display.wallet_service_display import WalletServiceDisplay
from market_place_cli.service_interface_logic.common import get_net, wallet_has_password
from market_place_cli.service_interface_request.wallet_service_request import WalletRequest
from market_place_cli.service_interface_request.order_service_request import OrderRequest
from market_place_cli.service_interface_request.common_request import get_table_choice
import sys


class OrderServiceLogic:

    def __init__(self):
        self.title = 'OrderService'
        self.console = None
        self.od = None  # order display instance
        self.net_type = 'M'
        self.main_functions = ['Show Pending Order', 'Show Paid Order', 'Show Filed Order',
                               'Show Refunded Order', 'Show Order Detail', 'Pay An Order',
                               'Refund Order']

    @property
    def Name(self):
        return self.title

    def StartLogic(self, console: Console, is_testnet: bool):
        self.console = console
        self.net_type = get_net(is_testnet)
        self.od = OrderServiceDisplay(self.console)
        console.clear()
        while True:
            choice = MainInterface.display_service_choice(console, self.title, self.main_functions, True)
            if choice == '1':
                self.show_pending_order_logic()
            elif choice == '2':
                self.show_paid_order_logic()
            elif choice == '3':
                self.show_filed_order_logic()
            elif choice == '4':
                self.show_refunded_order_logic()
            elif choice == '5':
                self.show_order_detail_logic()
            elif choice == '6':
                self.pay_order_logic()
            elif choice == '7':
                self.show_refundable_order_logic()
            elif choice.lower() == 'b':
                break

    def show_pending_order_logic(self):
        self.show_order_page(status='OrderPending')

    def show_paid_order_logic(self):
        self.show_order_page(status='OrderPaid')

    def show_filed_order_logic(self):
        self.show_order_page(status='OrderFiled')

    def show_refunded_order_logic(self):
        self.show_order_page(status='OrderRefund')

    def show_refundable_order_logic(self):
        self.show_order_page(status='OrderRefundable')

    def show_order_detail_logic(self):
        wr = WalletRequest(self.console)
        orderReq = OrderRequest(self.console)

        password = ''
        if wallet_has_password(self.net_type):
            password = wr.get_password()

        index = wr.get_payment_address()
        orderService = OrderService(self.net_type, password, index)
        oID = orderReq.get_order_id()
        info = orderService.get_order_info(oID)
        self.od.display_order_info(info)

    def show_order_page(self, status: str):
        wr = WalletRequest(self.console)
        password = ''
        if wallet_has_password(self.net_type):
            password = wr.get_password()
        index = wr.get_payment_address()
        o = OrderService(self.net_type, password, index)
        cur = 1
        page_size = 10

        title = self._construct_page_title(status)
        extra = self._construct_page_button(status)

        while True:
            display_result = self._construct_order_page_data(o, cur, status)
            w = self.od.display_order_page(title, display_result)
            has_next = len(display_result['list']) >= page_size or len(display_result['list']) >= page_size
            choice = get_table_choice(self.console, w, has_next, extra=extra)
            if choice == 'p' and cur > 1:
                cur -= 1
            elif choice == 'n' and has_next:
                cur += 1
            elif choice == 'e':
                break
            elif status == 'OrderRefundable' and choice == 'r':
                order_list = display_result['list']
                self.refund_order_detail_logic(index, order_list)

    def pay_order_logic(self):
        order_req = OrderRequest(self.console)
        wr = WalletRequest(self.console)
        order_id = order_req.get_order_id()
        password = ''

        if wallet_has_password(self.net_type):
            password = wr.get_password()
        index = wr.get_payment_address()
        amt = wr.get_amount()
        if amt < 0:
            self.console.print('[bright_red]!!! Invalid Amount !!!')
            self.console.input('Press ENTER to exit...')
            return
        order_service = OrderService(self.net_type, password, index)
        wsd = WalletServiceDisplay(self.console)
        ws = WalletService(wsd, self.net_type, password)
        pubKey = ws.fetch_wallet_info(index, 'pub')

        order_info = order_service.get_order_info(order_id)
        recipient = order_info['recipient']
        amt = self._overpay_protection(order_info, amt)
        ws.account_pay(index, recipient, amt, order_id+';'+pubKey)

        # mock payment code for local testing
        # resp = order_service.mock_order_payment(order_id, recipient, pubKey, amt)
        # self.console.print(Panel.fit(resp["content"]))

    def refund_order_detail_logic(self, index: int, order_list: list):
        wr = WalletRequest(self.console)
        orderReq = OrderRequest(self.console)
        password = ''
        if wallet_has_password(self.net_type):
            password = wr.get_password()

        order_service = OrderService(self.net_type, password, index)
        order_id = orderReq.get_order_id()
        provider = [item for item in order_list if item['id'] == order_id]
        if len(provider) == 0:
            return
        ms = MarketService(self.net_type, password)
        provider_host = ms.get_provider_host(provider[0]['provider'])
        info = order_service.refund_order(provider_host, order_id)
        self.console.input('Press ENTER to exit...')

    def _construct_order_page_data(self, o: OrderService, cur_page: int, order_status: str):
        display_result = {
            'pagination': {}
        }
        if order_status == 'OrderRefundable':
            filed_result = o.get_order_info_page(current=cur_page, status='OrderFiled')
            paid_result = o.get_order_info_page(current=cur_page, status='OrderPaid')
            display_result['list'] = paid_result['list'] + filed_result['list']
            display_result['pagination']['total'] = paid_result['pagination']['total'] + filed_result['pagination']['total']
            display_result['pagination']['current'] = paid_result['pagination']['current']
            display_result['pagination']['pageSize'] = paid_result['pagination']['pageSize']
        else:
            display_result = o.get_order_info_page(current=cur_page, status=order_status)
        return display_result

    def _construct_page_title(self, order_status: str):
        title = 'Order Information Table'
        if order_status == 'OrderPending':
            title = 'Pending ' + title
        elif order_status == 'OrderPaid':
            title = 'Paid ' + title
        elif order_status == 'OrderFiled':
            title = 'Filed ' + title
        elif order_status == 'OrderComplete':
            title = 'Completed ' + title
        elif order_status == 'OrderRefund':
            title = 'Refund ' + title
        return title

    def _construct_page_button(self, order_status: str):
        if order_status == 'OrderRefundable':
            extra = {'r': '[R]Refund'}
        else:
            extra = {}
        return extra

    def _overpay_protection(self, order_info: dict, amt: int):
        check_amt = order_info['amountPaid'] + amt
        remain_amt = order_info['amount'] > order_info['amountPaid']
        if order_info['status'] == 'OrderPending':
            if check_amt > order_info['amount'] and remain_amt > 0:
                self.console.print('[bright_red]The input amount is larger than remaining order amount !!!')
                choice = self.console.input('[bright_green]Continue the payment with remaining amount (default Y)[Y/n]: ')
                if choice.lower() == 'n':
                    return amt
                else:
                    amt = order_info['amount'] - order_info['amountPaid']
                    self.console.print('')
                    self.console.print(f'[bright_green]The payment amount will be: {amt}')
                    self.console.print('')
                    self.console.input('Press ENTER to continue...')
                    return amt
            return amt
        else:
            self.console.print(f'[bright_green]Order is already paid with status - {order_info["status"]}')
            self.console.input('Press ENTER to exit...')
            sys.exit(0)

