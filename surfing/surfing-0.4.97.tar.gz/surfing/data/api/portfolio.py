from typing import Tuple, List

import pandas as pd
import datetime
from sqlalchemy import func
import numpy as np
from .raw import RawDataApi
from .basic import BasicDataApi
from .derived import DerivedDataApi
from ...util.singleton import Singleton
from ...util.calculator_item import CalculatorBase
from ...util.calculator import Calculator

TRADE_HISTORY_TEMP = [
    {
        'datetime':datetime.date(2018,12,4),
        'fund_weight':[
            {
                'fund_id':'005267!0',
                'weight':0.2,
                'fund_type':'低估价值',
            },
            {
                'fund_id':'166005!0',
                'weight':0.1,
                'fund_type':'成长价值',
            },
            {
                'fund_id':'006551!0',
                'weight':0.1,
                'fund_type':'稳态红利',
            },
            {
                'fund_id':'090010!0',
                'weight':0.15,
                'fund_type':'稳态红利',
            },
            {
                'fund_id':'003396!0',
                'weight':0.15,
                'fund_type':'低估价值',
            },
            {
                'fund_id':'161005!0',
                'weight':0.15,
                'fund_type':'稳态红利',
            },
            {
                'fund_id':'005827!0',
                'weight':0.15,
                'fund_type':'成长价值',
            },
            
        ]
    },
    {
        'datetime':datetime.date(2021,3,2),
        'fund_weight':[
            {
                'fund_id':'005267!0',
                'weight':0.2,
                'fund_type':'低估价值',
            },
            {
                'fund_id':'166005!0',
                'weight':0.2,
                'fund_type':'成长价值',
            },
            {
                'fund_id':'006551!0',
                'weight':0.2,
                'fund_type':'稳态红利',
            },
            {
                'fund_id':'090010!0',
                'weight':0.1,
                'fund_type':'稳态红利',
            },
            {
                'fund_id':'003396!0',
                'weight':0.1,
                'fund_type':'低估价值',
            },
            {
                'fund_id':'161005!0',
                'weight':0.1,
                'fund_type':'稳态红利',
            },
            {
                'fund_id':'118001!0',
                'weight':0.1,
                'fund_type':'成长价值',
            },
            
        ]
    },
]

BENCHMARK_INFO = {
    '稳态红利':'csi_dvi',
    '成长价值':'csi300_value',
    '低估价值':'csi_retval',    
}



class PortfolioDataApi(metaclass=Singleton):

    def get_all_fund_info(self, fund_list=None):
        try:
            mutual_fund_list = [_ for _ in fund_list if '!' in _]
            hedge_fund_list = [_ for _ in fund_list if '!' not in _]
            mutual_fund_info = pd.DataFrame()
            hedge_fund_info = pd.DataFrame()
            if len(mutual_fund_list) > 0:
                mutual_fund_info = BasicDataApi().get_fund_info(fund_list=mutual_fund_list)[['fund_id','desc_name']]
                mutual_fund_info.loc[:,'fund_type'] = '公募'    
            if len(hedge_fund_list) > 0:
                hedge_fund_info = BasicDataApi().get_fof_info_strategy_exsit(fof_id_list=hedge_fund_list)[['fof_id','fof_name']].rename(columns={'fof_id':'fund_id','fof_name':'desc_name'})
                hedge_fund_info.loc[:,'fund_type'] = '私募'
            df_list = [i for i in [mutual_fund_info, hedge_fund_info] if not i.empty ]
            fund_info = pd.concat(df_list)
            return fund_info

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_all_fund_info')

    def get_part_fund_info(self, fund_list=None):
        try:
            mutual_fund_list = [_ for _ in fund_list if '!' in _]
            hedge_fund_list = [_ for _ in fund_list if '!' not in _]
            hedge_fund_info = pd.DataFrame()
            mutual_fund_info = pd.DataFrame()
            if len(mutual_fund_list) > 0:
                mutual_fund_info = BasicDataApi().get_fund_info(fund_list=mutual_fund_list)[['fund_id','desc_name']]
                mutual_fund_info.loc[:,'fund_type'] = '公募'    
            if len(hedge_fund_list) > 0:
                hedge_fund_info = BasicDataApi().get_fof_info_strategy_exsit(fof_id_list=hedge_fund_list)[['fof_id','fof_name']].rename(columns={'fof_id':'fund_id','fof_name':'desc_name'})
                hedge_fund_info.loc[:,'fund_type'] = '私募'
            df_list = [i for i in [mutual_fund_info, hedge_fund_info] if not i.empty ]
            fund_info = pd.concat(df_list)
            return fund_info

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_part_fund_info')


    def get_all_fund_nav(self, start_date=None, end_date=None, fund_list: Tuple[str] = ()):
        try:
            if start_date is None:
                _start_date = ''
            else:
                _start_date = start_date-datetime.timedelta(days=40)
            end_date = end_date if end_date is not None else ''
            mutual_fund_nav = pd.DataFrame()
            hedge_fund_nav = pd.DataFrame
            #print(f'start_date {start_date} end_date {end_date} fund_list {fund_list}')
            if len(fund_list) > 0:
                mutual_fund_list = [_ for _ in fund_list if '!' in _]
                hedge_fund_list = [_ for _ in fund_list if '!' not in _]
                if len(mutual_fund_list) > 0:
                    mutual_fund_nav = BasicDataApi().get_fund_nav_with_date(start_date=_start_date,end_date=end_date,fund_list=mutual_fund_list)
                if len(hedge_fund_list) > 0:
                    hedge_fund_nav = DerivedDataApi().get_fof_nav_public_adj(fof_id_list=hedge_fund_list, start_date=_start_date, end_date=end_date)
            else:
                mutual_fund_nav = BasicDataApi().get_fund_nav_with_date(start_date=_start_date,end_date=end_date)
                hedge_fund_nav = DerivedDataApi().get_fof_nav_public_adj_dt(start_date=_start_date, end_date=end_date)
            
            if not mutual_fund_nav.empty:
                mutual_fund_nav = mutual_fund_nav.pivot_table(index='datetime',columns='fund_id',values='adjusted_net_value')
                dts = BasicDataApi().get_trading_day_list(start_date=mutual_fund_nav.index[0]).datetime
                mutual_fund_nav = mutual_fund_nav.reindex(mutual_fund_nav.index.intersection(dts)).ffill()

            if not hedge_fund_nav.empty:
                hedge_fund_nav = hedge_fund_nav.pivot_table(index='datetime',columns='fund_id',values='nav')
            df_list = [i for i in [mutual_fund_nav, hedge_fund_nav] if not i.empty ]
            if isinstance(start_date, str):
                fund_nav = pd.concat(df_list, axis=1).sort_index().ffill()
            else:
                fund_nav = pd.concat(df_list, axis=1).sort_index().ffill().loc[start_date:]
            fund_nav.index.name = 'datetime'
            return fund_nav

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_all_fund_nav')

    def get_all_fund_nav_(self, start_date=None, end_date=None, fund_list: Tuple[str] = ()):
        try:
            if start_date is None:
                _start_date = ''
            else:
                _start_date = start_date-datetime.timedelta(days=40)
            end_date = end_date if end_date is not None else ''
            mutual_fund_nav = pd.DataFrame()
            hedge_fund_nav = pd.DataFrame
            #print(f'start_date {start_date} end_date {end_date} fund_list {fund_list}')
            if len(fund_list) > 0:
                mutual_fund_list = [_ for _ in fund_list if '!' in _]
                hedge_fund_list = [_ for _ in fund_list if '!' not in _]
                if len(mutual_fund_list) > 0:
                    mutual_fund_nav = BasicDataApi().get_fund_nav_with_date(start_date=_start_date,end_date=end_date,fund_list=mutual_fund_list)
                if len(hedge_fund_list) > 0:
                    hedge_fund_nav = RawDataApi().get_hf_fund_nav(fund_ids=hedge_fund_list, start_date=_start_date, end_date=end_date)
            else:
                mutual_fund_nav = BasicDataApi().get_fund_nav_with_date(start_date=_start_date,end_date=end_date)
                hedge_fund_nav = RawDataApi().get_hf_fund_nav_dt(start_date=_start_date, end_date=end_date)

            if not mutual_fund_nav.empty:
                mutual_fund_nav = mutual_fund_nav.pivot_table(index='datetime',columns='fund_id',values='adjusted_net_value')
            if not hedge_fund_nav.empty:
                hedge_fund_nav = hedge_fund_nav.pivot_table(index='datetime',columns='fund_id',values='nav')
            df_list = [i for i in [mutual_fund_nav, hedge_fund_nav] if not i.empty ]
            if isinstance(start_date, str):
                fund_nav = pd.concat(df_list, axis=1)
                fund_nav = fund_nav.reindex(fund_nav.index.union([start_date])).sort_index().ffill()
            else:
                fund_nav = pd.concat(df_list, axis=1)
                fund_nav = fund_nav.reindex(fund_nav.index.union([start_date])).sort_index().ffill().loc[start_date:]
            fund_nav.index.name = 'datetime'
            return fund_nav

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_all_fund_nav')



    def trade_history_parse(self, trade_history):
        try:
            fund_type = {}
            order_list = []
            for dic in trade_history:
                dt = dic['datetime']
                _dic = {dt:{}}
                for trade_i in dic['fund_weight']:
                    type_i = trade_i['fund_type'] 
                    fund_id = trade_i['fund_id']
                    weight = trade_i['weight']
                    _dic[dt][fund_id]=weight
                    if type_i not in fund_type:
                        fund_type[type_i] = [fund_id]
                    elif type_i in fund_type and fund_id not in fund_type[type_i]:
                        fund_type[type_i].append(fund_id)
                    else:
                        pass
                order_list.append(_dic)
            return order_list, fund_type

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.trade_history_parse')

    def get_portfolio_nav(self, trade_history):
        try:
            order_list, fund_type = self.trade_history_parse(trade_history)
            fund_list = set(list([j for dic in order_list for i in dic.values() for j in i.keys()]))
            hf_fund_con = any(['!' not in _fund_id for _fund_id in fund_list])
            _begin_date = min([j for i in order_list for j in i.keys()])
            fund_nav = self.get_all_fund_nav(start_date=_begin_date,fund_list=fund_list)
            if fund_nav.empty:
                print('not fund nav existed')
                data = {
                    '净值':pd.DataFrame(),
                    '各基净值':pd.DataFrame(),
                    '各基权重':pd.DataFrame(),
                    '大类净值':pd.DataFrame(),
                    '持有信息':{},
                }
                data['净值'].index.name = 'datetime'
                data['各基净值'].index.name = 'datetime'
                data['各基权重'].index.name = 'datetime'
                data['大类净值'].index.name = 'datetime'
                return data
            fund_nav = fund_nav.ffill()
            order_dic = { dt: i[dt] for i in order_list for dt in list(i.keys())}
            date_list = [j for i in order_list for j in i.keys()] + [fund_nav.index[-1]]
            date_pairs = [[dt, date_list[idx+1]] for idx, dt in enumerate(date_list) if dt != date_list[-1]]
            port_amount = 1 
            port_mv_result = []
            port_weight_result = []
            port_type_result = []
            port_share_result = {}
            for dts in date_pairs:
                b_d = dts[0]
                e_d = dts[1]
                existed_fund_nav_list = list(fund_nav.loc[b_d:].iloc[0].dropna().keys())
                fund_wgt_dt = pd.Series({k : v for k, v in order_dic[b_d].items() if v > 0 and k in existed_fund_nav_list})
                fund_wgt_dt = fund_wgt_dt / fund_wgt_dt.sum()
                fund_amt_dt = port_amount * fund_wgt_dt
                fund_nav_dt = fund_nav.loc[b_d:e_d,fund_wgt_dt.keys()]
                fund_vol_dt = port_amount * fund_wgt_dt / fund_nav_dt.iloc[0]
                port_share_result[b_d] = fund_vol_dt.to_dict()
                fund_amount_dt = fund_nav_dt * fund_vol_dt
                fund_weight_dt = fund_amount_dt.div(fund_amount_dt.sum(axis=1), axis=0)
                port_weight_result.append(fund_weight_dt)
                port_mv = fund_amount_dt.sum(axis=1).to_frame()
                port_mv.columns = ['组合']
                port_mv = port_mv / port_mv.iloc[0] * port_amount
                port_amount = port_mv['组合'].values[-1]
                port_mv_result.append(port_mv)
                fund_type_result = []
                for fund_type_i, fund_list_i in fund_type.items():
                    _fund_list = list(set(fund_list_i).intersection(fund_wgt_dt.index.tolist()))
                    fund_mv_type_i = fund_amount_dt[_fund_list].sum(axis=1).rename(fund_type_i).to_frame()
                    fund_mv_type_i = fund_mv_type_i.pct_change(1).iloc[1:]
                    fund_type_result.append(fund_mv_type_i)
                fund_type_amt_dt = pd.concat(fund_type_result, axis=1)
                port_type_result.append(fund_type_amt_dt)
            port_mv_result = [i.iloc[:-1] if i.index[-1] != port_mv_result[-1].index[-1] else i for i in port_mv_result]
            port_mv_result = pd.concat(port_mv_result)
            if hf_fund_con:
                port_mv_result = CalculatorBase.data_resample_weekly_nav(port_mv_result, rule='W-FRI').dropna()
                today = datetime.datetime.today().date()
                yesterday = today - datetime.timedelta(days=1)
                if port_mv_result.index[-1] > today:
                    id_list = port_mv_result.index.tolist()
                    id_list[-1] = yesterday
                    port_mv_result.index = id_list

            port_mv_result = port_mv_result.reindex(pd.date_range(start=port_mv_result.index[0], end=port_mv_result.index[-1]))
            port_mv_result.index = [i.date() for i in port_mv_result.index]
            port_mv_result.index.name = 'datetime'
            port_weight_result = [i.iloc[:-1] if i.index[-1] != port_weight_result[-1].index[-1] else i for i in port_weight_result]
            port_weight_result = pd.concat(port_weight_result)
            port_type_result = pd.concat(port_type_result)
            port_type_result = (port_type_result.fillna(0) + 1).cumprod()
            port_type_result.loc[_begin_date,:] = 1
            port_type_result = port_type_result.sort_index()
            data = {
                '净值':port_mv_result,
                '各基净值':fund_nav,
                '各基权重':port_weight_result,
                '大类净值':port_type_result,
                '持有信息':port_share_result,
            }
            return data
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_portfolio_nav')
            data = {
                '净值':pd.DataFrame(),
                '各基净值':pd.DataFrame(),
                '各基权重':pd.DataFrame(),
                '大类净值':pd.DataFrame(),
                '持有信息':{},
            }
            data['净值'].index.name = 'datetime'
            data['各基净值'].index.name = 'datetime'
            data['各基权重'].index.name = 'datetime'
            data['大类净值'].index.name = 'datetime'
            return data
   
    def get_portfolio_benchmark_info(self):
        try:
            index_info = BasicDataApi().get_index_info(index_list=['hs300','national_debt','csi500','gem','sp500rmb','mmf','hsi'])
            res = []
            for r in index_info.itertuples():
                res.append([r.index_id, r.desc_name])
            return res

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_portfolio_benchmark_info')
            return []

    def get_portfolio_mv(self, fund_nav, index_id, begin_date, end_date, time_para, trade_history):
        try:
            if fund_nav.empty:
                df = pd.DataFrame()
                df.index.name = 'datetime'
                data = {
                    'data':df,
                    'stats':[],
                }
                return data
            def print_st(num):
                return round(num,4) 
            fund_nav = fund_nav.dropna()
            fund_nav.columns=['组合']
            basic = BasicDataApi()
            derived = DerivedDataApi()
            order_list, fund_type = self.trade_history_parse(trade_history)
            fund_list = set(list([j for dic in order_list for i in dic.values() for j in i.keys()]))
            hf_fund_con = any(['!' not in _fund_id for _fund_id in fund_list])
            frequency = '1W' if hf_fund_con else '1D'
            index_price = self.get_index_and_asset_price(index_list=[index_id],begin_date=fund_nav.index[0], end_date=fund_nav.index[-1])
            name_dic = basic.get_index_and_asset_name_dic([index_id])
            begin_date, end_date = RawDataApi().get_date_range(time_para, begin_date, end_date)
            df = pd.merge(fund_nav.reset_index(), index_price.reset_index(),how='outer').set_index('datetime').sort_index().ffill().dropna().reindex(fund_nav.index).bfill()
            df = df.loc[begin_date:end_date]
            df = df / df.iloc[0]
            df.loc[:,'价格比'] = df.组合 / df[index_id]
            df = df.rename(columns=name_dic)
            mv_df = df[['组合']].rename(columns={'组合':'mv'})
            mv_df.index.name = 'date'
            mdd_details = Calculator.get_mdd_recover_result(mv_df=mv_df)
            mdd1 = print_st(mdd_details['mdd1'])
            mdd1_d1 = str(mdd_details['mdd1_d1'])
            mdd1_d2 = str(mdd_details['mdd1_d2'])
            mdd1_lens = mdd_details['mdd1_lens']
            mdd2 = print_st(mdd_details['mdd2'])
            mdd2_d1 = str(mdd_details['mdd2_d1'])
            mdd2_d2 = str(mdd_details['mdd2_d2'])
            mdd2_lens = mdd_details['mdd2_len']
            bk_stats = Calculator.get_stat_result_from_df(df=mv_df.reset_index(), date_column='date', value_column='mv', frequency=frequency).__dict__
            ar = print_st(bk_stats['annualized_ret'])
            av = print_st(bk_stats['annualized_vol'])
            r_mdd = print_st(bk_stats['recent_drawdown'])
            r_mdd_b1 = str(bk_stats['recent_mdd_date1'])
            sharpe = round(bk_stats['sharpe'],2)
            st1 = f'年化收益: {ar} 年化波动: {av} 夏普比率: {sharpe}'
            st2 = f'最近回撤: {r_mdd} 最近回撤开始 {r_mdd_b1}'
            st3 = f'最大回撤恢复 {mdd1} {mdd1_d1} : {mdd1_d2}, {mdd1_lens} days'
            st4 = f'第二回撤恢复 {mdd2} {mdd2_d1} : {mdd2_d2}, {mdd2_lens} days'
            
            stats_dic = {
                '年化收益':ar,
                '年化波动':av,
                '夏普比率':sharpe,
                '最近回撤':r_mdd,
                '最近回撤开始':r_mdd_b1,
                '最大回撤':mdd1,
                '最大回撤开始时间':mdd1_d1,
                '最大回撤结束时间':mdd1_d2,
                '最大回撤持续时间':mdd1_lens,
                '第二回撤':mdd2,
                '第二回撤开始时间':mdd2_d1,
                '第二回撤结束时间':mdd2_d2,
                '第二回撤持续时间':mdd2_lens,
            }
            mdd_dic_1 = {
                'd1':str(mdd_details['mdd1_d1']),
                'd2':str(mdd_details['mdd1_d2']),
                'v1':df['组合'].loc[mdd_details['mdd1_d1']: mdd_details['mdd1_d2']].min(),
                'v2':df['组合'].loc[mdd_details['mdd1_d1']: mdd_details['mdd1_d2']].max(),
            }
            mdd_dic_2 = {
                'd1':str(mdd_details['mdd2_d1']),
                'd2':str(mdd_details['mdd2_d2']),
                'v1':df['组合'].loc[mdd_details['mdd2_d1']: mdd_details['mdd2_d2']].min(),
                'v2':df['组合'].loc[mdd_details['mdd2_d1']: mdd_details['mdd2_d2']].max(),
            }
            data = {
                    'data':df,
                    'mdd_1':mdd_dic_1,
                    'stats': [st1, st2, st3],
                    'stats_details':stats_dic,
                }
            if mdd_dic_2['d1'] != 'None':
                data['mdd_2'] = mdd_dic_2
                data['stats'].append(st4)
            return data
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_portfolio_mv')
            df = pd.DataFrame()
            df.index.name = 'datetime'
            data = {
                'data':df,
                'stats':[],
                'stats_details':{},
            }
            return data

    def get_portfolio_cur_mdd(self, fund_nav, begin_date, end_date, time_para):
        try:        
            if fund_nav.empty:
                data = {
                    '历史回撤':pd.DataFrame(),
                    '最低值':None,
                }
                data['历史回撤'].index.name = 'datetime'
                return data
            begin_date, end_date = RawDataApi().get_date_range(time_para, begin_date, end_date)
            fund_nav = fund_nav.loc[begin_date:end_date]
            df = fund_nav / fund_nav.cummax() - 1
            df.columns=['历史回撤']
            df_min = df['历史回撤'].min()
            df.index.name = 'datetime'
            data = {
                '历史回撤': df,
                '最低值': df_min,
            }
            return data
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_portfolio_cur_mdd')
            data = {
                '历史回撤':pd.DataFrame(),
                '最低值':None,
            }
            data['历史回撤'].index.name = 'datetime'
            return data

    def get_portfolio_ret_distribution(self, fund_nav, period, begin_date, end_date, time_para):
        try:
            if fund_nav.empty:
                data = {
                    '分布_频度':[],
                    '分布_收益':[],
                    '收益':pd.DataFrame(),
                }
                data['收益'].index.name = 'datetime'
                return data
            begin_date, end_date = RawDataApi().get_date_range(time_para, begin_date, end_date)
            fund_nav = fund_nav.loc[begin_date:end_date].dropna()    
            fund_nav = CalculatorBase.data_resample_weekly_nav(df=fund_nav, rule=period)
            ret = fund_nav.pct_change(1).iloc[1:]
            ret.columns=['收益']
            result = np.histogram(a=ret['收益'],bins=8)
            fre = result[0].tolist()
            _sum = np.sum(fre)
            fre = [ i / _sum for i in fre]
            rets = result[1].round(3).tolist()
            rets = [f'[{round(i*100,2)}%,{round(rets[idx+1]*100,2)}%)' for idx, i in enumerate(rets) if i != rets[-1]]
            data = {'分布_频度':fre,
                '分布_收益':rets,
                '收益':ret
            }
            return data

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_portfolio_ret_distribution')
            data = {
                '分布_频度':[],
                '分布_收益':[],
                '收益':pd.DataFrame(),
            }
            data['收益'].index.name = 'datetime'
            return data

    def get_portfolio_stats(self, fund_nav, index_id, trade_history):
        try:
            if fund_nav.empty:
                return None
            fund_nav = fund_nav.dropna()
            fund_nav.columns=['组合']
            order_list, fund_type = self.trade_history_parse(trade_history)
            fund_list = set(list([j for dic in order_list for i in dic.values() for j in i.keys()]))
            hf_fund_con = any(['!' not in _fund_id for _fund_id in fund_list])
            frequency = '1W' if hf_fund_con else '1D'
            basic = BasicDataApi()
            derived = DerivedDataApi()
            index_price = self.get_index_and_asset_price(index_list=[index_id],begin_date=fund_nav.index[0], end_date=fund_nav.index[-1])
            name_dic = basic.get_index_and_asset_name_dic([index_id])
            df = pd.merge(fund_nav.reset_index(), index_price.reset_index(),how='outer').set_index('datetime').sort_index().ffill().dropna().reindex(fund_nav.index)
            df = df / df.iloc[0]
            df = df.rename(columns=name_dic)
            result = []
            for col in df:
                res_status = Calculator.get_benchmark_stat_result(dates=df.index,
                                                                values=df[col],
                                                                benchmark_values=df[name_dic[index_id]],
                                                                frequency = frequency,
                                                                risk_free_rate=0.025, )
                
                indicators_tem={
                    '开始日期': str(res_status.start_date),
                    '截止日期': str(res_status.end_date),
                    '累计收益': str(round((res_status.last_unit_nav-1)*100,2)) + "%",
                    '最近一月收益':str(round(res_status.recent_1m_ret*100 ,2)) + "%",
                    '年化收益率': str(round(res_status.annualized_ret*100 ,2)) + "%",
                    '年化波动率': str(round(res_status.annualized_vol*100 ,2)) + "%",
                    '夏普比率': round(res_status.sharpe,2),
                    '最大回撤': str(round(res_status.mdd*100 ,2)) + "%",
                    '最大回撤开始日期': str(res_status.mdd_date1),
                    '最大回撤结束日期': str(res_status.mdd_date2),
                    '最大回撤持续时长': res_status.mdd_lens,
                    '卡玛比率': round(res_status.ret_over_mdd ,2),
                    '下行标准差': str(round(res_status.downside_std*100 ,2)) + "%",
                    'alpha': str(round(res_status.alpha*100 ,2)) + "%",
                    'beta': round(res_status.beta ,2),
                    '信息比率': round(res_status.ir ,2),
                    'CL模型_alpha': str(round(res_status.alpha_cl*100 ,2)) + "%",
                    'CL模型_beta': str(round(res_status.beta_cl*100 ,2)) + "%",
                    '相对胜率': str(round(res_status.win_rate*100 ,2)) + "%",
                    '绝对胜率': str(round(res_status.win_rate_0*100 ,2)) + "%",
                    'name':col
                }
                if col != '组合':
                    indicators_tem['alpha'] = '-'
                    indicators_tem['beta'] = '-'
                    indicators_tem['信息比率'] = '-'
                    indicators_tem['CL模型_alpha'] = '-'
                    indicators_tem['CL模型_beta'] = '-'
                    indicators_tem['相对胜率'] = '-'
                result.append(indicators_tem)
                # indicators_tem={
                #     '开始日期': str(res_status.start_date),
                #     '截止日期': str(res_status.end_date),
                #     '累计收益': (res_status.last_unit_nav-1)*100,
                #     '最近一月收益':res_status.recent_1m_ret*100,
                #     '年化收益率': res_status.annualized_ret*100,
                #     '年化波动率': res_status.annualized_vol*100,
                #     '夏普比率': res_status.sharpe,
                #     '最大回撤': res_status.mdd*100,
                #     '最大回撤开始日期': str(res_status.mdd_date1),
                #     '最大回撤结束日期': str(res_status.mdd_date2),
                #     '最大回撤持续时长': res_status.mdd_lens,
                #     '卡玛比率': res_status.ret_over_mdd,
                #     '下行标准差': res_status.downside_std*100,
                #     'alpha': res_status.alpha*100,
                #     'beta': res_status.beta,
                #     '信息比率': res_status.ir,
                #     'CL模型_alpha': res_status.alpha_cl*100,
                #     'CL模型_beta': res_status.beta_cl*100,
                #     '相对胜率': res_status.win_rate*100,
                #     '绝对胜率': res_status.win_rate_0*100,
                #     'name':col
                # }
                # result.append(indicators_tem)
            df = pd.DataFrame(result).set_index('name').T
            df.index.name = '指标'
            for col in df:
                df[col] = df[col].where(pd.notnull(df[col]), None)
            return df
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_portfolio_stats')

    def get_rolling_corr(self, fund_navs, frequency, windows, step):
        try:
            fund_navs_period = CalculatorBase.data_resample_weekly_nav(df=fund_navs, rule=frequency)
            fund_ret = fund_navs_period.pct_change(1).iloc[1:]  
            # 弱鸡排列
            col_pair = []
            cols = fund_ret.columns.tolist()
            for idx_i, col_i in enumerate(cols):
                cols_list = cols[idx_i+1:]
                for idx_j, col_j in enumerate(cols_list):
                    col_pair.append([col_i,col_j])

            corr_result_df = []
            for col_pair_i in col_pair:
                df = fund_ret[col_pair_i]
                idx_list = df.reset_index().index.tolist()
                corr_result = []
                b = idx_list[0]
                _result = []
                
                # 计算窗口划分 不包含min_windows概念
                while(1):
                    e = b + windows
                    if e > idx_list[-1]:
                        break
                    else:
                        _result.append([b,e])
                        b += step

                # 计算部分
                for idxs in _result:
                    _df = df.iloc[idxs[0]:idxs[1]]
                    corr_result.append({'datetime':_df.index[-1], f'{col_pair_i[0]}_{col_pair_i[1]}':_df.corr().iloc[1,0]})
                df = pd.DataFrame(corr_result).set_index('datetime')
                corr_result_df.append(df)
            df = pd.concat(corr_result_df,axis=1)
            return df
        
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_rolling_corr')
            return pd.DataFrame()
    
    def get_port_fund_list(self, trade_history):
        try:
            order_list, fund_type = self.trade_history_parse(trade_history)
            fund_list = []
            for order in order_list:
                for d, fund_wgt in order.items():
                    fund_list.extend(list(fund_wgt))
            fund_list = list(set(fund_list))
            fund_info = self.get_all_fund_info(fund_list)
            result = [[r.fund_id, r.desc_name] for r in fund_info.itertuples()]
            return result
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_port_fund_list')
            return []

    def get_port_fund_pos_date(self,fund_id, trade_history,benchmark_id_info): 
        try:
            order_list, fund_type = self.trade_history_parse(trade_history)
            fund_type_dic = { vi: benchmark_id_info[k] for k, v in fund_type.items() for vi in v}
            index_id = fund_type_dic[fund_id]
            basic = BasicDataApi()
            derived = DerivedDataApi()
            fund_list = [fund_id]
            fund_info = self.get_part_fund_info(fund_list=fund_list)
            desc_name_dic = fund_info.set_index('fund_id')['desc_name'].to_dict()
            index_info = BasicDataApi().get_index_info(index_list=[index_id])
            index_desc_name_dic = index_info.set_index('index_id')['desc_name'].to_dict()
            desc_name_dic.update(index_desc_name_dic)
            begin_date, end_date = RawDataApi().get_date_range(time_para='ALL', begin_date=None, end_date=None)
            fund_nav = self.get_all_fund_nav(fund_list=[fund_id])
            if fund_nav.empty:
                df = pd.DataFrame()
                df.index.name = 'datetime'
                data = {
                '净值':df,
                '持有期':[],
                }
                return data
            fund_nav = fund_nav.ffill()
            index_price = self.get_index_and_asset_price(index_list=[index_id],begin_date=fund_nav.index[0], end_date=fund_nav.index[-1])
            nav_df = fund_nav.join(index_price).ffill().dropna()
            
            result = []
            for order in order_list:
                for d, fund_wgt in order.items():
                    fund_wgt['datetime'] = d
                    result.append(fund_wgt)

            weight_df = pd.DataFrame(result).set_index('datetime')
            pos_con = 1 - weight_df[fund_id].isnull()
            result = []
            is_empty = True
            for r in pos_con.iteritems():
                if is_empty and r[1] == 1:
                    dic = {'begin_date':r[0]}
                    is_empty = False
                elif not is_empty and r[1] == 0:
                    dic['end_date'] = r[0]
                    dic['rise'] =  bool(nav_df.loc[:dic['end_date']].iloc[-1][fund_id] > nav_df.loc[dic['begin_date']:,fund_id].values[0])
                    dic['begin_date'] = str(dic['begin_date'])
                    dic['end_date'] = str(dic['end_date'])
                    result.append(dic)
                    dic = {}
                    is_empty = True
            if not is_empty:
                dic['end_date'] = end_date
                dic['rise'] =  bool(nav_df.loc[:dic['end_date']].iloc[-1][fund_id] > nav_df.loc[dic['begin_date']:,fund_id].values[0])
                dic['begin_date'] = str(dic['begin_date'])
                dic['end_date'] = str(dic['end_date'])
                result.append(dic)
            nav_df.index.name = 'datetime'
            nav_df = nav_df / nav_df.iloc[0]
            nav_df.loc[:,'价格比'] = nav_df[fund_id] / nav_df[index_id]
            data = {
                '净值':nav_df.rename(columns=desc_name_dic),
                '持有期':result}
            return data
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_port_fund_pos_date')
            df = pd.DataFrame()
            df.index.name = 'datetime'
            data = {
                '净值':df,
                '持有期':[],
                }
            return data

    def get_port_ret_resolve_date_range(self, trade_history):
        try:
            order_list, fund_type = self.trade_history_parse(trade_history)
            begin_date, end_date = RawDataApi().get_date_range(time_para='ALL', begin_date=None, end_date=None)
            begin_date = list(order_list[0].keys())[0]
            data = {'begin_date':begin_date,'end_date':end_date}
            return data
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_port_ret_resolve_date_range')
            return {}
    
    def get_port_ret_resolve(self, share_list , begin_date , end_date):
        try:
            if len(share_list) < 1:
                return {}
            basic = BasicDataApi()
            fund_list = list(set([i for dt, share_list in share_list.items() for i in list(share_list.keys())]))
            fund_info = self.get_all_fund_info(fund_list=fund_list)
            desc_name_dic = fund_info.set_index('fund_id').to_dict()['desc_name']
            all_ret_dict = []
            for i in range(len(list(share_list.keys()))):
                this_date = list(share_list.keys())[i]
                if i+1 < len(list(share_list.keys())) :
                    next_date = list(share_list.keys())[i+1]
                else :
                    next_date = datetime.date.today()
                if next_date <= begin_date: 
                    continue
                elif next_date <= end_date: 
                    cal_end = next_date
                elif next_date > end_date: 
                    cal_end = end_date
                if this_date >= end_date: 
                    break
                elif this_date <= begin_date: 
                    cal_start = begin_date
                elif this_date > begin_date: 
                    cal_start = this_date
                ret_dict = {}
                for fund_id in list(share_list[this_date].keys()):
                    fund_share = share_list[this_date][fund_id]
                    fund_nav = self.get_all_fund_nav_(start_date=cal_start,end_date=cal_end,fund_list=[fund_id])
                    fund_nav = fund_nav.ffill()
                    fund_ret = round((fund_nav.iloc[-1].values[0] * fund_share - fund_nav.iloc[0].values[0] * fund_share)*100,2)
                    ret_dict[desc_name_dic[fund_id]] = fund_ret
                all_ret_dict.append(ret_dict)
            dic = ((((pd.DataFrame(all_ret_dict)/100).T.fillna(0)+1).prod(axis=1) - 1) * 100).to_dict()
            dic = {k:round(v,2) for k,v in dic.items()}

            _df = pd.DataFrame([dic]).T.sort_values(by=0)
            if _df.shape[0] > 30:
                dic = pd.concat([_df.iloc[:15], _df.iloc[-15:]]).to_dict()[0]
            return dic
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_port_ret_resolve')
            return {}

    def get_port_fund_weight(self, fund_wgt, trade_history):
        try:
            if fund_wgt.empty:
                data = {
                    '基金':pd.DataFrame(),
                    '类型':pd.DataFrame(),
                    '类型对照':{},
                }
                return data

            order_list, fund_type = self.trade_history_parse(trade_history)
            fund_info = self.get_all_fund_info(fund_wgt.columns.tolist())
            name_dic = fund_info.set_index('fund_id').to_dict()['desc_name']
            fund_wgt = fund_wgt.rename(columns=name_dic)
            result = {}
            for types, fund_list in fund_type.items():
                result[types] = [name_dic[_] for _ in fund_list]

            _result = []
            for type_i, fund_list in result.items():
                _df = fund_wgt[fund_list].sum(axis=1)
                _df.name = type_i
                _result.append(_df)
            fund_type_wgt = pd.concat(_result,axis=1)
            trade_list = [j for i in order_list for j in i.keys()]
            dts = fund_wgt.index.tolist()
            dts = [dt for idx, dt in enumerate(dts) if idx % 10 == 0]
            fund_wgt_part_1 = fund_wgt.loc[dts]
            index_list = trade_list + [fund_wgt.index[0]] + [fund_wgt.index[-1]]
            fund_wgt_part_2 = fund_wgt.loc[fund_wgt.index.intersection(index_list)]
            fund_wgt = pd.concat([fund_wgt_part_1,fund_wgt_part_2]).sort_index()
            fund_wgt = fund_wgt.drop_duplicates()
            fund_type_wgt = fund_type_wgt.reindex(fund_wgt.index)
            data = {
                '基金':fund_wgt,
                '类型':fund_type_wgt,
                '类型对照':result,
            }
            return data
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_port_fund_weight')
            data = {
                '基金':pd.DataFrame(),
                '类型':pd.DataFrame(),
                '类型对照':{},
            }
            return data


    def get_port_fund_mdd_details(self, trade_history):
        try:
            order_list, fund_type = self.trade_history_parse(trade_history)
            result = self.get_portfolio_nav(trade_history=trade_history)
            df = result['净值']
            if df.empty:
                df = pd.DataFrame()
                df.index.name ='datetime'
                data = {
                    'mdd': df,
                    'fund_nav': df,
                }
                return data

            fund_wgt = result['各基权重']
            fund_nav = result['各基净值']

            fund_type_dic = {}
            for type_i, fund_list in fund_type.items():
                for fund_id in fund_list:
                    fund_type_dic[fund_id] = type_i
            mdd_part1 = (df.loc[:, '组合'] / df.loc[:, '组合'].rolling(10000, min_periods=1).max())
            mdd = round(1 - mdd_part1.min(),4)
            mdd_date1 = df.loc[:mdd_part1.idxmin(),'组合'].idxmax()
            mdd_date2 = mdd_part1.idxmin()
            exchange_list = [j for i in order_list for j in list(i.keys()) ]
            exchange_list = np.array(exchange_list)
            exchange_dts = exchange_list[(exchange_list> mdd_date1) & (exchange_list < mdd_date2)].tolist()
            fund_list = list(set([z for i in order_list for j in i.values() for z in j.keys() ]))
            if len(exchange_dts) == 0:
                date_list = [[mdd_date1,mdd_date2]]
            else:
                l = [mdd_date1] + exchange_dts + [mdd_date2]
                date_list = [ [i,l[l.index(i)+1]] for i in l if i != l[-1]]
            fund_info = self.get_all_fund_info(fund_list=fund_list)
            desc_name_dic = fund_info.set_index('fund_id').to_dict()['desc_name']
            _mdd_list = []
            for date_group in date_list:
                b_d = date_group[0]
                e_d = date_group[1]
                fund_wgt_dt = fund_wgt.loc[:b_d].iloc[-1].dropna()
                mdd_i = ((fund_nav.loc[:e_d].iloc[-1] / fund_nav.loc[:b_d].iloc[-1] - 1) * fund_wgt_dt)
                _mdd_list.append(mdd_i.dropna())
            mdd_dict = ((pd.concat(_mdd_list,axis=1).fillna(0) + 1).prod(axis=1) - 1).to_dict()
            df_result = pd.DataFrame([desc_name_dic]).T
            df_result.columns = ['基金名']
            df_result.loc[:,'回撤贡献'] = df_result.index.map(mdd_dict)
            df_result.loc[:,'类型'] = df_result.index.map(fund_type_dic)
            df_result = df_result.dropna()
            df_result.index.name = '基金代码'
            df_result = df_result.reset_index()

            fund_nav = fund_nav.loc[mdd_date1:mdd_date2][df_result['基金代码']].rename(columns=desc_name_dic)
            fund_nav = fund_nav.reindex(pd.date_range(start=fund_nav.index[0], end=fund_nav.index[-1]))
            fund_nav.index.name = 'datetime'
            data = {
                'mdd': df_result,
                'fund_nav': fund_nav,
            }
            return data

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_port_fund_mdd_details')
            df = pd.DataFrame()
            df.index.name ='datetime'
            data = {
                'mdd': df,
                'fund_nav': df,
            }
            return data

    def get_port_rolling_beta_index_info(self):
        try:
            index_info = BasicDataApi().get_asset_info_real(real_id_list=['hs300','csi500','national_debt']).drop_duplicates(subset='real_id')
            res = []
            for r in index_info.itertuples():
                res.append([r.real_id, r.real_name])
            return res
        
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_port_rolling_beta_index_info')
            return []

    def get_port_fund_alpha_detail(self, trade_history, benchmark_id_info): 
        try:
            derived = DerivedDataApi()
            order_list, fund_type = self.trade_history_parse(trade_history)
            result = PortfolioDataApi().get_portfolio_nav(trade_history=trade_history)
            fund_nav = result['各基净值']
            fund_wgt = result['各基权重']
            if fund_nav.empty:
                return {}
            
            dts_list = [j for i in order_list for j in i.keys()] + [fund_nav.index[-1]]
            dts_list = [[i,dts_list[dts_list.index(i)+1]] for i in dts_list if i != dts_list[-1]]
            basic = BasicDataApi()
            index_price = self.get_index_and_asset_price(index_list=list(benchmark_id_info.values()),begin_date=fund_nav.index[0], end_date=fund_nav.index[-1])
            fund_info = self.get_all_fund_info(fund_list=fund_nav.columns.tolist())
            fund_desc_dic = fund_info.set_index('fund_id')['desc_name'].to_dict()
            index_desc_dic = basic.get_index_and_asset_name_dic(list(benchmark_id_info.values()))
            result = {}
            for fund_ti,_fund_list in fund_type.items():
                _result = []
                for dts in dts_list:
                    b_d = dts[0]
                    e_d = dts[1]
                    fund_wgt_i = fund_wgt.loc[b_d:].iloc[0]
                    type_fund_list = fund_wgt_i.index.intersection(_fund_list).tolist() 
                    wgts = fund_wgt_i[type_fund_list]
                    _fund_nav = fund_nav.loc[b_d:e_d][type_fund_list]
                    _fund_ret = (_fund_nav.iloc[-1] / _fund_nav.iloc[0] - 1)# * wgts
                    _fund_ret = _fund_ret.to_dict()
                    index_id = benchmark_id_info[fund_ti]
                    index_rets = index_price.loc[b_d:e_d,index_id]
                    index_rets_i = index_rets.iloc[-1] / index_rets.iloc[0] - 1  
                    dic={
                        'begin_date':str(b_d),
                        'end_date':str(e_d),
                        'index_ret': int(index_rets_i * 10000),
                        'index_name':index_desc_dic[index_id],
                        'fund_details':[],
                    }
                    for _fund_id in type_fund_list:
                        _dic = {
                                'fund':fund_desc_dic[_fund_id],
                                'ret':int((_fund_ret[_fund_id] - index_rets_i) * 10000*wgts[_fund_id]),
                        }
                        dic['fund_details'].append(_dic)
                    _result.append(dic)
                result[fund_ti] = _result
            return result

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_port_fund_alpha_detail')
            return {}

    def get_port_recent_ret_details(self, trade_history, index_id, time_para, begin_date, end_date, benchmark_id_info):
        try:
            order_list, fund_type = self.trade_history_parse(trade_history)
            begin_date, end_date = RawDataApi().get_date_range(time_para, begin_date, end_date)
            result = PortfolioDataApi().get_portfolio_nav(trade_history=trade_history)
            fund_nav=result['净值']
            if fund_nav.empty:
                df = pd.DataFrame()
                df.index.name = 'datetime'
                data = {
                '组合收益':df,
                '组合收益描述':[],
                '资产价格比收益':df,
                '资产价格比收益描述':[],
                '个基近期收益':df,
            }
            # 取非0权重大类
            fund_wgt = result['各基权重']
            _result = []
            for type_i, fund_list in fund_type.items():
                _df = fund_wgt.tail()[fund_list].sum(axis=1)
                _df.name = type_i
                _result.append(_df)
            fund_type_wgt = pd.concat(_result,axis=1)
            fund_type_wgt = fund_type_wgt.tail(1).reset_index(drop=True).T

            exchange_list = [j for i in order_list for j in list(i.keys()) ]
            exchange_list = np.array(exchange_list)
            dts_list = [begin_date] + exchange_list[exchange_list>begin_date].tolist() + [end_date]
            date_pairs = [[dt, dts_list[idx+1]] for idx, dt in enumerate(dts_list) if dt != dts_list[-1]]

            port_nav = PortfolioDataApi().get_portfolio_mv(fund_nav=fund_nav, index_id=index_id,begin_date=begin_date,end_date=end_date,time_para=time_para,trade_history=trade_history)
            fund_info = self.get_all_fund_info(fund_list = result['各基净值'].columns.tolist())
            fund_desc_dic = fund_info.set_index('fund_id')['desc_name'].to_dict()
            fund_type_dic = { vi: k for k, v in fund_type.items() for vi in v}
            cols = port_nav['data'].columns
            cols = [i for i in cols if '价格比' not in i]
            result_1 = port_nav['data'][cols]
            bps = str(int((port_nav['data']['组合'].values[-1] / port_nav['data']['组合'].values[0] - 1) * 10000)) +'BP'
            res_1 = port_nav['stats'][0]
            result_1_str = f'{res_1} 总收益 {bps}'
            result_1_str_dic = {k: v for k, v in port_nav['stats_details'].items() if k in ['年化收益','年化波动','夏普比率']}
            result_1_str_dic['总收益'] = bps
            _index_price = result['大类净值'].loc[begin_date:]
            benchmark_id_info_r = {v: k for k, v in benchmark_id_info.items()}
            index_price = self.get_index_and_asset_price(index_list=list(benchmark_id_info.values()),begin_date=fund_nav.index[0], end_date=fund_nav.index[-1])
            index_price = index_price.rename(columns=benchmark_id_info_r)
            index_price = index_price.reindex(_index_price.index.union(index_price.index)).ffill().bfill().reindex(_index_price.index)
            result_2 = _index_price / _index_price.iloc[0] / (index_price / index_price.iloc[0])

            price_ratio = result_2.copy()
            res_2_dic = (_index_price.iloc[-1] / _index_price.iloc[0] - 1) * 10000
            result_2_str = ' '.join([f'{k} {int(v)}BP' for k, v in res_2_dic.items()])

            fund_navs = result['各基净值']
            _port_index_list = result['净值'].index.tolist()
            _result_3 = []
            for dts in date_pairs:
                b_d, e_d = dts
                if e_d <= _port_index_list[0] or b_d >= _port_index_list[-1]:
                    continue
                if dts != date_pairs[-1]:
                    _fund_wgt = fund_wgt.loc[b_d:e_d].iloc[:-1]
                else:
                    _fund_wgt = fund_wgt.loc[b_d:e_d]
                b_d = _fund_wgt.index[0]
                e_d = _fund_wgt.index[-1] 
                fund_wgt_i = _fund_wgt.dropna(axis=1).mean()
                _df_i = fund_wgt_i.to_frame()
                _df_i.columns=['权重']

                _df_i.loc[:,'基金名'] = _df_i.index.map(fund_desc_dic)
                _df_i.loc[:,'开始时间'] = b_d
                _df_i.loc[:,'结束时间'] = e_d
                _df_i.loc[:,'基金类型'] = _df_i.index.map(fund_type_dic)
                _fund_nav_i = fund_navs.loc[b_d:e_d][_df_i.index]
                _fund_ret = _fund_nav_i.iloc[-1] / _fund_nav_i.iloc[0] - 1
                _df_i.loc[:,'基金涨跌'] = _fund_ret
                _df_i.loc[:,'基金收益'] = _df_i.基金涨跌 * _df_i.权重
                _result_3.append(_df_i)
            result_3 = pd.concat(_result_3)
            result_3['权重'] = result_3['权重'].map(lambda x: str(round(100*x,2))) +'%'
            dic = (result_3[['基金类型','基金收益']].groupby('基金类型').sum()*10000).astype(int).astype(str)
            result_2_str = ' '.join([f'{k} {int(v)}BP' for k, v in dic.to_dict()['基金收益'].items()])
            result_2_dic = { k: str(int(v))+'BP' for k,v in dic.to_dict()['基金收益'].items()}
            result_3['基金收益'] = result_3['基金收益'].map(lambda x: str(int(10000*x))) +'BP'
            result_3['基金涨跌'] = result_3['基金涨跌'].map(lambda x : str(round(x * 100,2))+'%')
            result_3 = result_3[['基金名','开始时间','结束时间','基金类型','基金涨跌','权重','基金收益']]
            result_2 = result_2.reindex(pd.date_range(start=result_2.index[0], end=result_2.index[-1]))
            result_2.index.name = 'datetime'
            data = {
                '组合收益':result_1,
                '组合收益描述':result_1_str,
                '组合收益细节':result_1_str_dic,
                '资产价格比收益':result_2,
                '资产价格比收益描述':result_2_str,
                '资产价格比收益细节':result_2_dic,
                '个基近期收益':result_3,
            }
            return data
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_port_recent_ret_details')
            df = pd.DataFrame()
            df.index.name = 'datetime'
            data = {
                '组合收益':df,
                '组合收益描述':[],
                '组合收益细节':{},
                '资产价格比收益':df,
                '资产价格比收益描述':[],
                '资产价格比收益细节':{},
                '个基近期收益':df,
            }
            return data

    def get_port_info(self, trade_history, benchmark_id_info):
        try:
            # _benchmark_id_info = {}
            # for i in benchmark_id_info:
            #     _benchmark_id_info[i['asset_name']] = i['index_id']  
            data = PortfolioDataApi().get_portfolio_nav(trade_history=trade_history)
            order_list, fund_type = self.trade_history_parse(trade_history)
            fund_nav = data['净值']
            res_status = Calculator.get_stat_result(dates=fund_nav.index, values=fund_nav['组合'])
            dic = {
                '年化收益':round(res_status.annualized_ret,4),
                '年化波动':round(res_status.annualized_vol,4),
                '最大回撤':round(res_status.mdd,4),
                '夏普比率':round(res_status.sharpe,2),
                '近一周收益':round(res_status.recent_1w_ret,4),
                '近一月收益':round(res_status.recent_1m_ret,4),
                '创建日期':str(res_status.start_date),
                '当前回撤':round(res_status.recent_drawdown,4),
                '近一周开始时间':str(res_status.w1_begin_date),
                '近一周结束时间':str(res_status.w1_end_date),
            }
            fund_weight = data['各基权重'].tail(1).dropna(axis=1).T
            fund_weight.columns = ['weight']
            result = {}
            for types, fund_list in fund_type.items():
                for fund_id in fund_list:
                    result[fund_id] = types
            fund_weight.loc[:,'fund_type'] = fund_weight.index.map(result)
            asset_weight = fund_weight.groupby('fund_type').sum().round(2)['weight'].to_dict()

            fund_info = self.get_all_fund_info(fund_weight.index.tolist())
            name_dic = fund_info.set_index('fund_id').to_dict()['desc_name']

            asset_weight_result = []
            for k, v in asset_weight.items():
                _dic = {
                    'index_id':benchmark_id_info[k],
                    'weight':v,
                    'asset_name':k,
                }
                asset_weight_result.append(_dic)
            fund_weight.loc[:,'desc_name'] = fund_weight.index.map(name_dic)
            fund_weight = fund_weight.sort_values('weight', ascending=False)

            fund_pos_result = []
            for r in fund_weight.itertuples():
                _dic = {
                    'fund_id':r.Index,
                    'weight':round(r.weight,4),
                    'desc_name':r.desc_name,
                }
                fund_pos_result.append(_dic)
            data = {
                'port_status':dic,
                'port_asset_weight':asset_weight_result,
                'port_fund_weight':fund_pos_result,
            }
            return data
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.get_port_info')
            df = pd.DataFrame()
            df.index.name = 'datetime'
            data = {
                'port_status':{},
                'port_asset_weight':[],
                'port_fund_weight':[],
            }
            return data

    def calc_port_status(self, trade_history):
        try:
            data = self.get_portfolio_nav(trade_history=trade_history)
            fund_nav = data['净值']
            p_s = Calculator.get_stat_result(dates=fund_nav.index, values=fund_nav.组合).__dict__
            dic = {
                '最近净值':p_s['last_unit_nav'],
                '最近涨幅':p_s['last_increase_rate'],
                '截止日期':str(p_s['end_date']),
                '年化收益率':p_s['annualized_ret'],
                '年化波动率':p_s['annualized_vol'],
                '最大回撤':p_s['mdd'],
                '夏普率':p_s['sharpe'],
                '卡玛比率':p_s['ret_over_mdd'],
                '最近一年收益率':p_s['recent_y1_ret'],
                '最近三年收益率':p_s['recent_y3_ret'],
                '最近五年收益率':p_s['recent_y5_ret'],
            }
            return dic

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from portfolio.calc_port_status')
            return {
                    '最近净值':None,
                    '最近涨幅':None,
                    '截止日期':None,
                    '年化收益率':None,
                    '年化波动率':None,
                    '最大回撤':None,
                    '夏普率':None,
                    '卡玛比率':None,
                    '最近一年收益率':None,
                    '最近三年收益率':None,
                    '最近五年收益率':None,
                }

    def get_asset_price(self, begin_date, end_date, time_para, asset_list: Tuple[str] = ()):
        try:
            begin_date, end_date = RawDataApi().get_date_range(time_para, begin_date, end_date)
            raw = RawDataApi()
            derived = DerivedDataApi()
            basic = BasicDataApi()
            asset_info = basic.get_asset_info(asset_id_list=asset_list)
            asset_list = asset_info.asset_id.tolist()
            _asset_list = [i for i in asset_list if i.split('-')[0] == 'fund']
            _res = []
            for r in asset_info.itertuples():
                if r.asset_id in _asset_list:
                    _res.append(r.real_name)
                else:
                    _res.append(r.asset_name)
            asset_info.loc[:,'show_name'] = _res
            inputs_asset_list = asset_info.asset_id.tolist()
            asset_dic = asset_info.set_index('asset_id').to_dict()['real_id']
            asset_list_0 = ['asset-dollar']
            asset_list_1 = ['asset-btc']
            asset_list_2 = ['asset-usdebt']
            _asset_list_0 = [i for i in inputs_asset_list if i in asset_list_0]
            _asset_list_1 = [i for i in inputs_asset_list if i in asset_list_1]
            _asset_list_2 = [i for i in inputs_asset_list if i in asset_list_2]
            _asset_list_3 = [i for i in inputs_asset_list if i.split('-')[0] == 'fund']
            _asset_list_4 = [i for i in inputs_asset_list if i.split('-')[0] == 'stgindex']
            _asset_list_41 = [i for i in inputs_asset_list if i.split('-')[0] == 'comedy']
            _asset_sum = _asset_list_0 + _asset_list_1 + _asset_list_2 + _asset_list_3 + _asset_list_4 + _asset_list_41
            _asset_list_5 = [i for i in inputs_asset_list if i not in _asset_sum]
            _asset_list_6 = [i for i in inputs_asset_list if i.split('-')[0] == 'macro']

            result = []
            if len(_asset_list_0+_asset_list_6) > 0:
                _asset_list_0 = _asset_list_0+_asset_list_6
                real_ids = [asset_dic[i] for i in _asset_list_0]
                _df = raw.get_em_macroeconomic_daily(codes=real_ids,start_date=begin_date,end_date=end_date).pivot_table(index='datetime',columns='codes',values='value')
                result.append(_df)
            if len(_asset_list_1) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_1]
                _df = raw.get_btc(asset_ids=real_ids,start_date=begin_date,end_date=end_date).pivot_table(index='date',columns='codes',values='close')
                result.append(_df)
            if len(_asset_list_2) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_2]
                _df = raw.get_em_future_price(future_ids=real_ids,start_date=begin_date,end_date=end_date).pivot_table(index='datetime',columns='future_id',values='close')
                result.append(_df)
            if len(_asset_list_3) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_3]
                _df = derived.get_fof_nav_public_adj(fof_id_list=real_ids,start_date=begin_date,end_date=end_date).pivot_table(index='datetime',columns='fund_id',values='nav')
                result.append(_df)
            if len(_asset_list_4) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_4]
                _df = raw.get_hf_index_price(index_ids=real_ids,start_date=begin_date,end_date=end_date).pivot_table(index='index_date',columns='index_id',values='close')
                result.append(_df)
            if len(_asset_list_41) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_41]
                _df = raw.get_em_future_price(future_ids=real_ids,start_date=begin_date,end_date=end_date).pivot_table(index='datetime',columns='future_id',values='close')
                result.append(_df)
            if len(_asset_list_5) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_5]
                _df = basic.get_index_price_dt(index_list=real_ids,start_date=begin_date,end_date=end_date).pivot_table(index='datetime',columns='index_id',values='close')
                result.append(_df)

            df_result = pd.concat(result,axis=1).sort_index()
            df_result = df_result / df_result.bfill().iloc[0]
            df_result_show = df_result.rename(columns=asset_info.set_index('real_id').to_dict()['show_name'])
            df_result_real = df_result.ffill().rename(columns=asset_info.set_index('real_id').to_dict()['real_name'])
            df_result_show.index.name = 'datetime'
            df_result_real.index.name = 'datetime'
            asset_info = asset_info.drop_duplicates(subset=['real_id'])
            dic = {'data':df_result_show,'_input_asset_nav':df_result_real,'_input_asset_info':asset_info}
            return dic
        
        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from port.get_asset_price')

    def get_asset_price_dt(self, asset_list, begin_date, end_date):
        try:
            raw = RawDataApi()
            derived = DerivedDataApi()
            basic = BasicDataApi()
            _begin_date = begin_date
            #asset_list = ['asset-big_cap','stgindex-bond','theme-csi_const_eng','industry-mech']
            asset_info = basic.get_asset_info(asset_id_list=asset_list)
            asset_dic = asset_info.set_index('asset_id').to_dict()['real_id']
            asset_info = basic.get_asset_info(asset_id_list=asset_list)
            inputs_asset_list = asset_list
            asset_list_0 = ['asset-dollar']
            asset_list_1 = ['asset-btc']
            asset_list_2 = ['asset-usdebt']
            _asset_list_0 = [i for i in inputs_asset_list if i in asset_list_0]
            _asset_list_1 = [i for i in inputs_asset_list if i in asset_list_1]
            _asset_list_2 = [i for i in inputs_asset_list if i in asset_list_2]
            _asset_list_3 = [i for i in inputs_asset_list if i.split('-')[0] == 'fund']
            _asset_list_4 = [i for i in inputs_asset_list if i.split('-')[0] == 'stgindex']
            _asset_list_41 = [i for i in inputs_asset_list if i.split('-')[0] == 'comedy']
            _asset_sum = _asset_list_0 + _asset_list_1 + _asset_list_2 + _asset_list_3 + _asset_list_4 + _asset_list_41
            _asset_list_5 = [i for i in inputs_asset_list if i not in _asset_sum]

            result = []
            if len(_asset_list_0) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_0]
                _df = raw.get_em_macroeconomic_daily(codes=real_ids,start_date=_begin_date,end_date=end_date).pivot_table(index='datetime',columns='codes',values='value')
                result.append(_df)
            if len(_asset_list_1) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_1]
                _df = raw.get_btc(asset_ids=real_ids,start_date=_begin_date,end_date=end_date).pivot_table(index='date',columns='codes',values='close')
                result.append(_df)
            if len(_asset_list_2) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_2]
                _df = raw.get_em_future_price(future_ids=real_ids,start_date=_begin_date,end_date=end_date).pivot_table(index='datetime',columns='future_id',values='close')
                result.append(_df)
            if len(_asset_list_3) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_3]
                _df = derived.get_fof_nav_public_adj(fof_id_list=real_ids,start_date=_begin_date,end_date=end_date).pivot_table(index='datetime',columns='fund_id',values='nav')
                result.append(_df)
            if len(_asset_list_4) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_4]
                _df = raw.get_hf_index_price(index_ids=real_ids,start_date=_begin_date,end_date=end_date).pivot_table(index='index_date',columns='index_id',values='close')
                result.append(_df)
            if len(_asset_list_41) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_41]
                _df = raw.get_em_future_price(future_ids=real_ids,start_date=_begin_date,end_date=end_date).pivot_table(index='datetime',columns='future_id',values='close')
                result.append(_df)
            if len(_asset_list_5) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_5]
                _df = basic.get_index_price_dt(index_list=real_ids,start_date=_begin_date,end_date=end_date).pivot_table(index='datetime',columns='index_id',values='close')
                result.append(_df)

            df_result = pd.concat(result,axis=1).sort_index()
            df_result = df_result.bfill().ffill()
            return df_result

        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from port.get_asset_price_dt')
            return pd.DataFrame()

    def get_asset_price_dt_back_with_asset_id(self, asset_list, begin_date, end_date):
        try:
            raw = RawDataApi()
            derived = DerivedDataApi()
            basic = BasicDataApi()
            _begin_date = begin_date
            #asset_list = ['asset-big_cap','stgindex-bond','theme-csi_const_eng','industry-mech']
            asset_info = basic.get_asset_info(asset_id_list=asset_list)
            asset_dic = asset_info.set_index('asset_id').to_dict()['real_id']
            asset_info = basic.get_asset_info(asset_id_list=asset_list)
            asset_asset_id_dic = asset_info.set_index('real_id')['asset_id'].to_dict()
            inputs_asset_list = asset_list
            asset_list_0 = ['asset-dollar']
            asset_list_1 = ['asset-btc']
            asset_list_2 = ['asset-usdebt']
            _asset_list_0 = [i for i in inputs_asset_list if i in asset_list_0]
            _asset_list_1 = [i for i in inputs_asset_list if i in asset_list_1]
            _asset_list_2 = [i for i in inputs_asset_list if i in asset_list_2]
            _asset_list_3 = [i for i in inputs_asset_list if i.split('-')[0] == 'fund']
            _asset_list_4 = [i for i in inputs_asset_list if i.split('-')[0] == 'stgindex']
            _asset_list_41 = [i for i in inputs_asset_list if i.split('-')[0] == 'comedy']
            _asset_sum = _asset_list_0 + _asset_list_1 + _asset_list_2 + _asset_list_3 + _asset_list_4 + _asset_list_41
            _asset_list_5 = [i for i in inputs_asset_list if i not in _asset_sum]

            result = []
            if len(_asset_list_0) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_0]
                _df = raw.get_em_macroeconomic_daily(codes=real_ids,start_date=_begin_date,end_date=end_date).pivot_table(index='datetime',columns='codes',values='value')
                result.append(_df)
            if len(_asset_list_1) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_1]
                _df = raw.get_btc(asset_ids=real_ids,start_date=_begin_date,end_date=end_date).pivot_table(index='date',columns='codes',values='close')
                result.append(_df)
            if len(_asset_list_2) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_2]
                _df = raw.get_em_future_price(future_ids=real_ids,start_date=_begin_date,end_date=end_date).pivot_table(index='datetime',columns='future_id',values='close')
                result.append(_df)
            if len(_asset_list_3) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_3]
                _df = derived.get_fof_nav_public_adj(fof_id_list=real_ids,start_date=_begin_date,end_date=end_date).pivot_table(index='datetime',columns='fund_id',values='nav')
                result.append(_df)
            if len(_asset_list_4) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_4]
                _df = raw.get_hf_index_price(index_ids=real_ids,start_date=_begin_date,end_date=end_date).pivot_table(index='index_date',columns='index_id',values='close')
                result.append(_df)
            if len(_asset_list_41) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_41]
                _df = raw.get_em_future_price(future_ids=real_ids,start_date=_begin_date,end_date=end_date).pivot_table(index='datetime',columns='future_id',values='close')
                result.append(_df)
            if len(_asset_list_5) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_5]
                _df = basic.get_index_price_dt(index_list=real_ids,start_date=_begin_date,end_date=end_date).pivot_table(index='datetime',columns='index_id',values='close')
                result.append(_df)

            df_result = pd.concat(result,axis=1).sort_index()
            df_result = df_result.bfill().ffill()
            df_result = df_result.rename(columns=asset_asset_id_dic)
            return df_result

        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from port.get_asset_price_dt')
            return pd.DataFrame()

    def get_product_price_part(self, begin_date, end_date, time_para, product_list: Tuple[str] = (), manager_id=None):
        try:
            begin_date, end_date = RawDataApi().get_date_range(time_para, begin_date, end_date)
            derived = DerivedDataApi()
            basic = BasicDataApi()
            if manager_id == None:
                hf_info = basic.get_fof_info_strategy_exsit(fof_id_list=product_list,manager_id='1')
            else:
                hf_info = basic.get_fof_info_ignore_other_info(fof_id_list=product_list,manager_id=manager_id)

            name_dic = hf_info.set_index('fof_id')['fof_name'].to_dict()
            asset_info = basic.get_asset_info_real(real_id_list=product_list)
            asset_info = asset_info.drop_duplicates('real_id')

            if not asset_info.empty:
                _name_dic = asset_info.set_index('real_id').to_dict()['real_name']
                for k, v in _name_dic.items():
                    name_dic[k] = v
            _df = hf_info.rename(columns={'fof_id':'real_id','strategy_type':'asset_name','fof_name':'real_name'})[['real_id','asset_name','real_name']]
            if not _df.empty:
                _df.loc[:,'asset_type'] = '典型产品'
            asset_info = asset_info.append(_df).drop_duplicates('real_id')
            result = []
            real_ids = product_list
            _df1 = derived.get_fof_nav_public_adj(fof_id_list=real_ids,start_date=begin_date,end_date=end_date).dropna(subset=['nav'])
            if not _df1.empty > 0:
                _df1 = _df1.pivot_table(index='datetime',columns='fund_id',values='nav')
            _df2 = derived.get_fof_nav(manager_id=manager_id, fof_id_list=real_ids).dropna(subset=['adjusted_nav'])
            if not _df2.empty > 0:
                _df2 = _df2.pivot_table(index='datetime',columns='fof_id',values='adjusted_nav').loc[begin_date:end_date]
                if not _df1.empty:
                    _df = _df1.append(_df2)
                    res = []
                    for fund_id in _df2:
                        if fund_id in _df1:
                            b_d = _df1[fund_id].dropna().index[0]
                            e_d = _df1[fund_id].dropna().index[-1]
                            df_part1 = _df2[[fund_id]].loc[:b_d]
                            df_part2 = _df2[[fund_id]].loc[e_d:]
                            _res = [_df1[[fund_id]],df_part1,df_part2]
                            _res = [i for i in _res if not i.empty]
                            _df = pd.concat(_res).sort_index()
                            _df = _df[~_df.index.duplicated(keep='first')]
                            res.append(_df)
                        else:
                            res.append(_df2[[fund_id]])
                    res_tmp = [_df1[[fund_id]] for fund_id in _df1 if fund_id not in _df2]
                    res = res+res_tmp
                    res = [i.dropna() for i in res]
                    _df = pd.concat(res,axis=1).sort_index()
                else:
                    _df = _df2.copy()
            else:
                _df = _df1.copy()            
            if not _df.empty > 0:
                result.append(_df)
            _df = basic.get_index_price_dt(index_list=real_ids,start_date=begin_date,end_date=end_date)
            if not _df.empty > 0:
                _df = _df.pivot_table(index='datetime',columns='index_id',values='close')
                result.append(_df)
            df_result = pd.concat(result,axis=1).sort_index().dropna(how='all',axis=1)
            df_result = df_result.dropna(axis=0,how='all')
            dic = {
                'df_result':df_result, 
                'name_dic':name_dic,
                'asset_info':asset_info,
            }
            return dic
        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from port.get_product_price_part')

    def calculate_product_price(self, data_dic, begin_date, end_date, time_para, price_type:str='价格线', benchmark_id:str='hs300'):
        try:
            df_result = data_dic['df_result']
            name_dic = data_dic['name_dic']
            asset_info = data_dic['asset_info']
            begin_date, end_date = RawDataApi().get_date_range(time_para, begin_date, end_date)
            if price_type == '价格线':
                pass
            elif price_type == '价格比线':
                basic = BasicDataApi()
                index_price = basic.get_index_price_dt(index_list=[benchmark_id],start_date=begin_date,end_date=end_date)
                index_price = index_price.pivot_table(index='datetime', values='close', columns='index_id')
                index_price = index_price.reindex(df_result.index.union(index_price.index)).sort_index().ffill().reindex(df_result.index)
                index_price.columns = ['benchmark']
                result = []
                for fund_id in df_result:
                    _df_i = df_result[[fund_id]]
                    _df_i = _df_i.join(index_price).dropna()
                    _df_i = _df_i / _df_i.iloc[0]
                    _df_i[fund_id] = _df_i[fund_id] / _df_i.benchmark
                    result.append(_df_i[[fund_id]])
                df_result = pd.concat(result, axis=1).sort_index()
            df_result = df_result / df_result.bfill().iloc[0]
            df_result = df_result.rename(columns=name_dic)
            dic = {'data':df_result,'_input_asset_nav':df_result.ffill(),'_input_asset_info':asset_info}
            return dic
        
        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from port.get_product_price')

    def get_product_price_ratio_input_fund_data(self, begin_date, end_date, time_para, fund_id):
        try:
            raw = RawDataApi()
            begin_date, end_date = raw.get_date_range(time_para, begin_date, end_date)
            hf_info = raw.get_hf_fund_info([fund_id])
            hf_name_dic = hf_info.set_index('fund_id')['desc_name'].to_dict()
            hf_fund_nav = raw.get_hf_fund_nav(fund_ids=[fund_id],start_date=begin_date,end_date=end_date)
            hf_fund_nav = hf_fund_nav.pivot_table(index='datetime', values='nav', columns='fund_id')
            data_dic = {
                'hf_fund_nav': hf_fund_nav,
                'hf_name_dic': hf_name_dic,
            }
            return data_dic

        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from port.get_product_price_ratio_input_fund_data')

    def get_product_price(self, begin_date, end_date, time_para, product_list: Tuple[str] = (), price_type:str='价格线', benchmark_id:str='hs300'):#'价格比线'
        try:
            begin_date, end_date = RawDataApi().get_date_range(time_para, begin_date, end_date)
            raw = RawDataApi()
            derived = DerivedDataApi()
            basic = BasicDataApi()
            hf_info = basic.get_fof_info_strategy_exsit(fof_id_list=product_list)
            name_dic = hf_info.set_index('fof_id')['fof_name'].to_dict()
            asset_info = basic.get_asset_info_real(real_id_list=product_list)
            asset_info = asset_info.drop_duplicates('real_id')

            if not asset_info.empty:
                _name_dic = asset_info.set_index('real_id').to_dict()['real_name']
                for k, v in _name_dic.items():
                    name_dic[k] = v
            _df = hf_info.rename(columns={'fof_id':'real_id','strategy_type':'asset_name','fof_name':'real_name'})[['real_id','asset_name','real_name']]
            if not _df.empty:
                _df.loc[:,'asset_type'] = '典型产品'
            asset_info = asset_info.append(_df).drop_duplicates('real_id')
            result = []
            real_ids = product_list
            _df = derived.get_fof_nav_public_adj(fof_id_list=real_ids,start_date=begin_date,end_date=end_date)
            if not _df.empty > 0:
                _df = _df.pivot_table(index='datetime',columns='fund_id',values='nav')
                result.append(_df)
            _df = basic.get_index_price_dt(index_list=real_ids,start_date=begin_date,end_date=end_date)
            if not _df.empty > 0:
                _df = _df.pivot_table(index='datetime',columns='index_id',values='close')
                result.append(_df)
            df_result = pd.concat(result,axis=1).sort_index()
            if price_type == '价格线':
                pass
            elif price_type == '价格比线':
                index_price = basic.get_index_price_dt(index_list=[benchmark_id],start_date=begin_date,end_date=end_date)
                index_price = index_price.pivot_table(index='datetime', values='close', columns='index_id')
                index_price = index_price.reindex(df_result.index.union(index_price.index)).sort_index().ffill().reindex(df_result.index)
                index_price.columns = ['benchmark']
                result = []
                for fund_id in df_result:
                    _df_i = df_result[[fund_id]].dropna()
                    _df_i = _df_i.join(index_price)
                    _df_i = _df_i / _df_i.iloc[0]
                    _df_i[fund_id] = _df_i[fund_id] / _df_i.benchmark
                    result.append(_df_i[[fund_id]])
                df_result = pd.concat(result, axis=1).sort_index()
            df_result = df_result / df_result.bfill().iloc[0]
            df_result = df_result.rename(columns=name_dic)
            dic = {'data':df_result,'_input_asset_nav':df_result.ffill(),'_input_asset_info':asset_info}
            return dic
        
        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from port.get_product_price')

    def product_recent_rate_data(self, product_list, manager_id=None):
        try:
            raw = RawDataApi()
            derived = DerivedDataApi()
            basic = BasicDataApi()
            if manager_id == None:
                hf_info = basic.get_fof_info_strategy_exsit(fof_id_list=product_list,manager_id='1')
            else:
                hf_info = basic.get_fof_info_ignore_other_info(fof_id_list=product_list,manager_id=manager_id)

            name_dic = hf_info.set_index('fof_id')['fof_name'].to_dict()
            asset_info = basic.get_asset_info_real(real_id_list=product_list)
            asset_info = asset_info.drop_duplicates('real_id')
            if not asset_info.empty:
                _name_dic = asset_info.set_index('real_id').to_dict()['real_name']
                for k, v in _name_dic.items():
                    name_dic[k] = v
            result = []
            real_ids = product_list
            _df1 = derived.get_fof_nav_public_adj(fof_id_list=real_ids,start_date='20090101').dropna(subset=['nav'])
            if not _df1.empty > 0:
                _df1 = _df1.pivot_table(index='datetime',columns='fund_id',values='nav')
            _df2 = derived.get_fof_nav(manager_id=manager_id, fof_id_list=real_ids).dropna(subset=['adjusted_nav'])
            if not _df2.empty > 0:
                _df2 = _df2.pivot_table(index='datetime',columns='fof_id',values='adjusted_nav')
                if not _df1.empty:
                    _df = _df1.append(_df2)
                    res = []
                    for fund_id in _df2:
                        if fund_id in _df1:
                            b_d = _df1[fund_id].dropna().index[0]
                            e_d = _df1[fund_id].dropna().index[-1]
                            df_part1 = _df2[[fund_id]].loc[:b_d]
                            df_part2 = _df2[[fund_id]].loc[e_d:]
                            _res = [_df1[[fund_id]],df_part1,df_part2]
                            _res = [i for i in _res if not i.empty]
                            _df = pd.concat(_res).sort_index()
                            _df = _df[~_df.index.duplicated(keep='first')]
                            res.append(_df)
                        else:
                            res.append(_df2[[fund_id]])
                    res_tmp = [_df1[[fund_id]] for fund_id in _df1 if fund_id not in _df2]
                    res = res+res_tmp
                    res = [i.dropna() for i in res]
                    _df = pd.concat(res,axis=1).sort_index()
                else:
                    _df = _df2.copy()
            else:
                _df = _df1.copy() 
            data_dic = {
                'name_dic':name_dic,
                'result':[_df],
            }
            return data_dic
        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from port.product_recent_rate_data')
    
    def calc_product_recent_rate(self, data_dic, product_list, year:int=None, weekly:bool=False):
        try:
            derived = DerivedDataApi()
            basic = BasicDataApi()
            result = data_dic['result']
            name_dic = data_dic['name_dic']
            real_ids = product_list
            _df = basic.get_index_price_dt(start_date='20091231',index_list=real_ids)
            if not _df.empty > 0:
                _df = _df.pivot_table(index='datetime',columns='index_id',values='close')
                result.append(_df)
            index_price = pd.concat(result,axis=1).sort_index().ffill()
            if weekly:
                # 周度
                index_price_w = basic.data_resample_monthly_nav(index_price,rule='1W').bfill()
                index_ret = index_price_w.pct_change(1).dropna().tail(12)
                td = index_ret.index
                td = [i.strftime('%Y%m%d') for i in td]
            else:
                if year is None:
                    # 年度
                    index_price_y = basic.data_resample_monthly_nav(index_price.bfill(),rule='Y')
                    _df = index_price.bfill().iloc[[0]]
                    index_price_y = index_price_y.append(_df).sort_index().drop_duplicates().bfill()
                    index_ret_year = index_price_y.pct_change(1).dropna()
                    td = index_ret_year.index
                    td = [str(i.year) for i in td]
                    index_ret = index_ret_year.copy()
                else:
                    index_price_m = index_price.loc[datetime.date(year-1,12,31):datetime.date(year,12,31)]
                    index_price_m = basic.data_resample_monthly_nav(index_price_m,rule='1M').bfill()
                    index_ret_m = index_price_m.pct_change(1).dropna()
                    td = index_ret_m.index
                    td = [str(i.year) + str(i.month).zfill(2) for i in td ]
                    index_ret = index_ret_m.copy()
            index_ret.index = td
            index_ret.loc['均值',:] = index_ret.mean()
            index_ret = index_ret.round(4)*100
            index_ret = index_ret.rename(columns=name_dic)
            index_ret = index_ret.T
            index_ret.index.name = 'index_id'
            return index_ret
        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from port.product_recent_rate')

    def product_recent_rate(self, product_list, year:int=None, weekly:bool=False):
        try:
            raw = RawDataApi()
            derived = DerivedDataApi()
            basic = BasicDataApi()
            hf_info = basic.get_fof_info_strategy_exsit()
            name_dic = hf_info.set_index('fof_id')['fof_name'].to_dict()
            asset_info = basic.get_asset_info_real(real_id_list=product_list)
            asset_info = asset_info.drop_duplicates('real_id')
            if not asset_info.empty:
                _name_dic = asset_info.set_index('real_id').to_dict()['real_name']
                for k, v in _name_dic.items():
                    name_dic[k] = v
            result = []
            real_ids = product_list
            _df = derived.get_fof_nav_public_adj(fof_id_list=real_ids,start_date='20091231')
            if not _df.empty > 0:
                _df = _df.pivot_table(index='datetime',columns='fund_id',values='nav')
                result.append(_df)
            _df = basic.get_index_price_dt(start_date='20091231',index_list=real_ids)
            if not _df.empty > 0:
                _df = _df.pivot_table(index='datetime',columns='index_id',values='close')
                result.append(_df)

            index_price = pd.concat(result,axis=1).sort_index().ffill().dropna()
            if weekly:
                # 周度
                index_price_w = basic.data_resample_monthly_nav(index_price,rule='1W').bfill()
                index_ret = index_price_w.pct_change(1).dropna().tail(12)
                td = index_ret.index
                td = [i.strftime('%Y%m%d') for i in td]
            else:
                if year is None:
                    # 年度
                    index_price_y = basic.data_resample_monthly_nav(index_price.bfill(),rule='Y')
                    _df = index_price.iloc[[0]]
                    index_price_y = index_price_y.append(_df).sort_index().drop_duplicates()
                    index_ret_year = index_price_y.pct_change(1).dropna()
                    td = index_ret_year.index
                    td = [str(i.year) for i in td]
                    index_ret = index_ret_year.copy()
                else:
                    index_price_m = index_price.loc[datetime.date(year-1,12,31):datetime.date(year,12,31)]
                    index_price_m = basic.data_resample_monthly_nav(index_price_m,rule='1M').bfill()
                    index_ret_m = index_price_m.pct_change(1).dropna()
                    td = index_ret_m.index
                    td = [str(i.year) + str(i.month).zfill(2) for i in td ]
                    index_ret = index_ret_m.copy()
            index_ret.index = td
            index_ret.loc['均值',:] = index_ret.mean()
            index_ret = index_ret.round(4)*100
            index_ret = index_ret.rename(columns=name_dic)
            index_ret = index_ret.T
            index_ret.index.name = 'index_id'
            return index_ret
        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from port.product_recent_rate')

    def asset_recent_rate(self, asset_list, year:int=None, weekly:bool=False):
        #如果year为空 返回年度收益
        #如果year为整数 返回当年月度收益 year从2010开始
        try:
            raw = RawDataApi()
            derived = DerivedDataApi()
            basic = BasicDataApi()
            asset_info = basic.get_asset_info(asset_id_list=asset_list)
            asset_list = asset_info.asset_id.tolist()
            _asset_list = [i for i in asset_list if i.split('-')[0] == 'fund']
            _res = []
            for r in asset_info.itertuples():
                if r.asset_id in _asset_list:
                    _res.append(r.real_name)
                else:
                    _res.append(r.asset_name)
            asset_info.loc[:,'show_name'] = _res
            inputs_asset_list = asset_info.asset_id.tolist()
            asset_dic = asset_info.set_index('asset_id').to_dict()['real_id']
            name_dic = asset_info.set_index('real_id').to_dict()['real_name']
            name_dic = {k : v.replace('CFCI','指数')for k, v in name_dic.items()}
            asset_list_0 = ['asset-dollar']
            asset_list_1 = ['asset-btc']
            asset_list_2 = ['asset-usdebt']
            _asset_list_0 = [i for i in inputs_asset_list if i in asset_list_0]
            _asset_list_1 = [i for i in inputs_asset_list if i in asset_list_1]
            _asset_list_2 = [i for i in inputs_asset_list if i in asset_list_2]
            _asset_list_3 = [i for i in inputs_asset_list if i.split('-')[0] == 'fund']
            _asset_list_4 = [i for i in inputs_asset_list if i.split('-')[0] == 'stgindex']
            _asset_sum = _asset_list_0 + _asset_list_1 + _asset_list_2 + _asset_list_3 + _asset_list_4
            _asset_list_5 = [i for i in inputs_asset_list if i not in _asset_sum]

            result = []
            if len(_asset_list_0) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_0]
                _df = raw.get_em_macroeconomic_daily(codes=real_ids,start_date='20091231').pivot_table(index='datetime',columns='codes',values='value')
                result.append(_df)
            if len(_asset_list_1) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_1]
                _df = raw.get_btc(asset_ids=real_ids,start_date='20091231').pivot_table(index='date',columns='codes',values='close')
                result.append(_df)
            if len(_asset_list_2) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_2]
                _df = raw.get_em_future_price(future_ids=real_ids,start_date='20091231').pivot_table(index='datetime',columns='future_id',values='close')
                result.append(_df)
            if len(_asset_list_3) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_3]
                _df = derived.get_fof_nav_public_adj(fof_id_list=real_ids,start_date='20091231').pivot_table(index='datetime',columns='fund_id',values='nav')
                result.append(_df)
            if len(_asset_list_4) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_4]
                _df = raw.get_hf_index_price(index_ids=real_ids,start_date='20091231').pivot_table(index='index_date',columns='index_id',values='close')
                result.append(_df)
            if len(_asset_list_5) > 0:
                real_ids = [asset_dic[i] for i in _asset_list_5]
                _df = basic.get_index_price_dt(index_list=real_ids,start_date='20091231').pivot_table(index='datetime',columns='index_id',values='close')
                result.append(_df)

            index_price = pd.concat(result,axis=1).sort_index().ffill().dropna().rename(columns=name_dic)
            if weekly:
                index_price_w = basic.data_resample_monthly_nav(index_price,rule='1W').bfill()
                index_ret = index_price_w.pct_change(1).dropna().tail(12)
                td = index_ret.index
                td = [i.strftime('%Y%m%d') for i in td]
            else:
                if year is None:
                    # 年度
                    ## 年度收益净值调整
                    b_d = index_price.index.values[0]
                    if b_d < datetime.date(b_d.year,12,1):
                        _b_d = datetime.date(b_d.year-1,12,31)
                        index_price.loc[_b_d] = index_price.iloc[0]
                        index_price = index_price.sort_index()
                    else:
                        _b_d = index_price.loc[:datetime.date(b_d.year,12,31)].index[0]
                        index_price = index_price.loc[_b_d:].copy()
                    index_price_y = basic.data_resample_monthly_nav(index_price.bfill(),rule='12M')
                    index_ret_year = index_price_y.pct_change(1).dropna()
                    td = index_ret_year.index
                    td = [str(i.year) for i in td]
                    index_ret = index_ret_year.copy()
                else:
                    index_price_m = index_price.loc[datetime.date(year-1,12,31):datetime.date(year,12,31)]
                    index_price_m = basic.data_resample_monthly_nav(index_price_m,rule='1M').bfill()
                    index_ret_m = index_price_m.pct_change(1).dropna()
                    td = index_ret_m.index
                    td = [str(i.year) + str(i.month).zfill(2) for i in td ]
                    index_ret = index_ret_m.copy()
            last_day = td[-1]
            index_ret.index = td
            index_ret = index_ret.T.sort_values(last_day, ascending=False).T
            index_ret.loc['均值',:] = index_ret.mean()
            index_ret = index_ret.round(4)*100
            index_ret = index_ret.T
            index_ret.index.name = 'index_id'
            return index_ret

        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from port.asset_recent_rate')

    def get_all_asset_price(self, start_date:str='', end_date:str='', id_list:list=[]):
        try:
            result = []
            derived = DerivedDataApi()
            basic = BasicDataApi()
            index_price = basic.get_index_price_dt(start_date=begin_date, end_date=end_date, index_list=id_list)
            if not index_price.empty:
                index_price = index_price.pivot_table(index='datetime', values='close', columns='index_id')
                result.append(index_price)
            fund_nav = basic.get_fund_nav_with_date(start_date=begin_date, end_date=end_date, fund_list=id_list)
            if not fund_nav.empty:
                fund_nav = fund_nav.pivot_table(index='datetime', values='adjusted_net_value', columns='fund_id')
                result.append(fund_nav)
            hf_fund_nav = derived.get_fof_nav_public_adj(fof_id_list=id_list, start_date=begin_date, end_date=end_date)
            if not hf_fund_nav.empty:
                hf_fund_nav = hf_fund_nav.pivot_table(index='datetime', values='nav', columns='fund_id')
                result.append(hf_fund_nav)
            fund_nav = pd.concat(result, axis=1).sort_index().dropna()
            return fund_nav

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from port.get_all_asset_price')
            return []

    def get_index_and_asset_price(self, index_list, begin_date, end_date):
        try:
            basic = BasicDataApi()
            derived = DerivedDataApi()
            index_id_list = [i for i in index_list if '-' not in i]
            asset_id_list = [i for i in index_list if '-' in i]
            index_price = pd.DataFrame()
            asset_price = pd.DataFrame()
            if len(index_id_list) > 0:
                #print(f'index_ids {index_id_list}')
                index_price = basic.get_index_price_dt(index_list=index_id_list, start_date=begin_date, end_date=end_date)
                index_price = index_price.pivot_table(index='datetime',columns='index_id',values='close')
            if len(asset_id_list) > 0:
                #print(f'asset_id_list {asset_id_list}')
                asset_price = derived.get_asset_price_dt_back_with_asset_id(asset_list=asset_id_list,begin_date=begin_date-datetime.timedelta(days=10),end_date=end_date)
            df = pd.concat([index_price,asset_price],join='outer', axis=1).sort_index().ffill().reindex(index_price.index)
            return df
        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from port.get_index_and_asset_price')
            return pd.DataFrame()