import pandas as pd
import numpy as np
import platform
import matplotlib as mpl
import pylab as pl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.dates as mdates
import datetime
from matplotlib.patches import Rectangle
from ....data.manager.score import FundScoreManager
CURRENT_PLATFORM = platform.system()
if CURRENT_PLATFORM == 'Darwin':
    mpl.rcParams['font.family'] = ['Heiti TC']
else:
    mpl.rcParams['font.family'] = ['STKaiti']
pd.plotting.register_matplotlib_converters()
class FundPainter(object):

    @staticmethod
    def plot_fund_weights(  fund_weights_history:dict, 
                            fund_cash_history:dict, 
                            fund_marktet_price_history:dict,
                            saa:dict):
        res = []
        for k,v in fund_weights_history.items():
            v = v
            v['date'] = k
            v['cash'] = fund_cash_history[k]  / fund_marktet_price_history[k]
            res.append(v)
        weights_df = pd.DataFrame(res).set_index('date')
        weights_df = weights_df.div(weights_df.sum(axis=1), axis=0)
        weights_df.fillna(0)[1:].round(3).plot.area(figsize=(18,9),legend=False,fontsize = 17)
        s = pl.title('fund weights history', fontsize=20)
        st = [k+':'+str(round(v,2)) for k, v in saa.items() if v > 0]
        st = ' '.join(st)
        plt.suptitle(st,y=0.87,fontsize=17)
        plt.grid()

    @staticmethod
    def plot_index_fund_fee( index_fee:pd.DataFrame):
        mpl.rcParams['font.size'] = 15
        p = index_fee.plot.pie(y='amount',figsize = (8,8))
        l = plt.legend(fontsize=17 ,loc = 'lower left')
        t = plt.title('index fee amount', fontsize=20)
        y = plt.ylabel(ylabel='fee amount', fontsize=17)
        plt.grid()

    @staticmethod
    def plot_fund_mdd_periods(  fund_mv:pd.DataFrame, 
                                fund_weights_history:dict, 
                                fund_nav:pd.DataFrame, 
                                fund_info:pd.DataFrame):
        df = fund_mv
        mdd_part1 = (df.loc[:, 'mv'] / df.loc[:, 'mv'].rolling(10000, min_periods=1).max())
        mdd = round(1 - mdd_part1.min(),4)
        mdd_date1 = df.loc[:mdd_part1.idxmin(),'mv'].idxmax()
        mdd_date2 = mdd_part1.idxmin()
        d1 = mdd_date1.strftime('%Y-%m-%d')
        d2 = mdd_date2.strftime('%Y-%m-%d')
        date_list = np.array(list(fund_weights_history.keys()))
        date_list = date_list[(date_list >= mdd_date1) & (date_list <= mdd_date2)]
        d = date_list[0]
        fund_list = [k for k,v in fund_weights_history[d].items() if isinstance(v, float) and (round(v,3) > 0)] 
        if 'cash' in fund_list:
            fund_list.remove('cash')
        df = fund_nav[fund_list].loc[mdd_date1:mdd_date2,:] 
        if df.empty:
            return 
        fig, ax = plt.subplots(figsize= [18,9])
        df = df/df.iloc[0]
        for col in df:
            df[col] = 1 - (1 - df[col].values )* fund_weights_history[d][col]
        table_df = fund_info.set_index('fund_id').loc[fund_list,:].reset_index()[['fund_id','desc_name','index_id']].sort_values(['index_id'])
        fund_desc_dict = fund_info.reset_index()[['fund_id','desc_name']].set_index('fund_id').to_dict()['desc_name']
        df_mdd = pd.DataFrame(((1-df.iloc[-1])*100).round(2))
        df_mdd.columns = ['max draw down %']
        table_df = table_df.set_index('fund_id').join(df_mdd).reset_index()
        fund_list = table_df.fund_id.tolist()
        df = df.rename(columns = fund_desc_dict)
        for col in df.columns:
            plt.plot(df.index, df[[col]], linewidth=1.0, label = col)
        plt.legend(fontsize=17 ,loc = 'lower left')
        plt.title('fund bt during mdd period  nav of all funds', fontsize=20)
        ax.xaxis.set_ticks_position('top')
        t = plt.table(cellText=table_df.values.tolist(),
          colLabels=table_df.columns,
          colWidths= [0.25,0.45,0.15,0.15],  
          loc='bottom',
          )
        t.auto_set_font_size(False)
        t.set_fontsize(17)
        t.auto_set_column_width('fund_id')
        t.AXESPAD = 0.1
        t.scale(1, 2)
        plt.grid()
        plt.suptitle(f'mdd : {mdd}, from {d1} to {d2}',y=0.87,fontsize=17)    
        plt.show()

    @staticmethod
    def plot_fund_mdd_amounts(  fund_mv:pd.DataFrame, 
                                fund_nav:pd.DataFrame, 
                                fund_info:pd.DataFrame,
                                fund_position_history:dict):
        df = fund_mv
        date_list = df.index.tolist()
        fund_ret = fund_nav / fund_nav.shift(1) - 1
        mdd_part1 = (df.loc[:, 'mv'] / df.loc[:, 'mv'].rolling(10000, min_periods=1).max())
        mdd_date1 = df.loc[:mdd_part1.idxmin(),'mv'].idxmax()
        mdd_date2 = mdd_part1.idxmin()
        res = []
        for d in fund_position_history:
            if d < mdd_date1 or d > mdd_date2:
                continue
            res_d = {}
            res_d['datetime'] = d
            if fund_position_history[d] == {}:
                continue
            else:
                for fund_id in fund_position_history[d]:
                    if fund_position_history[d][fund_id]['volume'] > 0:
                        res_d[fund_id] = fund_position_history[d][fund_id]['volume']
            res.append(res_d)
        volume_df = pd.DataFrame(res).set_index('datetime').loc[mdd_date1:mdd_date2]
        res = []
        for d, r in volume_df.iterrows():
            next_d = date_list[date_list.index(d) + 1]
            pos_n_1 = r.dropna()
            pos_n_1.name = 'pos'
            fund_id_list = pos_n_1.index.tolist()
            nav_n_1 = fund_nav.loc[d][fund_id_list]
            nav_n_1.name = 'nav'
            fund_ret_n = fund_ret.loc[next_d][fund_id_list] 
            fund_ret_n.name = 'ret'
            fund_pnl_i = pd.DataFrame([pos_n_1,nav_n_1,fund_ret_n]).T
            pnl_l = fund_pnl_i.prod(axis=1)
            pnl_l.name = d
            res.append(pnl_l)
        pnl_df = pd.DataFrame(res).fillna(0)
        desc_name_dict = fund_info.set_index('fund_id')[['desc_name']].to_dict()['desc_name']
        pnl_df.cumsum().rename(columns = desc_name_dict).plot.line(figsize=(18,9))
        plt.grid()
        plt.legend(fontsize=14 ,loc = 'lower left')
        plt.title('money loss during mdd period', fontsize=20)    
        plt.show()

    @staticmethod
    def plot_fund_ret_each_year(turnover_df:pd.DataFrame,
                                mdd: float,
                                annual_ret: float):
        annual_ret = round(annual_ret, 3)
        mdd = round(mdd, 3)
        ret_year = round(turnover_df.year_ret.mean(), 3)
        p = turnover_df.set_index('year')[['year_mdd','year_ret']].plot.bar(figsize=(12,9))
        t = plt.title('return and mdd each year', fontsize=20)
        s = plt.suptitle(f'annual ret: {annual_ret}, ret mean {ret_year},mdd {mdd}', y=0.87, fontsize=17)
        h = plt.axhline(y=annual_ret, linestyle=':', label='annual ret', color='darkorange')
        r = plt.xticks(rotation=0)
        l = plt.legend(fontsize=17 ,loc='upper left')
        plt.grid()
        
    @staticmethod
    def plot_turnover_rate_each_year(turnover_df:pd.DataFrame, turnover_rate_yearly_avg:float):
        turnover_rate_yearly_avg = round(turnover_rate_yearly_avg,2)
        p = turnover_df.set_index('year')[['turnover_rate_yearly']].plot.bar(figsize=(12,9))
        t = plt.title('turnover rate each year %', fontsize=20)
        s = plt.suptitle(f'mean {turnover_rate_yearly_avg}', y=0.87, fontsize=17)
        y = turnover_df['turnover_rate_yearly'].mean()
        h = plt.axhline(y=y, linestyle=':', label='turnover rate mean')
        r = plt.xticks(rotation=0)
        l = plt.legend(fontsize=17 ,loc='upper left')
        plt.grid()

    @staticmethod
    def plot_fund_score(fund_mv:pd.DataFrame, 
                        fund_weights_history:dict, 
                        trade_history:dict,
                        index_price:pd.DataFrame,
                        asset_weights:dict,
                        fund_info:pd.DataFrame,
                        fund_nav:pd.DataFrame,
                        fund_score:dict,
                        fund_score_raw:dict,
                        fund_indicator:pd.DataFrame,
                        asset=str,
                        is_tuning=bool,
                        score_select=dict,
                        ):
        fund_w = fund_weights_history
        end_date = fund_mv.index.tolist()[-1]
        date_list = list(trade_history.keys()) + [end_date]
        fund_asset_df = fund_info[['fund_id','index_id']].set_index('fund_id')
        fund_indicator = fund_indicator.pivot_table(index = ['fund_id','datetime'])
        traded_to_submit_date = {}
        for d in trade_history:
            dic = trade_history[d][0]
            traded_to_submit_date[dic.trade_date] = dic.submit_date
        res = []
        for k,v in asset_weights.items():
            v['date'] = k
            res.append(v)
        weights_df = pd.DataFrame(res).set_index('date')
        weights_df = weights_df.drop(['cash'], axis = 1).dropna()[1:]
        res = []
        for dic, s in zip(weights_df.to_dict('records'), weights_df.sum(axis = 1).values):
            res.append({ k: v/ s for k, v in dic.items()})
        df = pd.DataFrame(res)
        cols = df.columns.tolist()
        name_dic = fund_info[['fund_id','desc_name']].set_index('fund_id')
        b_d = fund_nav.index[0]
        e_d = fund_nav.index[-1]
        bench_df = index_price.loc[b_d:e_d,[asset]].dropna()
        bench_df = bench_df/bench_df.iloc[0]
        for i in range(len(date_list) - 1):   
            b_d = date_list[i]
            e_d = date_list[i+1]
            if b_d == e_d:
                break
            bench_df_tmp = bench_df.loc[b_d:e_d,:]
            bench_df_tmp = bench_df_tmp/bench_df_tmp.iloc[0]
            f_l = [k  for k ,v in fund_w[b_d].items() if isinstance(v, float) and round(v ,3 ) > 0]
            if 'cash' in f_l:
                f_l.remove('cash')
            f_l = [f for f in f_l if fund_asset_df.loc[f,'index_id'] == asset]
            mv_b = bench_df.loc[b_d,asset]
            fund_tmp = fund_nav.loc[b_d:e_d,f_l].copy()
            fund_tmp = fund_tmp/fund_tmp.iloc[0]
            fund_tmp = fund_tmp
            res = []
            submit_d = traded_to_submit_date[b_d]
            if len(f_l) < 1:
                continue
            fig, ax = plt.subplots(figsize= [16,12])
            plt.plot(bench_df_tmp.index, bench_df_tmp[asset], label=asset,linewidth=5.0)
            for f in f_l:
                desc = name_dic.loc[f,'desc_name']
                f_i_dict= fund_indicator.loc[f,submit_d].to_dict()
                dic = {
                    'fund_id' : f,
                    'desc_name' : desc,
                    'score' : round(fund_score[submit_d][asset][score_select[asset]][f],4),
                    'weight': round(fund_w[b_d][f], 4),
                    'score_raw': round(fund_score_raw[submit_d][asset][score_select[asset]][f],4),
                }
                for s in ['alpha','beta','fee_rate','track_err']:
                    dic[s] = round(f_i_dict[s],4)
                res.append(dic)    
                plt.plot(fund_tmp.index, fund_tmp[f], label=f+'_'+desc,linestyle='--',linewidth=3.0)    
            
            if is_tuning:
                fund_not_select = [f for f, v in fund_score[submit_d][asset][score_select[asset]].items() if f not in f_l][:10]
                if len(fund_not_select) < 1:
                    plt.legend(fontsize=17, loc = 'lower left')
                    plt.title(f'{asset} {b_d} {e_d}', fontsize=25)
                    plt.grid()
                    ax.xaxis.set_ticks_position('top')
                    continue
                fund_tmp = fund_nav.loc[b_d:e_d,fund_not_select].copy()
                fund_tmp = fund_tmp/fund_tmp.iloc[0]
                fund_tmp = fund_tmp
                for f in fund_not_select:
                    desc = name_dic.loc[f,'desc_name']
                    f_i_dict= fund_indicator.loc[f,submit_d].to_dict()
                    dic = {
                        'fund_id' : f,
                        'desc_name' : desc,
                        'score' : round(fund_score[submit_d][asset][score_select[asset]][f],4),
                        'weight': 0,
                        'score_raw': round(fund_score_raw[submit_d][asset][score_select[asset]][f],4),
                    }
                    for s in ['alpha','beta','fee_rate','track_err']:
                        dic[s] = round(f_i_dict[s],4)
                    res.append(dic)   
                    plt.plot(fund_tmp.index, fund_tmp[f], label=f+'_'+desc,linestyle=':',linewidth=3.0)    

            plt.legend(fontsize=17, loc = 'lower left')
            plt.title(f'{asset} {b_d} {e_d}', fontsize=25)
            _score = FundScoreManager().funcs[asset][score_select[asset]].__dict__
            _score = {fac:w for fac, w in _score.items() if w != 0}
            plt.suptitle(_score, y=0.87, fontsize=18)
            ax.xaxis.set_ticks_position('top')
            fund_df = pd.DataFrame(res)
            fund_df = fund_df[['desc_name','fund_id','weight','alpha','beta','track_err','fee_rate','score_raw','score']]
            fund_df = fund_df.sort_values('score', ascending = False)
            t = plt.table(
                cellText=fund_df.values.tolist(),
                colLabels=fund_df.columns,
                loc='bottom',
                colWidths= [0.25,0.12,0.09,0.09,0.09,0.09,0.09,0.09,0.09]          
            )
            t.auto_set_font_size(False)
            t.set_fontsize(17)
            t.auto_set_column_width('fund_id')
            t.AXESPAD = 0.1
            t.scale(1, 4)
            plt.grid()
            plt.show()

    @staticmethod
    def plot_fund_alpha(fund_nav:pd.DataFrame, 
                        fund_info:pd.DataFrame, 
                        index_price:pd.DataFrame,
                        fund_position_history:dict,
                        backtest_result:dict):

        rebalance_date = backtest_result['rebalance_date'] + [backtest_result['market_value'].index.tolist()[-1]]
        fund_desc_name = fund_info[['fund_id','desc_name']].set_index('fund_id').to_dict()['desc_name']  
        res = {}
        for idx, d in enumerate(rebalance_date[:-1]):
            for fund_id in fund_position_history[d]:
                if fund_position_history[d][fund_id]['volume'] > 0:
                    index_id = fund_position_history[d][fund_id]['index_id']
                    dic_i = {
                        'start_date':d,
                        'fund_id': fund_id,
                        'volume':fund_position_history[d][fund_id]['volume'],
                        'end_date':rebalance_date[idx + 1],
                        'index_id':index_id,
                        'price':fund_position_history[d][fund_id]['price'],
                    }
                    if index_id in res:
                        res[index_id].append(dic_i)
                    else:
                        res[index_id] = [dic_i]
                    
        for index_id in res:
            df_index_funds = pd.DataFrame(res[index_id])
            df_index_funds['amount'] = df_index_funds['price'] * df_index_funds['volume']
            result = []
            red_box = []
            green_box = []
            for d_idx, d in enumerate(sorted(set(df_index_funds.start_date))):
                df_i  = df_index_funds[df_index_funds.start_date == d].copy()
                amount_sum = df_i.amount.sum()
                df_i.loc[:,'weight'] = df_i['amount'].map(lambda x: round(x / amount_sum,2))
                df_i = df_i.sort_values('weight').reset_index(drop=True)
                d1 = d
                d2 = df_i.end_date.values[0]
                index_ret = index_price.loc[d2,index_id] / index_price.loc[d1,index_id] - 1
                dic = {
                    'start_date':d1,
                    'end_date':d2,
                    index_id:int(10000*index_ret),
                }
                for _idx, r in df_i.iterrows():
                    f_r = int(10000 * (fund_nav.loc[d2,r.fund_id] / fund_nav.loc[d1,r.fund_id] - 1 - index_ret))
                    fund_loc = f'fund_{_idx+1}'
                    sign = "+" if f_r >= 0 else "-"
                    dic[fund_loc] = f'{fund_desc_name[r.fund_id]} {sign} {abs(f_r)}'
                    if f_r >= index_ret:
                        red_box.append((d_idx+1,_idx+1+2))
                    else:
                        green_box.append((d_idx+1,_idx+1+2))
                result.append(dic)
            df_result = pd.DataFrame(result)
            l = df_result.columns.tolist()
            l1 = ['start_date','end_date',index_id]
            l2 = [i for i in l if i not in l1]
            table_df = df_result[l1 + l2].fillna('')
            fig, ax = plt.subplots()
            ax.axis('tight')
            ax.axis('off')
            col_l = [0.2,0.2,0.15] + [0.60] * (table_df.shape[1]-3)
            the_table = ax.table(cellText=table_df.values.tolist(),
            colLabels=table_df.columns,
            colWidths= col_l,  
            loc='center')
            the_table.auto_set_font_size(False)
            the_table.set_fontsize(11)
            the_table.AXESPAD = 0.1
            the_table.scale(1, 3)
            for i in red_box:
                the_table[i].set_facecolor('#ffe5ad')
            for i in green_box:
                the_table[i].set_facecolor('#cffdbc')
            plt.show()

    @staticmethod
    def plot_mv_on_each_asset(fund_nav:pd.DataFrame, 
                                fund_info:pd.DataFrame, 
                                index_price:pd.DataFrame,
                                fund_position_history:dict,
                                backtest_result:dict):
        fund_info['trade_fee'] = fund_info['purchase_fee'] + fund_info['redeem_fee']
        fee_df = fund_info[['fund_id','trade_fee']].set_index('fund_id')

        rebalance_date = backtest_result['rebalance_date'] + [backtest_result['market_value'].index.tolist()[-1]]
        res = {}
        for idx, d in enumerate(rebalance_date[:-1]):
            for fund_id in fund_position_history[d]:
                if fund_position_history[d][fund_id]['volume'] > 0:
                    index_id = fund_position_history[d][fund_id]['index_id']
                    dic_i = {
                        'start_date':d,
                        'fund_id': fund_id,
                        'volume':fund_position_history[d][fund_id]['volume'],
                        'end_date':rebalance_date[idx + 1],
                        'index_id':index_id,
                        'price':fund_position_history[d][fund_id]['price'],
                    }
                    if index_id in res:
                        res[index_id].append(dic_i)
                    else:
                        res[index_id] = [dic_i]
                        
        for index_id in res:
            index_res = []
            df_index_funds = pd.DataFrame(res[index_id])
            df_index_funds['amount'] = df_index_funds['price'] * df_index_funds['volume']
            last_value = 1
            for d_idx, d in enumerate(sorted(set(df_index_funds.start_date))):
                df_i  = df_index_funds[df_index_funds.start_date == d].copy()
                amount_sum = df_i.amount.sum()
                df_i.loc[:,'weight'] = df_i['amount'].map(lambda x: x / amount_sum)
                d1 = d
                d2 = df_i.end_date.values[0]
                fund_sub_list = df_i.fund_id.tolist()
                index_df_i = fund_nav.loc[d1:d2][df_i.fund_id.tolist()]
                for fund_id in fund_sub_list:
                    fund_i_fee = fee_df.loc[fund_id,'trade_fee']
                    fee_discount_l = np.linspace(1,1-fund_i_fee,index_df_i.shape[0])
                    index_df_i[fund_id] = index_df_i[fund_id] * fee_discount_l
                w_df = df_i[['fund_id','volume']].set_index('fund_id').T
                weighted_s = (index_df_i * w_df.values).sum(axis=1)
                if weighted_s.empty:
                    continue
                ws = weighted_s.iloc[:-1]
                ws = ws / ws[0] * last_value
                last_value = ws[-1] 
                index_res.append(ws)
            
            asset_weighted_index = pd.DataFrame(pd.concat(index_res)).rename(columns={0:index_id+' fund weighted sum'})
            asset_weighted_index = index_price[[index_id]].join(asset_weighted_index).dropna()
            asset_weighted_index = asset_weighted_index / asset_weighted_index.iloc[0]
            asset_weighted_index.plot.line(figsize=(15,12))
            last_value = round(asset_weighted_index[index_id+' fund weighted sum'].values[-1],4)
            plt.title(f'{index_id} funds weighted price vs {index_id} ', fontsize=25)
            plt.suptitle(f'last asset value {last_value}', y=0.87, fontsize=17)
            plt.legend(fontsize=17, loc = 'lower left')
            plt.grid()
            plt.show()

    @staticmethod
    def plot_recent_ret(df_plot_i:pd.DataFrame,begin_date:datetime.date,end_date:datetime.date,st:str,port_id:str):
        df_plot_i.index = [str(i) for i in df_plot_i.index]
        df_plot_i.plot.line(figsize=(12,6))
        plt.title(f'portfolio {port_id} mv from {begin_date} to {end_date}', fontsize=20)
        plt.suptitle(st,y=0.87,fontsize=17)
        plt.legend(loc='lower left',fontsize = 15)
        plt.grid()
        plt.show()

    @staticmethod
    def plot_fund_rank( score_dic:pd.DataFrame, 
                        fund_info:pd.DataFrame, 
                        fund_id:str,
                        begin_date:datetime.date,
                        fund_index_map:dict):
        index_id = fund_index_map[fund_id]
        res = []
        for d in score_dic:
            if d > begin_date:
                score_d = score_dic[d][index_id]
                sorted_score = sorted(score_d.items(), key=lambda x:x[1], reverse=True)
                sorted_score = [i[0] for i in sorted_score]
                try:
                    rank = sorted_score.index(fund_id)
                except:
                    rank = 666
                res.append({'datetime':d,'rank':rank})
        desc_name = fund_info[fund_info.fund_id == fund_id].desc_name.values[0]
        score = pd.DataFrame(res).set_index('datetime')
        score.plot.line(figsize=(12,6))
        plt.title(f'{fund_id}  {desc_name}  rank  ', fontsize=25)
        plt.grid()
        plt.show()

    @staticmethod
    def plot_rolling_analysis( annual_ret:pd.DataFrame, 
                               fund_annual_ret:float,
                               year:int,
                               index_id:'str',
                               ret_list:list):
        
        df1 = annual_ret.dropna()[[index_id,'战略配置']]
        index = df1.index
        saa1 = df1[index_id]
        taa1 = df1.战略配置
        df2 = annual_ret.dropna()[['战略配置','战术配置']]
        index = df2.index
        saa2 = df2.战略配置
        taa2 = df2.战术配置
        df3 = annual_ret.dropna()[['战术配置','优选基金']]
        index = df3.index
        saa3 = df3.战术配置
        taa3 = df3.优选基金
        df4 = annual_ret.dropna()[[index_id,'优选基金']]
        index = df4.index
        saa4 = df4[index_id]
        taa4 = df4.优选基金

        df1.plot.line(figsize=(16,6))
        plt.fill_between(index, saa1, taa1,
                        where=(saa1 < taa1),
                        alpha=0.30, color='#ff7f0e', interpolate=False)
        plt.fill_between(index, saa1, taa1,
                        where=(saa1 > taa1),
                        alpha=0.30, color='#1f77b4', interpolate=False)
        pl.legend(loc='upper left',fontsize = 17)
        pl.title(f'滚动{year}年化收益对比', fontsize=20)
        plt.grid()
        plt.show()
        
        df2.plot.line(figsize=(16,6))
        plt.fill_between(index, saa2, taa2,
                        where=(saa2 < taa2),
                        alpha=0.30, color='#ff7f0e', interpolate=False)
        plt.fill_between(index, saa2, taa2,
                        where=(saa2 > taa2),
                        alpha=0.30, color='#1f77b4', interpolate=False)
        pl.legend(loc='upper left',fontsize = 17)
        pl.title(f'滚动{year}年化收益对比', fontsize=20)
        plt.grid()
        plt.show()
        
        df3.plot.line(figsize=(16,6))
        plt.fill_between(index, saa3, taa3,
                        where=(saa3 < taa3),
                        alpha=0.30, color='#ff7f0e', interpolate=False)
        plt.fill_between(index, saa3, taa3,
                        where=(saa3 > taa3),
                        alpha=0.30, color='#1f77b4', interpolate=False)
        pl.legend(loc='upper left',fontsize = 17)
        pl.title(f'滚动{year}年化收益对比', fontsize=20)
        plt.grid()
        plt.show()
        df4.plot.line(figsize=(16,6))
        plt.fill_between(index, saa4, taa4,
                        where=(saa4 < taa4),
                        alpha=0.30, color='#ff7f0e', interpolate=False)
        plt.fill_between(index, saa4, taa4,
                        where=(saa4 > taa4),
                        alpha=0.30, color='#1f77b4', interpolate=False)
        pl.legend(loc='upper left',fontsize = 17)
        pl.title(f'滚动{year}年化收益对比', fontsize=20)
        plt.grid()
        plt.show()
        df_funds = annual_ret.dropna()[['优选基金']].rename(columns={'优选基金':'value'})
        df_funds.plot.hist(bins=20, figsize=(16,10),legend=None)
        plt.title(f'基金滚动{year}年收益分布', fontsize=25)
        plt.grid()
        plt.show()
        df_funds = df_funds.groupby('value')['value'].agg('count').pipe(pd.DataFrame).rename(columns = {'value': 'frequency'})
        df_funds['pdf'] = df_funds['frequency'] / sum(df_funds['frequency'])
        df_funds['cdf'] = df_funds['pdf'].cumsum()
        df_funds.index.name = '年化收益'
        index_loc = df_funds.index.values[df_funds.index.values > fund_annual_ret][0]
        cdf_loc = df_funds.loc[index_loc, 'cdf']
        df_funds = 1 - df_funds[['cdf']]
        df_funds[['cdf']].plot.line(figsize=(12,6), legend=None)
        _st_low = ''
        _st_high = ''
        mean_ret = round(100 * abs(df_funds['cdf'] - 0.5).idxmin(),2)
        for ret_i in ret_list:
            if ret_i < mean_ret/100:
                prob = round(1 - df_funds[['cdf']].loc[:ret_i].cdf.values[-1],3)
                _ret_s = f'ret {ret_i} prob {prob}  '
                _st_low += _ret_s
            else:
                prob = round(df_funds[['cdf']].loc[:ret_i].cdf.values[-1],3)
                _ret_s = f'ret {ret_i} prob {prob}  '
                _st_high += _ret_s
        plt.scatter(index_loc, 1-cdf_loc, marker='D', color='C1', s=60)
        plt.title(f'{year}年年化收益 累积密度分布', fontsize=20)
        rate = round((1-cdf_loc)*100,2)
        st = f'组合年化收益 {round(fund_annual_ret * 100, 2)}%  获取年化收益胜率 {rate}%  50%胜率年化收益 {mean_ret}%'
        st = st + '\n 低于收益概率' + _st_low + '\n 高于收益概率' + _st_high
        plt.suptitle(st,y=0.87,fontsize=17)
        plt.grid()
        plt.show()
        
    @staticmethod
    def plot_legend_aside(df):
        df.index = [str(i) for i in df.index]
        df.plot(figsize=(14,8),fontsize=20)
        plt.title('同期跑赢指数基金',fontsize=25)
        plt.legend(loc='upper left',fontsize=15, bbox_to_anchor=(1,1))
        plt.grid()
        plt.show()
