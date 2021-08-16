
from typing import List, Optional, Tuple, Dict
from collections import defaultdict
import datetime
import json
import io
import traceback
import math

import numpy as np
import pandas as pd

from sqlalchemy.orm import sessionmaker

# from ...util.singleton import Singleton
from ...util.wechat_bot import WechatBot
from ...util.calculator import Calculator
from ...util.aip_calc import xirr
from ...constant import HoldingAssetType, FOFTradeStatus, FOFIncentiveFeeMode
from ..api.basic import BasicDataApi
from ..api.derived import DerivedDataApi
from ..view.basic_models import FOFInfo, HedgeFundNAV, FOFInvestorPosition, FOFInvestorPositionSummary
from ..view.derived_models import FOFNav, FOFNavCalc, FOFPosition, FOFInvestorData, FOFPositionDetail
from ..wrapper.mysql import BasicDatabaseConnector, DerivedDatabaseConnector
from ..nav_reader.hedge_fund_nav_reader import HedgeFundNAVReader
from ..nav_reader.fof_nav_reader import FOFNAVReader
from .manager_hedge_fund import HedgeFundDataManager


class FOFDataManagerLite:

    _DAYS_PER_YEAR_FOR_INTEREST = 360

    def __init__(self):
        # pd.set_option('display.max_rows', None)
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.float_format', lambda x: '%.4f' % x)
        self._start_date: Optional[str] = None
        self._end_date: Optional[str] = None
        self._date_list: Optional[np.ndarray] = None
        self._fof_scale: Optional[pd.DataFrame] = None
        self._fof_redemp: Optional[pd.DataFrame] = None
        self._asset_allocation: Optional[pd.DataFrame] = None
        self._hedge_pos: Optional[pd.DataFrame] = None
        self._hedge_nav: Optional[pd.DataFrame] = None
        self._fund_pos: Optional[pd.DataFrame] = None
        self._manually: Optional[pd.DataFrame] = None
        self._fof_nav: Optional[pd.DataFrame] = None
        self._fof_position: Optional[pd.DataFrame] = None
        # self._fof_investor_pos: Optional[pd.DataFrame] = None
        self._fof_position_details: Optional[pd.DataFrame] = None
        self._total_net_assets: float = None
        self._total_shares: float = None

        self._wechat_bot = WechatBot()

    def _get_days_this_year_for_fee(self, the_date: datetime.date) -> int:
        '''计算今年一共有多少天'''
        return pd.Timestamp(year=the_date.year, month=12, day=31).dayofyear

    @staticmethod
    def _do_calc_v_net_value_by_mv(nav: float, acc_nav: str, trades_info: pd.DataFrame, incentive_fee_type: str, incentive_fee_ratio: str, decimals: float) -> float:
        regular_carry = trades_info[trades_info.carry_calc_type == 0]
        redemp_carry = trades_info[trades_info.carry_calc_type == 1]
        pay_mng_fee = 0
        for tag, carry in zip([0, 1], [regular_carry, redemp_carry]):
            if carry.empty:
                continue
            if incentive_fee_type == '1':
                # 盈利
                if tag == 0:
                    excess_ret = acc_nav - carry.water_line
                elif tag == 1:
                    excess_ret = pd.Series(np.fmin(acc_nav - carry.acc_net_value, carry.water_line - carry.acc_net_value))
                else:
                    assert False, f'invalid carry calc type {tag}'
                # 盈 或 亏
                earn_con = (excess_ret > 0).astype('int')
                # earning
                earning = (carry.unit_total * excess_ret * earn_con).round(2)
                # 费
                pay_mng_fee += (earning * float(incentive_fee_ratio)).round(2).sum()
            elif incentive_fee_type == '2':
                fee_df = pd.DataFrame(json.loads(incentive_fee_ratio)).sort_values(by='start', ascending=False)
                assert not fee_df.empty, f'invalid fee str {incentive_fee_ratio} (fee_type){incentive_fee_type}'

                for row in carry.itertuples(index=False):
                    if tag == 0:
                        if acc_nav < row.water_line:
                            # 小于水位线的份额不需要计提业绩报酬
                            continue
                        excess_ret = acc_nav - row.water_line
                    elif tag == 1:
                        excess_ret = min(acc_nav - row.acc_net_value, row.water_line - row.acc_net_value)
                        if excess_ret < 0:
                            continue
                    else:
                        assert False, f'invalid carry calc type {tag}'

                    earning = round(row.unit_total * excess_ret, 2)
                    left_earning = earning
                    for fee_row in fee_df.itertuples(index=False):
                        level_profit: float = row.water_line * (fee_row.start if fee_row.start else 0)
                        if left_earning > level_profit:
                            pay_mng_fee += (left_earning - level_profit) * (fee_row.val if fee_row.val else 0)
                            left_earning = level_profit

        # 通过MV来算出净值
        unit_total_sum = trades_info.unit_total.sum()
        mv = round(nav * unit_total_sum, 2)
        mv -= pay_mng_fee
        v_nav = round(mv / unit_total_sum, decimals)
        return v_nav

    @staticmethod
    def _do_calc_v_net_value_by_nav(nav: pd.DataFrame, acc_nav: pd.DataFrame, water_line: pd.Series, incentive_fee_type: pd.Series, incentive_fee_ratio: pd.Series, decimals: pd.Series) -> pd.Series:
        # 盈利
        excess_ret = acc_nav - water_line
        # 盈 或 亏
        earn_con = (excess_ret > 0).astype('int')
        # earning
        earning = (excess_ret * earn_con).round(2)
        # 费
        if incentive_fee_type == '1':
            pay_mng_fee = (earning * float(incentive_fee_ratio)).round(2)
        elif incentive_fee_type == '2':
            fee_df = pd.DataFrame(json.loads(incentive_fee_ratio)).sort_values(by='start', ascending=False)
            assert not fee_df.empty, f'invalid fee str {incentive_fee_ratio} (fee_type){incentive_fee_type}'

            def _calc_v_net_value_for_fund(x: float, water_line: float) -> float:
                if math.isclose(x, 0) or x < 0:
                    return 0
                mng_fee = 0
                for row in fee_df.itertuples(index=False):
                    level_profit: float = water_line * (row.start if row.start else 0)
                    if x > level_profit:
                        mng_fee += (x - level_profit) * (row.val if row.val else 0)
                        x = level_profit
                return mng_fee
            pay_mng_fee = earning.apply(lambda x: x.apply(_calc_v_net_value_for_fund, axis=1, water_line=water_line.at[x.name]))
        # 净值
        v_nav = (nav - pay_mng_fee).round(decimals)
        return v_nav

    @staticmethod
    def _calc_virtual_net_value(manager_id, fof_id, fund_list, asset_allocation=None, nav_tag='nav'):
        '''计算虚拟净值'''
        fund_info = BasicDataApi().get_fof_info(manager_id, fund_list)
        # TODO: 支持更多种类业绩计提方式的计算
        fund_info = fund_info.loc[fund_info.incentive_fee_mode.isin([
            FOFIncentiveFeeMode.SCST_HIGH_WL_S,
            FOFIncentiveFeeMode.INTE_HIGH_WL,
            FOFIncentiveFeeMode.INTE_HIGH_WL_WITH_SCST_R,
        ])]
        fund_info = fund_info.set_index('fof_id')
        incentive_fee_mode = fund_info['incentive_fee_mode'].to_dict()
        incentive_fee_type = fund_info['incentive_fee_type'].to_dict()
        incentive_fee_ratio = fund_info['incentive_fee_str'].to_dict()
        v_nav_decimals = fund_info['nav_decimals'].to_dict()

        df = FOFDataManagerLite.get_fof_nav(manager_id, fund_list)
        df = df.rename(columns={'fof_id': 'fund_id'})
        df = df[df.fund_id.isin(fund_info.index.array)]

        if asset_allocation is None:
            asset_allocation = FOFDataManagerLite.get_fof_asset_allocation(manager_id, [fof_id])
        asset_allocation = asset_allocation.loc[(asset_allocation.asset_type == HoldingAssetType.HEDGE) & (asset_allocation.fund_id.isin(fund_list)), :]
        df = df.append(asset_allocation.loc[asset_allocation.event_type.isin([FOFTradeStatus.PURCHASE, FOFTradeStatus.SUBSCRIBE]), ['datetime', 'fund_id', 'water_line', 'nav']].rename(columns={'water_line': 'acc_net_value'}))
        df = df.drop_duplicates(subset=['fund_id', 'datetime'])
        asset_allocation = asset_allocation.set_index('datetime')

        date_list: np.ndarray = pd.date_range(df.datetime.sort_values().array[0], datetime.datetime.now().date()).date
        nav = df.pivot(index='datetime', columns='fund_id', values=[nav_tag, 'acc_net_value'])
        nav = nav.reindex(date_list).ffill().stack().reset_index(level='fund_id')
        if nav_tag != 'nav':
            nav = nav.rename(columns={nav_tag: 'nav'})

        v_nav_result = []
        datas_to_calc_v = defaultdict(list)
        for row in nav.itertuples():
            try:
                one = asset_allocation.loc[[row.Index], :]
                one = one.loc[one.fund_id == row.fund_id, :]
            except KeyError:
                pass
            else:
                for one_in_date in one.itertuples():
                    if one_in_date.event_type in (FOFTradeStatus.REDEEM, ):
                        assert one_in_date.fund_id in datas_to_calc_v, '!!!!'
                        fund_data = datas_to_calc_v[one_in_date.fund_id]
                        redempt_share = one_in_date.share
                        for a_trade in fund_data:
                            assert a_trade[1] < one_in_date.Index, '!!!'
                            if a_trade[2] >= redempt_share:
                                a_trade[2] -= redempt_share
                                break
                            assert redempt_share >= a_trade[2], '!!!'
                            redempt_share -= a_trade[2]
                            a_trade[2] = 0
                    if one_in_date.event_type in (FOFTradeStatus.DEDUCT_REWARD_AND_DIVIDEND_VOLUME, FOFTradeStatus.DEDUCT_REWARD_AND_DIVIDEND_CASH, FOFTradeStatus.DEDUCT_REWARD):
                        assert one_in_date.fund_id in datas_to_calc_v, '!!!!'
                        fund_data = datas_to_calc_v[one_in_date.fund_id]
                        if incentive_fee_mode[row.fund_id] == FOFIncentiveFeeMode.SCST_HIGH_WL_S:
                            if one_in_date.event_type in (FOFTradeStatus.DEDUCT_REWARD_AND_DIVIDEND_VOLUME, FOFTradeStatus.DEDUCT_REWARD_AND_DIVIDEND_CASH):
                                total_share = one_in_date.share
                            else:
                                total_share = -one_in_date.share
                            new_fund_data = []
                            for a_trade in fund_data:
                                assert a_trade[1] < one_in_date.Index, '!!!'
                                if one_in_date.water_line < a_trade[3]:
                                    # 如果当前相对于这笔记录还在水下 把记录原样加回来
                                    new_fund_data.append(a_trade)
                                else:
                                    # 如果当前相对于这笔记录在水上 累加份额后续归到同一条记录上
                                    total_share += a_trade[2]
                            datas_to_calc_v[one_in_date.fund_id] = new_fund_data + [[one_in_date.fund_id, one_in_date.Index, total_share, one_in_date.water_line, one_in_date.water_line, 0]]
                        elif incentive_fee_mode[row.fund_id] in (FOFIncentiveFeeMode.INTE_HIGH_WL, FOFIncentiveFeeMode.INTE_HIGH_WL_WITH_SCST_R):
                            total_share = 0
                            # assert one_in_date.water_line >= a_trade[3], f'the water line should greater or equal than all water lines before this trade (water_line){one_in_date.water_line} (weird_trade){a_trade} (manager_id){manager_id} (fof_id){fof_id}'
                            if incentive_fee_mode[row.fund_id] == FOFIncentiveFeeMode.INTE_HIGH_WL:
                                for a_trade in fund_data:
                                    total_share += a_trade[2]
                                datas_to_calc_v[one_in_date.fund_id] = [[one_in_date.fund_id, one_in_date.Index, total_share, one_in_date.water_line, one_in_date.water_line, 0]]
                                print(f'(total_share){total_share} (fund_id){row.fund_id} (new_datas_to_calc_v){datas_to_calc_v[one_in_date.fund_id]}')
                            else:
                                # 除了最后合并的水位线 其他如果当时是在水下 需要用赎回时单人单笔高水位法来计提业绩报酬
                                new_fund_data = []
                                for a_trade in fund_data:
                                    if a_trade[3] > a_trade[4]:
                                        a_trade[5] = 1
                                        new_fund_data.append(a_trade)
                                    else:
                                        total_share += a_trade[2]
                                print(f'(total_share){total_share} (fund_id){row.fund_id} (fund_data){fund_data} (new_fund_data){new_fund_data}')
                                datas_to_calc_v[one_in_date.fund_id] = new_fund_data + [[one_in_date.fund_id, one_in_date.Index, total_share, one_in_date.water_line, one_in_date.water_line, 0]]
                        else:
                            assert False, f'do not support the fee mode {incentive_fee_mode[row.fund_id]} temp (manager_id){manager_id} (fof_id){fof_id}'

                    if one_in_date.event_type in (FOFTradeStatus.PURCHASE, FOFTradeStatus.SUBSCRIBE, FOFTradeStatus.DIVIDEND_VOLUME):
                        datas_to_calc_v[one_in_date.fund_id].append([one_in_date.fund_id, one_in_date.Index, one_in_date.share, one_in_date.water_line if not pd.isnull(one_in_date.water_line) else one_in_date.nav, one_in_date.acc_net_value, 0])

            df = pd.DataFrame(datas_to_calc_v[row.fund_id], columns=['fund_id', 'datetime', 'unit_total', 'water_line', 'acc_net_value', 'carry_calc_type'])
            df = df[df.unit_total != 0]
            if df.empty:
                continue
            v_nav = FOFDataManagerLite._do_calc_v_net_value_by_mv(row.nav, row.acc_net_value, df[['unit_total', 'water_line', 'acc_net_value', 'carry_calc_type']], incentive_fee_type[row.fund_id], incentive_fee_ratio[row.fund_id], v_nav_decimals[row.fund_id])
            v_nav_result.append({'datetime': row.Index, 'fund_id': row.fund_id, 'v_nav': v_nav})
        df = pd.DataFrame.from_dict(v_nav_result)
        if not df.empty:
            df = df.pivot(index='datetime', columns='fund_id', values='v_nav')
        return df

    def _calc_adj_nav_for_a_fund(df: pd.DataFrame):
        net_asset_value = df.nav
        if df.shape[0] < 2:
            return pd.Series({'datetime': df.datetime.array[-1], 'ta_factor': 1, 'adj_nav': net_asset_value.array[-1], 'change_rate': np.nan})

        acc_unit_value = df.acc_net_value
        last_diff = round(acc_unit_value.array[-2] - net_asset_value.array[-2], 6)
        this_diff = round(acc_unit_value.array[-1] - net_asset_value.array[-1], 6)
        assert math.isclose(this_diff - last_diff, 0) or (this_diff > last_diff), f'!!!(fof_id){df.fof_id.array[0]} (this_diff){this_diff} (last_diff){last_diff}'

        if math.isclose(last_diff, this_diff):
            ta_factor = df.ta_factor.array[-2]
        else:
            dividend = this_diff - last_diff
            # ta_factor = df.ta_factor.array[-2] * (1 + dividend / (net_asset_value.array[-2] - dividend))
            ta_factor = df.ta_factor.array[-2] * ((dividend + net_asset_value.array[-1]) / net_asset_value.array[-1])
        if pd.isnull(ta_factor):
            ta_factor = 1
        adj_nav = net_asset_value.array[-1] * ta_factor
        return pd.Series({'datetime': df.datetime.array[-1], 'ta_factor': ta_factor, 'adj_nav': adj_nav, 'change_rate': adj_nav / df.adjusted_nav.dropna().array[-1]})

    @staticmethod
    def _calc_adjusted_net_value(manager_id: str, fund_list: List[str]):
        '''计算复权净值'''

        df = FOFDataManagerLite.get_fof_nav(manager_id, fund_list)
        return df.groupby(by='fof_id', sort=False).apply(FOFDataManagerLite._calc_adj_nav_for_a_fund)

    def _init(self, manager_id: str, fof_id: str, debug_mode=False):
        def _calc_water_line_and_confirmed_nav(x):
            x = x.reset_index()
            x_with_water_line = x[x.water_line.notna()]
            return pd.Series({'confirmed_nav': json.dumps(x[['share', 'nav']].to_dict(orient='records')),
                              'water_line': json.dumps(x_with_water_line[['share', 'water_line']].to_dict(orient='records'))})

        # 获取fof基本信息
        fof_info: Optional[pd.DataFrame] = FOFDataManagerLite.get_fof_info(manager_id, [fof_id])
        assert fof_info is not None, f'get fof info for {manager_id}/{fof_id} failed'

        self._MANAGEMENT_FEE_PER_YEAR = fof_info.management_fee if fof_info.management_fee is not None else 0
        self._CUSTODIAN_FEE_PER_YEAR = fof_info.custodian_fee if fof_info.custodian_fee is not None else 0
        self._ADMIN_SERVICE_FEE_PER_YEAR = fof_info.administrative_fee if fof_info.administrative_fee is not None else 0
        self._DEPOSIT_INTEREST_PER_YEAR = fof_info.current_deposit_rate if fof_info.current_deposit_rate is not None else 0.003
        self._SUBSCRIPTION_FEE = fof_info.subscription_fee if fof_info.subscription_fee is not None else 0
        self._ESTABLISHED_DATE = fof_info.established_date
        self._INCENTIVE_FEE_MODE = fof_info.incentive_fee_mode
        self._MIN_CUSTODIAN_FEE_BASE = fof_info.min_custodian_fee_amt if fof_info.min_custodian_fee_amt is not None else 0
        self._MIN_ADMIN_FEE_BASE = fof_info.min_admin_fee_amt if fof_info.min_admin_fee_amt is not None else 0
        if debug_mode:
            print(f'fof info: (manager_id){manager_id} (fof_id){fof_id} (management_fee){self._MANAGEMENT_FEE_PER_YEAR} (custodian_fee){self._CUSTODIAN_FEE_PER_YEAR} '
                  f'(admin_service_fee){self._ADMIN_SERVICE_FEE_PER_YEAR} (current_deposit_rate){self._DEPOSIT_INTEREST_PER_YEAR} (subscription_fee){self._SUBSCRIPTION_FEE} '
                  f'(incentive_fee_mode){self._INCENTIVE_FEE_MODE} (established_date){self._ESTABLISHED_DATE} (min_custodian_fee_base){self._MIN_CUSTODIAN_FEE_BASE} (min_admin_fee_base){self._MIN_ADMIN_FEE_BASE}')

        # 获取FOF份额变化信息
        fof_scale = DerivedDataApi().get_hedge_fund_investor_pur_redemp(manager_id, [fof_id])
        # 客户认购/申购记录
        self._fof_scale = fof_scale[fof_scale.event_type.isin([FOFTradeStatus.SUBSCRIBE, FOFTradeStatus.PURCHASE])].set_index('datetime').sort_index()
        self._start_date = self._fof_scale.index.min()
        assert not pd.isnull(self._start_date), f'subscribe/purchase record from investor lacked for doing fof calc (manager_id){manager_id} (fof_id){fof_id}'
        # 客户赎回记录
        self._fof_redemp = fof_scale[fof_scale.event_type.isin([FOFTradeStatus.REDEEM, ])].set_index('datetime').sort_index()

        investor_div_carry = DerivedDataApi().get_hedge_fund_investor_div_carry(manager_id, [fof_id])
        self._investor_div = investor_div_carry[investor_div_carry.event_type.isin([FOFTradeStatus.DIVIDEND_VOLUME, FOFTradeStatus.DIVIDEND_CASH])].set_index('datetime').sort_index()
        self._investor_carry = investor_div_carry[investor_div_carry.event_type.isin([FOFTradeStatus.DEDUCT_REWARD, ])].set_index('datetime').sort_index()

        # trading_day_list = BasicDataApi().get_trading_day_list(start_date=self._start_date, end_date=datetime.datetime.now().date())
        # 将昨天作为end_date
        self._end_date = datetime.datetime.now().date() - datetime.timedelta(days=1)
        if debug_mode:
            print(f'(start_date){self._start_date} (end_date){self._end_date}')
        self._date_list: np.ndarray = pd.date_range(self._start_date, self._end_date).date

        # 获取fof持仓
        self._asset_allocation: Optional[pd.DataFrame] = FOFDataManagerLite.get_fof_asset_allocation(manager_id, [fof_id]).sort_values(by='datetime')
        assert self._asset_allocation is not None, f'get fof pos for {manager_id}/{fof_id} failed'

        positions = self._asset_allocation.loc[self._asset_allocation.event_type.isin([FOFTradeStatus.PURCHASE, FOFTradeStatus.SUBSCRIBE]), :]
        self._water_line_and_confirmed_nav = positions.groupby(by='fund_id', sort=False).apply(_calc_water_line_and_confirmed_nav)
        self._total_cost = positions.pivot_table(index='datetime', columns='fund_id', values='amount', aggfunc=np.sum).sum()
        positions = positions.pivot(index='datetime', columns=['asset_type', 'fund_id'], values='share')
        positions = positions.reindex(index=self._date_list).cumsum().ffill()
        # 持仓中的公募基金
        try:
            self._fund_pos = positions[HoldingAssetType.MUTUAL]
        except KeyError:
            print('no fund pos found')

        # 持仓中的私募基金
        try:
            self._hedge_pos = positions[HoldingAssetType.HEDGE]
        except KeyError:
            print('no hedge pos found')

        # 获取私募基金净值数据
        if self._hedge_pos is not None:
            hedge_fund_list = list(self._hedge_pos.columns.unique())
            hedge_fund_nav = FOFDataManagerLite.get_fof_nav(manager_id, hedge_fund_list)
            hedge_fund_nav = hedge_fund_nav.pivot(index='datetime', columns='fof_id').reindex(index=self._date_list)
            # self._hedge_nav = hedge_fund_nav['v_net_value']
            self._all_latest_nav = hedge_fund_nav['nav'].ffill().iloc[-1, :]
            self._all_latest_acc_nav = hedge_fund_nav['acc_net_value'].ffill().iloc[-1, :]
            self._latest_nav_date = hedge_fund_nav['nav'].apply(lambda x: x[x.notna()].index.array[-1])

            # 我们自己算一下虚拟净值 然后拿它对_hedge_nav查缺补漏
            v_nav_calcd = FOFDataManagerLite._calc_virtual_net_value(manager_id, fof_id, hedge_fund_list, self._asset_allocation)
            # 最后再ffill
            # self._hedge_nav = self._hedge_nav.combine_first(v_nav_calcd.reindex(index=self._date_list)).ffill()
            # FIXME: 这里虚拟净值只能先全用自己算的
            self._hedge_nav = v_nav_calcd.reindex(index=self._date_list).ffill()
            if debug_mode:
                print(self._hedge_nav)
            self._hedge_latest_v_nav = self._hedge_nav.iloc[-1, :]
        else:
            self._all_latest_nav = None
            self._latest_nav_date = None
            self._all_latest_acc_nav = None
            self._hedge_latest_v_nav = None

        # 获取人工手工校正信息
        manually = BasicDataApi().get_fof_assert_correct(manager_id, fof_id)
        self._manually = manually.set_index('date')

    def _get_hedge_mv(self):
        if self._hedge_pos is None:
            return
        else:
            return (self._hedge_nav * self._hedge_pos).round(2).sum(axis=1).fillna(0)

    def _get_fund_mv(self):
        if self._fund_pos is None:
            return
        else:
            return (self._fund_pos * self._fund_nav).round(2).sum(axis=1).fillna(0)

    def calc_fof_nav(self, manager_id: str, fof_id: str, dump_to_db=True, debug_mode=False):
        self._init(manager_id=manager_id, fof_id=fof_id, debug_mode=debug_mode)

        if self._fund_pos is not None:
            fund_list: List[str] = self._fund_pos.columns.to_list()
            fund_info: Optional[pd.DataFrame] = BasicDataApi().get_fund_info(fund_list=fund_list)
            assert fund_info is not None, f'get fund info of {fund_list} failed'
            monetary_fund: List[str] = fund_info[fund_info.wind_class_1.isin(['货币市场型基金'])].fund_id.to_list()

            # 根据公募基金持仓获取相应基金的净值
            fund_nav: Optional[pd.DataFrame] = BasicDataApi().get_fund_nav_with_date_range(start_date=self._start_date, end_date=self._end_date, fund_list=fund_list)
            assert fund_nav is not None, f'get fund nav of {fund_list} failed'
            fund_nav = fund_nav.pivot(index='datetime', columns='fund_id')
            if self._latest_nav_date is not None:
                self._latest_nav_date = self._latest_nav_date.append(fund_nav['unit_net_value'].apply(lambda x: x[x.notna()].index.array[-1].date()))
            else:
                self._latest_nav_date = fund_nav['unit_net_value'].apply(lambda x: x[x.notna()].index.array[-1].date())
            fund_nav = fund_nav.reindex(index=self._date_list)
            self._monetary_daily_profit = fund_nav['daily_profit'][monetary_fund].fillna(0)
            fund_nav = fund_nav.ffill()
            if self._all_latest_acc_nav is not None:
                self._all_latest_acc_nav = self._all_latest_acc_nav.append(fund_nav['acc_net_value'].iloc[-1, :])
            else:
                self._all_latest_acc_nav = fund_nav['acc_net_value'].iloc[-1, :]
            self._fund_nav = fund_nav['unit_net_value']
            if self._all_latest_nav is not None:
                self._all_latest_nav = self._all_latest_nav.append(self._fund_nav.iloc[-1, :])
            else:
                self._all_latest_nav = self._fund_nav.iloc[-1, :]
        else:
            self._monetary_daily_profit = None
        # 公募基金总市值
        fund_mv: pd.DataFrame = self._get_fund_mv()

        # 获取FOF资产配置信息
        asset_alloc = self._asset_allocation.set_index('datetime')

        hedge_fund_mv = self._get_hedge_mv()

        # 循环遍历每一天来计算
        shares_list = pd.Series(dtype='float64', name='share')
        other_assets_list = pd.Series(dtype='float64', name='cash')
        fof_nav_list = pd.Series(dtype='float64', name='nav')
        today_fund_mv_list = pd.Series(dtype='float64', name='total_fund_mv')
        today_hedge_mv_list = pd.Series(dtype='float64', name='total_hedge_mv')
        net_assets_list = pd.Series(dtype='float64', name='net_asset')
        net_assets_fixed_list = pd.Series(dtype='float64', name='net_asset_fixed')
        management_fee_list = pd.Series(dtype='float64', name='management_fee')
        custodian_fee_list = pd.Series(dtype='float64', name='custodian_fee')
        administrative_fee_list = pd.Series(dtype='float64', name='administrative_fee')
        deposit_interest_list = pd.Series(dtype='float64', name='interest')
        positions_list = pd.Series(dtype='float64', name='position')
        position_details = {}
        # investor_pos_list = []
        for date in self._date_list:
            total_amount = 0
            share_increased = 0

            try:
                scale_data = self._fof_scale.loc[[date], :]
            except KeyError:
                pass
            else:
                # 后边都是汇总信息了 所以在这里先加一下记录
                # to_append_to_investor_pos = scale_data.loc[:, ['fof_id', 'investor_id', 'purchase_amount', 'raising_interest', 'share_changed', 'event_type']]
                # to_append_to_investor_pos['purchase_amount'] = to_append_to_investor_pos.purchase_amount.add(to_append_to_investor_pos.raising_interest, fill_value=0)
                # investor_pos_list.append(to_append_to_investor_pos.rename(columns={'purchase_amount': 'amount'}))

                purchase_sum = scale_data.purchase_amount.sum() + scale_data.raising_interest.sum()
                share_sum = scale_data.share_changed.sum()
                assert not pd.isnull(purchase_sum), '!!!'
                total_amount += purchase_sum
                assert not pd.isnull(share_sum), '!!!'
                share_increased += share_sum
                share_increased = round(share_increased, 2)

            if other_assets_list.empty:
                other_assets = 0
            else:
                other_assets = other_assets_list.iat[-1]
            other_assets += total_amount
            other_assets = round(other_assets, 2)

            try:
                # 看看当天有没有卖出FOF
                redemp_data = self._fof_redemp.loc[[date], :]
            except KeyError:
                # 处理没有赎回的情况
                total_amount_redemp = 0
            else:
                # 后边都是汇总信息了 所以在这里先加一下记录
                # investor_pos_list.append(redemp_data.loc[:, ['fof_id', 'investor_id', 'redemp_confirmed_amount', 'share_changed', 'event_type']].rename(columns={'redemp_confirmed_amount': 'amount'}))

                # 汇总今天所有的赎回资金
                total_amount_redemp = redemp_data.redemp_confirmed_amount.sum()
                share_increased += redemp_data.share_changed.sum()
                other_assets -= total_amount_redemp
            finally:
                share_increased = round(share_increased, 2)
                other_assets = round(other_assets, 2)

            if not math.isclose(total_amount, 0) or not math.isclose(total_amount_redemp, 0):
                if debug_mode:
                    print(f'{manager_id}/{fof_id} share changed (date){date} (amount){total_amount} (redemp_amount){total_amount_redemp} (share){share_increased}')

            # 这个日期之后才正式成立，所以在此之前都不需要处理后续步骤
            if not pd.isnull(self._ESTABLISHED_DATE) and (date < self._ESTABLISHED_DATE):
                other_assets_list.loc[date] = other_assets
                if not math.isclose(share_increased, 0):
                    shares_list.loc[date] = share_increased
                continue

            try:
                # 看看当天FOF有没有分红
                investor_div_data = self._investor_div.loc[[date], :]
            except KeyError:
                pass
            else:
                share_increased += investor_div_data.share_changed.sum()
                # 这里减掉现金分红和业绩报酬
                other_assets -= (investor_div_data.cash_dividend.sum() + investor_div_data.carry_amount.sum())

            try:
                # 看看当天FOF有没有计提业绩报酬
                investor_carry_data = self._investor_carry.loc[[date], :]
            except KeyError:
                pass
            else:
                share_increased += investor_carry_data.share_changed.sum()
                # 这里减掉业绩报酬
                other_assets -= investor_carry_data.carry_amount.sum()
            finally:
                share_increased = round(share_increased, 2)
                other_assets = round(other_assets, 2)

            try:
                expenses = 0
                today_asset_alloc = asset_alloc.loc[[date], :]
                for row in today_asset_alloc.itertuples():
                    if row.event_type in (FOFTradeStatus.PURCHASE, FOFTradeStatus.SUBSCRIBE):
                        assert not pd.isnull(row.amount), '!!!'
                        expenses += row.amount
                        try:
                            position_details[row.fund_id]['amount'] += row.amount
                        except KeyError:
                            position_details[row.fund_id] = {'start_date': date, 'amount': row.amount, 'dividend_cash': 0, 'redeem_amount': 0}
                    if row.event_type in (FOFTradeStatus.DEDUCT_REWARD, FOFTradeStatus.DIVIDEND_VOLUME, FOFTradeStatus.DEDUCT_REWARD_AND_DIVIDEND_VOLUME):
                        assert not pd.isnull(row.share), '!!!'
                        if row.event_type in (FOFTradeStatus.DIVIDEND_VOLUME, FOFTradeStatus.DEDUCT_REWARD_AND_DIVIDEND_VOLUME):
                            if row.asset_type == HoldingAssetType.HEDGE:
                                self._hedge_pos.loc[self._hedge_pos.index >= date, row.fund_id] += row.share
                            elif row.asset_type == HoldingAssetType.MUTUAL:
                                self._fund_pos.loc[self._fund_pos.index >= date, row.fund_id] += row.share
                        else:
                            if row.asset_type == HoldingAssetType.HEDGE:
                                self._hedge_pos.loc[self._hedge_pos.index >= date, row.fund_id] -= row.share
                            elif row.asset_type == HoldingAssetType.MUTUAL:
                                self._fund_pos.loc[self._fund_pos.index >= date, row.fund_id] -= row.share
                        # 重刷hedge_fund_mv
                        hedge_fund_mv = self._get_hedge_mv()
                        fund_mv = self._get_fund_mv()
                    if row.event_type == FOFTradeStatus.DIVIDEND_CASH:
                        other_assets += row.amount
                        assert row.fund_id in position_details, f'no pos of {row.fund_id} for DIVIDEND_CASH'
                        position_details[row.fund_id]['dividend_cash'] += row.amount
                # assert other_assets >= expenses, f'no enough cash to buy asset!! (date){date} (total cash){other_assets} (expenses){expenses}'
                other_assets -= expenses
            except KeyError:
                pass

            try:
                today_asset_redemp = asset_alloc.loc[[date], :]
                for row in today_asset_redemp.itertuples():
                    if row.event_type in (FOFTradeStatus.REDEEM, ):
                        if row.asset_type == HoldingAssetType.HEDGE:
                            self._hedge_pos.loc[self._hedge_pos.index >= date, row.fund_id] -= row.share
                            hedge_fund_mv = self._get_hedge_mv()
                        elif row.asset_type == HoldingAssetType.MUTUAL:
                            redemp_share = row.share
                            if self._monetary_daily_profit is not None and row.fund_id in self._monetary_daily_profit.columns:
                                redemp_share += round(redemp_share * self._monetary_daily_profit.shift(1).at[date, row.fund_id] / 10000, 2)
                            self._fund_pos.loc[self._fund_pos.index >= date, row.fund_id] -= redemp_share
                            fund_mv = self._get_fund_mv()
                        other_assets += row.amount
                        assert row.fund_id in position_details, f'no pos of {row.fund_id} for REDEEM'
                        position_details[row.fund_id]['redeem_amount'] += row.amount
            except KeyError:
                pass

            # 处理货基
            if self._monetary_daily_profit is not None:
                for fund_id, col in self._monetary_daily_profit.iteritems():
                    if not pd.isnull(self._fund_pos.at[date, fund_id]) and not math.isclose(self._fund_pos.at[date, fund_id], 0):
                        self._fund_pos.loc[self._fund_pos.index >= date, fund_id] += round(self._fund_pos.at[date, fund_id] * col[date] / 10000, 2)
                fund_mv = self._get_fund_mv()

            # 计提管理费, 计提行政服务费, 计提托管费
            if not net_assets_list.empty:
                last_net_asset = net_assets_list.iat[-1]
                management_fee_list.loc[date] = round(last_net_asset * self._MANAGEMENT_FEE_PER_YEAR / self._get_days_this_year_for_fee(date), 2)
                custodian_fee_list.loc[date] = round((last_net_asset if last_net_asset > self._MIN_CUSTODIAN_FEE_BASE else self._MIN_CUSTODIAN_FEE_BASE) * self._CUSTODIAN_FEE_PER_YEAR / self._get_days_this_year_for_fee(date), 2)
                administrative_fee_list.loc[date] = round((last_net_asset if last_net_asset > self._MIN_ADMIN_FEE_BASE else self._MIN_ADMIN_FEE_BASE) * self._ADMIN_SERVICE_FEE_PER_YEAR / self._get_days_this_year_for_fee(date), 2)
                misc_fees = management_fee_list.array[-1] + custodian_fee_list.array[-1] + administrative_fee_list.array[-1]
            else:
                misc_fees = 0

            # 应收银行存款利息
            if other_assets_list.empty:
                deposit_interest = 0
            else:
                if other_assets_list.iat[-1] > 0:
                    deposit_interest = round(other_assets_list.iat[-1] * self._DEPOSIT_INTEREST_PER_YEAR / self._DAYS_PER_YEAR_FOR_INTEREST, 2)
                else:
                    deposit_interest = 0
            deposit_interest_list.loc[date] = deposit_interest

            # 计算修正净资产
            try:
                errors_to_be_fixed = round(self._manually.at[date, 'amount'], 2)
            except KeyError:
                errors_to_be_fixed = 0
            other_assets += (deposit_interest - misc_fees + errors_to_be_fixed)
            other_assets_list.loc[date] = other_assets

            # 获取持仓中当日公募、私募基金的MV
            if fund_mv is not None:
                try:
                    today_fund_mv = fund_mv.loc[date]
                except KeyError:
                	today_fund_mv = 0
            else:
                today_fund_mv = 0
            today_fund_mv_list.loc[date] = today_fund_mv

            if hedge_fund_mv is not None:
            	try:
                	today_hedge_mv = hedge_fund_mv.loc[date]
            	except KeyError:
                	today_hedge_mv = 0
            else:
                today_hedge_mv = 0
            today_hedge_mv_list.loc[date] = today_hedge_mv

            # 计算净资产
            today_net_assets = today_fund_mv + today_hedge_mv + other_assets
            net_assets_list.loc[date] = today_net_assets

            if self._fund_pos is not None:
            	try:
                	fund_pos_info = pd.concat([self._fund_pos.loc[date, :].rename('share'), self._fund_nav.loc[date, :].rename('nav')], axis=1)
                	fund_pos_info = fund_pos_info[fund_pos_info.share.notna()]
                	fund_pos_info['asset_type'] = HoldingAssetType.MUTUAL
            	except KeyError:
                	fund_pos_info = None
            else:
                fund_pos_info = None

            if self._hedge_pos is not None:
            	try:
                	hedge_pos_info = pd.concat([self._hedge_pos.loc[date, :].rename('share'), self._hedge_nav.loc[date, :].rename('nav')], axis=1)
                	hedge_pos_info = hedge_pos_info[hedge_pos_info.share.notna()]
                	hedge_pos_info['asset_type'] = HoldingAssetType.HEDGE
            	except KeyError:
                	hedge_pos_info = None
            else:
            	hedge_pos_info = None

            if fund_pos_info is not None or hedge_pos_info is not None:
                position = pd.concat([fund_pos_info, hedge_pos_info], axis=0).rename_axis(index='fund_id')
                if not position.empty:
                    position = position[position.share != 0]
                    position['mv'] = position.share * position.nav
                    position_details_the_date = pd.DataFrame.from_dict(position_details, orient='index').reindex(position.index)
                    position['hold_date'] = (date - position_details_the_date.start_date).dt.days + 1
                    position['total_ret'] = position.mv / position_details_the_date.amount - 1
                    # if fund_nav.datetime.array[-1] > pur_sub_aa.confirmed_date.array[-1]:
                    #     the_xirr = f'{round(xirr(pur_sub_aa.amount.to_list() + (-redempt_aa.amount).to_list() + [-mv], pur_sub_aa.datetime.to_list() + redempt_aa.datetime.to_list() + [fund_nav.datetime.array[-1]]) * 100, 2)}%'
                    # else:
                    #     the_xirr = np.nan
                    # position['ann_ret'] = the_xirr
                    position['ann_ret'] = (position.total_ret + 1).pow(FOFDataManagerLite._DAYS_PER_YEAR_FOR_INTEREST / position.hold_date) - 1
                    # position['ann_ret_at']
                    position = position.reset_index()
            else:
                position = pd.Series(dtype='object').to_frame()
            positions_list.loc[date] = json.dumps(position.to_dict(orient='records'))

            today_net_assets_fixed = today_net_assets
            net_assets_fixed_list.loc[date] = today_net_assets_fixed

            # 如果今日有投资人申购fof 记录下来
            if not math.isclose(share_increased, 0):
                shares_list.loc[date] = share_increased
            # 计算fof的nav
            if shares_list.sum() != 0:
                fof_nav = today_net_assets_fixed / shares_list.sum()
            else:
                fof_nav = 1
            fof_nav_list.loc[date] = round(fof_nav, 4)
        # 汇总所有信息
        if debug_mode:
            total_info = pd.concat([shares_list, other_assets_list, fof_nav_list, today_fund_mv_list, today_hedge_mv_list, net_assets_list, net_assets_fixed_list, deposit_interest_list, positions_list], axis=1).sort_index()
            print(total_info)
        self._fof_nav = pd.concat([fof_nav_list, net_assets_fixed_list, shares_list.cumsum(), deposit_interest_list, management_fee_list, custodian_fee_list, administrative_fee_list], axis=1).sort_index().rename_axis('datetime')
        self._fof_nav['share'] = self._fof_nav.share.ffill()
        if not pd.isnull(self._ESTABLISHED_DATE):
            self._fof_nav = self._fof_nav[self._fof_nav.index >= self._ESTABLISHED_DATE]
        self._fof_nav['fof_id'] = fof_id
        self._fof_nav['manager_id'] = manager_id

        dividend_record = self._investor_div.loc[~self._investor_div.index.duplicated(), :].drop_duplicates(subset=['fof_id', 'manager_id'])
        if dividend_record.empty:
            self._fof_nav['acc_net_value'] = self._fof_nav.nav
            self._fof_nav['adjusted_nav'] = self._fof_nav.nav
            self._fof_nav['ta_factor'] = 1
            self._fof_nav['dy_per_share'] = np.nan
        else:
            dividend_cum = (dividend_record.acc_unit_value - dividend_record.net_asset_value)
            self._fof_nav['dy_per_share'] = dividend_cum - dividend_cum.shift(1, fill_value=0).astype('float64')
            dividend_sep = self._fof_nav.dy_per_share.dropna().reindex(self._fof_nav.index, method='ffill')
            self._fof_nav['acc_net_value'] = self._fof_nav.nav.add(dividend_sep, fill_value=0)
            adjusted_nav_and_ta_factor = HedgeFundDataManager.calc_whole_adjusted_net_value(self._fof_nav[['nav', 'acc_net_value']].rename(columns={'nav': 'net_asset_value', 'acc_net_value': 'acc_unit_value'}))
            self._fof_nav['adjusted_nav'], self._fof_nav['ta_factor'] = adjusted_nav_and_ta_factor['adj_nav'], adjusted_nav_and_ta_factor['adj_factor']
        self._fof_nav['ta_factor'] = self._fof_nav.ta_factor.astype('float64')
        self._fof_nav['ret'] = self._fof_nav.adjusted_nav / self._fof_nav.adjusted_nav.array[0] - 1
        self._fof_nav = self._fof_nav.reset_index()

        self._fof_position = pd.concat([positions_list, other_assets_list.rename('other_assets')], axis=1).rename_axis('datetime').reset_index()
        self._fof_position = self._fof_position[self._fof_position.position.notna()]
        self._fof_position['fof_id'] = fof_id
        self._fof_position['manager_id'] = manager_id
        self._fof_position['deposit_in_bank'] = None

        # self._fof_investor_pos = pd.concat(investor_pos_list).rename(columns={'share_changed': 'shares'}).reset_index(drop=True)
        # self._fof_investor_pos = self._fof_investor_pos.groupby(by=['fof_id', 'investor_id'], sort=False).sum().reset_index()
        # self._fof_investor_pos['datetime'] = date
        # self._fof_investor_pos['manager_id'] = manager_id

        self._total_net_assets = net_assets_list.array[-1]
        self._total_shares = shares_list.sum()

        if self._hedge_pos is not None:
            asset_type = pd.Series(HoldingAssetType.HEDGE, index=self._hedge_pos.columns, name='asset_type')
        else:
            asset_type = None
        if self._fund_pos is not None:
            if asset_type is not None:
                asset_type = asset_type.append(pd.Series(HoldingAssetType.MUTUAL, index=self._fund_pos.columns, name='asset_type'))
            else:
                asset_type = pd.Series(HoldingAssetType.MUTUAL, index=self._fund_pos.columns, name='asset_type')
            if self._hedge_pos is not None:
                all_pos = self._hedge_pos.iloc[-1, :].append(self._fund_pos.iloc[-1, :]).rename('total_shares')
            else:
                all_pos = self._fund_pos.iloc[-1, :].rename('total_shares')
        else:
            if self._hedge_pos is not None:
                all_pos = self._hedge_pos.iloc[-1, :].rename('total_shares')
            else:
                all_pos = None
        if all_pos is not None and self._all_latest_nav is not None:
            all_pos = all_pos[all_pos != 0]
            latest_mv = all_pos * self._all_latest_nav
            dividend = self._asset_allocation.loc[self._asset_allocation.event_type.isin([FOFTradeStatus.DIVIDEND_CASH, FOFTradeStatus.DEDUCT_REWARD_AND_DIVIDEND_CASH]), :].pivot(index='datetime', columns='fund_id', values='amount').sum()
            redemptions = self._asset_allocation.loc[self._asset_allocation.event_type == FOFTradeStatus.REDEEM, :].pivot(index='datetime', columns='fund_id', values='share').sum()
            total_ret = latest_mv.add(dividend, fill_value=0).add(redemptions, fill_value=0).sub(self._total_cost)
            total_rr = total_ret / self._total_cost
        else:
            latest_mv = None
            total_ret = None
            total_rr = None

        fof_position_details_list = [self._latest_nav_date.rename('datetime') if self._latest_nav_date is not None else pd.Series(name='datetime'),
                                     asset_type if asset_type is not None else pd.Series(name='asset_type'),
                                     all_pos if all_pos is not None else pd.Series(name='total_shares'),
                                     total_ret.rename('total_ret') if total_ret is not None else pd.Series(name='total_ret'),
                                     total_rr.rename('total_rr') if total_rr is not None else pd.Series(name='total_rr'),
                                     self._total_cost.rename('total_cost') if self._total_cost is not None else pd.Series(name='total_cost'),
                                     self._all_latest_nav.rename('nav') if self._all_latest_nav is not None else pd.Series(name='nav'),
                                     self._all_latest_acc_nav.rename('acc_nav') if self._all_latest_acc_nav is not None else pd.Series(name='acc_nav'),
                                     self._hedge_latest_v_nav.rename('v_nav') if self._hedge_latest_v_nav is not None else pd.Series(name='v_nav'),
                                     latest_mv.rename('latest_mv') if latest_mv is not None else pd.Series(name='latest_mv')]
        self._fof_position_details = self._water_line_and_confirmed_nav.join(fof_position_details_list, how='outer')
        self._fof_position_details = self._fof_position_details[self._fof_position_details.total_shares.notna()]
        self._fof_position_details = self._fof_position_details.rename_axis(index='fund_id').reset_index()
        self._fof_position_details['fof_id'] = fof_id
        self._fof_position_details['manager_id'] = manager_id

        if dump_to_db:
            self.dump_fof_nav_and_pos_to_db(manager_id, fof_id, debug_mode)
        else:
            print(self._fof_nav)

    def dump_fof_nav_and_pos_to_db(self, manager_id: str, fof_id: str, debug_mode=False) -> bool:
        ret = False
        if self._fof_nav is not None and not self._fof_nav.empty:
            renamed_fof_nav = self._fof_nav.rename(columns={'net_asset_fixed': 'mv', 'share': 'volume'})
            now_df = DerivedDataApi().get_fof_nav_calc(manager_id, [fof_id])
            if now_df is not None:
                now_df = now_df.drop(columns=['update_time', 'create_time', 'is_deleted']).astype(renamed_fof_nav.dtypes.to_dict())
                # merge on all columns
                df = renamed_fof_nav.round(6).merge(now_df.round(6), how='left', indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            else:
                df = renamed_fof_nav
            if debug_mode:
                print(df)
            if not df.empty:
                DerivedDataApi().delete_fof_nav_calc(manager_id=manager_id, fof_id=fof_id, date_list=df[(df.manager_id == manager_id) & (df.fof_id == fof_id)].datetime.to_list())
                df.to_sql(FOFNavCalc.__table__.name, DerivedDatabaseConnector().get_engine(), index=False, if_exists='append')
                # self._wechat_bot.send_fof_nav_update(df)
                ret = True
            fof_nav_datas = self._fof_nav.set_index('datetime').sort_index()
            fof_nav = fof_nav_datas.adjusted_nav
            if self._fof_scale is not None and self._fof_redemp is not None:
                mv = (self._fof_scale.share_changed.sum() - self._fof_redemp.share_changed.sum()) * fof_nav_datas.nav.array[-1]
            else:
                mv = np.nan
            res_status = Calculator.get_stat_result(fof_nav.index, fof_nav.array)
            print('[dump_fof_nav_and_pos_to_db] dump nav done')
        else:
            res_status = None
            print('[dump_fof_nav_and_pos_to_db] no nav, should calc it first')

        if self._fof_position is not None:
            now_df = DerivedDataApi().get_fof_position(manager_id, [fof_id])
            if now_df is not None:
                now_df = now_df.drop(columns=['update_time', 'create_time', 'is_deleted']).astype(self._fof_position.dtypes.to_dict())
                # merge on all columns
                df = self._fof_position.round(6).merge(now_df.round(6), how='left', indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            else:
                df = self._fof_position
            if debug_mode:
                print(df)
            if not df.empty:
                DerivedDataApi().delete_fof_position(manager_id=manager_id, fof_id=fof_id, date_list=df[(df.manager_id == manager_id) & (df.fof_id == fof_id)].datetime.to_list())
                df.to_sql(FOFPosition.__table__.name, DerivedDatabaseConnector().get_engine(), index=False, if_exists='append')
            print('[dump_fof_nav_and_pos_to_db] dump position done')
        else:
            print('[dump_fof_nav_and_pos_to_db] no position, should calc it first')

        if self._fof_position_details is not None and not self._fof_position_details.empty:
            now_df = DerivedDataApi().get_fof_position_detail(manager_id, [fof_id])
            if now_df is not None:
                now_df = now_df.drop(columns=['update_time', 'create_time', 'is_deleted']).astype(self._fof_position_details.dtypes.to_dict())
                # merge on all columns
                df = self._fof_position_details.round(4).merge(now_df.round(4), how='left', indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            else:
                df = self._fof_position_details
            if debug_mode:
                print(df)
            if not df.empty:
                DerivedDataApi().delete_fof_position_detail(manager_id=manager_id, fof_id_to_delete=fof_id, fund_id_list=df[(df.manager_id == manager_id) & (df.fof_id == fof_id)].fund_id.to_list())
                df.to_sql(FOFPositionDetail.__table__.name, DerivedDatabaseConnector().get_engine(), index=False, if_exists='append')
            stale_fund_list = set(now_df.fund_id.array).difference(set(self._fof_position_details.fund_id.array))
            print(f'[dump_fof_nav_and_pos_to_db] (manager_id){manager_id} (fof_id){fof_id} (stale_fund_list){stale_fund_list}')
            DerivedDataApi().delete_fof_position_detail(manager_id=manager_id, fof_id_to_delete=fof_id, fund_id_list=stale_fund_list)
            print('[dump_fof_nav_and_pos_to_db] dump position detail done')
        else:
            print('[dump_fof_nav_and_pos_to_db] no position detail, should calc it first')

        investor_return_df = FOFDataManagerLite().get_investor_return(manager_id=manager_id, fof_id=fof_id)
        if investor_return_df is not None and not investor_return_df.empty:
            investor_return_df = investor_return_df.drop(columns=['total_rr']).rename(columns={'latest_mv': 'mv'})
            now_df = FOFDataManagerLite().get_fof_investor_position(manager_id, [fof_id])
            if now_df is not None:
                now_df = now_df.drop(columns=['update_time', 'create_time', 'is_deleted'])
                now_df = now_df.astype(investor_return_df.dtypes.to_dict())
                # merge on all columns
                df = investor_return_df.reset_index().round(4).merge(now_df.round(4), how='left', indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            else:
                df = investor_return_df
            if debug_mode:
                print(df)
            if not df.empty:
                BasicDataApi().delete_fof_investor_position(manager_id=manager_id, fof_id_to_delete=fof_id, investor_id_list=df[(df.manager_id == manager_id) & (df.fof_id == fof_id)].investor_id.to_list())
                df.to_sql(FOFInvestorPosition.__table__.name, BasicDatabaseConnector().get_engine(), index=False, if_exists='append')
            stale_investor_list = set(now_df.investor_id.array).difference(set(investor_return_df.index.array))
            print(f'[dump_fof_nav_and_pos_to_db] (manager_id){manager_id} (fof_id){fof_id} (stale_investor_list){stale_investor_list}')
            BasicDataApi().delete_fof_investor_position(manager_id=manager_id, fof_id_to_delete=fof_id, investor_id_list=stale_investor_list)
            print('[dump_fof_nav_and_pos_to_db] dump investor position done')

            investor_data = investor_return_df[['fof_id', 'amount', 'manager_id']]
            now_df = FOFDataManagerLite().get_fof_investor_data(manager_id, [fof_id])
            if now_df is not None:
                now_df = now_df.drop(columns=['update_time', 'create_time', 'is_deleted'])
                # merge on all columns
                df = investor_data.rename(columns={'amount': 'total_investment'}).reset_index().round(4).merge(now_df.round(4), how='left', indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            else:
                df = investor_data
            if debug_mode:
                print(df)
            if not df.empty:
                DerivedDataApi().delete_fof_investor_data(manager_id=manager_id, fof_id_to_delete=fof_id, investor_id_list=df[(df.manager_id == manager_id) & (df.fof_id == fof_id)].investor_id.to_list())
                df.to_sql(FOFInvestorData.__table__.name, DerivedDatabaseConnector().get_engine(), index=False, if_exists='append')
            print('[dump_fof_nav_and_pos_to_db] dump investor data done')
        else:
            print('[dump_fof_nav_and_pos_to_db] get investor position failed')

        investor_summary_df = FOFDataManagerLite().get_investor_pos_summary(manager_id)
        if investor_summary_df is not None:
            now_df = FOFDataManagerLite().get_fof_investor_position_summary(manager_id)
            if now_df is not None:
                now_df = now_df.drop(columns=['update_time', 'create_time', 'is_deleted']).astype(investor_summary_df.dtypes.to_dict())
                # merge on all columns
                df = investor_summary_df.round(6).merge(now_df.round(6), how='left', indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            else:
                df = investor_summary_df
            if debug_mode:
                print(df)
            if not df.empty:
                for investor_id in df.investor_id.unique():
                    BasicDataApi().delete_fof_investor_position_summary(manager_id=manager_id, investor_id=investor_id, date_list=df[(df.manager_id == manager_id) & (df.investor_id == investor_id)].datetime.to_list())
                df.to_sql(FOFInvestorPositionSummary.__table__.name, BasicDatabaseConnector().get_engine(), index=False, if_exists='append')
            print('[dump_fof_nav_and_pos_to_db] dump investor summary done')
        else:
            print('[dump_fof_nav_and_pos_to_db] get investor summary failed')

        # ret = True
        # if ret:
        #     if res_status is not None:
        #         try:
        #             fof_data = {
        #                 'start_date': res_status.start_date.isoformat(),
        #                 'days': (fof_nav.index.array[-1] - res_status.start_date).days,
        #                 'mv': mv,
        #                 'nav': round(fof_nav_datas.nav.array[-1], 4),
        #                 'total_ret': f'{round(res_status.cumu_ret * 100, 2)}%',
        #                 'sharpe': round(res_status.sharpe, 6),
        #                 'annualized_ret': f'{round(res_status.annualized_ret * 100, 2)}%',
        #                 'mdd': f'{round(res_status.mdd * 100, 2)}%',
        #                 'annualized_vol': f'{round(res_status.annualized_vol * 100, 2)}%',
        #             }
        #             self._wechat_bot.send_fof_info(fof_id, fof_nav.index.array[-1], fof_data)
        #         except Exception as e:
        #             traceback.print_exc()
        #             self._wechat_bot.send_fof_info_failed(fof_id, e)

        # 把 is_calculating 的标记置为false
        Session = sessionmaker(BasicDatabaseConnector().get_engine())
        db_session = Session()
        fof_info_to_set = db_session.query(FOFInfo).filter((FOFInfo.manager_id == manager_id) & (FOFInfo.fof_id == fof_id)).one_or_none()
        # 用托管净值来算以下这些指标 所以这里不用算
        # fof_info_to_set.latest_cal_date = res_status.end_date
        # fof_info_to_set.net_asset_value = float(fof_nav_datas.nav.array[-1]) if not pd.isnull(fof_nav_datas.nav.array[-1]) else None
        # fof_info_to_set.acc_unit_value = float(fof_nav_datas.acc_net_value.array[-1]) if not pd.isnull(fof_nav_datas.acc_net_value.array[-1]) else None
        # fof_info_to_set.adjusted_net_value = float(fof_nav_datas.adjusted_nav.array[-1]) if not pd.isnull(fof_nav_datas.adjusted_nav.array[-1]) else None
        # fof_info_to_set.mdd = float(res_status.mdd) if not pd.isnull(res_status.mdd) else None
        # fof_info_to_set.ret_total = float(res_status.cumu_ret) if not pd.isnull(res_status.cumu_ret) else None
        # fof_info_to_set.ret_ann = float(res_status.annualized_ret) if not pd.isnull(res_status.annualized_ret) else None
        fof_info_to_set.total_volume = float(self._total_shares) if not pd.isnull(self._total_shares) else None
        fof_info_to_set.total_amount = float(self._total_net_assets) if not pd.isnull(self._total_net_assets) else None
        fof_info_to_set.is_calculating = False
        db_session.commit()
        db_session.close()

    def calc_pure_fof_data(self, manager_id: str, fof_id: str, debug_mode=False):
        # 获取FOF份额变化信息
        fof_scale = DerivedDataApi().get_hedge_fund_investor_pur_redemp(manager_id, [fof_id])
        # 客户认购/申购记录
        self._fof_scale = fof_scale[fof_scale.event_type.isin([FOFTradeStatus.SUBSCRIBE, FOFTradeStatus.PURCHASE])].set_index('datetime').sort_index()
        # 客户赎回记录
        self._fof_redemp = fof_scale[fof_scale.event_type.isin([FOFTradeStatus.REDEEM, ])].set_index('datetime').sort_index()
        # fof_nav数据优先级更大
        self._fof_nav = FOFDataManagerLite.get_fof_nav(manager_id, [fof_id])
        self._fof_nav['interest'] = np.nan
        self._fof_nav['management_fee'] = np.nan
        self._fof_nav['custodian_fee'] = np.nan
        self._fof_nav['administrative_fee'] = np.nan
        self._fof_nav['dy_per_share'] = np.nan
        self.dump_fof_nav_and_pos_to_db(manager_id, fof_id, debug_mode)

    def _gather_asset_info_of_fof(self, manager_id, fof_id, fund_list: List[str], v_nav: pd.DataFrame):
        fof_aa = FOFDataManagerLite.get_fof_asset_allocation(manager_id, [fof_id])
        hedge_nav = FOFDataManagerLite.get_fof_nav(manager_id, fund_list)
        trading_day = BasicDataApi().get_trading_day_list(start_date=hedge_nav.datetime.min(), end_date=hedge_nav.datetime.max())
        hedge_info = BasicDataApi().get_fof_info(manager_id, fund_list).set_index('fof_id')
        for fund_id in fund_list:
            try:
                fund_fof_aa = fof_aa.loc[fof_aa.fund_id == fund_id, :]
                pur_sub_aa = fund_fof_aa[fund_fof_aa.event_type.isin([FOFTradeStatus.PURCHASE, FOFTradeStatus.SUBSCRIBE])]
                if pur_sub_aa.empty:
                    continue
                redempt_aa = fund_fof_aa.loc[fund_fof_aa.event_type.isin([FOFTradeStatus.REDEEM, ]), :]
                aa_insentive_info = fund_fof_aa[fund_fof_aa.event_type.isin([FOFTradeStatus.DEDUCT_REWARD, FOFTradeStatus.DEDUCT_REWARD_AND_DIVIDEND_CASH, ])]
                aa_dividend_reinvestment = fund_fof_aa[fund_fof_aa.event_type.isin([FOFTradeStatus.DIVIDEND_VOLUME, FOFTradeStatus.DEDUCT_REWARD_AND_DIVIDEND_VOLUME, ])]
                aa_dividend_cash = fund_fof_aa.loc[fund_fof_aa.event_type.isin([FOFTradeStatus.DIVIDEND_CASH, FOFTradeStatus.DEDUCT_REWARD_AND_DIVIDEND_CASH, ]), :]
                fund_nav = hedge_nav[hedge_nav.fof_id == fund_id]
                fund_auv = fund_nav.set_index('datetime')['adjusted_nav']
                ret_date_with_last_pub = {}
                if fund_auv.size > 2:
                    ret_date_with_last_pub['date'] = fund_auv.index.array[-2]
                    ret_date_with_last_pub['rr'] = f'{round(((fund_auv.array[-1] / fund_auv.array[-2]) - 1) * 100, 2)}%'

                fund_auv = fund_auv.reindex(trading_day[trading_day.datetime.between(fund_auv.index.min(), fund_auv.index.max())].datetime).ffill()
                res_status = Calculator.get_stat_result(fund_auv.index, fund_auv.array)
                total_ret = fund_auv.array[-1] / fund_auv.array[0] - 1
                fund_data = {
                    'start_date': res_status.start_date.isoformat(),
                    'days': (fund_auv.index.array[-1] - res_status.start_date).days,
                    'nav': round(fund_nav.nav.array[-1], 4),
                    'total_ret': f'{round(total_ret * 100, 2)}%',
                    'sharpe': round(res_status.sharpe, 6),
                    'annualized_ret': f'{round(res_status.annualized_ret * 100, 2)}%',
                    'mdd': f'{round(res_status.mdd * 100, 2)}%',
                    'annualized_vol': f'{round(res_status.annualized_vol * 100, 2)}%',
                }

                latest_nav_date = fund_nav.loc[:, 'datetime'].iat[-1]
                Session = sessionmaker(BasicDatabaseConnector().get_engine())
                db_session = Session()
                fof_info_to_set = db_session.query(FOFInfo).filter((FOFInfo.manager_id == manager_id) & (FOFInfo.fof_id == fund_id)).one_or_none()
                fof_info_to_set.latest_cal_date = res_status.end_date
                fof_info_to_set.net_asset_value = float(fund_nav.nav.array[-1]) if not pd.isnull(fund_nav.nav.array[-1]) else None
                fof_info_to_set.acc_unit_value = float(fund_nav.acc_net_value.array[-1]) if not pd.isnull(fund_nav.acc_net_value.array[-1]) else None
                fof_info_to_set.adjusted_net_value = float(fund_nav.adjusted_nav.array[-1]) if not pd.isnull(fund_nav.adjusted_nav.array[-1]) else None
                fof_info_to_set.mdd = float(res_status.mdd) if not pd.isnull(res_status.mdd) else None
                fof_info_to_set.ret_total = float(res_status.cumu_ret) if not pd.isnull(res_status.cumu_ret) else None
                fof_info_to_set.ret_year_to_now = float(res_status.recent_year_ret) if not pd.isnull(res_status.recent_year_ret) else None
                fof_info_to_set.ret_ann = float(res_status.annualized_ret) if not pd.isnull(res_status.annualized_ret) else None
                fof_info_to_set.vol = float(res_status.annualized_vol) if not pd.isnull(res_status.annualized_vol) else None
                fof_info_to_set.sharpe = float(res_status.sharpe) if not pd.isnull(res_status.sharpe) else None
                db_session.commit()
                db_session.close()

                ret_data_with_last_date = {}
                last_date: datetime.date = fund_auv.index.array[-1]
                while last_date == fund_auv.index.array[-1] or last_date.isoweekday() != 5:
                    last_date -= datetime.timedelta(days=1)
                last_date_data = fund_auv[fund_auv.index <= last_date]
                if not last_date_data.empty:
                    last_date_data = last_date_data.iloc[[-1]]
                    ret_data_with_last_date['date'] = last_date_data.index.array[0]
                    ret_data_with_last_date['rr'] = f'{round(((fund_auv.array[-1] / last_date_data.array[0]) - 1) * 100, 2)}%'

                fund_auv = fund_auv[fund_auv.index >= pur_sub_aa.sort_values(by='datetime').datetime.array[0]]
                if not fund_auv.empty:
                    res_status = Calculator.get_stat_result(fund_auv.index, fund_auv.array)
                    mv = (pur_sub_aa.share.sum() - aa_insentive_info.share.sum() + aa_dividend_reinvestment.share.sum() - redempt_aa.share.sum()) * fund_nav.nav.array[-1]
                    real_mv = mv + redempt_aa.amount.sum() + aa_dividend_cash.amount.sum()
                    total_cost = pur_sub_aa.amount.sum()
                    # v_net_value = fund_nav.v_net_value.array[-1]
                    # if not pd.isnull(v_net_value):
                    #     v_net_value = round(float(v_net_value), 4)
                    # else:
                    if v_nav is not None:
                        try:
                            v_net_value = f'{round(v_nav[fund_id].iat[-1], 4)}(计算值)'
                        except KeyError:
                            v_net_value = '/'
                    else:
                        v_net_value = '/'
                    if fund_nav.datetime.array[-1] > pur_sub_aa.datetime.array[-1]:
                        redempt_aa['amount'] = -redempt_aa.amount
                        aa_dividend_cash['amount'] = -aa_dividend_cash.amount
                        total_cf = pd.concat([pur_sub_aa, redempt_aa, aa_dividend_cash]).sort_values(by='datetime')
                        the_xirr = f'{round(xirr(total_cf.amount.to_list() + [-mv], total_cf.datetime.to_list() + [fund_nav.datetime.array[-1]]) * 100, 2)}%'
                    else:
                        the_xirr = np.nan
                    holding_data = {
                        'start_date': res_status.start_date.isoformat(),
                        'days': (res_status.end_date - res_status.start_date).days,
                        'mv': mv,
                        'total_ret': f'{round((real_mv / total_cost - 1) * 100, 2)}%',
                        'v_nav': v_net_value,
                        'avg_cost': round(total_cost / pur_sub_aa.share.sum(), 4),
                        'sharpe': round(res_status.sharpe, 6),
                        'annualized_ret': the_xirr,
                        'mdd': f'{round(res_status.mdd * 100, 2)}%',
                        'annualized_vol': f'{round(res_status.annualized_vol * 100, 2)}%',
                    }
                    self._wechat_bot.send_hedge_fund_info(fof_id, fund_id, hedge_info.at[fund_id, 'desc_name'], latest_nav_date, fund_data, holding_data, ret_data_with_last_date, ret_date_with_last_pub)
            except Exception as e:
                traceback.print_exc()
                self._wechat_bot.send_hedge_fund_info_failed(fof_id, fund_id, e)

    def pull_hedge_fund_nav(self, manager_id: str = None, is_full: bool = False):
        '''
        开始从邮件读取净值

        Parameters
        ----------
        manager_id : str
            管理人ID 如果为默认值(None) 会请求并读取所有管理人的邮箱
        is_full: bool
            是否全量读取邮件 默认为False 表示增量读取每个邮箱的邮件(上次读过的就不再读了)

        Returns/Exceptions
        -------
        throw excepion if failed, or return True if succeed
        '''

        # import os
        import requests

        url = 'https://fof.prism-advisor.com/api/v1/manager_mail/email_task'
        verify_token = 'jisn401f7ac837da42b97f613d789819f37bee6a'

        res = requests.post(
            url=url,
            data={
                'verify_token': verify_token,
            }
        )
        for one in res.json()['data']:
            print(one)
            if one['manager_id'] == 'DEMO001':
                continue
            if manager_id is not None and (one['manager_id'] != manager_id):
                continue
            try:
                fof_nav_r = FOFNAVReader(one)
                nav_df: Optional[pd.DataFrame] = fof_nav_r.read_navs_and_dump_to_db(is_full)
                if nav_df is not None and not nav_df.empty:
                    # adj_nav = FOFDataManagerLite._calc_adjusted_net_value(one['manager_id'], fund_list)
                    for fof_id in nav_df.fof_id.unique():
                        fof_nav_df = nav_df[nav_df.fof_id == fof_id]
                        fof_nav_df = fof_nav_df.set_index('datetime')[['nav', 'acc_net_value']]
                        fof_others_nav = FOFDataManagerLite.get_fof_nav(one['manager_id'], [fof_id])
                        fof_others_nav = fof_others_nav[~fof_others_nav.datetime.isin(fof_nav_df.index.array)]
                        fof_others_nav = fof_others_nav.set_index('datetime')[['nav', 'acc_net_value']]
                        try:
                            adj_nav = HedgeFundDataManager.calc_whole_adjusted_net_value(fof_nav_df.append(fof_others_nav).rename(columns={'nav': 'net_asset_value', 'acc_net_value': 'acc_unit_value'}).sort_index())
                        except Exception:
                            continue
                        adj_nav = adj_nav.reindex(fof_nav_df.index.unique())
                        adj_nav = adj_nav[adj_nav.adj_factor.notna()]
                        if not adj_nav.empty:
                            print(adj_nav)
                            Session = sessionmaker(DerivedDatabaseConnector().get_engine())
                            db_session = Session()
                            for row in adj_nav.itertuples():
                                fof_nav_to_set = db_session.query(FOFNav).filter(FOFNav.manager_id == one['manager_id'], FOFNav.fof_id == fof_id, FOFNav.datetime == row.Index).one_or_none()
                                fof_nav_to_set.ta_factor = row.adj_factor
                                fof_nav_to_set.adjusted_nav = row.adj_nav
                                # fof_nav_to_set.change_rate = row.change_rate
                                db_session.commit()
                            db_session.close()
                    fund_list = list(nav_df.fof_id.unique())
                    # TODO: 这里先 hard code 一下
                    if one['fof_id'] == 'SLW695':
                        v_nav = FOFDataManagerLite._calc_virtual_net_value(one['manager_id'], one['fof_id'], fund_list)
                        self._gather_asset_info_of_fof(one['manager_id'], one['fof_id'], fund_list, v_nav)
            except Exception:
                traceback.print_exc()
                print(f"deal with manager_id {one['manager_id']} failed (fof_id){one['fof_id']}")
        return True

    def calc_all(self, manager_id: str, fof_id: str):
        if not self.pull_hedge_fund_nav(manager_id, fof_id):
            return
        try:
            self.calc_fof_nav(manager_id, fof_id)
        except Exception as e:
            traceback.print_exc()
            self._wechat_bot.send_fof_nav_update_failed(fof_id, f'calc fof nav failed (e){e}')

    @staticmethod
    def _concat_assets_price(main_asset: pd.DataFrame, secondary_asset: pd.Series) -> pd.DataFrame:
        # FIXME 理论上任意资产在任意交易日应该都是有price的 所以这里的判断应该是可以确保之后可以将N种资产的price接起来
        secondary_asset = secondary_asset[secondary_asset.index <= main_asset.datetime.array[0]]
        # 将price对齐
        secondary_asset /= (secondary_asset.array[-1] / main_asset.nav.array[0])
        # 最后一个数据是对齐用的 这里就不需要了
        return pd.concat([main_asset.set_index('datetime'), secondary_asset.iloc[:-1].to_frame('nav')], verify_integrity=True).sort_index().reset_index()

    # 以下是一些获取数据的接口
    @staticmethod
    def get_fof_info(manager_id: str, fof_id: str):
        fof_info = BasicDataApi().get_fof_info(manager_id, [fof_id])
        if fof_id is None:
            return
        return fof_info.sort_values(by=['manager_id', 'fof_id', 'datetime']).iloc[-1]

    @staticmethod
    def get_fof_investor_position(manager_id: str, fof_id: Tuple[str] = ()):
        df = BasicDataApi().get_fof_investor_position(manager_id, fof_id)
        if df is None:
            return
        return df.sort_values(by=['manager_id', 'fof_id', 'investor_id', 'datetime']).drop_duplicates(subset=['manager_id', 'fof_id', 'investor_id'], keep='last')

    @staticmethod
    def get_fof_investor_position_summary(manager_id: str, investor_id: Tuple[str] = ()):
        return BasicDataApi().get_fof_investor_position_summary(manager_id, investor_id)

    @staticmethod
    def get_fof_investor_data(manager_id: str, fof_id: Tuple[str] = ()):
        return DerivedDataApi().get_fof_investor_data(manager_id, fof_id)

    @staticmethod
    def get_fof_asset_allocation(manager_id: str, fof_id: Tuple[str] = ()):
        return BasicDataApi().get_fof_asset_allocation(manager_id, fof_id)

    @staticmethod
    def get_fof_scale_alteration(fof_id: Tuple[str] = ()):
        return BasicDataApi().get_fof_scale_alteration(fof_id)

    @staticmethod
    def get_fof_estimate_fee(fof_id: Tuple[str] = ()):
        return BasicDataApi().get_fof_estimate_fee(fof_id)

    @staticmethod
    def get_fof_estimate_interest(manager_id: str, fof_id: Tuple[str] = ()):
        return BasicDataApi().get_fof_estimate_interest(manager_id, fof_id)

    @staticmethod
    def get_fof_transit_money(fof_id: Tuple[str] = ()):
        return BasicDataApi().get_fof_transit_money(fof_id)

    @staticmethod
    def get_fof_account_statement(manager_id: str, fof_id: Tuple[str] = ()):
        return BasicDataApi().get_fof_account_statement(manager_id, fof_id)

    @staticmethod
    def get_fof_nav(manager_id: str, fof_id_list: Tuple[str], *, ref_index_id: str = '', ref_fund_id: str = '') -> Optional[pd.DataFrame]:
        def _filter_nav_public(x):
            try:
                return x[~x.datetime.between(fof_nav_min_max_date.at[x.fof_id.array[0], 'min_date'], fof_nav_min_max_date.at[x.fof_id.array[0], 'max_date'])]
            except KeyError:
                return x

        fof_nav = DerivedDataApi().get_fof_nav(manager_id, fof_id_list)
        fof_nav_public = FOFDataManagerLite.get_fof_nav_public(manager_id, fof_id_list)
        if fof_nav is None or fof_nav.empty:
            fof_nav = fof_nav_public
        else:
            fof_nav = fof_nav.drop(columns=['update_time', 'create_time', 'is_deleted'])
            if fof_nav_public is not None:
                fof_nav_min_max_date = fof_nav.groupby(by='fof_id', sort=False).apply(lambda x: pd.Series({'min_date': x.datetime.min(), 'max_date': x.datetime.max()}))
                fof_nav_public = fof_nav_public.groupby(by='fof_id', sort=False, group_keys=False).apply(_filter_nav_public)
                fof_nav = pd.concat([fof_nav, fof_nav_public], ignore_index=True).sort_values(by=['manager_id', 'fof_id', 'datetime'])
        if fof_nav is not None and not fof_nav.empty:
            if ref_index_id:
                index_price = BasicDataApi().get_index_price(index_list=[ref_index_id])
                if index_price is None or index_price.empty:
                    print(f'[get_fof_nav] get price of index {ref_index_id} failed (fof_id_list){fof_id_list}')
                    return fof_nav
                return FOFDataManagerLite._concat_assets_price(fof_nav, index_price.drop(columns=['_update_time', 'index_id']).set_index('datetime')['close'])
            elif ref_fund_id:
                fund_nav = BasicDataApi().get_fund_nav_with_date(fund_list=[ref_fund_id])
                if fund_nav is None or fund_nav.empty:
                    print(f'[get_fof_nav] get nav of fund {ref_fund_id} failed (fof_id_list){fof_id_list}')
                    return fof_nav
                return FOFDataManagerLite._concat_assets_price(fof_nav, fund_nav.drop(columns='fund_id').set_index('datetime')['adjusted_net_value'])
        return fof_nav

    @staticmethod
    def get_fof_nav_public(manager_id: str, fof_id: Tuple[str] = ()) -> Optional[pd.DataFrame]:
        fof_nav = DerivedDataApi().get_fof_nav_public(fof_id)
        if fof_nav is None:
            return
        fof_nav['manager_id'] = manager_id
        return fof_nav.drop(columns=['update_time', 'create_time', 'is_deleted'])

    @staticmethod
    def get_hedge_fund_nav(fund_id: Tuple[str] = ()):
        df = BasicDataApi().get_hedge_fund_nav(fund_id)
        if df is None:
            return
        return df.sort_values(by=['fund_id', 'datetime', 'insert_time']).drop_duplicates(subset=['fund_id', 'datetime'], keep='last')

    @staticmethod
    def get_investor_pos_summary(manager_id: str):
        fof_scale_info = DerivedDataApi().get_hedge_fund_investor_pur_redemp(manager_id)
        if fof_scale_info is None:
            return
        fof_nav = FOFDataManagerLite.get_fof_nav(manager_id, list(fof_scale_info.fof_id.unique()))
        if fof_nav is None or fof_nav.empty:
            return
        fof_nav = fof_nav.pivot(index='datetime', columns='fof_id', values='nav')
        fof_nav = fof_nav.reindex(fof_nav.index.union(fof_scale_info.datetime.unique())).rename_axis(index='datetime')
        fof_nav = fof_nav.combine_first(fof_scale_info.drop_duplicates(subset=['datetime', 'fof_id'], keep='last').pivot(index='datetime', columns='fof_id', values='net_asset_value')).sort_index().ffill()

        investor_pos = {}
        for row in fof_scale_info.itertuples(index=False):
            if row.investor_id not in investor_pos:
                investor_pos[row.investor_id] = {
                    'amount': pd.DataFrame(0, index=fof_nav.index.unique(), columns=fof_scale_info[fof_scale_info.investor_id == row.investor_id].fof_id.unique()),
                    'left_amount': pd.DataFrame(0, index=fof_nav.index.unique(), columns=fof_scale_info[fof_scale_info.investor_id == row.investor_id].fof_id.unique()),
                    'share': pd.DataFrame(0, index=fof_nav.index.unique(), columns=fof_scale_info[fof_scale_info.investor_id == row.investor_id].fof_id.unique()),
                    'left_share': pd.DataFrame(0, index=fof_nav.index.unique(), columns=fof_scale_info[fof_scale_info.investor_id == row.investor_id].fof_id.unique()),
                }

            pos = investor_pos[row.investor_id]
            if row.event_type in (FOFTradeStatus.PURCHASE, FOFTradeStatus.SUBSCRIBE):
                assert not pd.isnull(row.share_changed), '!!!'
                pos['share'].loc[pos['share'].index >= row.datetime, row.fof_id] += row.share_changed
                pos['left_share'].loc[pos['left_share'].index >= row.datetime, row.fof_id] += row.share_changed
                pos['amount'].loc[pos['amount'].index >= row.datetime, row.fof_id] += row.purchase_amount
                pos['left_amount'].loc[pos['left_amount'].index >= row.datetime, row.fof_id] += row.purchase_amount
                if row.event_type == FOFTradeStatus.PURCHASE:
                    pos['amount'].loc[pos['amount'].index >= row.datetime, row.fof_id] += row.raising_interest
                    pos['left_amount'].loc[pos['left_amount'].index >= row.datetime, row.fof_id] += row.raising_interest
            elif row.event_type in (FOFTradeStatus.REDEEM, ):
                assert not pd.isnull(row.share_changed), '!!!'
                pos['left_share'].loc[pos['left_share'].index >= row.datetime, row.fof_id] += row.share_changed
                pos['left_amount'].loc[pos['left_amount'].index >= row.datetime, row.fof_id] -= row.redemp_confirmed_amount

        result_df_list = []
        for investor_id, pos in investor_pos.items():
            left_share = pos['left_share'].sort_index()
            mv = (left_share * fof_nav).sum(axis=1)

            share = pos['share'].sort_index()
            redemp = share - left_share
            real_total_mv = mv + (redemp * fof_nav).sum(axis=1)
            amount = pos['amount'].sort_index().sum(axis=1)
            left_amount = pos['left_amount'].sort_index().sum(axis=1)
            total_ret = real_total_mv - amount
            total_rr = total_ret / amount
            share_sum = share.sum(axis=1)
            left_share_sum = left_share.sum(axis=1)
            whole_df = pd.concat([mv.rename('mv'), amount.rename('amount'), left_amount.rename('left_amount'), share_sum.rename('shares'), left_share_sum.rename('left_shares'), total_ret.rename('total_ret'), total_rr.rename('total_rr')], axis=1)
            whole_df['investor_id'] = investor_id
            result_df_list.append(whole_df)
        if not result_df_list:
            return
        df = pd.concat(result_df_list, axis=0).reset_index()
        df = df[df.amount != 0]
        df['manager_id'] = manager_id
        return df

    @staticmethod
    def get_investor_return(manager_id: str, fof_id: str, *, investor_id_list: Tuple[str] = (), start_date: Optional[datetime.date] = None, end_date: Optional[datetime.date] = None) -> Optional[pd.DataFrame]:
        '''计算投资者收益'''
        fof_nav = FOFDataManagerLite.get_fof_nav(manager_id, [fof_id])
        if fof_nav is None:
            return
        fof_nav = fof_nav.set_index('datetime')
        if start_date:
            fof_nav = fof_nav[fof_nav.index >= start_date]
        if end_date:
            fof_nav = fof_nav[fof_nav.index <= end_date]
        if fof_nav.empty:
            return
        fof_nav = fof_nav.reindex(pd.date_range(fof_nav.index.array[0], fof_nav.index.array[-1]).date)

        investor_pur_redemp = DerivedDataApi().get_hedge_fund_investor_pur_redemp(manager_id, [fof_id])
        if investor_pur_redemp is None:
            return
        investor_pur_redemp = investor_pur_redemp.sort_values(by='datetime')
        investor_div_carry = DerivedDataApi().get_hedge_fund_investor_div_carry(manager_id, [fof_id])
        if investor_div_carry is None:
            return
        investor_div_carry = investor_div_carry.sort_values(by='datetime')
        investor_mvs = defaultdict(list)
        for row in investor_pur_redemp.itertuples(index=False):
            if investor_id_list and row.investor_id not in investor_id_list:
                continue
            if row.event_type in (FOFTradeStatus.PURCHASE, FOFTradeStatus.SUBSCRIBE):
                if start_date is not None:
                    actual_start_date = max(row.datetime, start_date)
                else:
                    actual_start_date = row.datetime
                try:
                    init_mv = fof_nav.at[actual_start_date, 'nav'] * row.share_changed
                except KeyError:
                    init_mv = row.share_changed
                the_amount = row.purchase_amount
                if row.event_type == FOFTradeStatus.PURCHASE:
                    the_amount += row.raising_interest
                investor_mvs[row.investor_id].append({
                    'trade_ids': [row.id],
                    'start_date': actual_start_date,
                    'amount': the_amount,
                    'left_amount': the_amount,
                    'share': row.share_changed,
                    'left_share': row.share_changed,
                    'share_after_trans': row.share_after_trans,
                    'init_mv': init_mv,
                    'water_line': row.acc_unit_value,
                    'redemp_confirmed_amount': 0,
                    'dividend_cash': 0,
                    'type': 1,
                })
            elif row.event_type in (FOFTradeStatus.REDEEM, ):
                share_redemp = abs(row.share_changed)
                for one in investor_mvs[row.investor_id]:
                    if one['left_share'] >= share_redemp:
                        one['left_share'] -= share_redemp
                        one['trade_ids'].append(row.id)
                        # FIXME: 在这里记一下赎回金额
                        one['redemp_confirmed_amount'] += row.redemp_confirmed_amount
                        one['left_amount'] -= row.redemp_confirmed_amount
                        one['share_after_trans'] = row.share_after_trans
                        one['start_date'] = row.datetime
                        break
                    share_redemp -= one['left_share']
                    one['left_share'] = 0
                    one['left_amount'] = 0
                    one['trade_ids'].append(row.id)
                    one['share_after_trans'] = row.share_after_trans
                    one['start_date'] = row.datetime

        for row in investor_div_carry.itertuples(index=False):
            if investor_id_list and row.investor_id not in investor_id_list:
                continue
            if row.event_type in (FOFTradeStatus.DIVIDEND_VOLUME, ):
                assert row.investor_id in investor_mvs, '!!!'
                if row.share_changed > 0:
                    try:
                        init_mv = fof_nav.at[row.datetime, 'nav'] * row.share_changed
                    except KeyError:
                        init_mv = row.share_changed
                    investor_mvs[row.investor_id].append({
                        'trade_ids': [row.id],
                        'start_date': row.datetime,
                        'amount': 0,
                        'left_amount': 0,
                        'share': row.share_changed,
                        'left_share': row.share_changed,
                        'share_after_trans': row.share_after_trans,
                        'init_mv': init_mv,
                        'water_line': row.acc_unit_value,
                        'redemp_confirmed_amount': 0,
                        'dividend_cash': 0,
                        'type': 2,
                    })
            elif row.event_type in (FOFTradeStatus.DIVIDEND_CASH, ):
                assert row.investor_id in investor_mvs, '!!!'
                for one in investor_mvs[row.investor_id]:
                    # FIXME: 先找个地方存一下现金分红
                    one['dividend_cash'] += row.cash_dividend
                    break
            elif row.event_type in (FOFTradeStatus.DEDUCT_REWARD, ):
                assert row.investor_id in investor_mvs, '!!!'
                investor_mvs[row.investor_id].append({
                    'trade_ids': [row.id],
                    'start_date': row.datetime,
                    'amount': 0,
                    'left_amount': 0,
                    'share': row.share_changed,
                    'left_share': row.share_changed,
                    'share_after_trans': row.share_after_trans,
                    'init_mv': 0,
                    'water_line': row.acc_unit_value,
                    'redemp_confirmed_amount': 0,
                    'dividend_cash': 0,
                    'type': 2,
                })

        investor_returns = {}
        latest_nav = fof_nav.nav.array[-1]
        for investor_id, datas in investor_mvs.items():
            datas = pd.DataFrame(datas).sort_values(by='start_date')
            # TODO: hard code 0.2 and 4 and the second param should be acc nav
            # v_nav = FOFDataManagerLite._do_calc_v_net_value_by_mv(latest_nav, datas.left_share, latest_nav, datas.water_line, 0.2, 4)
            # 这里确保单取的几个Series的顺序不会发生任何变化 这样直接运算才是OK的
            mv = latest_nav * datas.loc[datas.type == 1, 'left_share']
            total_share = datas.share_after_trans.array[-1]
            latest_mv = latest_nav * total_share
            avg_v_nav = np.nan
            amount_sum = datas.amount.sum()
            if not math.isclose(amount_sum, 0):
                total_ret = latest_mv + datas.redemp_confirmed_amount.sum() + datas.dividend_cash.sum() - amount_sum
                total_rr = total_ret / amount_sum
            else:
                total_ret = np.nan
                total_rr = np.nan
            if not math.isclose(total_share, 0):
                avg_nav_cost = datas.left_amount.sum() / total_share
            else:
                avg_nav_cost = np.nan
            investor_returns[investor_id] = {
                'datetime': fof_nav.index.array[-1], 'manager_id': manager_id, 'fof_id': fof_id, 'v_nav': avg_v_nav, 'cost_nav': avg_nav_cost, 'total_ret': total_ret, 'total_rr': total_rr, 'amount': amount_sum, 'shares': total_share,
                'latest_mv': latest_mv, 'details': datas.loc[datas.type == 1, ['trade_ids', 'amount', 'left_share', 'water_line']].rename(columns={'left_share': 'share'}).join(mv.rename('mv')).to_json(orient='records')
            }
        return pd.DataFrame.from_dict(investor_returns, orient='index').rename_axis(index='investor_id')

    @staticmethod
    def calc_share_by_subscription_amount(manager_id: str, fof_id: str, amount: float, confirmed_date: datetime.date) -> Optional[float]:
        '''根据金额和日期计算申购fof产品的确认份额'''

        fof_info: Optional[pd.DataFrame] = FOFDataManagerLite.get_fof_info(manager_id, [fof_id])
        if fof_info is None:
            return
        fof_nav = FOFDataManagerLite.get_fof_nav(manager_id, [fof_id])
        if fof_nav is None:
            return
        try:
            # 用申购金额除以确认日的净值以得到份额
            return amount / (1 + fof_info.subscription_fee) / fof_nav.loc[fof_nav.datetime == confirmed_date, 'nav'].array[-1]
        except KeyError:
            return

    @staticmethod
    def remove_hedge_nav_data(fund_id: str, start_date: str = '', end_date: str = ''):
        BasicDataApi().delete_hedge_fund_nav(fund_id_to_delete=fund_id, start_date=start_date, end_date=end_date)

    @staticmethod
    def upload_hedge_nav_data(datas: bytes, file_name: str, hedge_fund_id: str) -> bool:
        '''上传单个私募基金净值数据'''
        '''目前支持：私募排排网 朝阳永续'''

        if not datas:
            return True

        try:
            # 下边这个分支是从私募排排网上多只私募基金净值数据的文件中读取数据
            # if file_type == 'csv':
            #     hedge_fund_info = BasicDataApi().get_fof_nav(datas['manager_id'])
            #     if hedge_fund_info is None:
            #         return
            #     fund_name_map = hedge_fund_info.set_index('desc_name')['fof_id'].to_dict()
            #     fund_name_map['日期'] = 'datetime'
            #     df = pd.read_csv(io.BytesIO(datas), encoding='gbk')
            #     lacked_map = set(df.columns.array) - set(fund_name_map.keys())
            #     assert not lacked_map, f'lacked hedge fund name map {lacked_map}'
            #     df = df.rename(columns=fund_name_map).set_index('datetime').rename_axis(columns='fund_id')
            #     df = df.stack().to_frame('adjusted_net_value').reset_index()
            #     # validate = 'many_to_many'
            try:
                if '产品详情-历史净值' in file_name:
                    df = pd.read_excel(io.BytesIO(datas), usecols=['净值日期', '单位净值', '累计净值', '复权累计净值'], na_values='--')
                    df = df.rename(columns=HedgeFundNAVReader.COLUMNS_DICT)
                    df['fund_id'] = hedge_fund_id
                elif '业绩走势' in file_name:
                    df = pd.read_excel(io.BytesIO(datas), usecols=['净值日期', '净值(分红再投)'], na_values='--')
                    df = df.rename(columns=HedgeFundNAVReader.COLUMNS_DICT)
                    df['fund_id'] = hedge_fund_id
                else:
                    assert False
            except Exception:
                try:
                    try:
                        df = pd.read_excel(io.BytesIO(datas), na_values='--')
                    except Exception:
                        df = pd.read_csv(io.BytesIO(datas), na_values='--')
                except Exception:
                    print(f'[upload_hedge_nav_data] can not read data from this file (file name){file_name} (fund_id){hedge_fund_id}')
                    return False
                else:
                    df = df.rename(columns=HedgeFundNAVReader.COLUMNS_DICT)
                    df['fof_id'] = hedge_fund_id

            df = df[df.drop(columns=['fof_id', 'datetime']).notna().any(axis=1)]
            now_df = BasicDataApi().get_hedge_fund_nav([hedge_fund_id])
            if now_df is not None:
                now_df = now_df.drop(columns=['update_time', 'create_time', 'insert_time', 'is_deleted', 'calc_date']).astype({'net_asset_value': 'float64', 'acc_unit_value': 'float64', 'v_net_value': 'float64', 'adjusted_net_value': 'float64'})
                df = df.reindex(columns=now_df.columns).astype(now_df.dtypes.to_dict())
                df['datetime'] = pd.to_datetime(df.datetime, infer_datetime_format=True).dt.date
                # merge on all columns
                df = df.round(6).merge(now_df, how='left', indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            if not df.empty:
                df['insert_time'] = datetime.datetime.now()
                print(f'[upload_hedge_nav_data] try to insert data to db (df){df}')
                df.to_sql(HedgeFundNAV.__table__.name, BasicDatabaseConnector().get_engine(), index=False, if_exists='append')
            else:
                print(f'[upload_hedge_nav_data] empty df, nothing to do')
            return True
        except Exception as e:
            print(f'[upload_hedge_nav_data] failed, got exception {e} (file_name){file_name} (hedge_fund_id){hedge_fund_id}')
            return False

    @staticmethod
    def _do_backtest(fund_nav_ffilled, wgts):
        INITIAL_CASH = 10000000
        INIT_NAV = 1
        UNIT_TOTAL = INITIAL_CASH / INIT_NAV

        positions = []
        mvs = []
        navs = []
        # 初始市值
        mv = INITIAL_CASH
        for index, s in fund_nav_ffilled.iterrows():
            s = s[s.notna()]
            if positions:
                # 最新市值
                mv = (positions[-1][1] * s).sum()

            if not positions or (s.size != positions[-1][1].size):
                # 调仓
                new_wgts = wgts.loc[s.index]
                # 各标的目标权重
                new_wgts /= new_wgts.sum()
                # 新的各标的持仓份数
                shares = (mv * new_wgts) / s
                # shares = (mv / s.size) / s
                positions.append((index, shares))

            nav = mv / UNIT_TOTAL
            mvs.append(mv)
            navs.append(nav)
        return positions, mvs, navs

    @staticmethod
    def virtual_backtest(manager_id: str, hedge_fund_ids: Dict[str, float], ref_fund_ids: Dict[str, str], start_date: datetime.date, end_date: Optional[datetime.date] = None, benchmark_ids: Tuple[str] = ()) -> Optional[Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, List[str]]]:
        '''
        对私募基金做虚拟回测

        Parameters
        ----------
        hedge_fund_ids : Dict[str, float]
            私募基金ID列表
        ref_fund_ids : Dict[str, str]
            ref基金ID列表
        start_date: datetime.date
            回测起始日期
        end_date: datetime.date
            回测终止日期
        benchmark_ids : Tuple[str]
            指数ID列表

        Returns
        -------
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, List[str]]
        '''

        DEFAULT_INCENTIVE_TYPE = '1'
        DEFAULT_INCENTIVE_RATIO = 0.2
        DEFAULT_DECIMAL = 4

        try:
            if end_date is None:
                end_date = datetime.date.today()
            # 获取必要的私募基金信息
            fund_info = BasicDataApi().get_fof_info(manager_id, list(hedge_fund_ids.keys()))
            if fund_info is None:
                return
            fund_info = fund_info.set_index('fof_id')

            # 统计一下需要替代的基金的ref ids
            funds_added = [ref for fund, ref in ref_fund_ids.items() if fund in hedge_fund_ids.keys()]
            # 获取私募基金净值数据
            fund_nav = FOFDataManagerLite.get_fof_nav(manager_id, list(hedge_fund_ids.keys()) + funds_added)
            if fund_nav is None:
                return

            # 这里首选复权净值
            fund_nav = fund_nav[(fund_nav.fof_id != 'SR9762') | (fund_nav.datetime >= pd.to_datetime('2020-07-01', infer_datetime_format=True).date())]
            adj_nav = fund_nav.pivot(index='datetime', columns='fof_id', values='adjusted_nav')
            # 处理ref fund
            for fund, ref in ref_fund_ids.items():
                org_nav = adj_nav[fund]
                org_nav = org_nav.ffill().dropna().sort_index()

                # 取出来ref nav在org fund成立之前的净值
                ref_nav = adj_nav.sort_index().loc[adj_nav.index <= org_nav.index.array[0], ref].ffill()
                org_nav *= ref_nav.array[-1]
                adj_nav[fund] = pd.concat([ref_nav.iloc[:-1], org_nav])
            # 最后再删掉所有的ref fund列
            adj_nav = adj_nav.loc[:, set(adj_nav.columns.array) - set(ref_fund_ids.values())]

            # 去掉全是nan的列
            valid_adj_nav = adj_nav.loc[:, adj_nav.notna().any(axis=0)]
            # 计算缺少的列
            adj_nav_lacked = set(adj_nav.columns.array) - set(valid_adj_nav.columns.array)
            if adj_nav_lacked:
                # TODO 如果某只基金完全没有复权净值 需要用累计净值来计算
                # FIXME 这里不能直接用数据库里存的虚拟净值 因为这个是邮件里发过来的单位净值虚拟后净值 而上边算出来的是复权净值虚拟后净值
                acc_nav = fund_nav[fund_nav.fof_id.isin(adj_nav_lacked)].pivot(index='datetime', columns='fof_id', values='acc_net_value')
                adj_nav = adj_nav.drop(columns=adj_nav_lacked).join(acc_nav, how='outer')
            fund_info = fund_info.reindex(adj_nav.columns)
            lacked_funds = list(set(hedge_fund_ids.keys()) - set(adj_nav.columns.array))
            for one in lacked_funds:
                del hedge_fund_ids[one]

            # 计算虚拟净值
            FOFDataManagerLite._adj_nav = adj_nav
            fund_nav = FOFDataManagerLite._do_calc_v_net_value_by_nav(adj_nav, adj_nav, adj_nav.loc[adj_nav.index >= start_date, :].bfill().iloc[0, :], fund_info.incentive_fee_type.fillna(DEFAULT_INCENTIVE_TYPE), fund_info.incentive_fee_str.fillna(DEFAULT_INCENTIVE_RATIO), fund_info.v_nav_decimals.fillna(DEFAULT_DECIMAL))
            FOFDataManagerLite._v_nav = fund_nav

            trading_day = BasicDataApi().get_trading_day_list(start_date=fund_nav.index.array[0], end_date=fund_nav.index.array[-1])
            trading_day = trading_day[trading_day.datetime.between(start_date, end_date)]
            fund_nav_ffilled = fund_nav.reindex(trading_day.datetime).ffill()
            fund_nav_ffilled = fund_nav_ffilled.loc[:, fund_nav_ffilled.notna().any(axis=0)].loc[fund_nav_ffilled.notna().any(axis=1), :]
            FOFDataManagerLite._nav_filled = fund_nav_ffilled

            adj_nav_ffilled = adj_nav.reindex(trading_day.datetime).ffill()
            adj_nav_ffilled = adj_nav_ffilled.loc[:, adj_nav_ffilled.notna().any(axis=0)].loc[adj_nav_ffilled.notna().any(axis=1), :]
            FOFDataManagerLite._adj_nav_filled = adj_nav_ffilled

            wgts = pd.Series(hedge_fund_ids)
            positions, mvs, navs = FOFDataManagerLite._do_backtest(fund_nav_ffilled, wgts)
            FOFDataManagerLite._positions = positions
            fof_nav = pd.Series(navs, index=fund_nav_ffilled.index, name='fof_nav')

            positions_not_v, mvs_not_v, navs_not_v = FOFDataManagerLite._do_backtest(adj_nav_ffilled, wgts)
            FOFDataManagerLite._positions_not_v = positions_not_v
            fof_nav_not_v = pd.Series(navs_not_v, index=adj_nav_ffilled.index, name='fof_nav_no_v')
            FOFDataManagerLite._fof_nav_not_v = fof_nav_not_v

            indicators = []
            if benchmark_ids:
                benchmarks = BasicDataApi().get_index_price(index_list=benchmark_ids)
                benchmarks = benchmarks.pivot(index='datetime', columns='index_id', values='close')
                benchmarks = benchmarks.loc[start_date:end_date, :]
                fof_with_benchmark = [benchmarks[one] for one in benchmarks.columns.array]
            else:
                fof_with_benchmark = []
            fof_with_benchmark.extend([fof_nav, fof_nav_not_v])
            for data in fof_with_benchmark:
                data = data[data.notna()]
                # data.index = pd.to_datetime(data.index).date
                res_status = Calculator.get_stat_result(data.index, data.array)
                data.index = pd.to_datetime(data.index)
                to_calc_win_rate = data.resample(rule='1W').last().diff()
                weekly_win_rate = (to_calc_win_rate > 0).astype('int').sum() / to_calc_win_rate.size
                indicators.append({
                    'name': data.name,
                    'days': (data.index.array[-1] - data.index.array[0]).days,
                    'total_ret': (data[-1] / data[0]) - 1,
                    'annualized_ret': res_status.annualized_ret,
                    'annualized_vol': res_status.annualized_vol,
                    'weekly_win_rate': weekly_win_rate,
                    'mdd': res_status.mdd,
                    'sharpe': res_status.sharpe,
                })
            fof_indicators = pd.DataFrame(indicators)
            if len(fof_with_benchmark) > 1:
                fof_with_benchmarks = pd.concat(fof_with_benchmark, axis=1)
                fof_with_benchmarks = fof_with_benchmarks[fof_with_benchmarks.fof_nav.notna() & fof_with_benchmarks.fof_nav_no_v.notna()]
                fof_with_benchmarks = fof_with_benchmarks.set_index(pd.to_datetime(fof_with_benchmarks.index, infer_datetime_format=True))
                fof_with_benchmarks = fof_with_benchmarks.resample('1W').last().ffill()
                fof_with_benchmarks = fof_with_benchmarks / fof_with_benchmarks.iloc[0, :]
                fof_with_benchmarks = fof_with_benchmarks.set_axis(fof_with_benchmarks.index.date, axis=0)
            else:
                fof_with_benchmarks = None
            return fof_nav, fof_indicators, fof_with_benchmarks, lacked_funds
        except Exception as e:
            print(f'[virtual_backtest] failed, got exception {e} (hedge_fund_ids){hedge_fund_ids} (start_date){start_date} (end_date){end_date} (benchmark_ids){benchmark_ids}')
            traceback.print_exc()
            return

    @staticmethod
    def virtual_backtest_sub(manager_id: str, hedge_fund_ids: Dict[str, str], start_date: datetime.date, end_date: Optional[datetime.date] = None) -> Optional[Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, List[str]]]:
        DEFAULT_INCENTIVE_RATIO = 0.2
        DEFAULT_DECIMAL = 4
        INIT_NAV = 1

        try:
            if end_date is None:
                end_date = datetime.date.today()
            # 获取必要的私募基金信息
            fund_info = BasicDataApi().get_fof_info(manager_id, list(hedge_fund_ids.keys()))
            if fund_info is None:
                return
            fund_info = fund_info.set_index('fof_id')

            # 获取私募基金净值数据
            fund_nav = FOFDataManagerLite.get_fof_nav(manager_id, list(hedge_fund_ids.keys()))
            if fund_nav is None:
                return
            # 这里首选复权净值
            adj_nav = fund_nav.pivot(index='datetime', columns='fof_id', values='adjusted_nav')
            # 去掉全是nan的列
            valid_adj_nav = adj_nav.loc[:, adj_nav.notna().any(axis=0)]
            # 计算缺少的列
            adj_nav_lacked = set(adj_nav.columns.array) - set(valid_adj_nav.columns.array)
            if adj_nav_lacked:
                # TODO 如果某只基金完全没有复权净值 需要用累计净值来计算
                # FIXME 这里不能直接用数据库里存的虚拟净值 因为这个是邮件里发过来的单位净值虚拟后净值 而上边算出来的是复权净值虚拟后净值
                acc_nav = fund_nav[fund_nav.fof_id.isin(adj_nav_lacked)].pivot(index='datetime', columns='fof_id', values='acc_net_value')
                adj_nav = adj_nav.join(acc_nav, how='outer')
            fund_info = fund_info.reindex(adj_nav.columns)
            lacked_funds = list(set(hedge_fund_ids.keys()) - set(adj_nav.columns.array))
            for one in lacked_funds:
                del hedge_fund_ids[one]

            # 计算虚拟净值
            # TODO: water_line不在这里了 需要改一下的
            fund_nav = FOFDataManagerLite._do_calc_v_net_value_by_nav(adj_nav, adj_nav, fund_info.water_line.fillna(INIT_NAV), fund_info.incentive_fee_type.fillna(DEFAULT_INCENTIVE_TYPE), fund_info.incentive_fee_str.fillna(DEFAULT_INCENTIVE_RATIO), fund_info.v_nav_decimals.fillna(DEFAULT_DECIMAL))

            trading_day = BasicDataApi().get_trading_day_list(start_date=fund_nav.index.array[0], end_date=fund_nav.index.array[-1])
            trading_day = trading_day[trading_day.datetime.between(start_date, end_date)]
            fund_nav_ffilled = fund_nav.reindex(trading_day.datetime).ffill()
            fund_nav_ffilled = fund_nav_ffilled.loc[:, fund_nav_ffilled.notna().any(axis=0)].loc[fund_nav_ffilled.notna().any(axis=1), :]

            benchmarks = BasicDataApi().get_index_price(index_list=list(set(hedge_fund_ids.values())))
            benchmarks = benchmarks.pivot(index='datetime', columns='index_id', values='close')
            benchmarks = benchmarks.loc[start_date:end_date, :]

            indicators = []
            for col in fund_nav_ffilled.columns.array:
                temp_nav = fund_nav_ffilled[col].dropna()
                the_benchmark = benchmarks[hedge_fund_ids[col]]
                the_benchmark = the_benchmark.reindex(temp_nav.index).ffill()
                res_status = Calculator.get_benchmark_stat_result(dates=temp_nav.index, values=temp_nav.array, benchmark_values=the_benchmark)
                indicators.append({
                    'fund_name': temp_nav.name,
                    'days': (temp_nav.index.array[-1] - temp_nav.index.array[0]).days,
                    'total_ret': (temp_nav[-1] / temp_nav[0]) - 1,
                    'annualized_ret': res_status.annualized_ret,
                    'annualized_vol': res_status.annualized_vol,
                    'mdd': res_status.mdd,
                    'sharpe': res_status.sharpe,
                    'ir': res_status.ir,
                })
            fund_nav_ffilled = fund_nav_ffilled.set_index(pd.to_datetime(fund_nav_ffilled.index, infer_datetime_format=True))
            fund_nav_ffilled = fund_nav_ffilled.resample('1W').last().ffill()
            fund_nav_ffilled = fund_nav_ffilled / fund_nav_ffilled.iloc[0, :]
            fund_nav_ffilled = fund_nav_ffilled.set_axis(fund_nav_ffilled.index.date, axis=0)
            return pd.DataFrame(indicators), fund_nav_ffilled
        except KeyError as e:
            print(f'[virtual_backtest] failed, got exception {e} (hedge_fund_ids){hedge_fund_ids} (start_date){start_date} (end_date){end_date}')
            return

    def _notify_fund_stats(self, manager_id: str, fof_id: str, fund_list: List[str]):
        # 手工发一个通知消息
        v_nav = FOFDataManagerLite._calc_virtual_net_value(manager_id, fof_id, fund_list)
        self._gather_asset_info_of_fof(manager_id, fof_id, fund_list, v_nav)


if __name__ == "__main__":
    MANAGER_ID = 'py1'
    FOF_ID = 'SLW695'

    fof_dm = FOFDataManagerLite()
    # fof_dm.pull_hedge_fund_nav(manager_id=MANAGER_ID, is_full=True)
    fof_dm.calc_fof_nav(manager_id=MANAGER_ID, fof_id=FOF_ID, dump_to_db=True, debug_mode=True)
    # fof_dm.calc_all(manager_id=MANAGER_ID, fof_id=FOF_ID)
    # fund_list = ['SNH765']
    # fof_dm._notify_fund_stats(manager_id=MANAGER_ID, fof_id=FOF_ID, fund_list=fund_list)
