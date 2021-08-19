import numpy as np
from surfing.data.api.raw import *
from surfing.data.api.basic import *
from surfing.data.api.derived import *

WENJIAN_FUND_LIST = ["SGM473","SNG191","SR9762","SNH765","SEW210","S3649A","SGM992","SJE335","SLC213","EE891B","SJJ077"]

class FOFApi(metaclass=Singleton):
    
    def get_pf_virtual_nav(self, fof_id='SLW695'):
        '''计算虚拟净值'''
        from surfing.data.manager.manager_fof_lite import FOFDataManagerLite
        try:
            fof_aa = BasicDataApi().get_fof_asset_allocation(manager_id='py1')
            fof_aa = fof_aa[fof_aa.asset_type == HoldingAssetType.HEDGE]
            df = FOFDataManagerLite._calc_virtual_net_value('py1', fof_id, list(fof_aa.fund_id.unique()))
            return df
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from {FOFApi.get_pf_virtual_nav}')

    def get_fof_pf_trade_history(self, fof_id_list=['SLW695'], manager_id='py1', fund_list=WENJIAN_FUND_LIST):
        '''获取FOF私募产品申赎记录'''
        from surfing.constant import HoldingAssetType, FOFTradeStatus
        try:
            with BasicDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                    FOFInfo
                ).filter(
                    FOFInfo.fof_id.in_(fund_list),
                    FOFInfo.manager_id == manager_id,
                )
                fund_info = pd.read_sql(query.statement, query.session.bind)
                rename_dict = fund_info[["fof_id","desc_name"]].set_index("fof_id").to_dict()["desc_name"]
                rename_dict["others_mv"] = "现金"

            fof_aa = BasicDataApi().get_fof_asset_allocation(manager_id=manager_id,fof_id_list=fof_id_list)
            fof_aa = fof_aa[(fof_aa.asset_type == HoldingAssetType.HEDGE) & (fof_aa.event_type.isin([FOFTradeStatus.PURCHASE, FOFTradeStatus.SUBSCRIBE, FOFTradeStatus.REDEEM]))]
            fof_aa['bs_flag'] = fof_aa.event_type.map(lambda x: -1 if x == FOFTradeStatus.REDEEM else 1)
            fof_aa['amount'] *= fof_aa.bs_flag
            fof_aa = fof_aa.pivot(index='datetime', columns='fund_id', values='amount').rename(columns = rename_dict)
            return fof_aa

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from {FOFApi.get_fof_pf_trade_history}')

    def get_fof_pf_amount(self, fof_id='SLW695', manager_id='py1', fund_list=WENJIAN_FUND_LIST):
        '''获取FOF私募产品金额'''
        import json
        from surfing.data.manager.manager_fof_lite import FOFDataManagerLite
        from surfing.constant import FOFTradeStatus
        try:
            def _calc_sub_asset_mv(x):
                pos = json.loads(x.position)
                df = pd.DataFrame(pos)
                if df.empty:
                    return
                df = df.set_index('fund_id')
                df = df[df.asset_type==2]
                sub_asset_mv[x.name] = df.share * df.nav
                return
            with BasicDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                    FOFInfo
                ).filter(
                    FOFInfo.fof_id.in_(fund_list),
                    FOFInfo.manager_id == manager_id,
                )
                fund_info = pd.read_sql(query.statement, query.session.bind)
                rename_dict = fund_info[["fof_id","desc_name"]].set_index("fof_id").to_dict()["desc_name"]
                rename_dict["others_mv"] = "现金"

            fof_found_date = pd.to_datetime('20200929').date()
            fof_nav = DerivedDataApi().get_fof_nav_calc(manager_id, [fof_id])
            fof_nav = fof_nav.set_index('datetime').sort_index()['nav']
            fof_sa = DerivedDataApi().get_hedge_fund_investor_pur_redemp(manager_id, [fof_id])
            fof_sa = fof_sa.set_index('datetime')
            fof_sa_sub = fof_sa.loc[fof_sa.event_type.isin([FOFTradeStatus.PURCHASE, FOFTradeStatus.SUBSCRIBE])]
            fof_sa_redemp = fof_sa.loc[fof_sa.event_type.isin([FOFTradeStatus.REDEEM,])]
            cumshares = fof_sa_sub.share_changed.fillna(0).add(fof_sa_redemp.share_changed.fillna(0), fill_value=0)
            cumshares = cumshares.groupby('datetime').sum()
            cumshares = cumshares.cumsum()
            # fof MV
            fof_mv = cumshares.reindex(fof_nav.index.union(cumshares.index)).ffill() * fof_nav
            fof_mv = fof_mv[fof_mv.index >= fof_found_date]
            pos_df = DerivedDataApi().get_fof_position(manager_id, [fof_id])
            sub_asset_mv = {}
            pos_df.set_index('datetime')[['position']].apply(_calc_sub_asset_mv, axis=1)
            # 子产品MV
            sub_asset_mv_df = pd.DataFrame.from_dict(sub_asset_mv, orient='index')
            sub_asset_mv_df = sub_asset_mv_df.reindex(fof_mv.index.union(sub_asset_mv_df.index))
            sub_asset_mv_df['others_mv'] = fof_mv - sub_asset_mv_df.sum(axis=1)
            # 子产品损益 = MV + 赎回给的现金 + 分红的现金 - 每次投入的成本
            fof_aa = FOFDataManagerLite.get_fof_asset_allocation(manager_id, [fof_id])
            fof_aa = fof_aa[fof_aa.asset_type==2].drop(columns='fof_id')
            # 赎回得到的现金
            cash_redemp = fof_aa.loc[fof_aa.event_type==FOFTradeStatus.REDEEM, ['datetime', 'fund_id', 'amount']]
            cash_redemp = cash_redemp.pivot_table(index='datetime', columns='fund_id', values='amount', aggfunc=np.sum)
            cash_redemp = cash_redemp.reindex(fof_nav.index).cumsum().ffill()
            # 成本
            cost = fof_aa.loc[fof_aa.event_type.isin([FOFTradeStatus.PURCHASE, FOFTradeStatus.SUBSCRIBE]), ['datetime', 'fund_id', 'amount']]
            cost = cost.pivot_table(index='datetime', columns='fund_id', values='amount', aggfunc=np.sum).cumsum().reindex(fof_nav.index).ffill()
            # 现金分红
            cash_dividend = fof_aa.loc[fof_aa.event_type==FOFTradeStatus.DIVIDEND_CASH, ['datetime', 'fund_id', 'amount']]
            if cash_dividend.empty:
                cash_dividend = None
            else:
                cash_dividend = cost.pivot_table(index='datetime', columns='fund_id', values='amount', aggfunc=np.sum).cumsum().reindex(fof_nav.index).ffill()
            if cash_dividend is not None:
                sub_asset_pal_fixed = sub_asset_mv_df.add(cash_redemp.fillna(0), fill_value=0).add(cash_dividend.fillna(0), fill_value=0).sub(cost.fillna(0), fill_value=0)
            else:
                sub_asset_pal_fixed = sub_asset_mv_df.add(cash_redemp.fillna(0), fill_value=0).sub(cost.fillna(0), fill_value=0)
            # FOF MV(周度)
            fof_mv_resampled = fof_mv.set_axis(pd.to_datetime(fof_mv.index), axis=0)
            fof_mv_resampled = fof_mv_resampled.resample('1W').last()
            fof_mv_resampled = fof_mv_resampled.set_axis(fof_mv_resampled.index.date, axis=0)
            # 子产品MV(周度)
            sub_asset_mv_resampled = sub_asset_mv_df.set_axis(pd.to_datetime(sub_asset_mv_df.index), axis=0)
            sub_asset_mv_resampled = sub_asset_mv_resampled.resample('1W').last()
            sub_asset_mv_resampled = sub_asset_mv_resampled.set_axis(sub_asset_mv_resampled.index.date, axis=0)
            # 子产品损益(周度)
            sub_asset_pal_fixed_sampled = sub_asset_pal_fixed.set_axis(pd.to_datetime(sub_asset_pal_fixed.index), axis=0)
            sub_asset_pal_fixed_sampled = sub_asset_pal_fixed_sampled.resample('1W').last()
            sub_asset_pal_fixed_sampled = sub_asset_pal_fixed_sampled.set_axis(sub_asset_pal_fixed_sampled.index.date, axis=0)
            sub_asset_pal_fixed_sampled = sub_asset_pal_fixed_sampled.rename(columns = rename_dict)
            fund_mv_df = sub_asset_mv_resampled
            fund_mv_df["amount"] = fund_mv_df.sum(axis = 1)
            fund_mv_df = fund_mv_df.div(fund_mv_df.amount, axis=0).drop(columns = "amount")
            return fund_mv_df, sub_asset_mv_resampled, sub_asset_pal_fixed_sampled
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from {FOFApi.get_fof_pf_amount}')