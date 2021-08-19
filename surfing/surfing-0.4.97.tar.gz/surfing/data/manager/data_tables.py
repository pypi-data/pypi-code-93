
import pandas as pd
import dataclasses
import datetime
from typing import Tuple


@dataclasses.dataclass
class StockInfoDataTables:

    values: pd.DataFrame = None             # 天度ratios
    finance: pd.DataFrame = None            # 财报ratios
    dividend: pd.DataFrame = None           # 分红
    equity: pd.DataFrame = None             # 股本
    prices: pd.DataFrame = None             # 价格
    real_dates: pd.DataFrame = None         # 财报发布日期

    balance: pd.DataFrame = None

    income: pd.DataFrame = None
    income_q: pd.DataFrame = None
    income_ttm: pd.DataFrame = None

    cash_flow: pd.DataFrame = None
    cash_flow_q: pd.DataFrame = None
    cash_flow_ttm: pd.DataFrame = None

    factor_dict: dict = None

    def __post_init__(self):
        self.factor_dict = {}


@dataclasses.dataclass
class StocksDataTables:
    stocks: dict = None                          # {'stock_id': StockInfoDataTables()}
    daily_collection: pd.DataFrame = None           # 最新截面数据

    def __post_init__(self):
        self.stocks = {}


@dataclasses.dataclass
class FundDataTables:
    # raw
    cs_index_component: pd.DataFrame = None
    # basic
    trading_days: pd.DataFrame = None
    index_info: pd.DataFrame = None
    index_price: pd.DataFrame = None
    _index_pct_df: pd.DataFrame = None
    index_pct: pd.DataFrame = None
    fund_info: pd.DataFrame = None
    fund_benchmark_info: pd.DataFrame = None
    active_fund_info: pd.DataFrame = None
    fund_nav: pd.DataFrame = None
    fund_unit_nav: pd.DataFrame = None
    fund_size: pd.DataFrame = None
    fund_com_hold: pd.DataFrame = None
    fund_manager_score: pd.DataFrame = None
    fund_manager_info: pd.DataFrame = None
    fund_manager_rank: pd.DataFrame = None
    fund_status_latest: pd.DataFrame = None
    fund_ipo_stats: pd.DataFrame = None
    fund_conv_stats: pd.DataFrame = None  # dump_one_df
    # hedge_fund_nav: pd.DataFrame = None
    # derived
    fund_indicator: pd.DataFrame = None
    fund_indicator_annual: pd.DataFrame = None
    _barra_cne5_factor_return: pd.DataFrame = None
    mng_indicator_score: pd.DataFrame = None
    fund_indicator_score: pd.DataFrame = None
    # fund helps
    fund_conv_list: set = None
    fund_list: set = None
    all_fund_list: set = None
    index_list: set = None
    fund_index_map: dict = None  # fund_id -> index_id
    index_date_list: list = None
    fund_end_date_dict: dict = None
    mng_index_list: dict = None
    mng_best_fund: dict = None
    # score helps
    index_fund_indicator_pack: pd.DataFrame = None  # pivot_table
    stock_ipo_data: dict = None
    conv_bond_ipo_data: dict = None
    stock_ipo_data_detail: dict = None
    conv_bond_ipo_data_detail: dict = None
    stock_ipo_info: dict = None
    conv_bond_ipo_info: dict = None

    def __post_init__(self):
        self.fund_list = self.fund_list or set([])
        self.fund_index_map = self.fund_index_map or {}
        self.stock_ipo_data = {}
        self.conv_bond_ipo_data = {}
        self.stock_ipo_data_detail = {}
        self.conv_bond_ipo_data_detail = {}
        self.stock_ipo_info = {}
        self.conv_bond_ipo_info = {}

    def __repr__(self):
        s = '<DTS'
        for k, v in self.__dict__.items():
            s += f' {k}:{v.shape if isinstance(v, pd.DataFrame) else (len(v) if isinstance(v, set) or isinstance(v, list) else None)}'
        s += '>'
        return s

    def _agg_indicator(self):
        self.fund_indicator = self.fund_indicator.rename(columns={'var':'var_'})
        self.index_fund_indicator_pack = self.fund_indicator.pivot_table(index=['index_id', 'datetime', 'fund_id'])
        self.index_list = set(self.index_fund_indicator_pack.index.levels[0]).union(['active'])

    def remove_fields(self, field_names: Tuple[str] = ()):
        '''将object中不使用的字段置为None'''

        for one in field_names:
            try:
                self.__dict__[one] = None
            except KeyError:
                print(f'[WARNING] try to remove field {one} that is not existed')
                continue

    def fix_data(self):
        # 将 fix_data_v1 去掉的原因是目前 basic 改用choice数据源，nav数据没有这个问题了。
        # self.fix_data_v1()
        self._agg_indicator()

    def fix_data_v1(self):
        '''
        这个改动主要原因是米筐数据源在nav的处理中有问题，导致一些被选中的基金受到影响，所以采用这个fix
        '''
        # ----- after load data_table, we need to do some process
        def change_nav_element(fund_id, d, rate):
            if fund_id in self.fund_nav.columns:
                self.fund_nav.loc[d:,fund_id] = self.fund_nav.loc[d:,fund_id] * rate

        #人工改数据
        fund_id = '003520!0'
        d = datetime.date(2019,3,24)
        rate = 1.0883/1.0013/1.0879*1.089826
        change_nav_element(fund_id, d, rate)

        # 泰达宏利沪深300指数增强A
        # rate number:  1.4287351257399752
        fund_id = '162213!0'
        d = datetime.date(2018,3,16)
        rate = 1.9315/1.4915/1.943*2.143646
        change_nav_element(fund_id, d, rate)

        # 万家1-3年政策性金融债C
        # rate number:  1.0931219248656086
        fund_id = '003521!0'
        d = datetime.date(2019,3,25)
        rate = 1.0916/1.0006/1.0912*1.093377
        change_nav_element(fund_id, d, rate) 