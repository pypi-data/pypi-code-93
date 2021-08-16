
import json
import os
import traceback
from typing import Dict, List

import pandas as pd
import numpy as np

from .....constant import SourceType
from .....fund.engine.trader import BasicFundTrader
from .....fund.engine.backtest import BasicFundBacktestEngine
from ....fund.basic.basic_data_helper import BasicDataHelper
from ....manager.manager_fund import FundDataManager
from ....view.derived_models import ThirdPartyPortfolioInfo, ThirdPartyPortfolioTrade, ThirdPartyPortfolioIndicator, ThirdPartyPortfolioPositionLatest
from ..derived_data_helper import DerivedDataHelper, DateJSONEncoder
from .common import ThirdPortfolioBase


class QiemanPortfolioProcessor(ThirdPortfolioBase):

    _FILE_SUFFIX = 'json'
    _INFO_COLUMNS_MAP = {
        'portfolio_id': 'po_id',
        'poName': 'po_name',
        'poDesc': 'po_desc',
        'poRichDesc': 'rich_desc',
        'establishedOn': 'start_date',
        'risk5LevelName': 'risk_level',
        'canWeeklyAip': 'can_aip',
    }

    def __init__(self, data_helper: DerivedDataHelper):
        super().__init__()

        self._data_helper = DerivedDataHelper()
        self._params_json: Dict[str, str] = {}
        self._dir_path = f'{os.path.dirname(os.path.abspath(__file__))}/data/qieman'
        self._trades_df_list = []
        self._nav: Dict[str, pd.DataFrame] = {}
        self._last_position: List[pd.Series] = []

    def init(self):

        def count_ceased_portfolio(x):
            with open(f'{self._dir_path}/portfolios/{x.name}.{self._FILE_SUFFIX}', 'r') as f:
                portfolio_info = json.load(f)
                ceased_on = portfolio_info.get('ceasedOn')
                if ceased_on is not None:
                    po_id = portfolio_info.get('poCode')
                    assert po_id == x.name.split('.')[0], 'po_id does not match'
                    print(f'{po_id} ceased on {ceased_on}')
                    ceased_portfolio.append(po_id)

        # self._fdm = FundDataManager(s3_retriever_activation=True)
        # self._fdm.init(score_pre_calc=True, print_time=True)

        from .....resource.data_store import DataStore
        self._fdm: FundDataManager = DataStore.load_dm()
        self._bdh = BasicDataHelper()
        self._trading_day: pd.DataFrame = FundDataManager.basic_data('get_trading_day_list').drop(columns='_update_time')

        list_all_df = pd.read_csv(f'{self._dir_path}/list_all.txt')
        self._list_verified: pd.DataFrame = pd.read_csv(f'{self._dir_path}/list_verified.txt').set_index('portfolio_id')
        pd.testing.assert_frame_equal(list_all_df[list_all_df.verified].reset_index(drop=True).set_index('portfolio_id'), self._list_verified)

        # 不处理已经停止的组合
        ceased_portfolio: List[str] = []
        self._list_verified.apply(count_ceased_portfolio, axis=1)
        self._list_verified = self._list_verified.loc[~self._list_verified.index.isin(ceased_portfolio), :]

        list_portfolio_file_df = pd.read_csv(f'{self._dir_path}/list_portfolio_file.txt', header=None, names=['file_name'])
        self._files_list = set(list_portfolio_file_df.file_name.array)

    def _calc_one(self, x: pd.Series):
        if '.' in x.name:
            print(f'Invalid portfolio name {x.name} (info){x}')
            return
        file_name = x.name + '.json'
        if file_name not in self._files_list:
            print(f'[ERROR] Can not found {file_name} (info){x}')
            return

        result_params = {}
        result_params['fund_weight_list'] = []
        page = 0
        while page is not None:
            with open(f'{self._dir_path}/portfolios/{x.name}_adj{page}.{self._FILE_SUFFIX}', 'r') as f:
                adj_info = json.load(f)
            is_last = adj_info.get('last', True)
            if not is_last:
                total = adj_info.get('totalPages')
                now = adj_info.get('page')
                if total is None or now is None or now >= total:
                    page = None
                else:
                    page += 1
            else:
                page = None

            content = adj_info.get('content')
            if content is None:
                print(f'[WARNING] Invalid content {adj_info}')
                continue

            for one_content in content:
                adjusted_on = pd.to_datetime(one_content.get('adjustedOn'), infer_datetime_format=True).date()
                details = one_content.get('details')
                if details is None:
                    print(f'[WARNING] Invalid details {adj_info}')
                    continue
                if not details:
                    print(f'[INFO] Empty details, do next one')
                    continue
                result_details = []
                for one in details:
                    fund_id = self._bdh._get_fund_id_from_order_book_id(one.get('fundCode'), adjusted_on)
                    if fund_id is None:
                        raw_fund_id = one.get('fundCode')
                        print(f'[WARNING] Can not found {raw_fund_id}')
                        fund_id = raw_fund_id + '!0'
                    result_details.append([fund_id, float(one.get('toPercent'))])
                adjusted_date = adjusted_on
                # 我们是第二天调仓，因此这里调整为之前的第一个交易日
                adjusted_date = self._trading_day[self._trading_day.datetime < adjusted_date].datetime.array[-1]
                result_params['fund_weight_list'].append([adjusted_date.isoformat(), result_details])

        # 按调仓日期排序
        result_params['fund_weight_list'].sort(key=lambda x: x[0])
        # # 使用的回测类型
        # result_params['back_test_type'] = 'basic'
        with open(f'{self._dir_path}/portfolios/{file_name}', 'r') as f:
            portfolio_base_info = json.load(f)
        result_params['start_date'] = portfolio_base_info.get('establishedOn')
        result_params['end_date'] = portfolio_base_info.get('navDate')

        start_date = pd.to_datetime(result_params.get('start_date'), infer_datetime_format=True).date()
        # 我们是第二天调仓，因此这里调整为之前的第一个交易日
        start_date = self._trading_day[self._trading_day.datetime < start_date].datetime.array[-1]
        end_date = pd.to_datetime(result_params.get('end_date'), infer_datetime_format=True).date()

        t = BasicFundTrader()
        b = BasicFundBacktestEngine(data_manager=self._fdm, trader=t, fund_weight_list=result_params['fund_weight_list'])
        b.init()
        b.run(start_date=start_date, end_date=end_date, print_time=False)
        result = b.get_fund_result()
        result['navDate_ours'] = result['market_value'].index.array[-1]
        result['fromSetupReturn_ours'] = result['last_unit_nav'] - 1
        resampled = result['market_value'].copy()
        resampled.index = pd.to_datetime(resampled.index)
        resampled_w = resampled.mv.resample('1W').apply(lambda x: x[-1] if not x.empty else np.nan)
        result['volatility_ours(w)'] = resampled_w.dropna().pct_change().std(ddof=1) * np.sqrt(52)

        resampled_m = resampled.mv.resample('1M').apply(lambda x: x[-1] if not x.empty else np.nan)
        result['volatility(m)'] = resampled_m.dropna().pct_change().std(ddof=1) * np.sqrt(12)
        result['volatility(d)'] = resampled.mv.dropna().pct_change().std(ddof=1) * np.sqrt(244)
        result['annualCompoundedReturn_ours'] = np.power(result['last_unit_nav'], 1 / (result['market_value'].shape[0] / 244)) - 1
        result['sharpe_ours'] = (result['annualCompoundedReturn_ours'] - 0.02) / result['volatility_ours(w)']
        # 遍历每个需要计算的时间区间
        for name, value in self._DIM_TYPE.items():
            bd = (result['navDate_ours'] - value).date()
            # 试图寻找bd及其之前的最近一天
            filtered_mv = result['market_value'].loc[result['market_value'].index <= bd, :]
            if filtered_mv.empty:
                continue
            # 计算区间内的return
            result[name + 'ours'] = result['market_value'].mv.array[-1] / filtered_mv.mv.array[-1] - 1

        # 删掉我们不需要的回测结果
        for one in ('hs300', 'csi500', 'gem', 'sp500rmb', 'national_debt', 'gold', 'cash', 'mmf', 'hsi', 'market_value', 'rebalance_date', 'hold_years', 'sharpe'):
            del result[one]
        # 挪过来一些组合的基础信息
        for one in ('poName', 'driveMode', 'poDesc', 'poRichDesc', 'establishedOn', 'risk5LevelName', 'nav', 'navDate', 'dailyReturn', 'weeklyReturn', 'monthlyReturn', 'quarterlyReturn', 'halfYearlyReturn', 'yearlyReturn', 'fromSetupReturn',
                    'annualCompoundedReturn', 'maxDrawdown', 'sharpe', 'volatility', 'canWeeklyAip'):
            result[one] = portfolio_base_info.get(one)
        extra_info = portfolio_base_info.get('extra')
        if extra_info is not None:
            result['benchmarks'] = extra_info.get('benchmarks')
        print(f'{x.name} done')
        return pd.Series(result, name=x.name).rename({'mdd': 'maxDrawdown_ours', 'last_unit_nav': 'nav_ours'})

    def _calc_basic_info(self, x: pd.Series):
        file_name = x.name + '.json'
        if file_name not in self._files_list:
            print(f'[ERROR] Can not found {file_name} (info){x}')
            return
        with open(f'{self._dir_path}/portfolios/{file_name}', 'r') as f:
            portfolio_base_info = json.load(f)

        result = {}
        for one in ('poName', 'poDesc', 'poRichDesc', 'establishedOn', 'risk5LevelName', 'canWeeklyAip'):
            result[one] = portfolio_base_info.get(one)
        poManagers_info = portfolio_base_info.get('poManagers')
        if poManagers_info is not None and poManagers_info:
            result['manager_name'] = poManagers_info[0].get('poManagerName')
        extra_info = portfolio_base_info.get('extra')
        if extra_info is not None:
            benchmarks = extra_info.get('benchmarks')
            if benchmarks is not None and benchmarks:
                result['benchmarks'] = json.dumps([one.get('code') for one in benchmarks])
        return pd.Series(result)

    def _calc_trades(self, x: pd.Series):
        fund_weight_list = []
        result_params = {}
        result_params['fund_weight_list'] = []
        page = 0
        while page is not None:
            with open(f'{self._dir_path}/portfolios/{x.name}_adj{page}.{self._FILE_SUFFIX}', 'r') as f:
                adj_info = json.load(f)
            is_last = adj_info.get('last', True)
            if not is_last:
                total = adj_info.get('totalPages')
                now = adj_info.get('page')
                if total is None or now is None or now >= total:
                    page = None
                else:
                    page += 1
            else:
                page = None

            content = adj_info.get('content')
            if content is None:
                print(f'[WARNING] Invalid content {adj_info}')
                continue

            for one_content in content:
                adjusted_on = pd.to_datetime(one_content.get('adjustedOn'), infer_datetime_format=True).date()
                details = one_content.get('details')
                if details is None:
                    print(f'[WARNING] Invalid details {one_content}')
                    continue
                if not details:
                    print(f'[INFO] Empty details, do next one')
                    continue
                fp_sum = 0
                tp_sum = 0
                result_details = []
                for one in details:
                    raw_fund_id = one.get('fundCode')
                    fund_id = self._bdh._get_fund_id_from_order_book_id(raw_fund_id, adjusted_on)
                    if fund_id is None:
                        print(f'[WARNING] Can not found fund {raw_fund_id} (po_id){x.name}')
                        fund_id = raw_fund_id + '!0'
                    result_details.append({'fund_id': fund_id, 'from_percent': float(one.get('fromPercent')), 'to_percent': float(one.get('toPercent'))})
                    fp_sum += float(one.get('fromPercent'))
                    tp_sum += float(one.get('toPercent'))
                fp_sum = round(fp_sum, 3)
                tp_sum = round(tp_sum, 3)
                if (fp_sum != 0 and fp_sum != 1) or tp_sum != 1:
                    print(f'sum of percent not equals 1 (po_id){x.name} (trade_date){adjusted_on} (fp_sum){fp_sum} (tp_sum){tp_sum}')
                adjusted_date = adjusted_on
                # 我们是第二天调仓，因此这里调整为之前的第一个交易日
                adjusted_date = self._trading_day[self._trading_day.datetime < adjusted_date].datetime.array[-1]
                fund_weight_list.append({'po_id': x.name, 'datetime': adjusted_on, 'details': json.dumps(result_details), 'comment': one_content.get('comment')})
                result_params['fund_weight_list'].append([adjusted_date, [(one['fund_id'], one['to_percent']) for one in result_details]])
        self._trades_df_list.append(pd.DataFrame(fund_weight_list))

        file_name = x.name + '.json'
        if file_name in self._files_list:
            with open(f'{self._dir_path}/portfolios/{file_name}', 'r') as f:
                portfolio_base_info = json.load(f)
            result_params['start_date'] = portfolio_base_info.get('establishedOn')
            result_params['end_date'] = portfolio_base_info.get('navDate')
        result_params['fund_weight_list'].sort(key=lambda x: x[0])
        self._params_json[x.name] = json.dumps(result_params, indent=4, cls=DateJSONEncoder)

    def _calc_indicators(self, x: pd.Series):
        params = json.loads(self._params_json.get(x.name))

        start_date = pd.to_datetime(params.get('start_date'), infer_datetime_format=True).date()
        # 我们是第二天调仓，因此这里调整为之前的第一个交易日
        start_date = self._trading_day[self._trading_day.datetime < start_date].datetime.array[-1]
        # end_date = pd.to_datetime(params.get('end_date'), infer_datetime_format=True).date()

        t = BasicFundTrader()
        b = BasicFundBacktestEngine(data_manager=self._fdm, trader=t, fund_weight_list=params['fund_weight_list'])
        b.init()
        b.run(start_date=start_date, end_date=None, print_time=False)

        last_position: pd.DataFrame = b.get_last_position()
        if last_position is None:
            print(f'[WARNING] {x.name} has no last position')
        else:
            self._last_position.append(pd.Series({'po_id': x.name, 'datetime': last_position.index.name, 'po_src': SourceType.qieman, 'position': last_position.loc[:, 'weight'].to_json()}))

        result = b.get_fund_result()
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
        self._nav[x.name] = result['market_value'].mv / result['market_value'].mv.array[0]
        self._nav[x.name].index = self._nav[x.name].index.map(lambda x: x.isoformat())
        # 删掉我们不需要的回测结果
        for one in ('market_value', 'last_unit_nav'):
            del result[one]
        print(f'{x.name} done')
        return pd.Series(result)

    def calc(self):
        # whole_result: pd.DataFrame = self._list_verified.apply(self._calc_one, axis=1)
        basic_info: pd.DataFrame = self._list_verified.apply(self._calc_basic_info, axis=1)
        basic_info['po_src'] = SourceType.qieman
        self._data_helper._upload_derived(basic_info.reset_index().rename(columns=self._INFO_COLUMNS_MAP), ThirdPartyPortfolioInfo.__table__.name)

        self._list_verified.apply(self._calc_trades, axis=1)
        trades = pd.concat(self._trades_df_list)
        trades['po_src'] = SourceType.qieman
        self._data_helper._upload_derived(trades, ThirdPartyPortfolioTrade.__table__.name)

        indicators: pd.DataFrame = self._list_verified.apply(self._calc_indicators, axis=1)
        indicators['po_src'] = SourceType.qieman
        self._data_helper._upload_derived(indicators.reset_index().rename(columns={'portfolio_id': 'po_id'}), ThirdPartyPortfolioIndicator.__table__.name)

        last_position = pd.DataFrame(self._last_position)
        self._data_helper._upload_derived(last_position, ThirdPartyPortfolioPositionLatest.__table__.name)

        # nav存cas
        from ....view.cas.third_party_portfolio_nav import ThirdPartyPortfolioNav
        for po_id, mv in self._nav.items():
            ThirdPartyPortfolioNav.create(
                po_id=po_id,
                date=mv.index.to_list(),
                nav=mv.to_list(),
            )

    def process(self, end_date: str) -> List[str]:
        failed_tasks: List[str] = []
        try:
            self.calc_everyday(end_date, [SourceType.qieman.value])
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('third_party_portfolio_qieman')
        return failed_tasks


if __name__ == '__main__':
    qieman_pp = QiemanPortfolioProcessor(DerivedDataHelper())
    # qieman_pp.init()
    # qieman_pp.calc()
    # qieman_pp.process('20201012')
