
from typing import List, Dict
import json
import datetime
import pandas as pd
import numpy as np

from pandas.tseries.offsets import DateOffset

from .....util.calculator import Calculator
from ....manager.manager_fund import FundDataManager
from ....view.derived_models import ThirdPartyPortfolioIndicator, ThirdPartyPortfolioPositionLatest
from ....api.derived import DerivedDataApi


class ThirdPortfolioBase:

    _DIM_TYPE = {
        'daily_ret': DateOffset(days=1),
        'weekly_ret': DateOffset(weeks=1),
        'monthly_ret': DateOffset(months=1),
        'quarterly_ret': DateOffset(months=3),
        'half_yearly_ret': DateOffset(months=6),
        'yearly_ret': DateOffset(years=1),
    }

    def _calc_one_portfolio(self, x, fund_nav, po_pos, po_nav, end_date):
        try:
            pos_data = po_pos.loc[x.po_id, :]
        except KeyError:
            print(f'can not calc portfolio {x.po_id}')
            return
        last_pos = pd.Series(json.loads(pos_data.position))
        fund_nav = fund_nav[fund_nav.fund_id.isin(last_pos.index)].pivot(index='datetime', columns='fund_id', values='adjusted_net_value')
        fund_nav = fund_nav.sort_index()
        # 净值增长率
        rate = fund_nav.iloc[-1, :] / fund_nav.iloc[0, :]
        # 持仓权重根据净值增长率变化
        new_pos = last_pos * rate
        pos_sum = new_pos.sum()
        nav_rate = pos_sum / last_pos.sum()
        new_pos /= pos_sum
        # portfolio最新净值
        po_nav_df: pd.Series = po_nav[x.po_id]
        new_po_nav = po_nav_df.array[-1] * nav_rate
        po_nav_df.loc[end_date.isoformat()] = new_po_nav
        # print(po_nav_df)

        result = {'po_id': x.po_id, 'datetime': end_date.date(), 'po_src': x.po_src, 'position': new_pos.to_json(), 'nav': new_po_nav}
        result['annual_ret'] = np.exp(np.log(new_po_nav) / (po_nav_df.shape[0] / Calculator.TRADING_DAYS_PER_YEAR)) - 1
        mdd_part = po_nav_df[:] / po_nav_df[:].rolling(window=po_nav_df.shape[0], min_periods=1).max()
        result['mdd'] = 1 - mdd_part.min()
        if np.isnan(result['mdd']):
            result['mdd_date2'] = None
            result['mdd_date1'] = None
        else:
            result['mdd_date2'] = mdd_part.idxmin()
            result['mdd_date1'] = po_nav_df[:result['mdd_date2']].idxmax()
        result['from_setup_ret'] = new_po_nav - 1
        po_nav_df.index = pd.to_datetime(po_nav_df.index)
        resampled_w = po_nav_df.resample('1W').apply(lambda x: x.array[-1] if not x.empty else np.nan)
        result['vol_by_week'] = resampled_w.dropna().pct_change().std(ddof=1) * np.sqrt(52)

        resampled_m = po_nav_df.resample('1M').apply(lambda x: x.array[-1] if not x.empty else np.nan)
        result['vol_by_month'] = resampled_m.dropna().pct_change().std(ddof=1) * np.sqrt(12)
        result['vol_by_day'] = po_nav_df.dropna().pct_change().std(ddof=1) * np.sqrt(244)
        result['annual_compounded_ret'] = np.power(new_po_nav, 1 / (po_nav_df.shape[0] / 244)) - 1
        if result['vol_by_week'] != 0:
            result['sharpe_ratio'] = (result['annual_compounded_ret'] - 0.02) / result['vol_by_week']
        else:
            result['sharpe_ratio'] = np.nan

        # 遍历每个需要计算的时间区间
        for name, value in self._DIM_TYPE.items():
            bd = (result['datetime'] - value).date()
            # 试图寻找bd及其之前的最近一天
            filtered_mv = po_nav_df.loc[po_nav_df.index.date <= bd]
            if filtered_mv.empty:
                continue
            # 计算区间内的return
            result[name] = po_nav_df.array[-1] / filtered_mv.array[-1] - 1

        result['nav'] = new_po_nav
        return pd.Series(result)

    def calc_everyday(self, end_date: str, po_src_list: List[int]):
        from ....view.cas.third_party_portfolio_nav import ThirdPartyPortfolioNav

        end_date_dt = pd.to_datetime(end_date, infer_datetime_format=True)
        _trading_day: pd.DataFrame = FundDataManager.basic_data('get_trading_day_list', start_date=(end_date_dt - DateOffset(months=1)).isoformat(), end_date=end_date).drop(columns='_update_time')

        fund_nav = FundDataManager.basic_data('get_fund_nav_with_date', start_date=_trading_day.datetime.array[-2], end_date=_trading_day.datetime.array[-1])

        # 获取所有portfolio信息
        po_info = DerivedDataApi().get_market_portfolio_info().drop(columns='_update_time')
        po_info = po_info[po_info.po_src.isin(po_src_list)]
        # 获取所有portfolio最新持仓
        po_pos = DerivedDataApi().get_market_portfolio_position_by_src(po_src_list).drop(columns='_update_time')
        po_pos = po_pos.set_index('po_id')
        # 获取所有portfolio最新净值
        po_nav: Dict[str, pd.Series] = {}
        for one in ThirdPartyPortfolioNav.objects.filter(po_id__in=po_info.po_id.to_list()):
            po_nav[one.po_id] = pd.Series(one.nav, index=one.date)

        # 遍历每个portfolio计算
        result = po_info.apply(self._calc_one_portfolio, axis=1, fund_nav=fund_nav, po_pos=po_pos, po_nav=po_nav, end_date=end_date_dt)
        result = result[result.notna().any(axis=1)].set_index('po_id').replace({np.nan: None})
        for col in result:
            if result[col].dtype in ('float64', 'int64'):
                result[col] = result[col].astype('object')
            elif isinstance(result[col].array[0], datetime.date):
                result[col] = result[col].transform(lambda x: x.isoformat())
        print(result)

        from sqlalchemy.orm import sessionmaker
        from surfing.data.wrapper.mysql import DerivedDatabaseConnector

        print(f'to update data of {ThirdPartyPortfolioPositionLatest.__table__.name}')
        Session = sessionmaker(DerivedDatabaseConnector().get_engine())
        db_session = Session()
        for row in db_session.query(ThirdPartyPortfolioPositionLatest).filter(ThirdPartyPortfolioPositionLatest.po_src.in_(po_src_list)).all():
            try:
                row_data = result.loc[row.po_id, :]
                row.datetime = row_data.datetime
                row.position = row_data.position
            except KeyError:
                print(f'not found {row.po_id} data')
        print('done, to commit')
        db_session.commit()

        print(f'to update data of {ThirdPartyPortfolioIndicator.__table__.name}')
        for row in db_session.query(ThirdPartyPortfolioIndicator).filter(ThirdPartyPortfolioIndicator.po_src.in_(po_src_list)).all():
            try:
                row_data = result.loc[row.po_id, :]
                row.datetime = row_data.datetime
                row.nav = row_data.nav
                row.sharpe_ratio = row_data.sharpe_ratio
                row.mdd = row_data.mdd
                row.annual_compounded_ret = row_data.annual_compounded_ret
                row.daily_ret = row_data.daily_ret
                row.weekly_ret = row_data.weekly_ret
                row.monthly_ret = row_data.monthly_ret
                row.quarterly_ret = row_data.quarterly_ret
                row.half_yearly_ret = row_data.half_yearly_ret
                row.yearly_ret = row_data.yearly_ret
                row.from_setup_ret = row_data.from_setup_ret
                row.vol_by_day = row_data.vol_by_day
                row.vol_by_week = row_data.vol_by_week
                row.vol_by_month = row_data.vol_by_month
                row.annual_ret = row_data.annual_ret
                row.mdd_d1 = row_data.mdd_date1
                row.mdd_d2 = row_data.mdd_date2
            except KeyError:
                print(f'not found {row.po_id} data')
        print('done, to commit')
        db_session.commit()
        db_session.close()

        for row in result.itertuples():
            ThirdPartyPortfolioNav.objects.filter(po_id=row.Index).update(
                date__append=[row.datetime],
                nav__append=[row.nav],
            )
