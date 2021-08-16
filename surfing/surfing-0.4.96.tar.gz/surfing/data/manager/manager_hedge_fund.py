
from typing import Dict, Any, Tuple, List
import math
import json
import io
import re
import datetime

import numpy as np
import pandas as pd

from sqlalchemy.orm import sessionmaker

from ...util.singleton import Singleton
from ...constant import FOFTradeStatus, DividendCalcMethod, EMailParserType, FOFIncentiveFeeMode
from ..view.derived_models import HedgeFundInvestorPurAndRedemp, HedgeFundInvestorDivAndCarry, HedgeFundCustodianData
from ..wrapper.mysql import DerivedDatabaseConnector
from ..api.basic import BasicDataApi
from ..api.derived import DerivedDataApi
from ..nav_reader.parser_runner import ParserRunner


class HedgeFundDataManager(metaclass=Singleton):

    def __init__(self):
        pass

    def _get_total_share(self, manager_id: str, fof_id: str, date: str, investor_id: str = '', exclude1: List[int] = [], exclude2: List[str] = []) -> Tuple[float, pd.DataFrame]:
        date = pd.to_datetime(date, infer_datetime_format=True).date()

        part1 = DerivedDataApi().get_hedge_fund_investor_pur_redemp(manager_id, [fof_id])
        assert part1 is not None, f'get pur redemp info failed (fof_id){fof_id} (manager_id){manager_id}'
        part1 = part1[part1.datetime <= date]
        part1 = part1[~part1.id.isin(exclude1)]
        part1_total_share = part1.share_changed.sum()
        if investor_id:
            part1 = part1.loc[part1.investor_id == investor_id, :]

        part2 = DerivedDataApi().get_hedge_fund_investor_div_carry(manager_id, [fof_id])
        assert part2 is not None, f'get div carry info failed (fof_id){fof_id} (manager_id){manager_id}'
        part2 = part2[part2.datetime <= date]
        part2 = part2[~part2.id.isin(exclude2)]
        part2_total_share = part2.share_changed.sum()
        if investor_id:
            part2 = part2.loc[part2.investor_id == investor_id, :]

        total_share = part1_total_share + part2_total_share
        share_separate = part1[['investor_id', 'share_changed']].groupby(by='investor_id', sort=False).sum().add(part2[['investor_id', 'share_changed']].groupby(by='investor_id', sort=False).sum(), fill_value=0)
        return total_share, share_separate

    def _refresh_datas_after_updating(self, manager_id: str, fof_id: str, investor_id: str, datetime):
        datetime: datetime.date = pd.to_datetime(datetime, infer_datetime_format=True).date()

        part1 = DerivedDataApi().get_hedge_fund_investor_pur_redemp(manager_id, [fof_id])
        assert part1 is not None, f'get pur redemp info failed (fof_id){fof_id} (manager_id){manager_id}'
        part1 = part1[part1.investor_id == investor_id].sort_values(by='datetime')

        part2 = DerivedDataApi().get_hedge_fund_investor_div_carry(manager_id, [fof_id])
        assert part2 is not None, f'get div carry info failed (fof_id){fof_id} (manager_id){manager_id}'
        part2 = part2[part2.investor_id == investor_id]

        total = pd.concat([part1, part2]).sort_values(by='datetime')
        total = total[total.datetime <= datetime]
        if total.empty:
            last_valid_share: float = 0
        else:
            last_valid_share: float = round(total.iloc[-1, :].share_after_trans, 2)

        part1_shares = part1.loc[part1.datetime > datetime, :]
        if not part1_shares.empty:
            part1_shares = part1_shares.set_index('datetime')
            part2_shares = part2.loc[part2.datetime > datetime, :]
            if not part2_shares.empty:
                part2_shares = part2_shares.set_index('datetime')
                part2_shares = part2_shares.reindex(part1_shares.index.union(part2_shares.index), method='ffill').reindex(part1_shares.index)
                part1_shares['share_changed'] = part1_shares.share_changed.add(part2_shares.share_changed, fill_value=0)

            to_refresh = part1_shares.set_index('id').share_changed.cumsum().round(2) + last_valid_share

            Session = sessionmaker(DerivedDatabaseConnector().get_engine())
            db_session = Session()
            for row in db_session.query(HedgeFundInvestorPurAndRedemp).filter(
                HedgeFundInvestorPurAndRedemp.manager_id == manager_id,
                HedgeFundInvestorPurAndRedemp.fof_id == fof_id,
                HedgeFundInvestorPurAndRedemp.investor_id == investor_id,
                HedgeFundInvestorPurAndRedemp.datetime > datetime,
            ).all():
                row.share_after_trans = float(to_refresh.at[row.id])
            db_session.commit()
            db_session.close()

    def _calc_share_details(self, fof_info, manager_id: str, fof_id: str, investor_id: str, date: str) -> List[Dict[str, Any]]:
        date = pd.to_datetime(date, infer_datetime_format=True).date()

        part1 = DerivedDataApi().get_hedge_fund_investor_pur_redemp(manager_id, [fof_id])
        assert part1 is not None, f'get pur redemp info failed (fof_id){fof_id} (manager_id){manager_id}'
        part1 = part1.loc[part1.investor_id == investor_id, ['datetime', 'event_type', 'share_changed', 'net_asset_value', 'acc_unit_value', 'water_line']]

        part2 = DerivedDataApi().get_hedge_fund_investor_div_carry(manager_id, [fof_id])
        assert part2 is not None, f'get div carry info failed (fof_id){fof_id} (manager_id){manager_id}'
        part2 = part2.loc[(part2.investor_id == investor_id) & (part2.event_type.isin([FOFTradeStatus.DIVIDEND_VOLUME, FOFTradeStatus.DEDUCT_REWARD])), ['datetime', 'event_type', 'share_changed', 'net_asset_value', 'acc_unit_value', 'water_line']]

        total = pd.concat([part1, part2]).sort_values(by='datetime')
        total = total[total.datetime <= date]
        share_details = []
        last_water_line = 1
        for row in total.itertuples(index=False):
            if row.event_type in (FOFTradeStatus.PURCHASE, FOFTradeStatus.SUBSCRIBE, FOFTradeStatus.DIVIDEND_VOLUME):
                share_details.append({'datetime': row.datetime, 'share': row.share_changed, 'water_line': row.water_line, 'acc_unit_value': row.acc_unit_value})
            elif row.event_type == FOFTradeStatus.REDEEM:
                share_changed = abs(row.share_changed)
                for one in share_details:
                    assert share_changed > 0, f'invalid share_changed {share_changed} (manager_id){manager_id} (fof_id){fof_id} (investor_id){investor_id}'
                    if (one['share'] > share_changed) or math.isclose(one['share'], share_changed, rel_tol=1e-6):
                        one['share'] -= share_changed
                        break
                    else:
                        share_changed -= one['share']
                        one['share'] = 0
                else:
                    assert False, f"not enough shares to redeem in history (manager_id){manager_id} (fof_id){fof_id} (investor_id){investor_id} (left_shares){one['share']} (left_redemp){share_changed}"
            elif row.event_type == FOFTradeStatus.DEDUCT_REWARD:
                if fof_info.incentive_fee_mode in (FOFIncentiveFeeMode.SCST_HIGH_WL_S,):
                    for one in share_details:
                        if math.isclose(one['share'], 0, rel_tol=1e-6):
                            continue
                        if one['water_line'] >= row.acc_unit_value:
                            # 当前水位线未超过该笔份额的水位线 不需要计提业绩报酬
                            continue
                        carry = round(self._calc_carry(row.acc_unit_value, one['water_line'], fof_info.incentive_fee_type, fof_info.incentive_fee_str) * one['share'] / row.net_asset_value, 2)
                        assert (one['share'] > carry) or math.isclose(one['share'], carry, rel_tol=1e-6), f"not enough shares to calc carry (manager_id){manager_id} (fof_id){fof_id} (investor_id){investor_id} (left_shares){one['share']} (carry){carry}"
                        one['share'] -= carry
                        # 水位线变成本次计提时的水位线了
                        one['water_line'] = row.acc_unit_value
                elif fof_info.incentive_fee_mode in (FOFIncentiveFeeMode.INTE_HIGH_WL, FOFIncentiveFeeMode.INTE_HIGH_WL_WITH_SCST_R):
                    assert row.water_line > last_water_line, f'water line should be increased monotonously for every investor (manager_id){manager_id} (fof_id){fof_id} (investor_id){investor_id} (last water line){last_water_line} (water line this time){row.water_line}'
                    # profit = self._calc_carry(row.acc_unit_value, last_water_line, fof_info.incentive_fee_type, fof_info.incentive_fee_str)
                else:
                    assert False, f'do not support the fee mode {fof_info.incentive_fee_mode} temp (fof_id){fof_id} (manager_id){manager_id}'
                last_water_line = row.water_line
            else:
                assert False, f'invalid event type {row.event_type} during doing carry calc'
        return share_details

    def investor_pur_redemp_update(self, datas: Dict[str, Any]) -> int:
        '''
        申赎记录更新/添加

        Parameters
        ----------
        datas : Dict[str, Any]
            数据, keys:
                id : 如果是添加 则不需要该字段; 否则则需要
                fof_id : 产品ID
                manager_id : 管理端ID
                datetime : 交易日期
                event_type : 交易类型(认购/申购/赎回)
                investor_id : 投资人ID
                net_asset_value : 单位净值
                acc_unit_value : 累计净值
                water_line : 水位线(一般是累计净值; 但整体高水位法下与累计净值可能不同)
                amount : 申购金额/认购金额
                raising_interest : 募集期利息
                redemp_share : 赎回份额
                redemp_fee : 赎回费

        Returns/Exceptions
        -------
        throw excepion if failed, or return id (an integer) if succeed
        '''
        fof_info = BasicDataApi().get_fof_info(datas['manager_id'], fof_id_list=[datas['fof_id']])
        assert fof_info is not None, '!!!!'
        assert fof_info.shape[0] == 1, f"invalid fof id {[datas['fof_id']]}"
        fof_info = fof_info.iloc[-1, :]

        event_type = datas['event_type']
        if event_type == FOFTradeStatus.PURCHASE:
            # 认购
            datas['purchase_amount'] = datas['amount']
            datas['share_changed'] = round((datas['amount'] + datas['raising_interest']) / datas['net_asset_value'], 2)
        elif event_type == FOFTradeStatus.SUBSCRIBE:
            # 申购
            datas['purchase_amount'] = datas['amount']
            datas['share_changed'] = round(datas['amount'] / datas['net_asset_value'], 2)
        elif event_type == FOFTradeStatus.REDEEM:
            # 赎回
            datas['share_changed'] = -datas['redemp_share']
            datas['redemp_confirmed_amount'] = round(datas['redemp_share'] * datas['net_asset_value'], 2) - datas['redemp_fee']

            # 计算业绩报酬计提
            carry_sum = 0
            share_details = self._calc_share_details(fof_info, datas['manager_id'], datas['fof_id'], datas['investor_id'], datas['datetime'])
            for one in share_details:
                if math.isclose(one['share'], 0, rel_tol=1e-6):
                    continue
                if (one['share'] > datas['redemp_share']) or math.isclose(one['share'], datas['redemp_share'], rel_tol=1e-6):
                    one['share'] -= datas['redemp_share']
                    if fof_info.incentive_fee_mode in (FOFIncentiveFeeMode.INTE_HIGH_WL_WITH_SCST_R,):
                        if one['acc_unit_value'] < one['water_line']:
                            # 如果这笔交易当时的交易净值在水下 需要在赎回时补扣业绩报酬
                            profit = self._calc_carry(min(datas['acc_unit_value'], one['water_line']), one['acc_unit_value'], fof_info.incentive_fee_type, fof_info.incentive_fee_str)
                            print(f"(profit){profit} (shares){datas['redemp_share']}")
                            carry_sum += round(profit * datas['redemp_share'], 2)
                    elif fof_info.incentive_fee_mode in (FOFIncentiveFeeMode.SCST_HIGH_WL_S,):
                        if datas['acc_unit_value'] > one['water_line']:
                            carry_sum += round(self._calc_carry(datas['acc_unit_value'], one['water_line'], fof_info.incentive_fee_type, fof_info.incentive_fee_str) * datas['redemp_share'], 2)
                    break
                else:
                    datas['redemp_share'] -= one['share']
                    if fof_info.incentive_fee_mode in (FOFIncentiveFeeMode.INTE_HIGH_WL_WITH_SCST_R,):
                        if one['acc_unit_value'] < one['water_line']:
                            # 如果这笔交易当时的交易净值在水下 需要在赎回时补扣业绩报酬
                            profit = self._calc_carry(min(datas['acc_unit_value'], one['water_line']), one['acc_unit_value'], fof_info.incentive_fee_type, fof_info.incentive_fee_str)
                            print(f"(profit){profit} (shares){one['share']}")
                            carry_sum += round(profit * one['share'], 2)
                    elif fof_info.incentive_fee_mode in (FOFIncentiveFeeMode.SCST_HIGH_WL_S,):
                        if datas['acc_unit_value'] > one['water_line']:
                            carry_sum += round(self._calc_carry(datas['acc_unit_value'], one['water_line'], fof_info.incentive_fee_type, fof_info.incentive_fee_str) * one['share'], 2)
                    one['share'] = 0
            else:
                assert False, f"not enough shares to redeem (fof_id){datas['fof_id']} (manager_id){datas['manager_id']} (left_shares){one['share']} (left_redemp){datas['redemp_share']}"
            datas['carry_amount'] = carry_sum
            datas['redemp_confirmed_amount'] = round(datas['redemp_confirmed_amount'] - carry_sum, 2)
        else:
            raise ValueError(f'invalid event_type {event_type}')

        _, share_separate = self._get_total_share(datas['manager_id'], datas['fof_id'], datas['datetime'], datas['investor_id'], exclude1=[datas['id']] if 'id' in datas else [])

        datas['share_changed'] = round(datas['share_changed'], 2)
        try:
            datas['share_after_trans'] = round(float(share_separate.at[datas['investor_id'], 'share_changed']) + datas['share_changed'], 2)
        except KeyError:
            datas['share_after_trans'] = datas['share_changed']

        datas['applied_date'] = datas['datetime']
        datas['deposited_date'] = datas['datetime']
        if 'water_line' not in datas:
            datas['water_line'] = datas['acc_unit_value']

        s = pd.Series(datas).drop(['amount', 'redemp_share'], errors='ignore')
        # TODO: 原子操作下面几步
        # TODO: 先刷后边的再删这一条
        if 'id' in datas:
            DerivedDataApi().delete_hedge_fund_investor_pur_redemp(id_to_delete=datas['id'])
        sql_obj = HedgeFundInvestorPurAndRedemp()
        for k, v in s.to_dict().items():
            setattr(sql_obj, k, v)
        with DerivedDatabaseConnector().managed_session() as session:
            session.add(sql_obj)
            session.commit()
            the_id = sql_obj.id
        # df.to_sql(HedgeFundInvestorPurAndRedemp.__table__.name, DerivedDatabaseConnector().get_engine(), index=False, if_exists='append')
        self._refresh_datas_after_updating(datas['manager_id'], datas['fof_id'], datas['investor_id'], datas['datetime'])
        return the_id

    def _calc_carry(self, nav: float, water_line: float, fee_type: str, fee_desc: str) -> float:
        profit: float = nav - water_line
        if fee_type == '1':
            return profit * float(fee_desc)
        elif fee_type == '2':
            fee_df = pd.DataFrame(json.loads(fee_desc)).sort_values(by='start', ascending=False)
            assert not fee_df.empty, f'invalid fee str {fee_desc} (fee_type){fee_type}'
            total_profit = 0
            for row in fee_df.itertuples(index=False):
                assert profit > 0, f'invalid profit (profit){profit} (nav){nav} (water_line){water_line} (fee_desc){fee_desc} (fee_type){fee_type}'
                level_profit: float = water_line * (row.start if row.start else 0)
                if profit > level_profit:
                    total_profit += (profit - level_profit) * (row.val if row.val else 0)
                    profit = level_profit
            return total_profit
        else:
            assert False, f'invalid fee type {fee_type}, do not support to calc carry by it'

    def investor_pur_redemp_remove(self, id: int):
        '''
        申赎记录删除

        Parameters
        ----------
        id : int
            对应数据库中id

        Returns/Exceptions
        -------
        throw excepion if failed
        '''

        df = DerivedDataApi().get_hedge_fund_investor_pur_redemp_by_id(id)
        assert df is not None, f'failed to get hedge fund investor data by id {id}'
        assert df.shape[0] == 1, f'invalid id {id}'

        s = df.iloc[-1, :]
        DerivedDataApi().delete_hedge_fund_investor_pur_redemp(id_to_delete=id)
        self._refresh_datas_after_updating(s.manager_id, s.fof_id, s.investor_id, s.datetime)

    def investor_div_carry_add(self, datas: Dict[str, Any]):
        '''
        分红/业绩计提记录添加

        Parameters
        ----------
        datas : Dict[str, Any]
            数据, keys:
                fof_id : 产品ID
                datetime : 分红/计提日期
                manager_id : 管理端ID
                event_type : 交易类型(现金分红/红利再投/计提业绩报酬)
                investor_id : 投资人ID
                net_asset_value : 单位净值
                acc_unit_value : 累计净值
                water_line : 水位线(一般是累计净值; 但整体高水位法下与累计净值可能不同)
                total_dividend : 红利总额
                cash_dividend : 现金分红金额
                reinvest_amount : 再投资金额
                carry_amount : 业绩报酬金额
                share_changed : 份额变更
                share_after_trans : 分红/计提后份额

        Returns/Exceptions
        -------
        throw excepion if failed, or return id (an integer) if succeed
        '''

        event_type = datas['event_type']
        if event_type == FOFTradeStatus.DEDUCT_REWARD:
            # 计提业绩报酬 暂不需要额外处理
            datas['share_changed'] = round(datas['share_changed'], 2)
            datas['share_after_trans'] = round(datas['share_after_trans'], 2)
        else:
            total_share, share_separate = self._get_total_share(datas['manager_id'], datas['fof_id'], datas['datetime'], datas['investor_id'])
            share_separate = share_separate.share_changed.array[-1]
            # div = datas['total_dividend'] * share_separate / total_share

            div = datas['total_dividend']
            if event_type == FOFTradeStatus.DIVIDEND_CASH:
                # 现金分红
                datas['share_changed'] = 0
                datas['cash_dividend'] = div - (datas['carry_amount'] if not pd.isnull(datas['carry_amount']) else 0)
                datas['reinvest_amount'] = 0
            elif event_type == FOFTradeStatus.DIVIDEND_VOLUME:
                # 红利再投
                datas['reinvest_amount'] = div - (datas['carry_amount'] if not pd.isnull(datas['carry_amount']) else 0)
                datas['share_changed'] = round(datas['reinvest_amount'] / datas['net_asset_value'], 2)
                datas['cash_dividend'] = 0
            else:
                raise ValueError(f'invalid event_type {event_type}')

            datas['share_after_trans'] = round(share_separate + datas['share_changed'], 2)

            for k in ('reinvest_amount', 'cash_dividend', 'total_dividend'):
                datas[k] = float(datas[k])

        for k in ('net_asset_value', 'acc_unit_value', 'water_line', 'carry_amount', 'share_changed', 'share_after_trans'):
            datas[k] = float(datas[k])

        datas['applied_date'] = datas['datetime']
        datas['deposited_date'] = datas['datetime']
        df = pd.Series(datas).to_frame().T
        # TODO: 原子操作下面几步
        if 'id' in datas:
            DerivedDataApi().delete_hedge_fund_investor_div_carry(id_to_delete=datas['id'])
        df.to_sql(HedgeFundInvestorDivAndCarry.__table__.name, DerivedDatabaseConnector().get_engine(), index=False, if_exists='append')

    def investor_div_carry_remove(self, id: int):
        '''
        分红/业绩计提记录删除

        Parameters
        ----------
        id : int
            对应数据库中id

        Returns/Exceptions
        -------
        throw excepion if failed
        '''

        df = DerivedDataApi().get_hedge_fund_investor_div_carry_by_id(id)
        assert df is not None, f'failed to get hedge fund investor data by id {id}'
        assert df.shape[0] == 1, f'invalid id {id}'

        s = df.iloc[-1, :]
        DerivedDataApi().delete_hedge_fund_investor_div_carry(id_to_delete=id)
        self._refresh_datas_after_updating(s.manager_id, s.fof_id, s.investor_id, s.datetime)

    def calc_dividend_event(self, datas: Dict[str, Any]) -> pd.DataFrame:
        '''
        计算分红事件

        Parameters
        ----------
        datas : Dict[str, Any]
            数据, keys:
                fof_id : 产品ID
                manager_id : 管理端ID
                datetime : 分红日期
                event_type : 红利发放方式(现金分红/红利再投)
                net_asset_value : 单位净值
                acc_unit_value : 累计净值
                calc_method : 计算方法(红利总额/每单位红利)
                dividend_for_calc : 红利总额/每单位红利
                do_deduct_reward: 是否计提业绩报酬

        Returns/Exceptions
        -------
        throw excepion if failed, or return a pd.DataFrame if succeed
        '''

        total_share, share_separate = self._get_total_share(datas['manager_id'], datas['fof_id'], datas['datetime'])
        share_separate = share_separate.share_changed
        weight = share_separate / total_share

        calc_method = datas['calc_method']
        if calc_method == DividendCalcMethod.BY_TOTAL_AMOUNT:
            # 红利总额
            dividend_amount = datas['dividend_for_calc']
        elif calc_method == DividendCalcMethod.BY_PER_UNIT:
            # 每单位红利
            dividend_amount = round(total_share * datas['dividend_for_calc'], 2)
        else:
            raise ValueError(f'invalid calc_method {calc_method}')

        s = (dividend_amount * weight).round(2)
        event_type = datas['event_type']
        if datas['event_type'] == FOFTradeStatus.DIVIDEND_CASH:
            # 现金分红
            df = s.to_frame('total_dividend')
            df['cash_dividend'] = df.total_dividend
            if 'do_deduct_reward' in datas and datas['do_deduct_reward']:
                carry_df = self.calc_carry_event(datas)
                df = df.join(carry_df.set_index('investor_id').carry_amount)
                df['cash_dividend'] -= df.carry_amount.round(2)
            else:
                df['carry_amount'] = np.nan
            df['share_changed'] = 0
            df['reinvest_amount'] = 0
        elif datas['event_type'] == FOFTradeStatus.DIVIDEND_VOLUME:
            # 红利再投
            df = s.to_frame('total_dividend')
            df['reinvest_amount'] = df.total_dividend
            if 'do_deduct_reward' in datas and datas['do_deduct_reward']:
                carry_df = self.calc_carry_event(datas)
                df = df.join(carry_df.set_index('investor_id').carry_amount)
                df['reinvest_amount'] -= df.carry_amount.round(2)
            else:
                df['carry_amount'] = np.nan
            df['share_changed'] = (df.reinvest_amount / datas['net_asset_value']).round(2)
            df['cash_dividend'] = 0
        else:
            raise ValueError(f'invalid event_type {event_type}')
        df['share_after_trans'] = (share_separate + df.share_changed).round(2)

        df['fof_id'] = datas['fof_id']
        df['manager_id'] = datas['manager_id']
        df['datetime'] = datas['datetime']
        df['event_type'] = datas['event_type']
        columns_in_df = set(df.columns.array)
        if 'net_asset_value' not in columns_in_df:
            df['net_asset_value'] = datas['net_asset_value']
        if 'acc_unit_value' not in columns_in_df:
            df['acc_unit_value'] = datas['acc_unit_value']
        if 'water_line' not in columns_in_df:
            df['water_line'] = datas['acc_unit_value']
        return df.reset_index()

    def calc_carry_event(self, datas: Dict[str, Any]) -> pd.DataFrame:
        '''
        计算业绩计提事件

        Parameters
        ----------
        datas : Dict[str, Any]
            数据, keys:
                fof_id : 产品ID
                manager_id : 管理端ID
                datetime : 计提日期
                net_asset_value : 单位净值
                acc_unit_value : 累计净值

        Returns/Exceptions
        -------
        throw excepion if failed, or return a pd.DataFrame if succeed
        '''

        fof_info = BasicDataApi().get_fof_info(datas['manager_id'], fof_id_list=[datas['fof_id']])
        assert fof_info is not None, f"get fof info failed (fof_id){datas['fof_id']} (manager_id){datas['manager_id']}"
        assert fof_info.shape[0] == 1, f"invalid fof id {[datas['fof_id']]}"
        fof_info = fof_info.iloc[-1, :]

        date = pd.to_datetime(datas['datetime'], infer_datetime_format=True).date()

        part1 = DerivedDataApi().get_hedge_fund_investor_pur_redemp(datas['manager_id'], [datas['fof_id']])
        assert part1 is not None, f"get pur redemp info failed (fof_id){datas['fof_id']} (manager_id){datas['manager_id']}"
        part1 = part1[part1.datetime <= date]

        part2 = DerivedDataApi().get_hedge_fund_investor_div_carry(datas['manager_id'], [datas['fof_id']])
        assert part2 is not None, f"get pur div carry info failed (fof_id){datas['fof_id']} (manager_id){datas['manager_id']}"
        part2 = part2[part2.datetime <= date]

        carry_data = []
        total = pd.concat([part1, part2])
        if fof_info.incentive_fee_mode in (FOFIncentiveFeeMode.INTE_HIGH_WL, FOFIncentiveFeeMode.INTE_HIGH_WL_WITH_SCST_R):
            deduct_reward_info = part2[part2.event_type == FOFTradeStatus.DEDUCT_REWARD]
            if deduct_reward_info.empty:
                last_water_line = 1
            else:
                last_water_line = deduct_reward_info.sort_values(by='datetime').acc_unit_value.array[-1]
            print(f"(fof_id){datas['fof_id']} (manager_id){datas['manager_id']} (last_water_line){last_water_line} (acc_unit_value){datas['acc_unit_value']}")
            # 如果产品的水位线变高了 计提业绩报酬
            assert datas['acc_unit_value'] > last_water_line, f"latest acc nav {last_water_line} is not greater than the last water line {datas['acc_unit_value']}, can not do carry calc (fof_id){datas['fof_id']} (manager_id){datas['manager_id']}"
            profit = self._calc_carry(datas['acc_unit_value'], last_water_line, fof_info.incentive_fee_type, fof_info.incentive_fee_str)
            for investor_id in total.investor_id.unique():
                share_details = self._calc_share_details(fof_info, datas['manager_id'], datas['fof_id'], investor_id, datas['datetime'])
                share_before_trans = round(pd.DataFrame(share_details).share.sum(), 2)
                carry_amount_sum = 0
                for one in share_details:
                    if math.isclose(one['share'], 0, rel_tol=1e-6):
                        continue
                    if one['datetime'] == date:
                        # 今天新买入的交易不做业绩计提
                        continue
                    carry_amount_sum += round(profit * one['share'], 2)
                if not math.isclose(carry_amount_sum, 0):
                    carry_data.append({
                        'investor_id': investor_id,
                        'datetime': datas['datetime'],
                        'share_before_trans': share_before_trans,
                        'carry_amount': carry_amount_sum,
                        'share_changed': 0,
                        'share_after_trans': share_before_trans,
                        'net_asset_value': round(datas['net_asset_value'] - profit, fof_info.nav_decimals),
                        'acc_unit_value': round(datas['acc_unit_value'] - profit, fof_info.nav_decimals),
                        'water_line': round(datas['acc_unit_value'] - profit, fof_info.nav_decimals),
                    })
        elif fof_info.incentive_fee_mode in (FOFIncentiveFeeMode.SCST_HIGH_WL_S,):
            for investor_id in total.investor_id.unique():
                share_details = self._calc_share_details(fof_info, datas['manager_id'], datas['fof_id'], investor_id, datas['datetime'])
                share_before_trans = round(pd.DataFrame(share_details).share.sum(), 2)
                carry_amount_sum = 0
                share_changed = 0
                for one in share_details:
                    if math.isclose(one['share'], 0, rel_tol=1e-6):
                        continue
                    if one['water_line'] >= datas['acc_unit_value']:
                        # 当前水位线未超过该笔份额的水位线 不需要计提业绩报酬
                        continue
                    carry_amount = round(self._calc_carry(datas['acc_unit_value'], one['water_line'], fof_info.incentive_fee_type, fof_info.incentive_fee_str) * one['share'], 2)
                    carry = round(carry_amount / datas['net_asset_value'], 2)
                    assert (one['share'] > carry) or math.isclose(one['share'], carry, rel_tol=1e-6), f"not enough shares to calc carry (fof_id){datas['fof_id']} (manager_id){datas['manager_id']} (left_share){one['share']} (carry){carry}"
                    carry_amount_sum += carry_amount
                    share_changed -= carry
                    one['share'] -= carry
                    # 水位线变成本次计提时的水位线了
                    one['water_line'] = datas['acc_unit_value']
                carry_data.append({
                    'investor_id': investor_id,
                    'datetime': datas['datetime'],
                    'share_before_trans': share_before_trans,
                    'carry_amount': carry_amount_sum,
                    'share_changed': share_changed,
                    'share_after_trans': share_before_trans + share_changed,
                    'net_asset_value': datas['net_asset_value'],
                    'acc_unit_value': datas['acc_unit_value'],
                    'water_line': datas['acc_unit_value'],
                })
        else:
            assert False, f"do not support the fee mode {fof_info.incentive_fee_mode} temp (fof_id){datas['fof_id']} (manager_id){datas['manager_id']}"

        df = pd.DataFrame(carry_data)
        df['fof_id'] = datas['fof_id']
        df['manager_id'] = datas['manager_id']
        df['datetime'] = datas['datetime']
        df['event_type'] = FOFTradeStatus.DEDUCT_REWARD
        return df

    def upload_custodian_data(self, manager_id: str, fof_id: str, datas: io.BytesIO) -> datetime.date:
        '''
        上传/更新私募基金托管数据

        Parameters
        ----------
        manager_id : str
            manager id
        fof_id : str
            fof id
        datas : io.BytesIO
            open 托管数据表格获得的 file object

        Returns/Exceptions
        -------
        throw excepion if failed, or return a datetime.date if succeed
        '''

        parser_runner = ParserRunner(manager_id, EMailParserType.E_PARSER_VALUATION)
        total_df = parser_runner.parse_data(datas, manager_id)
        if total_df is None:
            raise Exception(f'could not parse this custodian data (manager_id){manager_id} (fof_id){fof_id}')

        total_df['fof_id'] = fof_id
        now_df = DerivedDataApi().get_hedge_fund_custodian_data(manager_id=manager_id, fof_id_list=[fof_id])
        if now_df is not None:
            now_df = now_df.drop(columns=['update_time', 'create_time', 'is_deleted', 'id', 'url']).replace({None: np.nan}).astype(total_df.dtypes.to_dict())
            # merge on all columns
            df = total_df.round(6).merge(now_df.round(6), how='left', indicator=True, validate='one_to_one')
            df = df[df._merge == 'left_only'].drop(columns=['_merge'])
        else:
            df = total_df
        if not df.empty:
            print(df)
            for row in df.itertuples(index=False):
                DerivedDataApi().delete_hedge_fund_custodian_data(row.manager_id, row.fof_id, row.datetime)
            df.to_sql(HedgeFundCustodianData.__table__.name, DerivedDatabaseConnector().get_engine(), index=False, if_exists='append')
        return total_df['datetime'].array[0]

    @staticmethod
    def calc_whole_adjusted_net_value(nav_acc_data: pd.DataFrame) -> pd.DataFrame:
        '''
        计算单只基金的全量复权净值

        Parameters
        ----------
        nav_acc_data : pd.DataFrame
            净值数据, index: datetime.date 净值日期
                columns:
                    net_asset_value : 单位净值(必须从1开始, 除非与累计净值完全相同)
                    acc_unit_value : 累计净值(必须从1开始, 除非与单位净值完全相同)

        Returns/Exceptions
        -------
        throw excepion if failed, or return a pd.DataFrame if succeed

        value returned : pd.DataFrame
            复权净值数据, index: datetime.date 净值日期
                columns:
                    adj_nav : 复权净值
                    adj_factor: 复权因子
                    change_rate: 涨跌幅
        '''

        # 先按index(datetime.date)排序
        nav_acc_data: pd.DataFrame = nav_acc_data.sort_index()
        if nav_acc_data.net_asset_value.equals(nav_acc_data.acc_unit_value):
            # 如果单位净值和累计净值完全一样 允许不从1开始 走一个单独的(简易)计算流程
            df = nav_acc_data
            df['adj_nav'] = df.net_asset_value
            df['change_rate'] = df.adj_nav.pct_change()
            df['adj_factor'] = 1
            df = df[['adj_nav', 'adj_factor', 'change_rate']]
            return df

        assert math.isclose(nav_acc_data.net_asset_value.array[0], 1) and math.isclose(nav_acc_data.acc_unit_value.array[0], 1), f'fund nav data should start with 1 (data){nav_acc_data}'

        assert nav_acc_data.acc_unit_value.round(6).ge(nav_acc_data.net_asset_value.round(6)).all(), f'acc_unit_value should always ge than net_asset_value (data){nav_acc_data}'
        # 公式一
        # days_before_dividend: pd.Series = (nav_acc_data.acc_unit_value - nav_acc_data.net_asset_value).round(6).drop_duplicates(keep='last')
        # 公式二
        days_before_dividend: pd.Series = (nav_acc_data.acc_unit_value - nav_acc_data.net_asset_value).round(6).drop_duplicates(keep='first')
        assert days_before_dividend.notna().all(), f'fund nav data should not contains NaN (data){nav_acc_data}'
        # 这里算出来每天的分红数据不应该出现负值 这样前边的 drop_duplicates 才是对的
        assert days_before_dividend.is_monotonic_increasing, f'dividend should always be monotonic increasing (data){nav_acc_data}'

        divdidend_that_day: pd.Series = days_before_dividend.sub(days_before_dividend.shift(1, fill_value=0))
        # 公式一
        # adj_factor: pd.Series = 1 + divdidend_that_day / (nav_acc_data.loc[divdidend_that_day.index, 'net_asset_value'].shift(1, fill_value=1) - divdidend_that_day)
        # 公式二
        net_asset_value = nav_acc_data.loc[divdidend_that_day.index, 'net_asset_value']
        adj_factor: pd.Series = (net_asset_value + divdidend_that_day) / net_asset_value

        # 公式一
        # df: pd.DataFrame = adj_factor.cumprod().reindex(nav_acc_data.index, method='bfill').to_frame('adj_factor')
        # 公式二
        df: pd.DataFrame = adj_factor.cumprod().reindex(nav_acc_data.index, method='ffill').to_frame('adj_factor')
        df['adj_nav'] = df.adj_factor * nav_acc_data.net_asset_value
        df['change_rate'] = df.adj_nav.pct_change()
        df = df[['adj_nav', 'adj_factor', 'change_rate']]
        return df
