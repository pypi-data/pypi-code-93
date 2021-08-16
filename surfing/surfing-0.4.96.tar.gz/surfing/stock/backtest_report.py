import os
import datetime
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from ..structure import PositionInfo
from ..data.wrapper import DataWrapper

class BacktestReport:
    # for single strategy

    def __init__(self,backtest_result=None,period=None,date_list=None,price_data=None,factor_data=None,stock_pool_data=None,stock_info=None,base_path=None,common_pool=None,pool=None):
        self.backtest_result = backtest_result
        self.hold_period     = period
        self.date_list       = date_list
        self.price_data      = price_data
        self.factor_data     = factor_data
        self.stock_info      = stock_info
        self.stock_pool_data = stock_pool_data
        self.base_path       = base_path
        self.common_pool     = common_pool
        self.pool            = pool
        self.post_open       = self.load_price('post_open')
        self.post_close      = self.load_price('post_close')
        self.post_vwap       = self.load_price('post_vwap')
        self.index_close     = self.load_index()
        self.report          = {} 

    # data process part
    def get_df(self, dic):
        return pd.DataFrame(data = dic['data'], columns = dic['columns'] )
    
    def get_sell_day(self, date):
        idx = self.date_list.index(date) + self.hold_period
        return self.date_list[idx]

    def filter_by_pool_2_series(self, dic, pool):
        return  pd.Series({k: v for k, v in  dic.items() if k in pool}).sort_index(ascending=True)

    def filter_dict_by_key(self, dic):
        dic = dict(filter(lambda elem: (elem[0] >= self.date_list[0] and elem[0] <= self.date_list[-1]), dic.items()))
        return dic

    def load_price(self, price_type):
        paths = os.path.join(self.base_path, price_type)
        meta_info = DataWrapper(paths).meta_info
        columns = meta_info['tickers']+['time']
        df = DataWrapper.base_load_npz(paths, price_type, columns)
        df = df.fillna(method='ffill')
        df.index = df.time.dt.strftime('%Y-%m-%d')
        df.drop(columns=['time'],inplace=True)
        df = df[self.common_pool]
        df = df.astype(float).round(3).copy()
        df['time'] = df.index
        data_dic = df.to_dict('index')
        return self.filter_dict_by_key(data_dic)

    def load_index(self):
        price_type = 'index_close'
        paths = os.path.join(self.base_path, price_type)
        meta_info = DataWrapper(paths).meta_info
        columns = meta_info['tickers']+['time']
        df = DataWrapper.base_load_npz(paths, price_type, columns)
        df = df[[self.pool, 'time']]
        df = df.loc[df['time'] >= self.backtest_result['mv']['data'][0][0]].copy()
        df = df.loc[df['time'] <= self.date_list[-1]].copy()
        return df.reset_index(drop=True)

    def analysis_df(self, df):
        df = pd.DataFrame(df)
        r1 = (df['close>open'].sum() /  df['close>open'].shape[0]) * 100
        r1 = round(r1, 2)                               #close > open rate
        r2 = (df['vwap>open'].sum() /  df['vwap>open'].shape[0]) * 100
        r2 = round(r2, 2)                               #vwap > open rate
        r3 = (df['close>vwap'].sum() /  df['close>vwap'].shape[0]) * 100
        r3 = round(r3, 2)                               #close > vwap  rate
        return r1, r2, r3
       
    # calculate part
    def result_mv(self):
        self.mv_df = self.get_df(self.backtest_result['mv'])    
        self.mv_result = {}
        self.mv_result['index_nv'] = self.index_close[self.pool] / self.index_close[self.pool].values[0]
        self.mv_result['strag_nv'] = self.mv_df['mv'] / self.mv_df['mv'].values[0]
        self.mv_result['hedge_nv'] = 0.5 * self.mv_result['index_nv'] + 0.5 * self.mv_result['strag_nv']
        self.mv_result['index_nv'] = self.mv_result['index_nv'].tolist()
        self.mv_result['strag_nv'] = self.mv_result['strag_nv'].tolist()
        self.mv_result['hedge_nv'] = self.mv_result['hedge_nv'].tolist()
        self.mv_result['date']     = self.mv_df['date'].tolist()

    def result_basic(self):
        st_b_day = datetime.datetime.strptime(self.mv_df.date.iloc[ 0], '%Y-%m-%d')
        st_e_day = datetime.datetime.strptime(self.mv_df.date.iloc[-1], '%Y-%m-%d')
        self.years =  (st_e_day - st_b_day).days / 365
        self.total_return = self.mv_df.mv.iloc[-1] / self.mv_df.mv.iloc[0]
        self.annualized_return = np.exp(np.log(self.total_return)/self.years) - 1
        self.annualized_volatiltity = (self.mv_df.mv.shift(1) / self.mv_df.mv).std() * np.sqrt((self.mv_df.shape[0] - 1) / self.years)
        self.sharpe = self.annualized_return / self.annualized_volatiltity
        
        self.buys_fee = PositionInfo.FEE_RATE['STOCK']['BUYFEE']
        self.sell_fee = PositionInfo.FEE_RATE['STOCK']['SELLFEE']
        self.slippage = PositionInfo.FEE_RATE['STOCK']['SLIPPAGE']

    def result_mdd(self):
        mdd_part1 = (self.mv_df.loc[:, 'mv'] / self.mv_df.loc[:, 'mv'].rolling(10000, min_periods=1).max())
        self.mdd_date1 = self.mv_df.loc[self.mv_df.loc[:mdd_part1.idxmin(),'mv'].idxmax(),'date']
        self.mdd_date2 = self.mv_df.loc[mdd_part1.idxmin(),'date']
        self.mdd = 1 - mdd_part1.min()

        self.mdd_below_level = 1 - self.mv_df.loc[:, 'mv'].min() / self.mv_df.loc[0, 'mv']
        if self.mdd_below_level  > 0:
            date_idx  = np.where(self.mv_df.loc[:,'mv'] <= self.mv_df.loc[0, 'mv'])[0][0]
            self.mdd_below_level_date1 = self.mv_df.loc[date_idx, 'date']
            self.mdd_below_level_date2 = self.mv_df.loc[self.mv_df.loc[:, 'mv'].idxmin(), 'date']
        else:
            self.mdd_below_level_date1 = None
            self.mdd_below_level_date2 = None

    def result_ic(self):
        self.ic_result = []
        for date in self.date_list[:-self.hold_period]:
            sel_date = self.get_sell_day(date)
            factor_1  = self.filter_by_pool_2_series(self.factor_data[date], self.stock_pool_data[date])
            price_1   = self.filter_by_pool_2_series(self.price_data[date],  self.stock_pool_data[date])
            price_2   = self.filter_by_pool_2_series(self.price_data[sel_date],  self.stock_pool_data[date])
            ic = pearsonr(factor_1.rank(pct=True), (price_2 / price_1).rank(pct=True))[0]
            self.ic_result.append({'date':date,'ic':ic})
        
        ic_df = pd.DataFrame(self.ic_result)
        self.ic_data = {
            'ic'    :   [0] + ic_df['ic'].values.tolist() + [0] * self.hold_period,
        }
        self.mean_ic = ic_df['ic'].mean()
        self.std_ic = ic_df['ic'].std()
        self.ir = self.mean_ic / self.std_ic

    def result_trade_pair(self):    
        trade_list = self.get_df(self.backtest_result['trade']).to_dict('records')
        trade_list_b = [_ for _ in trade_list if _['direction'] == 'BUY']
        trade_list_s = [_ for _ in trade_list if _['direction'] == 'SELL']
        self.trade_pair = []
        for trade_b in trade_list_b:
            for trade_s in trade_list_s:
                if trade_s['trade_volume'] == trade_b['trade_volume']: 
                    pct = (trade_s['trade_price'] / trade_b['trade_price'] - 1) * 100
                    self.trade_pair.append({'buy':trade_b, 'sel':trade_s, 'pct': pct})
                    break
        self.trade_pair = sorted(self.trade_pair, key = lambda i: i['pct'], reverse=True) 
        self.trade_pair_top = []
        self.trade_pair_bot = []
        for i in self.trade_pair[:10]:
            self.trade_pair_top.append(
                {
                    'pct'       :   str(round(i['pct'],2)) + '%',
                    'ticker'    :   i['buy']['ticker'],
                    'buy_time'  :   i['buy']['trade_time'],    
                    'sel_time'  :   i['sel']['trade_time'],
                    'chn_name'  :   self.stock_info[i['buy']['ticker']]['chn_name'],
                }
            ) 
        for i in self.trade_pair[-10:]:
            self.trade_pair_bot.append(
                {
                    'pct'       :   str(round(i['pct'],2)) + '%',
                    'ticker'    :   i['buy']['ticker'],
                    'buy_time'  :   i['buy']['trade_time'],    
                    'sel_time'  :   i['sel']['trade_time'],
                    'chn_name'  :   self.stock_info[i['buy']['ticker']]['chn_name'],
                }
            ) 

        self.mean_ret = np.mean([ _['pct'] for _ in self.trade_pair ])
        ticker_list = list(set([ _['ticker'] for _ in trade_list ]))
        ret_result = []
        recent_buy = []
        for ticker in ticker_list:
            ret_ticker = 0
            trade_time = 0
            trade_ticker_list = [ _ for _ in trade_list if _['ticker'] == ticker ]
            for i in trade_ticker_list:
                if (trade_ticker_list.index(i) == len(trade_ticker_list) - 1) and i['direction'] == 'BUY':
                    recent_buy.append({'ticker': ticker, 'date' : i['trade_time']})
                    continue
                trade_time += 1
                ret_ticker += i['trade_price'] * i['trade_volume'] * -1 if i['direction'] == 'BUY' else i['trade_price'] * i['trade_volume']
            ret_result.append({'ticker': ticker, 'earn_amount': ret_ticker, 'buy_times': int(trade_time/2)})
        
        self.stock_ret = pd.DataFrame(ret_result)
        ret_result = []
        self.stock_ret = self.stock_ret.sort_values(by='earn_amount', ascending=False)
        self.stock_ret = self.stock_ret.reset_index(drop=True)
        chn_name_list    = []
        sw_industry_list = []
        for ticker in self.stock_ret.ticker:
            chn_name_list.append(self.stock_info[ticker]['chn_name'])
            sw_industry_list.append(self.stock_info[ticker]['shenwan_industry_name'])

        self.stock_ret['chn_name'] =  chn_name_list
        self.stock_ret['sw_industry'] = sw_industry_list

        self.stock_ret['earn_amount'] = self.stock_ret['earn_amount'].astype(int)


        self.recent_buy = pd.DataFrame(recent_buy)
        chn_name_list    = []
        sw_industry_list = []
        for ticker in self.recent_buy.ticker:
            chn_name_list.append(self.stock_info[ticker]['chn_name'])
            sw_industry_list.append(self.stock_info[ticker]['shenwan_industry_name'])
        self.recent_buy['chn_name'] =  chn_name_list
        self.recent_buy['sw_industry'] = sw_industry_list
        self.recent_buy = self.recent_buy.to_dict('records')

        self.stock_ret_top10     = self.stock_ret.head(10).to_dict('records')
        self.stock_ret_bot10     = self.stock_ret.tail(10).to_dict('records')
        self.stock_ret_barchart  = {
            'earn_amount'   :  self.stock_ret['earn_amount'].values.tolist(),
            'ticker'        :  self.stock_ret['ticker'].values.tolist(),
        }
        
    def result_switch_price(self):
        buy_date_result = []
        sel_date_result = []
        for trade_i in self.backtest_result['trade']['data']:
            ticker      = trade_i[1]
            direction   = trade_i[2]
            date        = trade_i[5]
            open_p = self.post_open[date][ticker]
            cloz_p = self.post_close[date][ticker]
            vwap_p = self.post_vwap[date][ticker]
            con1 = (cloz_p > open_p) * 1
            con2 = (vwap_p > open_p) * 1
            con3 = (cloz_p > vwap_p) * 1
            if direction == 'BUY':
                buy_date_result.append({'close>open':con1,
                                        'vwap>open':con2,
                                        'close>vwap':con3})
            else:
                sel_date_result.append({'close>open':con1,
                                        'vwap>open':con2,
                                        'close>vwap':con3})
        self.buy_close_open, self.buy_vwap_open, self.buy_close_vwap = self.analysis_df(buy_date_result)
        self.sel_close_open, self.sel_vwap_open, self.sel_close_vwap = self.analysis_df(sel_date_result)
        

    def generate_report(self): 
        self.report['period']                   =   self.hold_period     
        self.report['year']                     =   str(round(self.years,2))
        self.report['annualized_return']        =   str(round(self.annualized_return, 2) * 100) + '%'
        self.report['annualized_volatility']    =   str(round(self.annualized_volatiltity,2))
        self.report['sharpe']                   =   str(round(self.sharpe,2))
        self.report['buy_fee']                  =   str(self.buys_fee)
        self.report['sell_fee']                 =   str(self.sell_fee)
        self.report['slippage']                 =   str(self.slippage)
        self.report['mdd']                      =   str(round(self.mdd*100,2)) + '%'
        self.report['mdd_date1']                =   self.mdd_date1
        self.report['mdd_date2']                =   self.mdd_date2
        self.report['mdd_below_level']          =   str(round(self.mdd_below_level*100,2)) + '%'
        self.report['mdd_below_level_date1']    =   self.mdd_below_level_date1
        self.report['mdd_below_level_date2']    =   self.mdd_below_level_date2
        self.report['ic_data']                  =   self.ic_data 
        self.report['mean_ic']                  =   str(round(self.mean_ic,4))
        self.report['ir']                       =   str(round(self.ir,4))
        self.report['buy_date_close>open']      =   str(self.buy_close_open) + '%'
        self.report['buy_date_vwap>open']       =   str(self.buy_vwap_open) + '%'
        self.report['buy_date_close>vwap']      =   str(self.buy_close_vwap) + '%'
        self.report['sel_date_close>open']      =   str(self.sel_close_open) + '%'
        self.report['sel_date_vwap>open']       =   str(self.sel_vwap_open) + '%'
        self.report['sel_date_close>vwap']      =   str(self.sel_close_vwap) + '%'
        self.report['trades_mean_ret']          =   str(round(self.mean_ret,3)) + '%'
        self.report['total_trade_fee']          =   str(self.buys_fee + self.sell_fee + 2 * self.slippage)
        self.report['trade_pair_top']           =   self.trade_pair_top
        self.report['trade_pair_bot']           =   self.trade_pair_bot
        self.report['stock_ret_top10']          =   self.stock_ret_top10
        self.report['stock_ret_bot10']          =   self.stock_ret_bot10
        self.report['recent_buy']               =   self.recent_buy
        self.report['stock_ret_barchart']       =   self.stock_ret_barchart
        self.report['mv']                       =   self.mv_result


    # main function of calculate backtest result
    def analysis_backtest_result(self):
        self.result_mv()
        self.result_basic()
        self.result_mdd()
        self.result_ic()
        self.result_trade_pair()
        self.result_switch_price()
        self.generate_report()
        return self.report