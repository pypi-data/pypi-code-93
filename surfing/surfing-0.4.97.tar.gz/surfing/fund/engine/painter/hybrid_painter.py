import pandas as pd
import numpy as np
import platform
import matplotlib as mpl
import pylab as pl
import datetime
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.dates as mdates
from ....util.calculator import Calculator
from matplotlib.patches import Rectangle
CURRENT_PLATFORM = platform.system()
if CURRENT_PLATFORM == 'Darwin':
    mpl.rcParams['font.family'] = ['Heiti TC']
else:
    mpl.rcParams['font.family'] = ['STKaiti']
    
pd.plotting.register_matplotlib_converters()
class HybridPainter(object):

    @staticmethod
    def plot_market_value(mv_df:pd.DataFrame, backtest_type:str, index_price:pd.DataFrame, saa_weight:dict, bk_stats:dict):
        index_df_raw = index_price.loc[mv_df.index[0]:mv_df.index[-1],]
        index_df = index_df_raw.copy().fillna(method='bfill')
        index_df = index_df / index_df.iloc[0]
        index_df['cash'] = 1
        w_l = []
        for idx, r in index_df_raw.iterrows():
            nan_asset = [k for k, v in r.to_dict().items() if np.isnan(v)]
            wgts = saa_weight.copy()
            for k in nan_asset:
                wgts[k] = 0
            s = sum([v  for k,v in wgts.items()])
            wgts = {k :v /s for k, v in wgts.items()}
            wgts['datetime'] = idx
            w_l.append(wgts)
        wgts_df = pd.DataFrame(w_l).set_index('datetime')
        mv_df['benchmark'] = (wgts_df * index_df).sum(axis = 1)
        mv_df = mv_df / mv_df.iloc[0]
        mv_df.plot.line(figsize=(20,12),legend=False,fontsize = 17)
        l = pl.legend(loc='lower left',fontsize = 17)
        s = pl.title(f'{backtest_type} market value', fontsize=20)
        ar = round(bk_stats['annual_ret'],4)
        mdd = round(bk_stats['mdd'], 4)
        sharpe = round(bk_stats['sharpe'],4)
        pl.suptitle(f'annual_ret : {ar} mdd : {mdd} sharpe : {sharpe}',y=0.87,fontsize=17)
        plt.grid()

    @staticmethod
    def plot_market_value_with_mdd_analysis(mv_df:pd.DataFrame, backtest_type:str, index_price:pd.DataFrame, saa_weight:dict, bk_stats:dict):
        def get_mdd_result_from_df(df:pd.DataFrame,
                                    date_column: str,
                                    value_column: str):
            dates = df[date_column].values
            values = df[value_column].values
            return mdd_recover_analysis(values,dates)

        def mdd_recover_analysis(values,dates):
            sr = pd.Series(values, index=dates).sort_index()
            if sr.empty:
                mdd = 0
                mdd_date1 = None
                mdd_date2 = None
                mdd_lens = 0
                return mdd, mdd_date1, mdd_date2, mdd_lens
            mdd_part =  sr[:] / sr[:].rolling(window=sr.shape[0], min_periods=1).max()
            mdd = 1 - mdd_part.min()
            if mdd == 0:
                mdd_date1 = None
                mdd_date2 = None
                mdd_lens = 0
            else:
                mdd_date = mdd_part.idxmin()
                mdd_date1 = sr[:mdd_date].idxmax()
                sr_tmp = sr[mdd_date1:]
                recover_sr = sr_tmp[sr_tmp> sr[mdd_date1]]
                if recover_sr.empty:
                    mdd_date2 = sr_tmp.index[-1]
                else: 
                    mdd_date2 = sr_tmp[sr_tmp> sr[mdd_date1]].index[0]
                mdd_lens = sr.loc[mdd_date1:mdd_date2].shape[0]
            return mdd, mdd_date1, mdd_date2, mdd_lens
                
        def plot_mdd_recover(mdd_date1_1, mdd_date1_2, df, c, ax):
            start = mdates.date2num(mdd_date1_1)
            end = mdates.date2num(mdd_date1_2)
            width = end - start
            price_max = df.loc[mdd_date1_1: mdd_date1_2].mv.max()
            bottom = df.loc[mdd_date1_1: mdd_date1_2].mv.min()
            height = price_max - bottom
            rect = Rectangle((start, bottom), width, height, color=c)
            ax.add_patch(rect)   

        def print_st(mdd):
            return str(round(mdd * 100,2)) + '%' 
            
        
        mdd1, mdd_date1_1, mdd_date1_2, mdd_lens1 = get_mdd_result_from_df(mv_df.reset_index(),'date','mv')
        mv_df_1 = mv_df.loc[:mdd_date1_1].reset_index()
        mv_df_2 = mv_df.loc[mdd_date1_2:].reset_index()

        mdd2, mdd_date2_1, mdd_date2_2, mdd_lens2 = get_mdd_result_from_df(mv_df_1,'date','mv')
        mdd3, mdd_date3_1, mdd_date3_2, mdd_lens3 = get_mdd_result_from_df(mv_df_2,'date','mv')
        if mdd3 > mdd2:
            mdd2 = mdd3
            mdd_date2_1 = mdd_date3_1
            mdd_date2_2 = mdd_date3_2
            mdd_lens2 = mdd_lens3
             
        index_df_raw = index_price.loc[mv_df.index[0]:mv_df.index[-1],]
        date_list = [datetime.datetime.strptime(i, '%Y-%m-%d').date() for i in bk_stats['hold_years']]
        date_list = sorted(list(set(date_list + [mv_df.index[-1]])))
        saa_weight = { k : v for k, v in saa_weight.items() if v > 0}
        _res = []
        last_value = 1
        for dt in date_list[:-1]:
            next_dt = date_list[date_list.index(dt) + 1]
            _df = index_df_raw.loc[dt:next_dt][list(saa_weight.keys())]
            _df = _df / _df.iloc[0]
            res_i = (_df * saa_weight).sum(axis=1)
            res_i = res_i * last_value
            last_value = res_i.values[-1]
            _res.append(res_i)
        benchmark_df = pd.concat(_res,axis=0)
        mv_df = mv_df.join(pd.DataFrame(benchmark_df,columns=['benchmark'])).bfill()
        mv_df = mv_df.drop_duplicates()
        df = mv_df / mv_df.iloc[0]
        df.index.name = 'date'
        fig, ax = plt.subplots(figsize= [20,12])
        df['price_ratio'] = df['mv'] / df['benchmark']       
        plt.plot(df.index, df['mv'], label = 'mv', linewidth=2.0)
        plt.plot(df.index, df['benchmark'], label = 'benchmark', linewidth=2.0)
        plt.plot(df.index, df['price_ratio'], label = 'price ratio', linewidth=2.0)
        
        stats_res = Calculator.get_stat_result_from_df(df=df.reset_index(), date_column='date', value_column='price_ratio').__dict__
        ar = print_st(bk_stats['annual_ret'])
        av = print_st(bk_stats['annual_vol'])
        sharpe = round(bk_stats['sharpe'],2)
        st1 = f'annual_ret : {ar} annual_vol : {av} sharpe : {sharpe}'
        st2 = f'first mdd {print_st(mdd1)} {mdd_date1_1} : {mdd_date1_2}, {mdd_lens1} days'
        st3 = f'second mdd {print_st(mdd2)} {mdd_date2_1} : {mdd_date2_2}, {mdd_lens2} days'
        ar_ = print_st(stats_res['annualized_ret'])
        av_ = print_st(stats_res['annualized_vol'])
        mdd_ = print_st(stats_res['mdd'])
        sharpe_ = round(stats_res['sharpe'],2)
        st4 = f'price ratio annaul ret {ar_} annual vol {av_} mdd {mdd_} sharpe {sharpe_}'
        st = st1 + '\n' + st2 + '\n' + st3 + '\n' + st4
        plt.legend(fontsize=20 ,loc = 'upper left')
        plt.title(f'market values ', fontsize=30)
        plt.suptitle(st, y=0.87, fontsize=18)
        plot_mdd_recover(mdd_date1_1, mdd_date1_2, df, 'silver', ax)
        plot_mdd_recover(mdd_date2_1, mdd_date2_2, df, 'gainsboro', ax)
        plt.grid() 
        #plt.savefig("test.svg")
        plt.show()

    @staticmethod
    def plot_asset_fund_mv_diff(asset_mv:pd.DataFrame, fund_mv:pd.DataFrame):
        asset_mv = asset_mv[['mv']]
        fund_mv = fund_mv[['mv']]
        asset_mv.columns = ['asset_mv']
        fund_mv.columns = ['fund_mv']
        check_diff = fund_mv.join(asset_mv)
        check_diff = check_diff / check_diff.iloc[0]
        check_diff['diff'] = 100 * (check_diff['fund_mv']  - check_diff['asset_mv']) / check_diff['asset_mv'] 
        check_diff[['fund_mv','asset_mv']].plot.line(figsize=(20,12),legend=False,fontsize = 17)
        l = pl.legend(loc='lower left',fontsize = 17)
        s = pl.title('asset and fund market value ', fontsize=20)
        plt.grid()
        check_diff[['diff']].plot.line(figsize=(20,12),legend=False,fontsize = 17)
        l = pl.legend(loc='lower left',fontsize = 17)
        s = pl.title('asset and fund market value diff % ', fontsize=20)
        plt.grid() 
        plt.show()

    @staticmethod
    def plot_four_layers_mv(mv_df:pd.DataFrame):
        mv_df = mv_df / mv_df.iloc[0]
        mv_df.plot.line(color=['C3','C1','C2','C0'],figsize=(14,8))
        plt.title('净值对比', fontsize=20)
        plt.legend(loc='upper left', fontsize=15)
        plt.grid() 
        plt.show()

    @staticmethod
    def plot_taa_detail(df, title):
        df.plot(figsize=(14,8))
        _res = []
        for index_id, v in df.iloc[-1].to_dict().items():
            _res.append(f'{index_id}:{round(v,3)}')
        s = ' '.join(_res)
        plt.title(title, fontsize=25)
        plt.legend(loc='lower left', fontsize=15)
        plt.suptitle(s,y=0.87,fontsize=17)
        plt.grid()
        plt.show()

    @staticmethod
    def plot_asset_price_ratio(fund_nav:pd.DataFrame, 
                        fund_info:pd.DataFrame, 
                        index_price:pd.DataFrame,
                        score_dict:dict,
                        backtest_result:dict,
                        dts:pd.Series,
                        saa:dict,
                        fund_trade: pd.DataFrame,
                        score_select: dict,
                        ):
        
        proper_number_dict = {'mmf':1} 
        for asset, w in saa.items():
            if asset in ['cash','mmf'] or w == 0:
                continue
            num = min(int(round(w / 0.05, 0)) , 4)
            proper_number_dict[asset] = num
        
        fund_info['trade_fee'] = 0.15 * fund_info['purchase_fee'] + fund_info['redeem_fee']
        fee_df = fund_info[['fund_id','trade_fee']].set_index('fund_id')
        dts = dts[(dts >=fund_nav.index[0]) & (dts <= fund_nav.index[-1])]
        fund_nav = fund_nav.reindex(dts)
        index_price = index_price.reindex(dts)
        rebalance_date = backtest_result['rebalance_date'] + [backtest_result['market_value'].index.tolist()[-1]]
        fund_desc_name = fund_info[['fund_id','desc_name']].set_index('fund_id').to_dict()['desc_name']  
        res = {}
        for idx, begin_date in enumerate(rebalance_date[:-1]):
            end_date = rebalance_date[idx + 1]
            for asset, num in proper_number_dict.items():
                #print(asset, num)
                _score_dict = score_dict[begin_date][asset][score_select[asset]]
                _score_list = sorted(_score_dict.items(), key=lambda x:x[1], reverse=True)
                #_fund_list = fund_trade[(fund_trade['trade_date'] == begin_date) & (fund_trade['is_buy']) & (fund_trade['index_id'] == asset)].fund_id.tolist()
                _fund_list = [i[0] for i in _score_list]
                dic = {
                    'index_id':asset,
                    'begin_date':begin_date,
                    'end_date':end_date,
                    'fund_list':_fund_list[:proper_number_dict[asset]]
                }
                if asset in res:
                    res[asset].append(dic)
                else:
                    res[asset] = [dic]
        _res = []
        for index_id in res:
            _index_id_res = []
            for date_dic in res[index_id]:
                fund_nav_i = fund_nav.loc[date_dic['begin_date']:date_dic['end_date'],date_dic['fund_list']]
                for fund_id in fund_nav_i:
                    fund_i_fee = fee_df.loc[fund_id,'trade_fee']
                    fee_discount_l = np.linspace(1,1-fund_i_fee,fund_nav_i.shape[0])
                    fund_nav_i[fund_id] = fund_nav_i[fund_id] * fee_discount_l
                fund_ret_combine = pd.DataFrame(fund_nav_i.pct_change(1).mean(axis=1).dropna())
                _index_id_res.append(fund_ret_combine)
            fund_combine_rets = pd.concat(_index_id_res).rename(columns={0:'funds'})
            index_ret = index_price[[index_id]].loc[rebalance_date[0]: rebalance_date[-1]].pct_change(1).dropna()
            price_ratio_index = (fund_combine_rets.join(index_ret)+1).cumprod()
            price_ratio_index = pd.DataFrame(price_ratio_index['funds'] / price_ratio_index[index_id]).rename(columns={0:index_id})
            _res.append(price_ratio_index)
        df_plot = pd.concat(_res, axis=1, sort=False)
        res = []
        for index_id in df_plot:
            _index_stats = Calculator.get_stat_result_from_df(df=df_plot.reset_index(), date_column='datetime', value_column=index_id).__dict__
            _index_stats['index_id'] = index_id 
            res.append(_index_stats)
        
        stats = pd.DataFrame(res).set_index('index_id')[['annualized_ret','annualized_vol','mdd','sharpe','mdd_date1','mdd_date2']]
        df_plot.plot.line(figsize=(14,8))
        plt.title('基金所属各资产价格比',fontsize=20)
        plt.legend(loc='upper left', fontsize=15)
        plt.grid()
        plt.show()
        return stats

    @staticmethod
    def regular_rebalance_in_index_strategy(begin_date:datetime.date,
                                            end_date:datetime.date,
                                            index_id:str,
                                            rebalance_year:float,
                                            top_funds:int,
                                            dts:pd.Series,
                                            fund_score_dic:dict,
                                            fund_info:pd.DataFrame,
                                            index_price:pd.DataFrame,
                                            fund_nav:pd.DataFrame):
        
        def _get_top_funds(fund_score_dic, index_id, dt, top_nums):
            _score_dict = fund_score_dic[dt][index_id]
            _score_list = sorted(_score_dict.items(), key=lambda x:x[1], reverse=True)
            _fund_list = [i[0] for i in _score_list]
            if top_nums > len(_fund_list):
                return _fund_list
            else:
                return _fund_list[:top_nums]

        rebalance_date = int(rebalance_year * 242)
        fund_info['trade_fee'] = 0.15 * fund_info['purchase_fee'] + fund_info['redeem_fee']
        fee_df = fund_info[['fund_id','trade_fee']].set_index('fund_id')
        desc_name = fund_info[['fund_id','desc_name']].set_index('fund_id').to_dict()['desc_name']

        _dts = dts[(dts >= begin_date) & (dts <= end_date )].tolist()
        res = []
        for _idx, _dt in enumerate(_dts):
            if _idx % rebalance_date == 0:
                dic = {
                    'start_date':_dt,
                    'fund_list':_get_top_funds(fund_score_dic, index_id, _dt, top_funds),
                }
            elif _idx % rebalance_date == (rebalance_date-1):
                dic['end_date'] = _dt
                res.append(dic)
                dic = {
                    'start_date':_dt,
                    'fund_list':_get_top_funds(fund_score_dic, index_id, _dt, top_funds),
                }
        dic['end_date'] = _dt
        res.append(dic)
        _res = []
        for date_dic in res:
            fund_nav_i = fund_nav.loc[date_dic['start_date']:date_dic['end_date'],date_dic['fund_list']]
            for fund_id in fund_nav_i:
                fund_i_fee = fee_df.loc[fund_id,'trade_fee']
                fee_discount_l = np.linspace(1,1-fund_i_fee,fund_nav_i.shape[0])
                fund_nav_i[fund_id] = fund_nav_i[fund_id] * fee_discount_l
            fund_ret_combine = pd.DataFrame(fund_nav_i.pct_change(1).mean(axis=1).dropna())
            _res.append(fund_ret_combine)
        fund_combine_rets = pd.concat(_res).rename(columns={0:'funds'})
        fund_df = (fund_combine_rets+1).cumprod()
        fund_df.loc[_dts[0],'funds'] = 1
        fund_df = fund_df.sort_index()
        fund_df = fund_df.join(index_price[[index_id]]).fillna(method='ffill')
        fund_df = fund_df/fund_df.iloc[0]
        fund_df['price_ratio'] = fund_df['funds'] / fund_df[f'{index_id}']
        fund_df.plot.line(figsize=(15,8))
        plt.title(f'Selects top {top_funds} funds and rebalance every {rebalance_year} year in {index_id}',fontsize=25)
        plt.legend(loc='upper left', fontsize=15)
        plt.grid()
        plt.show()
        stats = Calculator.get_stat_result_from_df(df=fund_df.reset_index(), date_column='datetime', value_column='funds').__dict__
        result_df = pd.DataFrame([stats])[['annualized_ret','annualized_vol','mdd','sharpe','mdd_date1','mdd_date2']]
        result_df.index = ['portfolio result']
        _res = []
        for dic in res:
            _dic = {
                'start_date': dic['start_date'],
                'end_date':dic['end_date'],
            }
            for idx, _fund_id in enumerate(dic['fund_list']):
                _dic[f'fund_{idx+1}'] = desc_name[_fund_id]
            _res.append(_dic)
        pos_df = pd.DataFrame(_res)
        _col_list = pos_df.columns.tolist()
        _col_list1 = ['start_date','end_date']
        _col_list2 = [_ for _ in _col_list if _ not in _col_list1]
        col_list = _col_list1 + _col_list2
        pos_df = pos_df[col_list]
        return result_df, pos_df

    @staticmethod
    def fund_rank_recent_analysis(fund_id,index_id,score_dict,fund_info,fund_indicator,fund_nav,index_price,score_func,score_select):
        _res = []
        indicators = []
        for k,v in score_func.__dict__.items():
            if v !=0 :
                _res.append(f'{k} {round(v,2)}')
                indicators.append(k)
        _score_func = ' '.join(_res)  
        desc_name = fund_info[fund_info['fund_id'] == fund_id].desc_name.values[0]
        dts_list = sorted(list(score_dict.keys()))
        res = {}
        for dt in dts_list:
            _score_dict = score_dict[dt]
            if index_id in _score_dict:
                _score_dict = _score_dict[index_id][score_select[index_id]]
            else:
                continue
            _score_list = sorted(_score_dict.items(), key=lambda x:x[1], reverse=True)
            _fund_list = [i[0] for i in _score_list]
            res[dt] = _fund_list
        _res = []
        for dt, _fl in res.items():
            if fund_id in _fl:
                _res.append({'datetime':dt,'rank':_fl.index(fund_id)})
        rank_df = pd.DataFrame(_res)
        rank_df.set_index('datetime').plot(figsize=(16,8))
        plt.title(f'fund rank {desc_name} {fund_id}', fontsize=25)
        plt.legend(loc='upper right', fontsize=15)
        _res = []
        for i in rank_df.tail().to_dict('records'):
            _dt = i['datetime']
            _rank = i['rank']
            _res.append(f'{_dt} {_rank}')
        s = _score_func + '\n'+ '\n'.join(_res)

        plt.suptitle(s, y=0.87, fontsize=18)
        plt.show()

        dl = rank_df.tail().datetime.tolist()
        result = fund_indicator[(fund_indicator['fund_id'] == fund_id)
               &(fund_indicator['datetime'].isin(dl))][indicators+['datetime']].set_index('datetime')

        df = fund_nav[[fund_id]].join(index_price[index_id]).dropna()
        df = df / df.iloc[0]
        df.loc[:,'price_ratio'] = df[fund_id] / df[index_id]
        l1 = 3 * 242 + 10 if index_id in ['hs300','csi500'] else 242 + 10
        l = min(df.shape[0], l1)

        df.iloc[-l:]['price_ratio'].plot(figsize=(16,8))
        plt.title(f'{fund_id} {desc_name} indicator periods price_ratio', fontsize=25)
        plt.grid()
        plt.show()
        df['price_ratio'].plot(figsize=(16,8))
        plt.title(f'{fund_id} {desc_name} price_ratio', fontsize=25)
        plt.grid()
        plt.show()
        return result