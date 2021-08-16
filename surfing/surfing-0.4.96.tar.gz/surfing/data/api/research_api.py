import time
from surfing.data.api.raw import *
from surfing.data.api.basic import *
from surfing.data.api.derived import *
from surfing.data.view.TL_models import *
from surfing.data.wrapper.mysql import TLDatabaseConnector, TestDatabaseConnector
from surfing.data.view.test_models import *
class ResearchApi(metaclass=Singleton):
    
    def get_index_quote(self,start_date,end_date, index_ids):
        """指数行情查询接口"""
        try:
            with BasicDatabaseConnector().managed_session() as db_session:
                rename_dic = {
                    'total_turnover': 'amount',
                }
                query = db_session.query(
                        IndexPrice.index_id,
                        IndexPrice.datetime,
                        IndexPrice.open,
                        IndexPrice.high,
                        IndexPrice.low,
                        IndexPrice.close,
                        IndexPrice.volume,
                        IndexPrice.total_turnover
                        
                    ).filter(
                        IndexPrice.index_id.in_(index_ids),
                        IndexPrice.datetime >= start_date, #根据日期筛选数据
                        IndexPrice.datetime <= end_date
                    )           
                df1 = pd.read_sql(query.statement, query.session.bind).rename(columns=rename_dic)
                
            with RawDatabaseConnector().managed_session() as db_session:
                rename_dic = {
                    'index_date':'datetime',
                }
                query = db_session.query(
                        HFIndexPrice.index_id,
                        HFIndexPrice.index_date,
                        HFIndexPrice.close
                    ).filter(
                        HFIndexPrice.index_id.in_(index_ids),
                        HFIndexPrice.index_date >= start_date, #根据日期筛选数据
                        HFIndexPrice.index_date <= end_date
                    )
                df2 = pd.read_sql(query.statement, query.session.bind).rename(columns=rename_dic) 
                
            with TestDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                        PfIndexPrice.index_id,
                        PfIndexPrice.datetime,
                        PfIndexPrice.close
                    ).filter(
                        PfIndexPrice.index_id.in_(index_ids),
                        PfIndexPrice.datetime >= start_date, #根据日期筛选数据
                        PfIndexPrice.datetime <= end_date
                    )
                df3 = pd.read_sql(query.statement, query.session.bind).rename(columns=rename_dic) 
            df = pd.concat([df1, df2, df3])
            return df
        except Exception as e:
            print('Failed to get data <err_msg> {}'.format(e) + ' from BasicDataApi.get_index_price')
            return None
            
    def get_index_info(self, desc_name:list=[]):
        '''指数基本信息模糊查询接口'''
        try:
            with BasicDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                            IndexInfo.index_id,
                            IndexInfo.desc_name,
                            IndexInfo.em_id,
                        )
                for name_i in desc_name:
                    query = query.filter(
                            IndexInfo.desc_name.like(f'%{name_i}%')
                        )
                df1 = pd.read_sql(query.statement, query.session.bind)
                dic = {
                    'real_id':'index_id',
                    'real_name':'desc_name',
                    'asset_id':'em_id',
                }
                query = db_session.query(
                            AssetInfo.asset_id,
                            AssetInfo.real_name,
                            AssetInfo.real_id,
                )
                for name_i in desc_name:
                    query = query.filter(
                            AssetInfo.real_name.like(f'%{name_i}%')
                        )
                df2 = pd.read_sql(query.statement, query.session.bind)
                df2 = df2.rename(columns=dic)[dic.values()]
                
            with TestDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                            PfIndexInfo.index_id,
                            PfIndexInfo.desc_name,       
                )
                for name_i in desc_name:
                    query = query.filter(
                            PfIndexInfo.desc_name.like(f'%{name_i}%')
                        )
                df3 = pd.read_sql(query.statement, query.session.bind)
                df = pd.concat([df1,df2,df3])
                return df
                
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from {ResearchApi.get_index_info}')

    def get_index_info_by_id(self, index_list:list=[]):
        '''指数基本信息查询接口'''
        try:
            with BasicDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                            IndexInfo.index_id,
                            IndexInfo.desc_name,
                            IndexInfo.em_id,
                        ).filter(
                            IndexInfo.index_id.in_(index_list)
                        )
                df1 = pd.read_sql(query.statement, query.session.bind)
                dic = {
                    'real_id':'index_id',
                    'real_name':'desc_name',
                    'asset_id':'em_id',
                }
                query = db_session.query(
                            AssetInfo.asset_id,
                            AssetInfo.real_name,
                            AssetInfo.real_id,
                        ).filter(
                            AssetInfo.real_id.in_(index_list)
                        )
                df2 = pd.read_sql(query.statement, query.session.bind)
                df2 = df2.rename(columns=dic)[dic.values()]
                
            with TestDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                            PfIndexInfo.index_id,
                            PfIndexInfo.desc_name,       
                        ).filter(
                            PfIndexInfo.index_id.in_(index_list)
                        )
                df3 = pd.read_sql(query.statement, query.session.bind)
            df = pd.concat([df1,df2,df3])
            return df
                
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from {ResearchApi.get_index_info}')


    def get_index_component(self,index_id,start_date,end_date):
        '''指数成分股查询'''
        with RawDatabaseConnector().managed_session() as db_session:
            try: 
                    query = db_session.query(
                        EmIndexComponent
                    ).filter(
                        EmIndexComponent.index_id.in_([index_id]),
                        EmIndexComponent.datetime <= end_date, 
                        EmIndexComponent.datetime >= start_date
                        )
                    index_stocks = pd.read_sql(query.statement, query.session.bind)
                    return index_stocks                  
            except Exception as e:
                    print(f'Failed to get data <err_msg> {e} from {ResearchApi.get_index_component}')

    def get_index_fac(self, start_date, end_date, index_ids:list=[]):
        '''指数衍生数据查询接口'''
        with DerivedDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                            IndexValuationLongTerm.index_id,
                            IndexValuationLongTerm.datetime,
                            IndexValuationLongTerm.pb_mrq,
                            IndexValuationLongTerm.pe_ttm,
                            IndexValuationLongTerm.roe,
                            IndexValuationLongTerm.ps_ttm,
                            IndexValuationLongTerm.dy,
                            IndexValuationLongTerm.pcf_ttm,
                            IndexValuationLongTerm.est_peg,
                            IndexValuationLongTerm.eps_ttm,
                    )
 
                if index_ids:
                    query = query.filter(
                        IndexValuationLongTerm.index_id.in_(index_ids),
                    )
                if start_date:
                    query = query.filter(
                        IndexValuationLongTerm.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        IndexValuationLongTerm.datetime <= end_date,
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {ResearchApi.get_index_valuation_long_term}')                    
                    
    def get_fund_nav(self , start_date , end_date , fund_id_list):
        '''公募净值查询接口'''
        try:
            with BasicDatabaseConnector().managed_session() as db_session:
                rename_dic = {
                    'adjusted_net_value': 'unitnav',
                    'acc_net_value':'cumnav',
                    'adjusted_net_value':'adjnav',
                    'daily_profit':'mmf_unityield',
                    'PURCHSTATUS':'purchase_status',
                    'REDEMSTATUS':'redeem_status',
                }
                query = db_session.query(
                    FundNav.fund_id,
                    FundNav.datetime,
                    FundNav.adjusted_net_value,
                    FundNav.unit_net_value,
                    FundNav.acc_net_value,
                    FundNav.daily_profit,
                ).filter(
                    FundNav.fund_id.in_(fund_id_list),
                    FundNav.datetime >= start_date,
                    FundNav.datetime <= end_date,
                )
                df = pd.read_sql(query.statement, query.session.bind)
                res = []
                for fund_id in fund_id_list:
                    df_i = df[df.fund_id == fund_id].copy()
                    df_i.loc[:,'ret'] = df_i.adjusted_net_value.pct_change(1)
                    res.append(df_i)
                df = pd.concat(res).rename(columns=rename_dic).reset_index(drop=True)
                fund_ids = df.fund_id.unique().tolist()
                fund_ids = [fund_id.split('!')[0] for fund_id in fund_ids]

            with RawDatabaseConnector().managed_session() as db_session:     

                query = db_session.query(
                        EmFundStatus.CODES,
                        EmFundStatus.DATES,
                        EmFundStatus.PURCHSTATUS,
                        EmFundStatus.REDEMSTATUS
                    )
                cons = (EmFundStatus.CODES.like(f'%{fund_id}%') for fund_id in fund_ids)
                query = query.filter(or_(cons))
                fund_status = pd.read_sql(query.statement, query.session.bind)
                df.loc[:,'_fund_id'] = df.fund_id.map(lambda x :x.split('!')[0]) 
                fund_status.loc[:,'_fund_id'] = fund_status.CODES.map(lambda x: x.split('.')[0])
                fund_ids = df._fund_id.unique().tolist()
                res = []
                for fund_id in fund_ids:
                    df_x = df[df._fund_id == fund_id].copy()
                    df_y = fund_status[fund_status._fund_id == fund_id].copy().rename(columns={'DATES':'datetime'})[['datetime','PURCHSTATUS','REDEMSTATUS']]
                    df_i = pd.merge(df_x, df_y, on='datetime',how='outer').set_index('datetime').sort_index()
                    df_i[['PURCHSTATUS','REDEMSTATUS']] = df_i[['PURCHSTATUS','REDEMSTATUS']].ffill()
                    df_i = df_i.dropna(subset=['fund_id']).drop(labels=['_fund_id'], axis=1)
                    res.append(df_i)
                df = pd.concat(res).rename(columns=rename_dic).reset_index()
                return df
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from ResearchApi.get_fund_nav')
    
    def get_fund_asset_alloc(self , start_date , end_date , fund_id_list):
        '''公募基金持仓资产查询接口'''
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundHoldAsset.fund_id,
                    FundHoldAsset.datetime,
                    FundHoldAsset.stock_nav_ratio,
                    FundHoldAsset.bond_nav_ratio,
                    FundHoldAsset.fund_nav_ratio,
                    FundHoldAsset.cash_nav_ratio,
                    FundHoldAsset.other_nav_ratio,
                    FundHoldAsset.first_repo_to_nav,
                    FundHoldAsset.avg_ptm,
                    FundHoldAsset._update_time,
                ).filter(
                    FundHoldAsset.fund_id.in_(fund_id_list),
                    FundHoldAsset.datetime >= start_date,
                    FundHoldAsset.datetime <= end_date,
                )
                df = pd.read_sql(query.statement, query.session.bind)
                dts = pd.to_datetime(df._update_time)
                dts = [i.date() for i in dts]
                df['publish_date'] = dts
                df = df.drop(labels=['_update_time'], axis=1)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_fund_hold_asset')
                
    def get_fund_hold_stock(self , start_date , end_date , fund_id_list):
        '''公募基金持仓股票查询接口'''
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundHoldStock
                ).filter(
                    FundHoldStock.fund_id.in_(fund_id_list),
                    FundHoldStock.datetime >= start_date,
                    FundHoldStock.datetime <= end_date,
                )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns = ["_update_time"])
                df = df.dropna(subset=['rank1_stock']).reset_index(drop=True)
                common_cols = ['fund_id','datetime']
                res = []
                for idx in df.index:
                    for i in range(1,11):
                        rank_cols = [f'rank{i}_stock',f'rank{i}_stock_code',f'rank{i}_stockval',f'rank{i}_stockweight']
                        rank_dic = {_i:_i.replace(str(i),'') for _i in rank_cols}
                        _df = df.loc[[idx]][common_cols+rank_cols].rename(columns=rank_dic).copy()
                        _df['rank'] = str(i)
                        res.append(_df)
                df = pd.concat(res)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_fund_hold_stock')

    def get_fund_info(self, fund_id = None ,desc_name = None ,wind_class_1 = None ,wind_class_2 = None ,
                  company_id = None, start_date = None ,size = None ,manager_id = None):
        """公募产品基本信息查询接口"""
        
        def obscure_return(Connector,list_,col_name,que):
            """
            支持模糊查询的方法
            Connector : databse managed session
            list_ : 一个含有模糊或者准确信息字符组成的list
            col_name: 筛选条件对应在databse的columns name
            return 一个含有准确信息字符串组成的list
            """
            with Connector as db_session:
                            query = db_session.query(
                                    que
                                )       
                            df = pd.read_sql(query.statement, query.session.bind)
            bool_df = pd.DataFrame()
            for str_ in list_:
                bool_df[str_] = (df[col_name].str.contains(str_))
            result = list(set(df[bool_df.any(axis = 1)][col_name].values.tolist()))
            return result
    
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query_size = db_session.query(
                                Fund_size_and_hold_rate.size,
                                Fund_size_and_hold_rate.fund_id                           
                            )
                df_size = pd.read_sql(query_size.statement, query_size.session.bind)
                query = db_session.query(
                            FundInfo.fund_id,
                            FundInfo.desc_name,
                            FundInfo.wind_class_1,
                            FundInfo.wind_class_2,
                            FundInfo.company_id,
                            FundInfo.start_date,
                            FundInfo.manager_id, 
                            FundInfo.end_date,
                        )
                if(fund_id != None):
                    query = query.filter(
                        FundInfo.fund_id.in_(fund_id),
                    )
                if(desc_name != None):
                    desc_name = obscure_return(BasicDatabaseConnector().managed_session(),desc_name,
                                                       "desc_name",FundInfo.desc_name)#模糊查询
                    query = query.filter(
                        FundInfo.desc_name.in_(desc_name),
                    )
                if(wind_class_1 != None):
                    wind_class_1 = obscure_return(BasicDatabaseConnector().managed_session(),wind_class_1,
                                                       "wind_class_1",FundInfo.wind_class_1)
                    query = query.filter(
                        FundInfo.wind_class_1.in_(wind_class_1),
                    )
                if(wind_class_2 != None):
                    wind_class_2 = obscure_return(BasicDatabaseConnector().managed_session(),wind_class_2,
                                                       "wind_class_2",FundInfo.wind_class_2)
                    query = query.filter(
                        FundInfo.wind_class_2.in_(wind_class_2),
                    )
                if(company_id != None):
                    company_id = obscure_return(BasicDatabaseConnector().managed_session(),company_id,
                                                      "company_id",FundInfo.company_id)#模糊查询
                    query = query.filter(
                        FundInfo.company_id.in_(company_id),
                    )
                if(start_date != None):
                    query = query.filter(
                        FundInfo.start_date >= start_date
                    )
                if(manager_id != None):
                    manager_id = obscure_return(BasicDatabaseConnector().managed_session(),manager_id,
                                                      "manager_id",FundInfo.manager_id)#模糊查询
                    query = query.filter(
                        FundInfo.manager_id.in_(manager_id),
                    )
                    
                df = pd.read_sql(query.statement, query.session.bind)
                df_size = df_size.dropna(subset=['size'],axis = 0)
                df_size = df_size.drop_duplicates(subset='fund_id', keep="last")#这里选取最新的基金规模             
                result_df = pd.merge(df,df_size,how = 'left',on = 'fund_id') 
                if (size != None):
                    result_df = result_df[(result_df['size'] > size[0]) & (result_df['size'] < size[1])]
                return result_df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e) + " get_fund_info()")
                return None

    def get_stock_quote(self , start_date , end_date , stock_id_list):
        '''股票行情查询接口'''
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                #EmStockPrice
                post = 'post_'
                rename_dic = {
                    'open':f'{post}open',
                    'close':f'{post}close',
                    'high':f'{post}high',
                    'low':f'{post}low',
                }
                query = db_session.query(
                    EmStockPostPrice.CODES,
                    EmStockPostPrice.DATES,
                    EmStockPostPrice.OPEN,
                    EmStockPostPrice.CLOSE,
                    EmStockPostPrice.HIGH,
                    EmStockPostPrice.LOW,
                    EmStockPostPrice.TRADESTATUS
                ).filter(
                    EmStockPostPrice.CODES.in_(stock_id_list),
                    EmStockPostPrice.DATES >= start_date-datetime.timedelta(days=30),
                    EmStockPostPrice.DATES <= end_date,
                )
                df = pd.read_sql(query.statement, query.session.bind).set_index('datetime')
                df = df.rename(columns=rename_dic)
                query = db_session.query(
                    EmStockPrice.CODES,
                    EmStockPrice.DATES,
                    EmStockPrice.OPEN,
                    EmStockPrice.CLOSE,
                    EmStockPrice.HIGH,
                    EmStockPrice.LOW,
                    EmStockPrice.VOLUME,
                    EmStockPrice.AMOUNT,
                ).filter(
                    EmStockPrice.CODES.in_(stock_id_list),
                    EmStockPrice.DATES >= start_date,
                    EmStockPrice.DATES <= end_date,
                )
                _df = pd.read_sql(query.statement, query.session.bind).set_index('datetime')

                res = []
                for code in df.stock_id.unique():
                    df_i = df[df.stock_id == code].copy()
                    df_i['ret'] = df_i.post_close.pct_change(1)
                    df_i = df_i.loc[start_date:]
                    _df_i = _df[_df.stock_id == code][['open','close','high','low','volume','amount']]
                    df_i = df_i.join(_df_i).reset_index()
                    res.append(df_i)
                df = pd.concat(res)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_stock_quote')
                
    def get_macro_value(self, code_list, start_date, end_date):
        '''宏观数据获取'''
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        EmMacroEconomicMonthly.codes,
                        EmMacroEconomicMonthly.datetime,
                        EmMacroEconomicMonthly.value,
                    ).filter(
                        EmMacroEconomicMonthly.codes.in_(code_list),
                        EmMacroEconomicMonthly.datetime >= start_date,
                        EmMacroEconomicMonthly.datetime <= end_date,
                    )
                df1 = pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time", errors='ignore')
                query = db_session.query(
                        EmMacroEconomicDaily.codes,
                        EmMacroEconomicDaily.datetime,
                        EmMacroEconomicDaily.value,
                    ).filter(
                        EmMacroEconomicDaily.codes.in_(code_list),
                        EmMacroEconomicDaily.datetime >= start_date,
                        EmMacroEconomicDaily.datetime <= end_date,
                    )
                df2 = pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time", errors='ignore')
                df = pd.concat([df1, df2])
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_macro_value')

    def get_macro_info(self, code_list=None, desc_list=None):
        '''宏观信息'''
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        EmMacroEconomicInfo.codes,
                        EmMacroEconomicInfo.desc_name,
                    )
                if code_list:
                    query = query.filter(
                            EmMacroEconomicInfo.codes.in_(code_list),   
                        )
                if desc_list:    
                    for i in desc_list:
                        query = query.filter(
                            EmMacroEconomicInfo.desc_name.like(f'%{i}%')
                        )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_macro_info')

    def get_future_info(self, future_ids=None, trans_type_list=None):
        '''期货信息'''
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        EmFutureInfoDetail.EMCODE,
                        EmFutureInfoDetail.TRADINGCODE,
                        EmFutureInfoDetail.FTTRANSTYPE
                        )
                if future_ids:
                    query = query.filter(
                            EmFutureInfoDetail.EMCODE.in_(future_ids),   
                        )
                if trans_type_list:    
                    for i in trans_type_list:
                        query = query.filter(
                            EmFutureInfoDetail.FTTRANSTYPE.like(f'%{i}%')
                        )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_future_info')

    def get_future_quote(self, future_ids, start_date=None, end_date=None):
        '''期货行情'''
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        EmFuturePriceDetail.CODES,
                        EmFuturePriceDetail.DATES,
                        EmFuturePriceDetail.OPEN,
                        EmFuturePriceDetail.HIGH,
                        EmFuturePriceDetail.LOW,
                        EmFuturePriceDetail.CLOSE,
                        EmFuturePriceDetail.PRECLOSE,
                        EmFuturePriceDetail.AVERAGE,
                        EmFuturePriceDetail.VOLUME,
                        EmFuturePriceDetail.AMOUNT,
                        EmFuturePriceDetail.HQOI,
                        EmFuturePriceDetail.CLEAR,
                        EmFuturePriceDetail.PRECLEAR,
                    ).filter(
                        EmFuturePriceDetail.CODES.in_(future_ids),
                    )
                if start_date:
                    query = query.filter(
                        EmFuturePriceDetail.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmFuturePriceDetail.DATES <= end_date,
                    )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time", errors='ignore')
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_macro_value')

    def get_industry_info(self, industry_class):
        '''行业分类详情查询接口'''
        try:
            if industry_class == "sw":
                with RawDatabaseConnector().managed_session() as db_session:
                    query = db_session.query(
                        EmIndustryInfo
                    ).filter(
                    )
                    df = pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time", errors='ignore')
                with BasicDatabaseConnector().managed_session() as db_session:
                    query = db_session.query(
                        IndexInfo.em_id,
                        IndexInfo.index_id
                    ).filter(
                        IndexInfo.em_id.in_(df.em_id)
                    )
                    df_1 = pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time", errors='ignore')
                    df = pd.merge(df, df_1, on='em_id')
                    return df
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from ResearchApi.get_industry_info')
            
    def get_stock_info_concept(self, stock_id_list=None):
        '''股票申万\中信行业分类查询接口'''
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmStockConceptInfo
                )
                if stock_id_list:
                    query = query.filter(
                        EmStockConceptInfo.codes.in_(stock_id_list),
                    )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time").set_index("codes")
                
                query = db_session.query(
                    EmStockInfo
                )
                if stock_id_list:
                    query = query.filter(
                        EmStockInfo.CODES.in_(stock_id_list),
                    )
                df = df.join(pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time").set_index("stock_id")[["bl_sws_ind_code"]])
                df['bl_sws_ind_code'] = df['bl_sws_ind_code'].map(lambda x: x.split('-') if isinstance(x, str) else None)
                df = df.explode('bl_sws_ind_code')
                query = db_session.query(
                    EmIndustryInfo.em_id,
                    EmIndustryInfo.ind_name,
                ).filter(
                    EmIndustryInfo.em_id.in_(df.bl_sws_ind_code.unique().tolist())
                )
                _df = pd.read_sql(query.statement, query.session.bind).rename(columns={'em_id':'bl_sws_ind_code'})
                df = pd.merge(df.reset_index(),_df,on='bl_sws_ind_code')
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_stock_info_concept')
                
    def get_stock_fin(self , start_date , end_date , stock_id_list):
        '''股票财务数据查询接口'''
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmStockFinFac.CODES,
                    EmStockFinFac.DATES,
                    EmStockFinFac.ROEAVG,
                    EmStockFinFac.EPSDILUTED,
                    EmStockFinFac.BPS,
                    EmStockFinFac._update_time,
                ).filter(
                    EmStockFinFac.DATES >= start_date,
                    EmStockFinFac.DATES <= end_date,
                    EmStockFinFac.CODES.in_(stock_id_list),
                )
                df = pd.read_sql(query.statement, query.session.bind)
                dts = pd.to_datetime(df._update_time)
                dts = [i.date() for i in dts]
                df['publish_date'] = dts
                df = df.drop(labels=['_update_time'], axis=1)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_stock_price')
                
                
    def get_stock_fin_fac(self , start_date , end_date , stock_id_list):
        '''股票衍生数据查询接口'''
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmStockDailyInfo.CODES,
                    EmStockDailyInfo.DATES,
                    EmStockDailyInfo.PETTMDEDUCTED,
                    EmStockDailyInfo.PBLYRN,
                    EmStockDailyInfo.PSTTM,
                    EmStockDailyInfo.ESTPEG,
                    EmStockDailyInfo.EVWITHOUTCASH,
                ).filter(
                    EmStockDailyInfo.CODES.in_(stock_id_list),
                    EmStockDailyInfo.DATES >= start_date,
                    EmStockDailyInfo.DATES <= end_date,
                )
                df = pd.read_sql(query.statement, query.session.bind)#.drop(columns = "_update_time")
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_stock_price')
                
                
    def get_capital_north_south(self , capital_class , start_date , end_date):
        '''北上\南下资金数据查询接口'''
        if capital_class == "south":
            with RawDatabaseConnector().managed_session() as db_session:
                try:
                    query = db_session.query(
                        EMSouthCapital
                    ).filter(
                        EMSouthCapital.datetime >= start_date,
                        EMSouthCapital.datetime <= end_date,
                    )
                    df = pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time")
                    return df
                except Exception as e:
                    print(f'Failed to get data <err_msg> {e} from ResearchApi.get_stock_price')
        else:
            with RawDatabaseConnector().managed_session() as db_session:
                try:
                    query = db_session.query(
                        EMNorthCapital
                    ).filter(
                        EMNorthCapital.datetime >= start_date,
                        EMNorthCapital.datetime <= end_date,
                    )
                    df = pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time")
                    return df
                except Exception as e:
                    print(f'Failed to get data <err_msg> {e} from ResearchApi.get_stock_price')
                
    
    def get_pf_info(self,
                    record_cd=None, 
                    name_list=None, 
                    stg_name=None, 
                    stg_child=None, 
                    company_name=None,
                    start_date=None,
                    mng_name=None):
        '''私募产品基本信息查询接口'''
        with TLDatabaseConnector().managed_session() as db_session:
            # 主策略对应
            main_type_name = '私募基金投资策略' 
            _query = db_session.query(
                SysCode.VALUE_NAME_CN,
                SysCode.VALUE_NUM_CD,
            ).filter(
                SysCode.CODE_TYPE_NAME == main_type_name
            )
            df = pd.read_sql(_query.statement, _query.session.bind)
            main_stg_dic = df.set_index('VALUE_NAME_CN')['VALUE_NUM_CD'].to_dict()
            main_stg_dic_re = df.set_index('VALUE_NUM_CD')['VALUE_NAME_CN'].to_dict()
            # 子策略对应
            child_type_name = '私募基金投资子策略'
            query = db_session.query(
                SysCode.VALUE_NAME_CN,
                SysCode.VALUE_NUM_CD,
            ).filter(
                SysCode.CODE_TYPE_NAME == child_type_name
            )
            df = pd.read_sql(query.statement, query.session.bind)
            child_stg_dic = df.set_index('VALUE_NAME_CN')['VALUE_NUM_CD'].to_dict()
            child_stg_dic_re = df.set_index('VALUE_NUM_CD')['VALUE_NAME_CN'].to_dict()

            # 返回字段
            query = db_session.query(
                Pfund.RECORD_CD,
                Pfund.INVEST_STRATEGY,
                Pfund.INVEST_STRATEGY_CHILD,
                Pfund.INVEST_CONSULTANT,
                Pfund.ESTABLISH_DATE,
                Pfund.END_DATE,
                Pfund.MANAGER,
                Pfund.STATUS,
                Pfund.SECURITY_ID,
            )
            # 按照备案号
            if record_cd:
                query = query.filter(
                    Pfund.RECORD_CD.in_(record_cd),
                )
            # 按照关键字搜索
            if name_list:
                _query = db_session.query(
                    MdSecurity.SECURITY_ID,
                    MdSecurity.SEC_SHORT_NAME,
                ).filter(MdSecurity.ASSET_CLASS=='FP')
                for i in name_list:
                    _query = _query.filter(
                        MdSecurity.SEC_SHORT_NAME.like(f'%{i}%')
                    )
                asset_info_df = pd.read_sql(_query.statement, _query.session.bind)
                query = query.filter(
                    Pfund.SECURITY_ID.in_(asset_info_df.SECURITY_ID),
                )
            # 按照主策略
            if stg_name:

                stg_list = [main_stg_dic.get(i) for i in stg_name]
                query = query.filter(
                    Pfund.INVEST_STRATEGY.in_(stg_list),
                )
            # 按照子策略
            if stg_child:

                stg_list = [child_stg_dic.get(i) for i in stg_child]
                query = query.filter(
                    Pfund.INVEST_STRATEGY_CHILD.in_(stg_list),
                )
            # 按照公司名搜索
            if company_name:
                _query = db_session.query(
                    MdInstitution.PARTY_ID,
                    MdInstitution.PARTY_SHORT_NAME,
                )
                for i in company_name:
                    _query = _query.filter(
                        MdInstitution.PARTY_SHORT_NAME.like(f'%{i}%')
                    )
                asset_info_df = pd.read_sql(_query.statement, _query.session.bind)
                query = query.filter(
                    Pfund.INVEST_CONSULTANT.in_(asset_info_df.PARTY_ID.dropna().unique()),
                )    
            # 按照成立日期
            if start_date:
                query = query.filter(
                    Pfund.ESTABLISH_DATE > start_date,
                ) 
            # 按照基金经理
            if mng_name:
                cons = (Pfund.MANAGER.like(f'%{i}%') for i in mng_name)
                query = query.filter(or_(cons))
            df = pd.read_sql(query.statement, query.session.bind).dropna(subset=['RECORD_CD'])
            df.loc[:,'INVEST_STRATEGY'] = df.INVEST_STRATEGY.map(main_stg_dic_re)
            df.loc[:,'INVEST_STRATEGY_CHILD'] = df.INVEST_STRATEGY_CHILD.map(child_stg_dic_re)
            # 替换机构名
            _query = db_session.query(
                MdInstitution.PARTY_ID,
                MdInstitution.PARTY_SHORT_NAME,
            ).filter(MdInstitution.PARTY_ID.in_(df.INVEST_CONSULTANT))
            _df = pd.read_sql(_query.statement, _query.session.bind).dropna(subset=['PARTY_ID'])
            _df['PARTY_ID'] = _df['PARTY_ID'].astype(str)
            company_dic = _df.set_index('PARTY_ID')['PARTY_SHORT_NAME'].to_dict()
            df.loc[:,'INVEST_CONSULTANT'] = df.INVEST_CONSULTANT.map(lambda x: company_dic.get(x))

            # 替换基金全名
            _query = db_session.query(
                MdSecurity.SECURITY_ID,
                MdSecurity.SEC_SHORT_NAME,
            ).filter(MdSecurity.SECURITY_ID.in_(df.SECURITY_ID))
            _df = pd.read_sql(_query.statement, _query.session.bind)
            name_dic = _df.set_index('SECURITY_ID')['SEC_SHORT_NAME'].to_dict()
            df.loc[:,'SEC_FULL_NAME'] = df.SECURITY_ID.map(name_dic)
            df = df.drop(columns=['SECURITY_ID'])

            # 替换运作状态
            _query = db_session.query(
                SysCode.VALUE_NUM_CD,
                SysCode.VALUE_NAME_CN,
            ).filter(SysCode.CODE_TYPE_ID == '40034' )
            _df = pd.read_sql(_query.statement, _query.session.bind)
            name_dic = _df.set_index('VALUE_NUM_CD')['VALUE_NAME_CN'].to_dict()
            df['STATUS'] = df.STATUS.map(name_dic)
            return df

    def get_pf_info2(self, record_cd):
        '''私募产品要素查询接口''' 
        with TLDatabaseConnector().managed_session() as db_session:    
            # 返回字段
            query = db_session.query(
                Pfund.RECORD_CD,
                Pfund.INVEST_CONSULTANT,
                Pfund.CUSTODIAN,
                Pfund.SUBSCRIPTION_START_POINT,
                Pfund.MIN_ADD,
                Pfund.STOP_LOSS_LINE,
                Pfund.WARN_LINE,
                Pfund.ISSUE_FEE,
                Pfund.REDEEM_FEE,
                Pfund.MANAGEMENT_FEE,
                Pfund.PERFORMANECE_RETURN,
                Pfund.APPLY_FEE,
                Pfund.CUSTODY_FEE,
                Pfund.SECURITY_ID,
            ).filter(
                Pfund.RECORD_CD.in_(record_cd),
            )
            df = pd.read_sql(query.statement, query.session.bind)
            _query = db_session.query(
                MdSecurity.SECURITY_ID,
                MdSecurity.SEC_SHORT_NAME,
            ).filter(MdSecurity.SECURITY_ID.in_(df.SECURITY_ID))
            _df = pd.read_sql(_query.statement, _query.session.bind)
            name_dic = _df.set_index('SECURITY_ID')['SEC_SHORT_NAME'].to_dict()
            df.loc[:,'SEC_FULL_NAME'] = df.SECURITY_ID.map(name_dic)
            df = df.drop(columns=['SECURITY_ID'])
            return df

    def search_pf_info(self, record_cd=None,start_date=None,info_items=None,with_detail=False):
        '''私募信息搜索 '''
        try:
            res = [self.get_pf_info(record_cd=record_cd,name_list=info_i,start_date=start_date) for info_i in info_items ]
            df_name = pd.concat(res).drop_duplicates()

            res = [self.get_pf_info(record_cd=record_cd,stg_name=info_i,start_date=start_date) for info_i in info_items ]
            df_stg = pd.concat(res).drop_duplicates()

            res = [self.get_pf_info(record_cd=record_cd,stg_child=info_i,start_date=start_date) for info_i in info_items ]
            df_stg_chd = pd.concat(res).drop_duplicates()

            time.sleep(1) # 搜索量大， 抱错
            res = [self.get_pf_info(record_cd=record_cd,company_name=info_i,start_date=start_date) for info_i in info_items ]
            df_stg_cpy = pd.concat(res).drop_duplicates()

            res = [self.get_pf_info(record_cd=record_cd,mng_name=info_i,start_date=start_date) for info_i in info_items ]
            df_stg_mng = pd.concat(res).drop_duplicates()

            df = pd.concat([df_name,df_stg,df_stg_chd,df_stg_cpy,df_stg_mng]).drop_duplicates().reset_index(drop=True)
            if with_detail:
                _df = self.get_pf_info2(df.RECORD_CD)
                df = pd.merge(df, _df, on='RECORD_CD', how='outer')
            return df
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from ResearchApi.search_pf_info')

    def get_pf_inst_info(self, reg_cd=None,inst_name=None,key_person=None,scale_list=None):
        '''私募投顾基本信息查询接口'''
        inst_info_df = None
        inst_scale_df = None
        # 返回字段
        with TLDatabaseConnector().managed_session() as db_session:    
            # 返回字段
            query = db_session.query(
                PfundInstInfo.REG_CD,
                PfundInstInfo.PROFILE,
                PfundInstInfo.IDEA_STRATEGY,
                PfundInstInfo.KEY_PERSON,
                PfundInstInfo.PARTY_ID,
            )
        # 按照备案号
        if reg_cd:
            query = query.filter(
                PfundInstInfo.REG_CD.in_(reg_cd),
            )
        # 按照投顾名
        if inst_name:
            _query = db_session.query(
                PfundInstScaleAmac.PARTY_ID,
                PfundInstScaleAmac.PARTY_FULL_NAME,
            )
            for i in inst_name:
                _query = _query.filter(
                    PfundInstScaleAmac.PARTY_FULL_NAME.like(f'%{i}%')
                )
            inst_info_df = pd.read_sql(_query.statement, _query.session.bind)
            query = query.filter(
                PfundInstInfo.PARTY_ID.in_(inst_info_df.PARTY_ID.dropna().unique()),
            )    
        # 核心人物
        if key_person:
            for i in key_person:
                query = query.filter(
                    PfundInstInfo.KEY_PERSON.like(f'%{i}%'),
                )
        # 按照规模
        if scale_list:
            _query = db_session.query(
                PfundInstScaleAmac.PARTY_ID,
                PfundInstScaleAmac.SCALE,
            ).filter(
                PfundInstScaleAmac.SCALE.in_(scale_list)
            )
            inst_scale_df = pd.read_sql(_query.statement, _query.session.bind)
            query = query.filter(
                PfundInstInfo.PARTY_ID.in_(inst_scale_df.PARTY_ID.dropna().unique()),
            )    
        df = pd.read_sql(query.statement, query.session.bind)
        # 添加机构名
        if inst_info_df is None:
            _query = db_session.query(
                PfundInstScaleAmac.PARTY_ID,
                PfundInstScaleAmac.PARTY_FULL_NAME,
            ).filter(
                    PfundInstScaleAmac.PARTY_ID.in_(df.PARTY_ID.dropna().unique())
            )
            inst_info_df = pd.read_sql(_query.statement, _query.session.bind)
        full_name_dic = inst_info_df.dropna(subset=['PARTY_ID']).set_index('PARTY_ID')['PARTY_FULL_NAME'].to_dict()
        df.loc[:,'PARTY_FULL_NAME'] = df.PARTY_ID.map(full_name_dic)
        
        # 添加规模
        if inst_scale_df is None:
            _query = db_session.query(
                PfundInstScaleAmac.PARTY_ID,
                PfundInstScaleAmac.SCALE,
            ).filter(
                    PfundInstScaleAmac.PARTY_ID.in_(df.PARTY_ID.dropna().unique())
            )
            inst_scale_df = pd.read_sql(_query.statement, _query.session.bind)
        scale_dic = inst_scale_df.dropna(subset=['PARTY_ID']).set_index('PARTY_ID')['SCALE'].to_dict()
        df.loc[:,'SCALE'] = df.PARTY_ID.map(scale_dic)
        # 主策略统计
        main_type_name = '私募基金投资策略' 
        _query = db_session.query(
            SysCode.VALUE_NAME_CN,
            SysCode.VALUE_NUM_CD,
        ).filter(
            SysCode.CODE_TYPE_NAME == main_type_name
        )
        sys_df = pd.read_sql(_query.statement, _query.session.bind)
        #main_stg_dic = _df.set_index('VALUE_NAME_CN')['VALUE_NUM_CD'].to_dict()
        main_stg_dic_re = sys_df.set_index('VALUE_NUM_CD')['VALUE_NAME_CN'].to_dict()
        query = db_session.query(
                Pfund.RECORD_CD,
                Pfund.INVEST_STRATEGY,    
            ).filter(
            Pfund.INVEST_CONSULTANT.in_(df.PARTY_ID.unique()),
        )    
        _df = pd.read_sql(query.statement, query.session.bind)
        _df.loc[:,'VALUE_NAME_CN'] = _df.INVEST_STRATEGY.map(main_stg_dic_re)
        if not df.empty:
            main_stg = _df.groupby('VALUE_NAME_CN').count().sort_values('RECORD_CD').index[-1]
            df.loc[:,'MAIN_FUND_TYPE'] = main_stg
        else:
            df['MAIN_FUND_TYPE'] = ''
        return df

    def get_pf_nav(self, start_date=None, end_date=None, record_cds:list=[], source='tl'):
        '''私募净值查询接口'''
        try:
            # 通联
            if source == 'tl':
                with TLDatabaseConnector().managed_session() as db_session:                
                    query1 = db_session.query(
                        Pfund.SECURITY_ID,
                        Pfund.RECORD_CD,
                        ).filter(
                        Pfund.RECORD_CD.in_(record_cds)
                        )           
                    df1 = pd.read_sql(query1.statement, query1.session.bind)
                    security_ids = df1['SECURITY_ID'].values.tolist()
                    query = db_session.query(
                            PfundNav.END_DATE,
                            PfundNav.NAV,
                            PfundNav.ADJ_NAV,
                            PfundNav.ACCUM_NAV,
                            PfundNav.SECURITY_ID
                        )
                    if record_cds:
                        query = query.filter(
                            PfundNav.SECURITY_ID.in_(security_ids),
                        )
                    if start_date:
                        query = query.filter(
                            PfundNav.END_DATE >= start_date,
                        )
                    if end_date:
                        query = query.filter(
                            PfundNav.END_DATE <= end_date,
                        )
                    df = pd.read_sql(query.statement, query.session.bind)
                    df = pd.merge(df1, df, left_on='SECURITY_ID', right_on='SECURITY_ID')
            # 自己计算
            elif source == 'py_calc':
                with TLDatabaseConnector().managed_session() as db_session:                
                    query1 = db_session.query(
                        Pfund.SECURITY_ID,
                        Pfund.RECORD_CD,
                        ).filter(
                        Pfund.RECORD_CD.in_(record_cds)
                        )           
                    df1 = pd.read_sql(query1.statement, query1.session.bind)
                    security_id_dic = df1.set_index('RECORD_CD')['SECURITY_ID'].to_dict()
                with DerivedDatabaseConnector().managed_session() as db_session:
                    name_dic = {
                        's_id':'SECURITY_ID',
                        'fof_id':'RECORD_CD',
                        'datetime':'END_DATE',
                        'nav':'NAV',
                        'adjusted_nav':'ADJ_NAV',
                        'acc_net_value':'ACCUM_NAV',
                    }
                    query = db_session.query(
                            FOFNavCalc.fof_id,
                            FOFNavCalc.datetime,
                            FOFNavCalc.nav,
                            FOFNavCalc.acc_net_value,
                            FOFNavCalc.adjusted_nav,
                        ).filter(
                            FOFNavCalc.fof_id.in_(record_cds),
                            FOFNavCalc.manager_id == "py1",
                        )
                    if start_date:
                        query = query.filter(
                            FOFNavCalc.datetime >= start_date,
                        )
                    if end_date:
                        query = query.filter(
                            FOFNavCalc.datetime <= end_date,
                        )
                    df = pd.read_sql(query.statement, query.session.bind)
                    df.loc[:,'s_id'] = df.fof_id.map(security_id_dic)
                    df = df.rename(columns=name_dic)[name_dic.values()]
            # 客服发送
            elif source == 'py':
                with TLDatabaseConnector().managed_session() as db_session:                
                    query1 = db_session.query(
                        Pfund.SECURITY_ID,
                        Pfund.RECORD_CD,
                        ).filter(
                        Pfund.RECORD_CD.in_(record_cds)
                        )           
                    df1 = pd.read_sql(query1.statement, query1.session.bind)
                    security_id_dic = df1.set_index('RECORD_CD')['SECURITY_ID'].to_dict()
                with DerivedDatabaseConnector().managed_session() as db_session:
                    name_dic = {
                        's_id':'SECURITY_ID',
                        'fof_id':'RECORD_CD',
                        'datetime':'END_DATE',
                        'nav':'NAV',
                        'adjusted_nav':'ADJ_NAV',
                        'acc_net_value':'ACCUM_NAV',
                    }
                    query = db_session.query(
                            FOFNav.fof_id,
                            FOFNav.datetime,
                            FOFNav.nav,
                            FOFNav.acc_net_value,
                            FOFNav.adjusted_nav,
                        ).filter(
                            FOFNav.fof_id.in_(record_cds),
                            FOFNav.manager_id == "py1",
                        )
                    if start_date:
                        query = query.filter(
                            FOFNav.datetime >= start_date,
                        )
                    if end_date:
                        query = query.filter(
                            FOFNav.datetime <= end_date,
                        )
                    df = pd.read_sql(query.statement, query.session.bind)
                    df.loc[:,'s_id'] = df.fof_id.map(security_id_dic)
                    df = df.rename(columns=name_dic)[name_dic.values()]
            return df

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from {ResearchApi.get_pfund_nav}')

    def get_stock_post_price(self,stock_list,start_date,end_date):
        '''获取股票后复权股价'''
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmStockPostPrice.CLOSE,
                    EmStockPostPrice.DATES,
                    EmStockPostPrice.CODES

                ).filter(
                    EmStockPostPrice.CODES.in_(stock_list),
                    EmStockPostPrice.DATES >= start_date,
                    EmStockPostPrice.DATES <= end_date 
                    )
                stock_price = pd.read_sql(query.statement, query.session.bind)
                return stock_price
            except Exception as e:
                    print(f'Failed to get data <err_msg> {e} from {ResearchApi.get_stock_post_price}')


    def get_trading_date(self, asset_type='cn_stock', start_date=None, end_date=None):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        TradingDayList
                    )
                if start_date:
                    query = query.filter(
                        TradingDayList.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        TradingDayList.datetime <= end_date,
                    )
                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {TradingDayList.__tablename__}')


if __name__ == '__main__':
    start_date = datetime.date(2019,1,1)
    end_date = datetime.date(2021,2,1)

    # 私募 信息 
    record_cd = ['SE1387','SE1383']
    #name_list = ['黑翼','CTA']
    #stg_name = ['股票策略']
    #stg_child = ['主观套利','指数增强']
    #company_name = ['黑翼']
    #start_date = datetime.date(2020,1,1)
    #mng_name = ['蒋彤','蒋锦志']
    # 选填
    ResearchApi().get_pf_info(record_cd=record_cd)

    # 私募净值
    record_cds = ['SE1387','SE1383']
    df = ResearchApi().get_pf_nav(record_cds=record_cds,
                                start_date=start_date,
                                end_date=end_date)
                            