import datetime as dt
import typing
from importlib import reload

from sentry_sdk import configure_scope

from shioaji import config
from shioaji.account import Account, FutureAccount, StockAccount
from shioaji.backend import _http
from shioaji.backend.solace import SolaceAPI
from shioaji.backend.solace.utils import mockca, read_config
from shioaji.backend.solace.tick import TickSTKv1, TickFOPv1
from shioaji.backend.solace.bidask import BidAskSTKv1, BidAskFOPv1
from shioaji.constant import Exchange, OrderState, Unit, ScannerType, TicksQueryType
from shioaji.contracts import (
    BaseContract,
    Contract,
    Future,
    Index,
    Option,
    Stock,
)
from shioaji.position import (
    Position,
    ProfitLoss,
    Settlement,
    AccountBalance,
    ProfitLossDetail,
)
from shioaji.data import (
    ShortStockSource,
    Snapshot,
    Ticks,
    Kbars,
    CreditEnquire,
    ChangePercentRank,
)
from shioaji.order import Order, StrictInt, Trade, conint
from shioaji.orderprops import OrderProps
from shioaji.utils import log, set_error_tracking


class Shioaji:
    """shioaji api

    Functions:
        login
        activate_ca
        list_accounts
        set_default_account
        get_account_margin
        get_account_openposition
        get_account_settle_profitloss
        get_stock_account_funds
        get_stock_account_unreal_profitloss
        get_stock_account_real_profitloss
        place_order
        update_order
        update_status
        list_trades

    Objects:
        Quote
        Contracts
        Order
    """

    def __init__(self, backend="http", simulation=False, proxies={}, currency="NTD"):
        """initialize Shioaji to start trading

        Args:
            backend (str): {http, socket}
                use http or socket as backend currently only support http, async socket backend coming soon.
            simulation (bool):
                - False: to trading on real market (just use your Sinopac account to start trading)
                - True: become simulation account(need to contract as to open simulation account)
            proxies (dict): specific the proxies of your https
                ex: {'https': 'your-proxy-url'}
            currency (str): {NTX, USX, NTD, USD, HKD, EUR, JPY, GBP}
                set the default currency for display
        """
        self._http = _http(False, proxies)
        read_config(simulation)
        reload(config)
        self._solace = SolaceAPI(
            config.SJCLIENT_SOL_HOST,
            config.SJCLIENT_SOL_VPN,
            config.SJCLIENT_SOL_USER,
            config.SJCLIENT_SOL_PASSWORD,
            simulation,
            proxies,
            config.SJCLIENT_SOL_CONNECT_TIMEOUT_MS,
            config.SJCLIENT_SOL_RECONNECT_RETRIES,
            config.SJCLIENT_SOL_KEEP_ALIVE_MS,
            config.SJCLIENT_SOL_RECONNECT_RETRY_WAIT,
            config.SJCLIENT_SOL_KEEP_ALIVE_LIMIT,
        )
        if simulation:
            self._solace.activated_ca = mockca()

        self.quote = self._solace
        self._api = self._http
        self.stock_account = None
        self.futopt_account = None
        self.OrderProps = OrderProps
        self.Contracts = getattr(self._http, "Contracts", None)
        self.Order = Order
        self._currency = currency
        self._tft = False
        self.simulation = simulation

    @property
    def tft(self) -> bool:
        return self._tft

    @tft.setter
    def tft(self, tft: bool):
        self._solace.tft = self._tft = tft

    def login(
        self,
        person_id: str,
        passwd: str,
        hashed: bool = False,
        receive_order_callback: bool = True,
        fetch_contract: bool = True,
        contracts_timeout: int = 0,
        contracts_cb: typing.Callable[[], None] = None,
    ) -> None:
        """login to trading server

        Args:
            person_id (str): Same as your eleader, ileader login id(usually your person ID)
            passwd  (str): the password of your eleader login password(not ca password)

        """
        with configure_scope() as scope:
            scope.user = dict(id=person_id)
        self.Contracts = self._solace.Contracts
        accounts = self._solace.login(person_id, passwd, hashed, receive_order_callback)
        if accounts:
            with configure_scope() as scope:
                scope.user = dict(id=person_id, username=accounts[0].username)
        if fetch_contract:
            self._solace.fetch_all_contract(contracts_timeout, contracts_cb)
        self.stock_account = self._solace.default_stock_account
        self.futopt_account = self._solace.default_futopt_account
        if not self.simulation:
            try:
                self._http.login(person_id, passwd)
                if self.futopt_account:
                    self.AccountMargin = self._http.get_account_margin(
                        self._currency, "1", self.futopt_account
                    )
                    self.AccountOpenPosition = self._http.get_account_openposition(
                        "0", "0", self.futopt_account
                    )
                    self.AccountSettleProfitLoss = self._http.get_account_settle_profitloss(
                        "0",
                        "Y",
                        (dt.date.today() + dt.timedelta(days=10)).strftime("%Y%m%d"),
                        dt.date.today().strftime("%Y%m%d"),
                        self._currency,
                        self.futopt_account,
                    )
            except Exception as e:
                log.error(e)
        error_tracking = self._solace.error_tracking(person_id)
        set_error_tracking(self.simulation, error_tracking)
        return accounts

    def logout(self):
        """ logout shioaji api """
        res = self._solace.logout()
        return res

    def activate_ca(self, ca_path: str, ca_passwd: str, person_id: str, store: int = 0):
        """activate your ca for trading

        Args:
            ca_path (str):
                the path of your ca, support both absloutely and relatively path, use same ca with eleader
            ca_passwd (str): password of your ca
            person_id (str): the ca belong which person ID
        """
        res = self._solace.activate_ca(ca_path, ca_passwd, person_id, store)
        return res

    def list_accounts(self):
        """list all account you have"""
        return self._solace.list_accounts()

    def set_default_account(self, account):
        """set default account for trade when place order not specific

        Args:
            account (:obj:Account):
                choice the account from listing account and set as default
        """
        if isinstance(account, StockAccount):
            self._solace.default_stock_account = account
            self.stock_account = account
        elif isinstance(account, FutureAccount):
            self._solace.default_futopt_account = account
            self.futopt_account = account

    def get_account_margin(self, currency="NTD", margin_type="1", account={}):
        """query margin

        Args:
            currency (str):{NTX, USX, NTD, USD, HKD, EUR, JPY, GBP}
                the margin calculate in which currency
                - NTX: 約當台幣
                - USX: 約當美金
                - NTD: 新台幣
                - USD: 美元
                - HKD: 港幣
                - EUR: 歐元
                - JPY: 日幣
                - GBP: 英鎊
            margin_type (str): {'1', '2'}
                query margin type
                - 1 : 即時
                - 2 : 風險
        """
        account = account if account else self.futopt_account
        return self._api.get_account_margin(currency, margin_type, account)

    def get_account_openposition(self, product_type="0", query_type="0", account={}):
        """query open position

        Args:
            product_type (str): {0, 1, 2, 3}
                filter product type of open position
                - 0: all
                - 1: future
                - 2: option
                - 3: usd base
            query_type (str): {0, 1}
                query return with detail or summary
                - 0: detail
                - 1: summary
        """
        account = account if account else self.futopt_account
        return self._api.get_account_openposition(product_type, query_type, account)

    def get_account_settle_profitloss(
        self,
        product_type="0",
        summary="Y",
        start_date="",
        end_date="",
        currency="",
        account={},
    ):
        """query settlement profit loss

        Args:
            product_type (str): {0, 1, 2}
                filter product type of open position
                - 0: all
                - 1: future
                - 2: option
            summary (str): {Y, N}
                query return with detail or summary
                - Y: summary
                - N: detail
            start_date (str): the start date of query range format with %Y%m%d
                ex: 20180101
            end_date (str): the end date of query range format with %Y%m%d
                ex: 20180201
            currency (str): {NTD, USD, HKD, EUR, CAD, BAS}
                the profit loss calculate in which currency
                - NTD: 新台幣
                - USD: 美元
                - HKD: 港幣
                - EUR: 歐元
                - CAD: 加幣
                - BAS: 基幣
        """
        account = account if account else self.futopt_account
        start_date = (
            start_date
            if start_date
            else (dt.date.today() + dt.timedelta(days=10)).strftime("%Y%m%d")
        )
        end_date = end_date if end_date else dt.date.today().strftime("%Y%m%d")
        currency = currency if currency else self._currency
        return self._api.get_account_settle_profitloss(
            product_type, summary, start_date, end_date, currency, account
        )

    def get_stock_account_funds(self, include_tax=" ", account: StockAccount = None):
        """query stock account funds

        Args:
            include_tax (str): {' ', '1'}
                - ' ': tax included
                - '1': tax excluded
        """
        account = account if account else self.stock_account
        return self._api.get_stock_account_funds(include_tax, account)

    def get_stock_account_unreal_profitloss(
        self, stock_type="A", currency="A", filter_rule=" ", account=None
    ):
        """query stock account unreal profitloss

        Args:
            stock_type (str): {A, 0, 1, 2, R}
                - 'A': 全部
                - '0': 現-上市櫃
                - '1': 資
                - '2': 券
                - 'R': 興櫃
            currency (str): {A, NTD, CNY}
                - A: 全部
                - NTD: 新台幣
                - CNY: 人民幣
            filter_rule (str): {' ', 1, 2, 3}
                - ' ': default, no filter
                - '1': filter delisting stock
                - '2': tax excluded
                - '3': filter delisting stock and tax excluded
        """
        account = account if account else self.stock_account
        return self._api.get_stock_account_unreal_profitloss(
            stock_type, currency, filter_rule, account
        )

    def get_stock_account_real_profitloss(
        self,
        stock_type="A",
        start_date="",
        end_date="",
        currency="A",
        filter_rule=" ",
        account=None,
    ):
        """query stock account real profitloss

        Args:
            stock_type (str): {A, 0, 1, 2, R}
                - 'A': 全部
                - '0': 現-上市櫃
                - '1': 資
                - '2': 券
                - 'R': 興櫃
            start_date (str):
                the start date of query range format with %Y%m%d
                ex: 20180201
            end_date (str):
                the end date of query range format with %Y%m%d
                ex: 20180201
            currency (str): {A, NTD, CNY}
                - A: 全部
                - NTD: 新台幣
                - CNY: 人民幣
            filter_rule (str): {' ', 1}
                - ' ': default, no filter
                - '1': filter cost is 0
        """
        account = account if account else self.stock_account
        start_date = (
            start_date
            if start_date
            else (dt.date.today() + dt.timedelta(days=10)).strftime("%Y%m%d")
        )
        end_date = end_date if end_date else dt.date.today().strftime("%Y%m%d")
        return self._api.get_stock_account_real_profitloss(
            stock_type, start_date, end_date, currency, filter_rule, account
        )

    def place_order(
        self,
        contract: Contract,
        order: Order,
        timeout: int = 5000,
        cb: typing.Callable[[Trade], None] = None,
    ) -> Trade:
        """placing order

        Args:
            contract (:obj:Shioaji.Contract):
            order (:obj:Shioaji.Order):
                pass Shioaji.Order object to place order
        """
        if not order.account:
            if isinstance(contract, Future) or isinstance(contract, Option):
                order.account = self.futopt_account
            elif isinstance(contract, Stock):
                order.account = self.stock_account
            else:
                log.error("Please provide the account place to.")
                return None

        trade = self._solace.place_order(contract, order, timeout, cb)
        return trade

    def update_order(
        self,
        trade: Trade,
        price: typing.Union[StrictInt, float] = None,
        qty: int = None,
        timeout: int = 5000,
        cb: typing.Callable[[Trade], None] = None,
    ) -> Trade:
        """update the order price or qty

        Args:
            trade (:obj:Trade):
                pass place_order return Trade object to update order
            price (float): the price you want to replace
            qty (int): the qty you want to subtract
        """
        trade = self._solace.update_order(trade, price, qty, timeout, cb)
        return trade

    def cancel_order(
        self,
        trade: Trade,
        timeout: int = 5000,
        cb: typing.Callable[[Trade], None] = None,
    ) -> Trade:
        """cancel order

        Args:
            trade (:obj:Trade):
                pass place_order return Trade object to cancel order
        """
        trade = self._solace.cancel_order(trade, timeout, cb)
        return trade

    def update_status(
        self,
        account: Account = None,
        timeout: int = 5000,
        cb: typing.Callable[[typing.List[Trade]], None] = None,
    ):
        """update status of all trades you have"""
        if account:
            self._solace.update_status(account, timeout=timeout, cb=cb)
        else:
            if self.stock_account:
                self._solace.update_status(self.stock_account, timeout=timeout, cb=cb)
            if self.futopt_account:
                self._solace.update_status(self.futopt_account, timeout=timeout, cb=cb)

    def list_positions(
        self,
        account: Account = None,
        unit: Unit = Unit.Common,
        timeout: int = 5000,
        cb: typing.Callable[[typing.List[Position]], None] = None,
    ) -> typing.List[Position]:
        """query account of unrealized gain or loss
        Args:
            account (:obj:Account):
                choice the account from listing account (Default: stock account)
        """
        if account:
            position = self._solace.list_positions(
                account, unit=unit, timeout=timeout, cb=cb
            )
        else:
            if self.stock_account:
                position = self._solace.list_positions(
                    self.stock_account, unit=unit, timeout=timeout, cb=cb
                )
        return position

    def list_profit_loss(
        self,
        account: Account = None,
        begin_date: str = "",
        end_date: str = "",
        timeout: int = 5000,
        cb: typing.Callable[[typing.List[ProfitLoss]], None] = None,
    ) -> typing.List[ProfitLoss]:
        """query account of profit loss

        Args:
            account (:obj:Account):
                choice the account from listing account (Default: stock account)
            begin_date (str): the start date of query profit loss (Default: today)
            end_date (str): the end date of query profit loss (Default: today)
        """
        if account:
            return self._solace.list_profit_loss(
                account, begin_date, end_date, timeout=timeout, cb=cb
            )
        else:
            if self.stock_account:
                return self._solace.list_profit_loss(
                    self.stock_account, begin_date, end_date, timeout=timeout, cb=cb,
                )

    def list_profit_loss_detail(
        self,
        account: Account = None,
        detail_id: int = 0,
        timeout: int = 5000,
        cb: typing.Callable[[typing.List[ProfitLossDetail]], None] = None,
    ):
        """query account of profit loss detail

        Args:
            account (:obj:Account):
                choice the account from listing account (Default: stock account)
            detail_id (int): the id is from ProfitLoss object, ProfitLoss is from list_profit_loss
        """
        if account:
            return self._solace.list_profit_loss_detail(
                account, detail_id, timeout=timeout, cb=cb
            )
        else:
            if self.stock_account:
                return self._solace.list_profit_loss_detail(
                    self.stock_account, detail_id, timeout=timeout, cb=cb
                )

    def list_settlements(
        self,
        account: Account = None,
        timeout: int = 5000,
        cb: typing.Callable[[typing.List[Settlement]], None] = None,
    ) -> typing.List[Settlement]:
        """ query stock account of settlements """
        return self._solace.list_settlements(self.stock_account, timeout=timeout, cb=cb)

    def list_trades(self) -> typing.List[Trade]:
        """list all trades"""
        return self._solace.trades

    def ticks(
        self,
        contract: BaseContract,
        date: str = dt.date.today().strftime("%Y-%m-%d"),
        query_type: TicksQueryType = TicksQueryType.AllDay,
        time_start: typing.Union[str, dt.time] = None,
        time_end: typing.Union[str, dt.time] = None,
        last_cnt: int = 0,
        timeout: int = 30000,
        cb: typing.Callable[[Ticks], None] = None,
    ) -> Ticks:
        """get contract tick volumn

        Arg:
            contract (:obj:Shioaji.BaseContract)
            date (str): "2020-02-02"
        """
        ticks = self._solace.ticks(
            contract,
            date,
            query_type,
            time_start,
            time_end,
            last_cnt,
            timeout,
            cb,
        )
        return ticks

    def kbars(
        self,
        contract: BaseContract,
        start: str = (dt.date.today() - dt.timedelta(days=1)).strftime("%Y-%m-%d"),
        end: str = dt.date.today().strftime("%Y-%m-%d"),
        timeout: int = 30000,
        cb: typing.Callable[[Kbars], None] = None,
    ) -> Kbars:
        """get Kbar

        Arg:
            contract (:obj:Shioaji.BaseContract)
            start (str): "2020-02-02"
            end (str): "2020-06-02"
        """
        kbars = self._solace.kbars(contract, start, end, timeout, cb)
        return kbars

    def snapshots(
        self,
        contracts: typing.List[typing.Union[Option, Future, Stock, Index]],
        timeout: int = 30000,
        cb: typing.Callable[[Snapshot], None] = None,
    ) -> typing.List[Snapshot]:
        """get contract snapshot info

        Arg:
            contract (:obj:List of contract)
        """
        snapshots = self._solace.snapshots(contracts, timeout, cb)
        return snapshots

    def scanners(
        self,
        scanner_type: ScannerType,
        ascending: bool = True,
        date: str = None,
        count: conint(ge=1, le=200) = 100,
        timeout: int = 30000,
        cb: typing.Callable[
            [typing.Union[typing.List[ChangePercentRank]]], None
        ] = None,
    ) -> typing.Union[typing.List[ChangePercentRank]]:
        """get contract snapshot info

        Arg:
            contract (:obj:List of contract)
        """
        scanners = self._solace.scanners(
            scanner_type, ascending, date, count, timeout, cb
        )
        return scanners

    def credit_enquires(
        self,
        contracts: typing.List[Stock],
        timeout: int = 30000,
        cb: typing.Callable[[CreditEnquire], None] = None,
    ) -> typing.List[CreditEnquire]:
        """get contract snapshot info

        Arg:
            contract (:obj:List of contract)
        """
        credit_enquires = self._solace.credit_enquires(contracts, timeout, cb)
        return credit_enquires

    def short_stock_sources(
        self,
        contracts: typing.List[Stock],
        timeout: int = 5000,
        cb: typing.Callable[[ShortStockSource], None] = None,
    ) -> typing.List[ShortStockSource]:
        """get contract snapshot info

        Arg:
            contract (:obj:List of contract)
        """
        short_stock_sources = self._solace.short_stock_sources(contracts, timeout, cb)
        return short_stock_sources

    def account_balance(
        self, timeout: int = 5000, cb: typing.Callable[[AccountBalance], None] = None,
    ):
        """get stock account balance"""
        return self._solace.account_balance(self.stock_account, timeout=timeout, cb=cb)

    def set_order_callback(
        self, func: typing.Callable[[OrderState, dict], None]
    ) -> None:
        self._solace.set_order_callback(func)

    def set_session_down_callback(self, func: typing.Callable[[], None]) -> None:
        self.quote.set_session_down_callback(func)

    def set_context(self, context: typing.Any):
        self.quote.set_context(context)

    def on_tick_stk_v1(
        self, bind: bool = False
    ) -> typing.Callable[[Exchange, TickSTKv1], None]:
        def wrap_deco(
            func: typing.Callable[[Exchange, TickSTKv1], None]
        ) -> typing.Callable[[Exchange, TickSTKv1], None]:
            self.quote.set_on_tick_stk_v1_callback(func, bind)
            return func

        return wrap_deco

    def on_tick_fop_v1(
        self, bind: bool = False
    ) -> typing.Callable[[Exchange, TickFOPv1], None]:
        def wrap_deco(
            func: typing.Callable[[Exchange, TickFOPv1], None]
        ) -> typing.Callable[[Exchange, TickFOPv1], None]:
            self.quote.set_on_tick_fop_v1_callback(func, bind)
            return func

        return wrap_deco

    def on_bidask_stk_v1(
        self, bind: bool = False
    ) -> typing.Callable[[Exchange, BidAskSTKv1], None]:
        def wrap_deco(
            func: typing.Callable[[Exchange, BidAskSTKv1], None]
        ) -> typing.Callable[[Exchange, BidAskSTKv1], None]:
            self.quote.set_on_bidask_stk_v1_callback(func, bind)
            return func

        return wrap_deco

    def on_bidask_fop_v1(
        self, bind: bool = False
    ) -> typing.Callable[[Exchange, BidAskFOPv1], None]:
        def wrap_deco(
            func: typing.Callable[[Exchange, BidAskFOPv1], None]
        ) -> typing.Callable[[Exchange, BidAskFOPv1], None]:
            self.quote.set_on_bidask_fop_v1_callback(func, bind)
            return func

        return wrap_deco

    def on_quote(
        self, func: typing.Callable[[str, dict], None]
    ) -> typing.Callable[[str, dict], None]:
        self.quote.set_quote_callback(func)
        return func

    def on_event(
        self, func: typing.Callable[[int, int, str, str], None]
    ) -> typing.Callable[[int, int, str, str], None]:
        self.quote.set_event_callback(func)
        return func

    def on_session_down(
        self, func: typing.Callable[[], None]
    ) -> typing.Callable[[], None]:
        self.quote.set_session_down_callback(func)
        return func

    def __del__(self):
        self._solace.__del__()
