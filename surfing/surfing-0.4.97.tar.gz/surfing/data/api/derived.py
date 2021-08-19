
from typing import Tuple, List

import pandas as pd
import datetime
from sqlalchemy import func
import statsmodels.api as sm
from statsmodels import regression
import numpy as np
from ...util.singleton import Singleton
from ..wrapper.mysql import DerivedDatabaseConnector
from .raw import RawDataApi
from .basic import BasicDataApi
from ..view.derived_models import *

class DerivedDataApi(metaclass=Singleton):
    def get_fund_indicator(self, fund_list):
        with DerivedDatabaseConnector().managed_session() as quant_session:
            try:
                query = quant_session.query(
                        FundIndicator.fund_id,
                        FundIndicator.datetime,
                        FundIndicator.alpha,
                        FundIndicator.beta,
                        FundIndicator.fee_rate,
                        FundIndicator.track_err,
                    ).filter(
                        FundIndicator.fund_id.in_(fund_list),
                    )
                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundIndicator.__tablename__}')

    def delete_fund_indicator_with_dt(self, date, fund_list):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    FundIndicator
                ).filter(
                    FundIndicator.fund_id.in_(fund_list),
                    FundIndicator.datetime == date,
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {FundIndicator.__tablename__}')
                return False

    def get_fund_indicator_by_date(self, fund_list, date):
        with DerivedDatabaseConnector().managed_session() as quant_session:
            try:
                query = quant_session.query(
                    FundIndicator
                ).filter(
                    FundIndicator.datetime == date,
                    FundIndicator.fund_id.in_(fund_list),
                )
                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundIndicator.__tablename__}')

    def get_fund_indicator_monthly(self, start_date, end_date, fund_list, columns: Tuple[str] = ()):
        with DerivedDatabaseConnector().managed_session() as quant_session:
            try:
                query = quant_session.query(
                    FundIndicatorMonthly.fund_id,
                    FundIndicatorMonthly.datetime,
                )
                if columns:
                    query = query.add_columns(*columns)
                query = query.filter(
                    FundIndicatorMonthly.fund_id.in_(fund_list),
                    FundIndicatorMonthly.datetime >= start_date,
                    FundIndicatorMonthly.datetime <= end_date
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundIndicatorMonthly.__tablename__}')

    def get_fund_indicator_group(self, start_date: str, end_date: str, data_cycle: str = ''):
        with DerivedDatabaseConnector().managed_session() as quant_session:
            try:
                query = quant_session.query(
                    FundIndicatorGroup
                )
                query = query.filter(
                    FundIndicatorGroup.datetime >= start_date,
                    FundIndicatorGroup.datetime <= end_date
                )
                if data_cycle:
                    query = query.filter(
                        FundIndicatorGroup.data_cycle == data_cycle
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundIndicatorGroup.__tablename__}')

    def get_latest_fund_indicator_group(self, data_cycle: str = ''):
        with DerivedDatabaseConnector().managed_session() as quant_session:
            try:
                sub_q = quant_session.query(
                    FundIndicatorGroup.datetime.label('latest_time'),
                )
                if data_cycle:
                    sub_q = sub_q.filter(
                        FundIndicatorGroup.data_cycle == data_cycle,
                    )
                sub_q = sub_q.order_by(
                    FundIndicatorGroup.datetime.desc(),
                ).limit(1).subquery()

                query = quant_session.query(FundIndicatorGroup).filter(
                    FundIndicatorGroup.datetime == sub_q.c.latest_time,
                )
                if data_cycle:
                    query = query.filter(
                        FundIndicatorGroup.data_cycle == data_cycle,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundIndicatorGroup.__tablename__}')

    def get_fund_score_extended_by_id(self, fund_id, data_cycle: str = '1Y'):
        with DerivedDatabaseConnector().managed_session() as quant_session:
            try:
                query = quant_session.query(
                    FundScoreExtended,
                ).filter(
                    FundScoreExtended.fund_id == fund_id,
                    FundScoreExtended.data_cycle == data_cycle,
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundScoreExtended.__tablename__}')
                return pd.DataFrame([])

    def get_latest_fund_score_new_by_id(self, fund_id, data_cycle: str = '1Y'):
        with DerivedDatabaseConnector().managed_session() as quant_session:
            try:
                query = quant_session.query(
                    FundScoreNew,
                ).filter(
                    FundScoreNew.fund_id == fund_id,
                    FundScoreNew.data_cycle == data_cycle,
                ).order_by(
                    FundScoreNew.datetime.desc()
                ).limit(1)

                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundScoreNew.__tablename__}')
                return pd.DataFrame([])

    def get_fund_score_extended(self, start_date: str, end_date: str, fund_list: Tuple[str] = (), columns: Tuple[str] = (), data_cycle: str = '1Y'):
        with DerivedDatabaseConnector().managed_session() as quant_session:
            try:
                if columns:
                    query = quant_session.query(
                        FundScoreExtended.fund_id,
                        FundScoreExtended.datetime,
                    )
                    query = query.add_columns(*columns)
                else:
                    query = quant_session.query(
                        FundScoreExtended,
                    )
                if fund_list:
                    query = query.filter(
                        FundScoreExtended.fund_id.in_(fund_list)
                    )
                query = query.filter(
                    FundScoreExtended.datetime >= start_date,
                    FundScoreExtended.datetime <= end_date,
                    FundScoreExtended.data_cycle == data_cycle,
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundScoreExtended.__tablename__}')

    def get_fund_score_extended_for_ranks(self, start_date: str, end_date: str, fund_list: Tuple[str] = ()):
        return self.get_fund_score_extended(start_date, end_date, fund_list=fund_list, columns=['wind_class_1', 'return_score', 'robust_score', 'timing_score', 'return_rank', 'robust_rank', 'timing_rank'])

    def get_index_valuation_develop(self, index_ids, start_date, end_date):
        with DerivedDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    IndexValuationLongTerm
                ).filter(
                    IndexValuationLongTerm.index_id.in_(index_ids),
                    IndexValuationLongTerm.datetime >= start_date,
                    IndexValuationLongTerm.datetime <= end_date,
                ).order_by(IndexValuationLongTerm.datetime.asc())
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {IndexValuationLongTerm.__tablename__}')
                return pd.DataFrame([])

    def get_index_pair(self):
        index_val = {'PE':'pe_ttm_nn','PB':'pb_mrq','ROE':'roe'}
        return index_val

    def get_index_val_info(self):
        index_info = BasicDataApi().get_index_info()
        desc_df = index_info.set_index('index_id').to_dict()['desc_name']
        info_dic = {
            'A股指数':['sse50','hs300','csi500','gem_50'],
            '港股指数':['hsi','hsi_stateown','hsi_ita','hsi_china25','hsi_mssize','hsi_shkscne','hsi_intertec'],
            '风格指数':['csi300_growth','csi300_value','csi_grow500','csi_v500','csi800_value','csi800_growth'],
        }
        info_list = ['行业指数','主题指数']
        asset_info = BasicDataApi().get_asset_info_by_type(info_list)
        result = []
        for asset_id, index_list in info_dic.items():
            dic = {'title':asset_id,'items':[]}
            for index_id in index_list:
                _dic = {
                    'id':index_id,
                    'name':desc_df[index_id],
                }
                dic['items'].append(_dic)
            result.append(dic)

        for asset_id in info_list:
            _df = asset_info[asset_info.asset_type == asset_id]
            dic = {'title':asset_id,'items':[]}
            for i in _df.itertuples():
                _dic = {
                    'id':i.real_id,
                    'name':i.asset_name,
                }
                dic['items'].append(_dic)
            result.append(dic)
        index_val = self.get_index_pair()
        data = {'index_group':result,'index_val':list(index_val.keys())}
        return data

    def get_index_valuation_with_period(self, begin_date, end_date, time_para, index_list, valuation_type='PE'):
        index_val = valuation_type
        data_type = f'{index_val}估值'
        inputs_dic = self.get_index_pair()
        columns = [inputs_dic[index_val]]
        
        begin_date, end_date = RawDataApi().get_date_range(time_para, begin_date, end_date)
        with DerivedDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    IndexValuationLongTerm.index_id,
                    IndexValuationLongTerm.datetime,
                ).add_columns(*columns).filter(
                    IndexValuationLongTerm.index_id.in_(index_list),
                    IndexValuationLongTerm.datetime >= begin_date,
                    IndexValuationLongTerm.datetime <= end_date,
                ).order_by(IndexValuationLongTerm.datetime.asc())
                df = pd.read_sql(query.statement, query.session.bind)
                l = df.columns.tolist()
                value_col = [i for i in l if i not in ['datetime','index_id']][0]
                index_info = BasicDataApi().get_index_info(index_list)
                desc_dic = index_info.set_index('index_id').to_dict()['desc_name']
                df = df.pivot_table(columns='index_id',values=value_col,index='datetime')
                _df = df.copy()
                _df = _df.replace(0,np.nan)
                df.loc['中位数',:] = _df.median()
                df.loc['最大值',:] = _df.max()
                df.loc['最小值',:] = _df.min()
                df.loc['现值',:] = _df.ffill().iloc[-1]
                df = df.rename(columns=desc_dic)
                
                df = df.loc[['中位数','最大值','最小值','现值']].round(2)   
                cols = df.columns.tolist()
                name_dic = {i:i.replace('(申万)','') for i in cols}
                df = df.rename(columns=name_dic).rename(columns={'HKCTMT人民币':'沪港通TMT'}) 
                return {'data':df,'title':data_type}
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {IndexValuationLongTerm.__tablename__}')
                return pd.DataFrame([])

    def get_index_valuation_last_date(self, dt, index_ids=[]):
        with DerivedDatabaseConnector().managed_session() as db_session:
            try:
                dt = db_session.query(
                    func.max(IndexValuationLongTerm.datetime)).filter(
                            IndexValuationLongTerm.index_id.in_(index_ids), 
                            IndexValuationLongTerm.datetime <= dt,
                ).one_or_none()[0]
                query = db_session.query(IndexValuationLongTerm).filter(
                        IndexValuationLongTerm.datetime == dt,
                        IndexValuationLongTerm.index_id.in_(index_ids),
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {IndexValuationLongTerm.__tablename__}')
                return pd.DataFrame([])

    def get_index_valuation_develop_without_date(self, index_ids):
        with DerivedDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    IndexValuationLongTerm
                ).filter(
                    IndexValuationLongTerm.index_id.in_(index_ids),
                ).order_by(IndexValuationLongTerm.datetime.asc())
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {IndexValuationLongTerm.__tablename__}')
                return pd.DataFrame([])

    def get_index_valuation_develop_columns_by_id(self, index_id, columns):
        with DerivedDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    *columns
                ).filter(
                    IndexValuationLongTerm.index_id == index_id,
                ).order_by(IndexValuationLongTerm.datetime.asc())
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {IndexValuationLongTerm.__tablename__}')
                return pd.DataFrame([])

    def delete_index_valuation(self, date_to_delete: datetime.date, index_id_list: List[str]) -> bool:
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    IndexValuationLongTerm
                ).filter(
                    IndexValuationLongTerm.index_id.in_(index_id_list),
                    IndexValuationLongTerm.datetime == date_to_delete,
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {IndexValuationLongTerm.__tablename__}')
                return False

    def get_asset_allocation_info(self, version:int=2):
        with DerivedDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    AssetAllocationInfo
                ).filter(
                    AssetAllocationInfo.version == version
                ).order_by(AssetAllocationInfo.allocation_id)
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {AssetAllocationInfo.__tablename__}')
                return pd.DataFrame([])

    def get_style_factor_return(self, start_date: str, end_date: str, index_list: Tuple[str] = ()):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    StyleAnalysisFactorReturn
                )
                if index_list:
                    query = query.filter(StyleAnalysisFactorReturn.universe_index.in_(index_list))
                query = query.filter(
                    StyleAnalysisFactorReturn.datetime >= start_date,
                    StyleAnalysisFactorReturn.datetime <= end_date,
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {StyleAnalysisFactorReturn.__tablename__}')
                return

    def get_barra_cne5_factor_return(self, start_date: str, end_date: str):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    BarraCNE5FactorReturn
                ).filter(
                    BarraCNE5FactorReturn.datetime >= start_date,
                    BarraCNE5FactorReturn.datetime <= end_date,
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {BarraCNE5FactorReturn.__tablename__}')
                return

    def get_allocation_distribution(self, version:str=1):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    AllocationDistribution
                ).filter(
                    AllocationDistribution.version == version
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {AllocationDistribution.__tablename__}')
                return

    def get_fund_manager_index(self, manager_id: Tuple[str] = (), start_date: str = '', end_date: str = '', fund_type: Tuple[str] = ()):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    FundManagerIndex
                )
                if manager_id:
                    query = query.filter(FundManagerIndex.manager_id.in_(manager_id))
                if start_date:
                    query = query.filter(FundManagerIndex.datetime >= start_date)
                if end_date:
                    query = query.filter(FundManagerIndex.datetime <= end_date)
                if fund_type:
                    query = query.filter(FundManagerIndex.fund_type.in_(fund_type))
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundManagerIndex.__tablename__}')

    def get_fund_manager_score(self, manager_id: Tuple[str] = (), start_date: str = '', end_date: str = '', fund_type: Tuple[str] = ()):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    FundManagerScore
                )
                if manager_id:
                    query = query.filter(FundManagerScore.manager_id.in_(manager_id))
                if start_date:
                    query = query.filter(FundManagerScore.datetime >= start_date)
                if end_date:
                    query = query.filter(FundManagerScore.datetime <= end_date)
                if fund_type:
                    query = query.filter(FundManagerScore.fund_type.in_(fund_type))
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundManagerScore.__tablename__}')

    def get_latest_fund_style_box(self):
        with DerivedDatabaseConnector().managed_session() as mn_session:
            try:
                sub_q = mn_session.query(
                    StyleBox.fund_id.label('temp_id'),
                    func.max(StyleBox.datetime).label('temp_date'),
                ).group_by(StyleBox.fund_id).subquery()

                query = mn_session.query(
                    StyleBox.fund_id,
                    StyleBox.x,
                    StyleBox.y,
                    StyleBox.datetime,
                ).filter(
                    StyleBox.fund_id == sub_q.c.temp_id,
                    StyleBox.datetime == sub_q.c.temp_date
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_latest_fund_style_box {e} from {StyleBox.__tablename__}')
                return

    def get_funds_latest_fund_style_box(self, fund_list:Tuple[str]):
        # x： 0 价值型 40 平衡型 60 成长型 100
        # y： 0 小盘 25 中盘 50 大盘 100
        with DerivedDatabaseConnector().managed_session() as mn_session:
            try:
                sub_q = mn_session.query(
                    StyleBox.fund_id.label('temp_id'),
                    func.max(StyleBox.datetime).label('temp_date'),
                ).filter(
                    StyleBox.fund_id.in_(fund_list),
                ).group_by(StyleBox.fund_id).subquery()

                query = mn_session.query(
                    StyleBox.fund_id,
                    StyleBox.x,
                    StyleBox.y,
                    StyleBox.datetime,
                ).filter(
                    StyleBox.fund_id == sub_q.c.temp_id,
                    StyleBox.datetime == sub_q.c.temp_date
                )
                df = pd.read_sql(query.statement, query.session.bind)
                df['x'] = df['x'].map(lambda x: 0 if x < 0 else x)
                df['x'] = df['x'].map(lambda x: 300 if x > 300 else x)
                df['y'] = df['y'].map(lambda y: 0 if y < 0 else y)
                df['y'] = df['y'].map(lambda y: 400 if y > 400 else y)
                df['x'] = df['x'] / 3
                df['y'] = df['y'] / 4
                return df
            except Exception as e:
                print(f'Failed to get_latest_fund_style_box {e} from {StyleBox.__tablename__}')
                return

    def get_fund_style_box(self, fund_id: Tuple[str] = (), datetime: str = ''):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    StyleBox
                )
                if fund_id:
                    query = query.filter(
                        StyleBox.fund_id.in_(fund_id),
                    )
                if datetime:
                    query = query.filter(
                        StyleBox.datetime == datetime,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_fund_style_box {e} from {StyleBox.__tablename__}')
                return

    def get_new_share_fund_rank(self):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    NewShareFundRank
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_new_share_fund_rank {e} from {NewShareFundRank.__tablename__}')
                return

    def get_convertible_bond_fund_rank(self):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    ConvertibleBondFundRank
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_convertible_bond_fund_rank {e} from {ConvertibleBondFundRank.__tablename__}')
                return

    def get_abs_return_fund_rank(self):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    AbsReturnFundRank
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_abs_return_fund_rank {e} from {AbsReturnFundRank.__tablename__}')
                return

    def delete_fund_style_box(self, date_to_delete: datetime.date, fund_list: List[str]):
        with DerivedDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    StyleBox
                ).filter(
                    StyleBox.fund_id.in_(fund_list),
                    StyleBox.datetime == date_to_delete,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {StyleBox.__tablename__}')

    def get_fund_manager_info(self, mng_list: Tuple[str] = (), fund_list: Tuple[str] = (), columns: Tuple[str] = ()):
        with DerivedDatabaseConnector().managed_session() as quant_session:
            try:
                if columns:
                    query = quant_session.query(
                        FundManagerInfo.mng_id,
                        FundManagerInfo.start_date,
                        FundManagerInfo.fund_id,
                    ).add_columns(*columns)
                else:
                    query = quant_session.query(
                        FundManagerInfo,
                    )
                if mng_list:
                    query = query.filter(
                        FundManagerInfo.mng_id.in_(mng_list),
                    )
                if fund_list:
                    query = query.filter(
                        FundManagerInfo.fund_id.in_(fund_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundManagerInfo.__tablename__}')

    def get_market_portfolio_indicator(self):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    ThirdPartyPortfolioIndicator
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_market_portfolio_indicator {e} from {ThirdPartyPortfolioIndicator.__tablename__}')
                return pd.DataFrame([])

    def get_market_portfolio_info(self):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    ThirdPartyPortfolioInfo
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_market_portfolio_info {e} from {ThirdPartyPortfolioInfo.__tablename__}')
                return pd.DataFrame([])

    def get_market_portfolio_trade_dates(self, po_id):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    ThirdPartyPortfolioTrade.datetime
                ).filter(
                    ThirdPartyPortfolioTrade.po_id == po_id,
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_market_portfolio_trade_dates {e} from {ThirdPartyPortfolioTrade.__tablename__}')
                return pd.DataFrame([])

    def get_market_portfolio_trade_by_date(self, po_id, date):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    ThirdPartyPortfolioTrade
                ).filter(
                    ThirdPartyPortfolioTrade.po_id == po_id,
                    ThirdPartyPortfolioTrade.datetime == date,
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_market_portfolio_trade_by_date {e} from {ThirdPartyPortfolioTrade.__tablename__}')
                return pd.DataFrame([])

    def get_market_portfolio_position(self, po_id):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    ThirdPartyPortfolioPositionLatest
                ).filter(
                    ThirdPartyPortfolioPositionLatest.po_id == po_id,
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_market_portfolio_position {e} from {ThirdPartyPortfolioPositionLatest.__tablename__}')
                return pd.DataFrame([])

    def get_market_portfolio_position_by_src(self, po_srcs: Tuple[int] = ()):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    ThirdPartyPortfolioPositionLatest
                )
                if po_srcs:
                    query = query.filter(
                        ThirdPartyPortfolioPositionLatest.po_src.in_(po_srcs),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_market_portfolio_position_by_src {e} from {ThirdPartyPortfolioPositionLatest.__tablename__}')
                return

    def get_stock_factor_info(self):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    StockFactorInfo
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_stock_factor_info {e} from {StockFactorInfo.__tablename__}')
                return

    def get_fund_industry_exposure(self, fund_id):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                sub_q = session.query(
                    FundIndicatorGroup.datetime.label('latest_time'),
                ).order_by(
                    FundIndicatorGroup.datetime.desc(),
                ).limit(1).subquery()

                query = session.query(
                    FundIndustryExposure
                ).filter(
                    FundIndustryExposure.fund_id == fund_id,
                    FundIndustryExposure.datetime == sub_q.c.latest_time,
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_fund_industry_exposure {e} from {FundIndicatorGroup.__tablename__}')
                return pd.DataFrame([])

    def get_fof_nav(self, manager_id: str, fof_id_list: Tuple[str] = ()):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    FOFNav,
                ).filter(
                    FOFNav.manager_id == manager_id,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFNav.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_nav <err_msg> {e} from {FOFNav.__tablename__}')

    def delete_fof_nav(self, manager_id: str, fof_id: str, date_list: List[datetime.date]) -> bool:
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    FOFNav
                ).filter(
                    FOFNav.manager_id == manager_id,
                    FOFNav.fof_id == fof_id,
                    FOFNav.datetime.in_(date_list),
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {FOFNav.__tablename__}')
                return False

    def get_fof_nav_public(self, fof_id_list: Tuple[str] = ()):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    FOFNavPublic,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFNavPublic.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_nav_public <err_msg> {e} from {FOFNavPublic.__tablename__}')

    def get_fof_nav_public_adj(self, fof_id_list:Tuple[str], start_date:str='', end_date:str=''):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    FOFNavPublic,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFNavPublic.fof_id.in_(fof_id_list),
                    )
                if start_date:
                    query = query.filter(
                        FOFNavPublic.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        FOFNavPublic.datetime <= end_date,
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                dic = {
                    'fof_id':'fund_id',
                    'datetime':'datetime',
                    'adjusted_nav':'nav',
                }
                df = df[list(dic.keys())].rename(columns=dic)
                return df
            except Exception as e:
                print(f'failed to get_fof_nav_public_adj <err_msg> {e} from {FOFNavPublic.__tablename__}')

    def get_fof_nav_public_adj_dt(self, start_date:str='', end_date:str=''):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    FOFNavPublic,
                )
                if start_date:
                    query = query.filter(
                        FOFNavPublic.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        FOFNavPublic.datetime <= end_date,
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                dic = {
                    'fof_id':'fund_id',
                    'datetime':'datetime',
                    'adjusted_nav':'nav',
                }
                df = df[list(dic.keys())].rename(columns=dic)
                return df
            except Exception as e:
                print(f'failed to get_fof_nav_public_adj_dt <err_msg> {e} from {FOFNavPublic.__tablename__}')

    def delete_fof_nav_public(self, fof_id_to_delete: str, datetime_list: Tuple[str]):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    FOFNavPublic
                ).filter(
                    FOFNavPublic.fof_id == fof_id_to_delete,
                    FOFNavPublic.datetime.in_(datetime_list),
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {FOFNavPublic.__tablename__}')
                return False

    def get_fof_nav_calc(self, manager_id, fof_id_list: Tuple[str] = ()):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    FOFNavCalc,
                ).filter(
                    FOFNavCalc.manager_id == manager_id,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFNavCalc.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_nav_calc <err_msg> {e} from {FOFNavCalc.__tablename__}')

    def delete_fof_nav_calc(self, manager_id: str, fof_id: str, date_list: List[datetime.date]) -> bool:
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    FOFNavCalc
                ).filter(
                    FOFNavCalc.manager_id == manager_id,
                    FOFNavCalc.fof_id == fof_id,
                    FOFNavCalc.datetime.in_(date_list),
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {FOFNavCalc.__tablename__}')
                return False

    def get_fof_nav_unconfirmed(self, manager_id, fof_id_list: Tuple[str] = ()):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    FOFUnconfirmedNav,
                ).filter(
                    FOFUnconfirmedNav.manager_id == manager_id,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFUnconfirmedNav.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_nav_unconfirmed <err_msg> {e} from {FOFUnconfirmedNav.__tablename__}')

    def delete_fof_nav_unconfirmed(self, manager_id: str, fof_id: str, date_list: List[datetime.date]) -> bool:
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    FOFUnconfirmedNav
                ).filter(
                    FOFUnconfirmedNav.manager_id == manager_id,
                    FOFUnconfirmedNav.fof_id == fof_id,
                    FOFUnconfirmedNav.datetime.in_(date_list),
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {FOFUnconfirmedNav.__tablename__}')
                return False

    def get_fof_position(self, manager_id: str, fof_id_list: Tuple[str] = ()):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    FOFPosition,
                ).filter(
                    FOFPosition.manager_id == manager_id,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFPosition.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_position <err_msg> {e} from {FOFPosition.__tablename__}')

    def delete_fof_position(self, manager_id: str, fof_id: str, date_list: List[datetime.date]) -> bool:
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    FOFPosition
                ).filter(
                    FOFPosition.manager_id == manager_id,
                    FOFPosition.fof_id == fof_id,
                    FOFPosition.datetime.in_(date_list),
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {FOFPosition.__tablename__}')
                return False

    def get_fof_investor_data(self, manager_id: str, fof_id_list: Tuple[str] = ()):
        with DerivedDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFInvestorData,
                ).filter(
                    FOFInvestorData.manager_id == manager_id,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFInvestorData.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_investor_data <err_msg> {e} from {FOFInvestorData.__tablename__}')

    def delete_fof_investor_data(self, manager_id: str, fof_id_to_delete: str, investor_id_list: List[str]) -> bool:
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    FOFInvestorData
                ).filter(
                    FOFInvestorData.fof_id == fof_id_to_delete,
                    FOFInvestorData.manager_id == manager_id,
                    FOFInvestorData.investor_id.in_(investor_id_list),
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {FOFInvestorData.__tablename__}')
                return False

    def get_fof_position_detail(self, manager_id: str, fof_id_list: Tuple[str] = ()):
        with DerivedDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFPositionDetail,
                ).filter(
                    FOFPositionDetail.manager_id == manager_id,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFPositionDetail.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_position_detail <err_msg> {e} from {FOFPositionDetail.__tablename__}')

    def delete_fof_position_detail(self, manager_id: str, fof_id_to_delete: str, fund_id_list: List[str]) -> bool:
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    FOFPositionDetail
                ).filter(
                    FOFPositionDetail.fof_id == fof_id_to_delete,
                    FOFPositionDetail.manager_id == manager_id,
                    FOFPositionDetail.fund_id.in_(fund_id_list),
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {FOFPositionDetail.__tablename__}')
                return False

    def get_hedge_fund_investor_pur_redemp(self, manager_id: str, fof_id_list: Tuple[str] = ()):
        with DerivedDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    HedgeFundInvestorPurAndRedemp,
                ).filter(
                    HedgeFundInvestorPurAndRedemp.manager_id == manager_id,
                )
                if fof_id_list:
                    query = query.filter(
                        HedgeFundInvestorPurAndRedemp.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_hedge_fund_investor_pur_redemp <err_msg> {e} from {HedgeFundInvestorPurAndRedemp.__tablename__}')

    def get_hedge_fund_investor_pur_redemp_by_id(self, id: int):
        with DerivedDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    HedgeFundInvestorPurAndRedemp,
                ).filter(
                    HedgeFundInvestorPurAndRedemp.id == id,
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_hedge_fund_investor_pur_redemp_by_id <err_msg> {e} from {HedgeFundInvestorPurAndRedemp.__tablename__}')

    def delete_hedge_fund_investor_pur_redemp(self, id_to_delete: int) -> bool:
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    HedgeFundInvestorPurAndRedemp
                ).filter(
                    HedgeFundInvestorPurAndRedemp.id == id_to_delete,
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {HedgeFundInvestorPurAndRedemp.__tablename__}')
                return False

    def get_hedge_fund_investor_div_carry(self, manager_id: str, fof_id_list: Tuple[str] = ()):
        with DerivedDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    HedgeFundInvestorDivAndCarry,
                ).filter(
                    HedgeFundInvestorDivAndCarry.manager_id == manager_id,
                )
                if fof_id_list:
                    query = query.filter(
                        HedgeFundInvestorDivAndCarry.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_hedge_fund_investor_div_carry <err_msg> {e} from {HedgeFundInvestorDivAndCarry.__tablename__}')

    def get_hedge_fund_investor_div_carry_by_id(self, id: int):
        with DerivedDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    HedgeFundInvestorDivAndCarry,
                ).filter(
                    HedgeFundInvestorDivAndCarry.id == id,
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_hedge_fund_investor_div_carry_by_id <err_msg> {e} from {HedgeFundInvestorDivAndCarry.__tablename__}')

    def delete_hedge_fund_investor_div_carry(self, id_to_delete: int) -> bool:
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    HedgeFundInvestorDivAndCarry
                ).filter(
                    HedgeFundInvestorDivAndCarry.id == id_to_delete,
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {HedgeFundInvestorDivAndCarry.__tablename__}')
                return False

    def get_hedge_fund_custodian_data(self, manager_id: str, fof_id_list: Tuple[str] = ()):
        with DerivedDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    HedgeFundCustodianData,
                )
                if fof_id_list:
                    query = query.filter(
                        HedgeFundCustodianData.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_hedge_fund_custodian_data <err_msg> {e} from {HedgeFundCustodianData.__tablename__}')

    def get_pf_indicator(self, pf_id_list:Tuple[str], start_date:str='', end_date:str=''):
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    PfIndicator,
                )
                if pf_id_list:
                    query = query.filter(
                        PfIndicator.pf_id.in_(pf_id_list),
                    )
                if start_date:
                    query = query.filter(
                        PfIndicator.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        PfIndicator.datetime <= end_date,
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'failed to get_pf_indicator <err_msg> {e} from {PfIndicator.__tablename__}')

            
    def delete_hedge_fund_custodian_data(self, manager_id: str, fof_id: str, datetime) -> bool:
        with DerivedDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    HedgeFundCustodianData
                ).filter(
                    HedgeFundCustodianData.manager_id == manager_id,
                    HedgeFundCustodianData.fof_id == fof_id,
                    HedgeFundCustodianData.datetime == datetime,
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {HedgeFundCustodianData.__tablename__}')
                return False

    def get_style_factor_ret(self, begin_date, end_date, time_para, index_list=['hs300']):
        try:
            start_date, end_date = RawDataApi().get_date_range(time_para, begin_date, end_date)
            df = self.get_style_factor_return(start_date, end_date, [index_list])
            dic = {
                'latest_size':'规模',
                'bp':'价值',
                'short_term_momentum':'短期动量',
                'long_term_momentum':'长期动量',
                'high_low':'波动率',
            }
            df = df.set_index('datetime')[['latest_size','bp','short_term_momentum','long_term_momentum','high_low','const']]
            df = df[list(dic.keys())].rename(columns=dic)
            df = (df+1).cumprod()
            df = df/df.iloc[0] - 1
            df.index.name = 'datetime'
            return df
        except Exception as e:
            print(f'failed to get data <err_msg> {e} from derived.get_style_factor_ret')
            return False

    def get_industry_stock_ret_and_size(self, begin_date, end_date, time_para, index_id='all_a'):
        try:
            def process_x(x):
                x.loc[:,'weight'] = x['size'] / x['size'].sum()
                x = x[x.weight >= 0.03]
                return x
            # load data
            today = datetime.date.today()
            _b_d = today - datetime.timedelta(days=90)
            raw_api = RawDataApi()
            basic_api = BasicDataApi()
            begin_date, end_date = raw_api.get_date_range(time_para, begin_date, end_date)
            stock_df = raw_api.get_em_stock_info()
            industry_df = raw_api.get_em_industry_info()
            stock_df = stock_df[stock_df.list_date < _b_d]
            if index_id == 'all_a':
                stock_list = stock_df.stock_id.to_list()
            else:
                df = raw_api.get_em_index_component(index_list=[index_id])
                stock_list = df.stock_list.dropna().iloc[-1].split(',')
            total_share = raw_api.get_em_daily_info_last_date(stock_list=stock_list,columns=['total_share'])
            stock_price = raw_api.get_em_stock_price(start_date=begin_date, end_date=end_date,stock_list=stock_list,columns=['close'])

            # data_clean
            industry_dic_name = industry_df.set_index('em_id').to_dict()['ind_name']
            stock_df = stock_df[['stock_id','name','bl_sws_ind_code']].dropna()
            stock_df.loc[:,'industry_1'] = stock_df.bl_sws_ind_code.map(lambda x: x.split('-')[0])
            stock_df.loc[:,'industry_2'] = stock_df.bl_sws_ind_code.map(lambda x: x.split('-')[1])
            stock_df = stock_df.drop(columns=['bl_sws_ind_code']).set_index('stock_id')
            stock_df.loc[:,'industry_1_name'] = stock_df.industry_1.map(industry_dic_name)
            stock_df.loc[:,'industry_2_name'] = stock_df.industry_2.map(industry_dic_name)
            total_share = total_share.pivot_table(index='stock_id',columns='datetime',values='total_share')
            total_share.columns = ['total_share']
            last_date = sorted(stock_price.datetime.unique().tolist())[-1]
            last_price = stock_price[stock_price['datetime'] == last_date]
            size_df = last_price.set_index('stock_id')[['close']].join(total_share).dropna()
            size_df.loc[:,'size'] = size_df.close*size_df.total_share
            stock_df = stock_df.join(size_df).copy()
            stock_df = stock_df.groupby('industry_2').apply(lambda x: process_x(x))
            stock_df = stock_df.drop(columns=['industry_2']).reset_index().set_index('stock_id')

            indus_size_1 = stock_df[['industry_1','size']].groupby('industry_1').sum()
            indus_size_2 = stock_df[['industry_2','size']].groupby('industry_2').sum()
            stock_price = stock_price.pivot_table(index='datetime',columns='stock_id',values='close').ffill()
            stock_ret = pd.DataFrame(stock_price.iloc[-1] / stock_price.iloc[0] - 1)
            stock_ret.columns=['stock_ret']
            stock_df = stock_df.join(stock_ret).dropna()
            industry_list = indus_size_1.index.tolist() + indus_size_2.index.tolist()
            index_info = basic_api.get_index_info_by_em_id(em_id_list=industry_list)
            industry_dic = index_info.set_index('index_id').to_dict()['em_id']
            index_list = list(industry_dic.keys())
            industry_price = basic_api.get_index_price_dt(start_date=begin_date,end_date=end_date,index_list=index_list,columns=['close'])
            industry_price = industry_price.pivot_table(columns='index_id',values='close',index='datetime').ffill()
            industry_price = industry_price.rename(columns=industry_dic)
            indus_ret = pd.DataFrame(industry_price.iloc[-1] / industry_price.iloc[0] - 1)
            indus_ret.columns= ['industry_ret']
            indus_size_1 = indus_size_1.join(indus_ret).dropna()
            indus_size_2 = indus_size_2.join(indus_ret).dropna()
            indus_size_1.loc[:,'industry_1_name'] = indus_size_1.index.map(industry_dic_name)
            indus_size_2.loc[:,'industry_2_name'] = indus_size_2.index.map(industry_dic_name)
            _df = stock_df.reset_index().set_index('industry_2')[['industry_1']]
            _df = _df[~_df.index.duplicated(keep='first')]
            indus_size_2 = indus_size_2.join(_df)
            data = {
                '股票收益':stock_df,
                '行业一级收益':indus_size_1,
                '行业二级收益':indus_size_2,
            }
            return data
        except Exception as e:
            print(f'failed to get data <err_msg> {e} from derived.get_industry_stock_ret_and_size')
            return False
        
    def get_all_industry_val(self, begin_date, end_date, time_para, value_type='估值',industry_type='一级行业'):
        try:
            industry_type_dic = {
                '一级行业':1,
                '二级行业':2
            }
            dic = {
                'pb_mrq':'PB',
                'roe':'ROE'
            }
            raw_api = RawDataApi()
            begin_date, end_date = raw_api.get_date_range(time_para, begin_date, end_date)
            industry_info_raw = RawDataApi().get_em_industry_info(ind_class_type=industry_type_dic[industry_type])
            em_id_raw = industry_info_raw.em_id.tolist()
            index_info = BasicDataApi().get_index_info_by_em_id(em_id_list=em_id_raw)
            index_info.desc_name = index_info.desc_name.map(lambda x: x.replace('(申万)',''))
            index_ids = index_info.index_id.tolist()
            asset_name = index_info.set_index('index_id').to_dict()['desc_name']
            if value_type == '估值':
                df = self.get_index_valuation_last_date(dt=end_date, index_ids=index_ids)
                df = df.set_index('index_id')[dic.keys()].rename(columns=dic).round(2)
                df.loc[:,'desc_name'] = df.index.map(asset_name)
                df = df.reset_index(drop=True)
            elif value_type == '估值分位':
                df = DerivedDataApi().get_index_valuation_develop(end_date=end_date,start_date=begin_date,index_ids=index_ids)
                index_pb = df.pivot_table(index='datetime',columns='index_id',values='pb_mrq')
                index_roe = df.pivot_table(index='datetime',columns='index_id',values='roe')
                pb_rank = index_pb.rank(pct=True, axis=0).iloc[-1]
                pb_rank.name = 'PB'
                roe_rank = index_roe.rank(pct=True, axis=0).iloc[-1]
                roe_rank.name = 'ROE'
                df = pd.concat([pb_rank, roe_rank],axis=1)
                df.loc[:,'desc_name'] = df.index.map(asset_name)
            
            df = df.replace({np.Inf:np.nan,-np.Inf:np.nan}).dropna()
            _x = df.ROE.values
            x = sm.add_constant(_x)
            y = df.PB.values
            model = regression.linear_model.OLS(y,x).fit()
            c = model.params[0]
            k = model.params[1]
            x_array = np.arange(min(_x),max(_x), (max(_x)-min(_x))/100)
            y_array = k*x_array + c
            df_line = pd.DataFrame({'ROE':x_array,'PB':y_array,}).round(2)
            df['PB'] = df['PB'].round(2)
            df['ROE'] = df['ROE'].round(2)
            data = {
                '散点':df,
                '虚线':df_line,
            }
            return data
        except Exception as e:
            print(f'failed to get data <err_msg> {e} from derived.get_all_industry_val')
            return False

    def index_val_history_info(self):   
        try:
            asset_list = ['行业指数','主题指数']
            index_info = BasicDataApi().get_asset_info_by_type(asset_list)
            result = {'大类资产':[['hs300','沪深300'],['csi500','中证500'],['gem','创业板']]}
            for asset_id in asset_list:
                _dfi = index_info[index_info['asset_type'] == asset_id]
                result[asset_id]=[]
                for r in _dfi.itertuples():
                    result[asset_id].append([r.real_id,r.asset_name])
            return result
        except Exception as e:
            print(f'failed to get data <err_msg> {e} from derived.index_val_history_info')
            return False

    def stock_debt_val_info(self):
        index_list = ['sse50','hs300','csi500','csi1000','gem']
        index_info = BasicDataApi().get_index_info(index_list)
        index_info = [{'id':r.index_id, 'name':r.desc_name} for r in index_info.itertuples()]
        valuation_type = [{'id':'PE','name':'风险溢价'},{'id':'DY','name':'股息率溢价'}]
        debt_ret_list = [   {'id':'TB_1Y','name':'1年国债收益率'},
                            {'id':'TB_3Y','name':'3年国债收益率'},
                            {'id':'TB_5Y','name':'5年国债收益率'},
                            {'id':'TB_10Y','name':'10年国债收益率'}]
        data = {
            '股指':index_info,
            '溢价方式':valuation_type,
            '债指':debt_ret_list,
        }
        return data

    def get_industry_stock_ret_and_size_v2(index_id, begin_date, end_date, time_para):
        try:
            def process_x(x):
                x.loc[:,'weight'] = x['size'] / x['size'].sum()
                x = x[x.weight >= 0.03]
                return x
            # load data
            today = datetime.date.today()
            _b_d = today - datetime.timedelta(days=90)
            raw_api = RawDataApi()
            basic_api = BasicDataApi()
            begin_date, end_date = raw_api.get_date_range(time_para, begin_date, end_date)
            df = raw_api.get_em_index_component(index_list=index_id)
            stock_list1 = df.stock_list.dropna()[0].split(',')
            stock_df = raw_api.get_em_stock_info(stock_list1)
            industry_df = raw_api.get_em_industry_info()
            stock_df = stock_df[stock_df.list_date < _b_d]
            stock_list = stock_df.stock_id.to_list()
            total_share = raw_api.get_em_daily_info_last_date(stock_list=stock_list,columns=['total_share'] )
            stock_price = raw_api.get_em_stock_price(start_date=begin_date, end_date=end_date,
                                                        stock_list=stock_list,columns=['close'])

            # data_clean
            industry_dic_name = industry_df.set_index('em_id').to_dict()['ind_name']
            stock_df = stock_df[['stock_id','name','bl_sws_ind_code']].dropna()
            stock_df.loc[:,'industry_1'] = stock_df.bl_sws_ind_code.map(lambda x: x.split('-')[0])
            stock_df.loc[:,'industry_2'] = stock_df.bl_sws_ind_code.map(lambda x: x.split('-')[1])
            stock_df = stock_df.drop(columns=['bl_sws_ind_code']).set_index('stock_id')
            stock_df.loc[:,'industry_1_name'] = stock_df.industry_1.map(industry_dic_name)
            stock_df.loc[:,'industry_2_name'] = stock_df.industry_2.map(industry_dic_name)
            total_share = total_share.pivot_table(index='stock_id',columns='datetime',values='total_share')
            total_share.columns = ['total_share']
            last_date = sorted(stock_price.datetime.unique().tolist())[-1]
            last_price = stock_price[stock_price['datetime'] == last_date]
            size_df = last_price.set_index('stock_id')[['close']].join(total_share).dropna()
            size_df.loc[:,'size'] = size_df.close*size_df.total_share
            stock_df = stock_df.join(size_df).copy()
            stock_df = stock_df.groupby('industry_2').apply(lambda x: process_x(x))
            stock_df = stock_df.drop(columns=['industry_2']).reset_index().set_index('stock_id')

            indus_size_1 = stock_df[['industry_1','size']].groupby('industry_1').sum()
            indus_size_2 = stock_df[['industry_2','size']].groupby('industry_2').sum()
            stock_price = stock_price.pivot_table(index='datetime',columns='stock_id',values='close').ffill()
            stock_ret = pd.DataFrame(stock_price.iloc[-1] / stock_price.iloc[0] - 1)
            stock_ret.columns=['stock_ret']
            stock_df = stock_df.join(stock_ret).dropna()
            industry_list = indus_size_1.index.tolist() + indus_size_2.index.tolist()
            index_info = basic_api.get_index_info_by_em_id(em_id_list=industry_list)
            industry_dic = index_info.set_index('index_id').to_dict()['em_id']
            index_list = list(industry_dic.keys())
            industry_price = basic_api.get_index_price_dt(start_date=begin_date,end_date=end_date,
                                                            index_list=index_list,columns=[IndexPrice.close])
            industry_price = industry_price.pivot_table(columns='index_id',values='close',index='datetime').ffill()
            industry_price = industry_price.rename(columns=industry_dic)
            indus_ret = pd.DataFrame(industry_price.iloc[-1] / industry_price.iloc[0] - 1)
            indus_ret.columns= ['industry_ret']
            indus_size_1 = indus_size_1.join(indus_ret).dropna()
            indus_size_2 = indus_size_2.join(indus_ret).dropna()
            indus_size_1.loc[:,'industry_1_name'] = indus_size_1.index.map(industry_dic_name)
            indus_size_2.loc[:,'industry_2_name'] = indus_size_2.index.map(industry_dic_name)
            _df = stock_df.reset_index().set_index('industry_2')[['industry_1']]
            _df = _df[~_df.index.duplicated(keep='first')]
            indus_size_2 = indus_size_2.join(_df)
            data = {
                '股票收益':stock_df,
                '行业一级收益':indus_size_1,
                '行业二级收益':indus_size_2,
            }
            return data
        except Exception as e:
            print(f'failed to get data <err_msg> {e} from derived.get_industry_stock_ret_and_size')
            return False


    def stock_debt_val_detail(self, index_id, valuation_type,debt_ret_index):
        try:
            dic = {
                'pe_ttm':'PE',
                'dy':'DY',
            }
            title_dic = {
                'PE':'风险溢价',
                'DY':'股息率溢价',
            }
            bond_yield = RawDataApi().get_em_macroeconomic_daily(codes=[debt_ret_index])
            index_risk = DerivedDataApi().get_index_valuation_develop_without_date(index_ids=[index_id])
            index_info = BasicDataApi().get_index_info([index_id])
            index_name = index_info.set_index('index_id').loc[index_id,'desc_name']

            index_risk = index_risk.set_index('datetime').rename(columns=dic)[[valuation_type]].join(bond_yield.set_index('datetime').rename(columns={'value':'debt_ret'})['debt_ret']).ffill()

            pctrank = lambda x: x.rank(pct=True).iloc[-1]
            if valuation_type == 'PE':
                index_risk.loc[:,'reverse_val'] = 1 / index_risk[valuation_type]
            else:
                index_risk.loc[:,'reverse_val'] = index_risk[valuation_type]
            index_risk.loc[:,'debt_ret'] = index_risk.debt_ret / 100
            index_risk.loc[:,'risk_value'] = index_risk.reverse_val - index_risk.debt_ret

            min_periods = int(3*242)
            window = index_risk.shape[0]
            window= 5 * 242
            index_risk['risk_values_pct'] = index_risk.risk_value.rolling(window=window, min_periods=min_periods).apply(pctrank, raw=False)
            index_col_pct = 'risk_values_pct'
            index_col = 'risk_value'
            diff = 0.00
            a1 = index_risk[index_risk[index_col_pct] >= (0.90 - diff)][[index_col]].rename(columns={index_col:'区间分位最高10%'})
            a2 = index_risk[(index_risk[index_col_pct] <= (0.90 + diff))&(index_risk[index_col_pct] >= 0.7-diff)][[index_col]].rename(columns={index_col:'区间分位最高30%'})
            a3 = index_risk[(index_risk[index_col_pct] <= (0.7 + diff))&(index_risk[index_col_pct] >= 0.3-diff)][[index_col]].rename(columns={index_col:'中间区间分位'})
            a4 = index_risk[(index_risk[index_col_pct] <= 0.3+diff)&(index_risk[index_col_pct] >= 0.05-diff)][[index_col]].rename(columns={index_col:'区间分位最低30%'})
            a5 = index_risk[(index_risk[index_col_pct] <= 0.1+diff)][[index_col]].rename(columns={index_col:'区间分位最低10%'})
            am = pd.DataFrame(index_risk[index_col].rolling(window=window,min_periods=min_periods).mean())
            am.columns=['均值']
            df = pd.concat([a1,a2,a3,a4,a5,am],axis=1).sort_index().dropna(axis=0,how='all')
            df.index.name = 'datetime'
            
            cols = df.columns.tolist()
            cols = [i for i in cols if i != '均值']
            for col in cols:
                df_i = df[[col]].copy()
                df_i.loc[:,'con'] = df_i[col].isnull()
                df_i.loc[:,'last_con'] = df_i[col].shift(-1).isnull()
                dts = df_i[( ~df_i.con) & (df_i.last_con)].index.tolist()
                for i in dts:
                    if df.loc[i:].shape[0] == 1:
                        continue
                    else:
                        i = df.loc[i:].index[1]
                        df.loc[i,col] = index_risk.risk_value.loc[i]
            
            title = index_name +title_dic[valuation_type]
            data = {
                'data':df,
                'title':title,
            }
            return data
        except Exception as e:
            print(f'failed to get data <err_msg> {e} from derived.stock_debt_val_detail')
            return False

    def industry_beta(self,begin_date, end_date, time_para):
        try:
            begin_date, end_date = RawDataApi().get_date_range(time_para, begin_date, end_date)
            index_info = BasicDataApi().get_asset_info_by_type(['行业指数'])
            index_ids = index_info.real_id.tolist()
            df = DerivedDataApi().get_index_valuation_develop(index_ids=index_ids,start_date=begin_date,end_date=end_date)
            pb_df = df.pivot_table(index='datetime',values='pb_mrq',columns='index_id')
            roe_df = df.pivot_table(index='datetime',values='roe',columns='index_id')   
            result = []
            dt_list = pb_df.index.tolist()
            for idx, dt, in enumerate(dt_list):
                if idx % 5 != 0:
                    continue
                _x = roe_df.loc[dt].dropna()
                x = sm.add_constant(_x)
                y = np.log(pb_df.loc[dt].dropna())
                model = regression.linear_model.OLS(y,x).fit()
                beta = model.params[1]
                result.append({'datetime':dt,'beta':beta})
            _df = pd.DataFrame(result).set_index('datetime')
            index_price = BasicDataApi().get_index_price_dt(start_date=_df.index[0],end_date=_df.index[-1],index_list=['hs300'])
            index_price = index_price.pivot_table(index='datetime',values='close',columns='index_id')
            _df = _df.join(index_price).ffill().reset_index()
            return _df
        except Exception as e:
            print(f'failed to get data <err_msg> {e} from derived.stock_debt_val_detail')
            return False

    def get_fund_type_classification(self):
        with DerivedDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundTypeClassification)
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fund_type_classification <err_msg> {e} from {FundTypeClassification.__tablename__}')


