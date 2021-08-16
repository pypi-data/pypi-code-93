
import json
import os
import traceback
from typing import Dict, List, Optional

import pandas as pd
import numpy as np

from .....constant import SourceType
from .....fund.engine.trader import BasicFundTrader
from .....fund.engine.backtest import BasicFundBacktestEngine
from ....fund.basic.basic_data_helper import BasicDataHelper
from ....manager.manager_fund import FundDataManager
from ....view.derived_models import ThirdPartyPortfolioInfo, ThirdPartyPortfolioTrade, ThirdPartyPortfolioIndicator, ThirdPartyPortfolioPositionLatest
from ..derived_data_helper import DerivedDataHelper
from .common import ThirdPortfolioBase


class ManuallyCrawledPortfolioProcessor(ThirdPortfolioBase):

    _BLOCK_LIST = [
    ]

    _SRC_TO_NAME = {
        'bcm': '交通银行',
        'ccb': '建设银行',
        'cgb': '广发银行',
        'citics': '中信证券',
        'citicb': '中信银行',
        'cmbc': '民生银行',
        'gtjas': '国泰君安',
        'guosens': '国信证券',
        'icbc': '工商银行',
        'pinganb': '平安银行',
        'spdb': '浦发银行',
    }

    def __init__(self, data_helper: DerivedDataHelper):
        super().__init__()

        self._data_helper = DerivedDataHelper()
        self._bdh = BasicDataHelper()
        self._params_json: Dict[str, str] = {}
        self._dir_path: str = f'{os.path.dirname(os.path.abspath(__file__))}/data/manually_crawled'
        self._trades_df_list: List[pd.DataFrame] = []
        self._nav: Dict[str, pd.DataFrame] = {}
        self._last_position: List[pd.Series] = []

    def init(self):
        # self._fdm = FundDataManager(s3_retriever_activation=True)
        # self._fdm.init(score_pre_calc=True, print_time=True)

        from .....resource.data_store import DataStore
        self._fdm: FundDataManager = DataStore.load_dm()
        self._trading_day: pd.DataFrame = FundDataManager.basic_data('get_trading_day_list').drop(columns='_update_time')

    def _calc_one(self, po_src: str, po_path: str):
        from ....view.cas.third_party_portfolio_nav import ThirdPartyPortfolioNav

        def transform_fund_id(x: pd.Series) -> Optional[str]:
            fund_id = self._bdh._get_fund_id_from_order_book_id(x.fund_id, x.trading_day)
            if fund_id is None:
                print(f'[WARNING] can not fund id {x.fund_id} (po_id){po_id} (po_name){po_name} (trading_day){x.trading_day}')
            return fund_id

        def calc_fund_weight_list(x) -> pd.Series:
            weights_sum = 0
            fund_weights = []
            for row in x.itertuples(index=False):
                fund_weights.append([row.fund_id, row.fund_weight])
                weights_sum += row.fund_weight
            weights_sum = round(weights_sum, 8)
            if weights_sum != 1:
                print(f'sum of percent not equals 1 (po_id){po_id} (po_name){po_name} (trade_date){x.trading_day.array[0]} (weights_sum){weights_sum}')
            return pd.Series({'fund_weight_list': fund_weights})

        def calc_fund_trade_list(x) -> pd.Series:
            fund_trades = []
            for row in x.itertuples(index=False):
                fund_trades.append({'fund_id': row.fund_id, 'from_percent': row.before_w, 'to_percent': row.after_w})
            return pd.Series({'po_id': po_id, 'details': json.dumps(fund_trades)})

        # 几个list，把当前目录下每个组合的几部分数据分别存储起来
        basic_info: List[pd.Series] = []
        trades_df_list: List[pd.DataFrame] = []
        last_positions: List[pd.Series] = []
        indicators: List[pd.Series] = []
        number = 1
        with os.scandir(po_path) as it:
            for entry in it:
                if not entry.is_file() or not entry.name.endswith('.csv'):
                    continue
                # 取文件名并且只取'_'前边的
                po_name = entry.name.split('.')[0].split('_')[0]
                # 转成大写后加一个6位数字，来生成一个组合ID
                po_id = po_src.upper() + str(number).zfill(6)
                number += 1
                # 这里如果找不到对应的枚举类型则需要去添加一下
                real_po_src = SourceType[po_src]
                # 根据英语简称找到中文的主理人名称
                manager_name = self._SRC_TO_NAME[po_src]

                # 读取调仓文件
                df = pd.read_csv(entry.path, dtype={'trading_day': 'str', 'fund_id': 'str'})
                # 调仓文件中最小的日期即为成立日期
                start_date = pd.to_datetime(df.trading_day.min(), infer_datetime_format=True).date()
                # 组合起来基础信息
                basic_info.append(pd.Series({'po_name': po_name, 'po_id': po_id, 'po_src': real_po_src, 'manager_name': manager_name, 'start_date': start_date.isoformat()}))

                df['trading_day'] = pd.to_datetime(df.trading_day, infer_datetime_format=True).dt.date
                # 转换成我们自己的fund_id
                df['fund_id'] = df.apply(transform_fund_id, axis=1)
                # 以trading day为单位来生成fund weight list
                fund_weight_list = df.groupby(by='trading_day', sort=False).apply(calc_fund_weight_list)
                # 我们是第二天调仓，因此这里调整为之前的第一个交易日
                fund_weight_list = [[self._trading_day[self._trading_day.datetime < row.Index].datetime.array[-1], row.fund_weight_list] for row in fund_weight_list.itertuples()]
                # 按日期升序排序
                fund_weight_list.sort(key=lambda x: x[0])
                # 我们是第二天调仓，因此这里调整为之前的第一个交易日
                start_date = self._trading_day[self._trading_day.datetime < start_date].datetime.array[-1]
                t = BasicFundTrader()
                b = BasicFundBacktestEngine(data_manager=self._fdm, trader=t, fund_weight_list=fund_weight_list)
                b.init()
                b.run(start_date=start_date, end_date=None, print_time=False)

                fund_trade = b.get_fund_trade()
                if not fund_trade.empty:
                    # 以trade day为单位来获取实际调仓记录
                    trades_df_list.append(fund_trade.groupby(by='trade_date', sort=False).apply(calc_fund_trade_list).reset_index().rename(columns={'trade_date': 'datetime'}))
                else:
                    print(f'[WARNING] got a empty fund trade (po_id){po_id} (po_name){po_name} (po_src){po_src}')

                # 获取最新持仓
                last_position: pd.DataFrame = b.get_last_position()
                if last_position is not None:
                    last_positions.append(pd.Series({'po_id': po_id, 'datetime': last_position.index.name, 'po_src': real_po_src, 'position': last_position.loc[:, 'weight'].to_json()}))
                else:
                    print(f'[WARNING] got a empty last positions (po_id){po_id} (po_name){po_name} (po_src){po_src}')

                result = b.get_fund_result()
                if result is None:
                    continue
                # 只保留我们需要的回测结果
                result = {k: v for k, v in result.items() if k in ('market_value', 'last_unit_nav', 'mdd', 'annual_ret', 'mdd_d1', 'mdd_d2', 'total_commission', 'rebalance_times')}
                result['datetime'] = result['market_value'].index.array[-1]
                result['from_setup_ret'] = result['last_unit_nav'] - 1
                resampled = result['market_value'].copy()
                resampled.index = pd.to_datetime(resampled.index)
                resampled_w = resampled.mv.resample('1W').apply(lambda x: x[-1] if not x.empty else np.nan)
                result['vol_by_week'] = resampled_w.dropna().pct_change().std(ddof=1) * np.sqrt(52)

                resampled_m = resampled.mv.resample('1M').apply(lambda x: x[-1] if not x.empty else np.nan)
                result['vol_by_month'] = resampled_m.dropna().pct_change().std(ddof=1) * np.sqrt(12)
                result['vol_by_day'] = resampled.mv.dropna().pct_change().std(ddof=1) * np.sqrt(244)
                result['annual_compounded_ret'] = np.power(result['last_unit_nav'], 1 / (result['market_value'].shape[0] / 244)) - 1
                if result['vol_by_week'] != 0:
                    result['sharpe_ratio'] = (result['annual_compounded_ret'] - 0.02) / result['vol_by_week']
                else:
                    result['sharpe_ratio'] = np.nan

                # 遍历每个需要计算的时间区间
                for name, value in self._DIM_TYPE.items():
                    bd = (result['datetime'] - value).date()
                    # 试图寻找bd及其之前的最近一天
                    filtered_mv = result['market_value'].loc[result['market_value'].index <= bd, :]
                    if filtered_mv.empty:
                        continue
                    # 计算区间内的return
                    result[name] = result['market_value'].mv.array[-1] / filtered_mv.mv.array[-1] - 1

                result['nav'] = result['last_unit_nav']
                result['po_id'] = po_id
                self._nav[po_id] = result['market_value'].mv / result['market_value'].mv.array[0]
                self._nav[po_id].index = self._nav[po_id].index.map(lambda x: x.isoformat())
                # 删掉我们不需要的回测结果
                for one in ('market_value', 'last_unit_nav'):
                    del result[one]
                indicators.append(pd.Series(result))

        print(pd.DataFrame(basic_info))
        self._data_helper._upload_derived(pd.DataFrame(basic_info), ThirdPartyPortfolioInfo.__table__.name)
        if trades_df_list:
            trades = pd.concat(trades_df_list)
            trades['po_src'] = real_po_src
            print(trades)
            self._data_helper._upload_derived(trades, ThirdPartyPortfolioTrade.__table__.name)
        else:
            print(f'empty trades of {po_src}')

        indicators = pd.DataFrame(indicators)
        indicators['po_src'] = real_po_src
        print(indicators)
        self._data_helper._upload_derived(indicators, ThirdPartyPortfolioIndicator.__table__.name)

        print(pd.DataFrame(last_positions))
        self._data_helper._upload_derived(pd.DataFrame(last_positions), ThirdPartyPortfolioPositionLatest.__table__.name)

        # nav存cas
        # from cassandra.cqlengine.query import BatchQuery
        # with BatchQuery() as batch:
        #     for po_id, mv in self._nav.items():
        #         ThirdPartyPortfolioNav.objects(po_id=po_id).batch(batch).update(
        #             date__append=mv.index.to_list(),
        #             nav__append=mv.to_list(),
        #         )
        for po_id, mv in self._nav.items():
            ThirdPartyPortfolioNav.create(
                po_id=po_id,
                date=mv.index.to_list(),
                nav=mv.to_list(),
            )

    def calc(self):
        # 遍历每个手工爬取的目录
        with os.scandir(self._dir_path) as it:
            for entry in it:
                if entry.is_dir():
                    # 计算每个目录下的组合
                    print(f'calc {entry.name}')
                    self._calc_one(entry.name, entry.path)
                    print(f'{entry.name} done')

    def process(self, end_date: str) -> List[str]:
        failed_tasks: List[str] = []
        try:
            po_src_list = []
            for one in SourceType:
                if one >= SourceType.bcm:
                    po_src_list.append(one.value)
            self.calc_everyday(end_date, po_src_list)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('third_party_portfolio_manually_crawled')
        return failed_tasks


if __name__ == '__main__':
    mc_pp = ManuallyCrawledPortfolioProcessor(DerivedDataHelper())
    # mc_pp.init()
    # mc_pp.calc()
    # mc_pp.process('20201012')
