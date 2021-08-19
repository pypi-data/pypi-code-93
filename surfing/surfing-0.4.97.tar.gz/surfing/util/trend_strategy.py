import pandas as pd
import numpy as np
import datetime 
import matplotlib as mpl
import matplotlib.pyplot as plt
import statsmodels.api as sm
mpl.rcParams['font.family'] = ['Heiti TC']


class TrendCalculator:
    
    @staticmethod
    # 短线下穿长线
    def cross_down(index_price, short_term_ma, long_term_ma):
        index_price['_tmp'] = index_price[short_term_ma] < index_price[long_term_ma]
        return index_price['_tmp'] & (~ index_price['_tmp'].shift(1).fillna(False)) 
    
    @staticmethod
    # 两条线过去一端时间没有相交，且line_1在line_2上面
    def up_with_no_cross(index_price, line_1, line_2, term):
        index_price['_tmp'] = (index_price[line_1] > index_price[line_2]) * 1
        return index_price['_tmp'].rolling(term).min() > 0

    @staticmethod
    # 短线下穿长线
    def cross_up(index_price, short_term_ma, long_term_ma):
        index_price['_tmp'] = index_price[short_term_ma] > index_price[long_term_ma]
        return index_price['_tmp'] & (~ index_price['_tmp'].shift(1).fillna(False)) 

    @staticmethod
    # 两线幅度差
    def diff_rate(index_price, line_1, line_2):
        return index_price[line_1] / index_price[line_2] - 1

class TrendStrategy:

    DATA_SOURCE = '/Users/huangkejia/Downloads/test/sp500rmb.xlsx'
    YEAR = 242
    RISK_FEE_RATE = 0.025

    def __init__(self):
        pass

    def init(self, df=None):
        dic = {
            '代码':'index_id',
            '日期':'datetime',
            '开盘价(元)':'open',
            '最高价(元)':'high',
            '最低价(元)':'low',
            '收盘价(元)':'close',
        }
        if df is None:
            self.index_price = pd.read_excel(self.DATA_SOURCE).iloc[:-2]
            self.index_price = self.index_price.rename(columns = dic).drop(['名称','成交额(百万)','成交量(股)'], axis=1)
            self.index_price['index_id'] = 'sp500rmb'
            self.index_price = self.index_price.set_index('datetime')
            self.index_price.index = pd.to_datetime(self.index_price.index).date
        else:
            self.index_price = df
            self.index_price = self.index_price.set_index('datetime')
        self.dts = self.index_price.index.tolist()
        self.index_id = self.index_price.index_id.unique().tolist()[0]

    def fac_calculator(self):
        self.index_price.index = pd.to_datetime(self.index_price.index).date
        self.index_price.loc[:,'ret'] = self.index_price['close'].pct_change(1)
        self.index_price.loc[:,'std5'] = self.index_price['ret'].rolling(window=5).std(ddof=1)
        self.index_price.loc[:,'std10'] = self.index_price['ret'].rolling(window=10).std(ddof=1)
        self.index_price.loc[:,'std120'] = self.index_price['ret'].rolling(window=120).std(ddof=1)   

        term = 120
        self.index_price['term_high'] = self.index_price['high'].rolling(window=term,min_periods=1).max()
        self.index_price['term_low'] = self.index_price['low'].rolling(window=term,min_periods=1).min()
        self.index_price['rsi'] = (self.index_price['close'] - self.index_price['term_low']) / (self.index_price['term_high'] - self.index_price['term_low']) * 100
        self.index_price['rsi_ma_x1'] = self.index_price['rsi'].rolling(window=5, min_periods=1).mean()
        self.index_price['rsi_ma_x2'] = self.index_price['rsi_ma_x1'].rolling(window=3, min_periods=1).mean()
        self.index_price['rsi_ma_x3'] = self.index_price['rsi_ma_x2'].rolling(window=2, min_periods=1).mean()

        short_term = 10
        self.index_price['term_s_high'] = self.index_price['high'].rolling(window=short_term,min_periods=1).max()
        self.index_price['term_s_low'] = self.index_price['low'].rolling(window=short_term,min_periods=1).min()
        self.index_price['rsi_s'] = (self.index_price['close'] - self.index_price['term_s_low']) / (self.index_price['term_s_high'] - self.index_price['term_s_low']) * 100
        self.index_price['rsi_s_ma_x1'] = self.index_price['rsi_s'].rolling(window=5, min_periods=1).mean()
        self.index_price['rsi_s_ma_x2'] = self.index_price['rsi_s_ma_x1'].rolling(window=3, min_periods=1).mean()
        self.index_price['rsi_s_ma_x3'] = self.index_price['rsi_s_ma_x2'].rolling(window=2, min_periods=1).mean()

        self.index_price['ma_2d'] = self.index_price['close'].rolling(2).mean()
        self.index_price['ma_1w'] = self.index_price['close'].rolling(5).mean()
        self.index_price['ma_2w'] = self.index_price['close'].rolling(10).mean()
        self.index_price['ma_3w'] = self.index_price['close'].rolling(15).mean()
        self.index_price['ma_1m'] = self.index_price['close'].rolling(20).mean()
        self.index_price['ma_3m'] = self.index_price['close'].rolling(60).mean()
        self.index_price['ma_6m'] = self.index_price['close'].rolling(121).mean()
        self.index_price['ma_9m'] = self.index_price['close'].rolling(180).mean()
        self.index_price['ma_1y'] = self.index_price['close'].rolling(self.YEAR).mean()
        self.index_price['ma_2y'] = self.index_price['close'].rolling(self.YEAR*2).mean()
        self.index_price['ma_3y'] = self.index_price['close'].rolling(self.YEAR*3).mean()
        self.index_price['ma_5y'] = self.index_price['close'].rolling(self.YEAR*5).mean()
        self.index_price['ma_7y'] = self.index_price['close'].rolling(self.YEAR*7).mean()
        self.index_price['y1_diff'] = self.index_price['close'] < self.index_price['ma_1y']
        self.index_price['m6_diff'] = self.index_price['close'] < self.index_price['ma_6m']
        self.index_price['m3_diff'] = self.index_price['close'] < self.index_price['ma_3m']
        self.index_price['m1_diff'] = self.index_price['close'] < self.index_price['ma_1m']
        self.index_price['d20_rise'] = self.index_price['ma_1m'] > self.index_price['ma_1m'].shift(1)
        self.index_price['d15_rise'] = self.index_price['ma_3w'] > self.index_price['ma_3w'].shift(1)
        self.index_price['d10_rise'] = self.index_price['ma_2w'] > self.index_price['ma_2w'].shift(1)
        self.index_price['d5_rise'] = self.index_price['ma_1w'] > self.index_price['ma_1w'].shift(1)
        self.index_price['long_term_rise'] = (self.index_price['ma_5y'] > self.index_price['ma_7y']) & \
                                        (self.index_price['ma_1y'] > self.index_price['ma_2y']) & \
                                        (self.index_price['ma_1m'] > self.index_price['ma_6m'])

        self.index_price['close_y1_diff'] = TrendCalculator.diff_rate(self.index_price, 'close','ma_1y')
        self.index_price['close_9m_diff'] = TrendCalculator.diff_rate(self.index_price, 'close','ma_9m')
        self.index_price['close_6m_diff'] = TrendCalculator.diff_rate(self.index_price, 'close','ma_6m')
        self.index_price['close_3m_diff'] = TrendCalculator.diff_rate(self.index_price, 'close','ma_3m')
        self.index_price['close_1m_diff'] = TrendCalculator.diff_rate(self.index_price, 'close','ma_1m')
        self.index_price['1m_y1_diff'] = TrendCalculator.diff_rate(self.index_price, 'ma_1m','ma_1y')
        self.index_price['1w_y1_diff'] = TrendCalculator.diff_rate(self.index_price, 'ma_1w','ma_1y')
        self.index_price['ma_y1_std242'] = self.index_price['ma_1y'].pct_change(1).rolling(242).std(ddof=1)
        self.index_price['ma_y1_std120'] = self.index_price['ma_1y'].pct_change(1).rolling(120).std(ddof=1)
        self.index_price['ma_y1_std60'] = self.index_price['ma_1y'].pct_change(1).rolling(60).std(ddof=1)
        self.index_price['ma_y1_std30'] = self.index_price['ma_1y'].pct_change(1).rolling(30).std(ddof=1)
        self.index_price['ma_y1_std20'] = self.index_price['ma_1y'].pct_change(1).rolling(20).std(ddof=1)
        self.index_price['ma_y1_std10'] = self.index_price['ma_1y'].pct_change(1).rolling(10).std(ddof=1)
        self.index_price['ma_y1_std5'] = self.index_price['ma_1y'].pct_change(1).rolling(5).std(ddof=1)
        self.index_price['top_fac'] = TrendCalculator.cross_down(self.index_price,'close','ma_9m') & \
                                (TrendCalculator.up_with_no_cross(self.index_price, 'close','ma_9m', 5).shift(1))#20
        self.index_price['bottom_fac'] = (self.index_price['rsi_ma_x3'].rolling(5).min() < 10)# & \
        self.index_price['stop_earn_fac'] = TrendCalculator.cross_up(self.index_price, 'ma_5y', 'ma_7y')


    def make_trade_signal(self, df:pd.DataFrame, start_fac:str='top_fac', end_fac:str='bottom_fac', if_stop_loss:bool=False):
        trade_status = False
        open_price = None
        start_signal_list = []
        end_signal_list = []
        for _dt in df.index:
            if not trade_status:
                if df.loc[_dt, start_fac]:
                    start_signal_list.append(_dt)
                    open_price = df.loc[_dt,'close']
                    trade_status = True
            if trade_status:
                if df.loc[_dt, end_fac]:
                    end_signal_list.append(_dt)
                    trade_status = False
                    continue
                if if_stop_loss:
                    if df.loc[_dt,'close'] / open_price > 1.35:
                        end_signal_list.append(_dt)
                        trade_status = False
        if trade_status:
            end_signal_list.append(_dt)
        return start_signal_list, end_signal_list

    def plot_signal_point(self, start_signal_list, end_signal_list, line_1, line_2, is_plot_type_1=False, is_plot_type_2=False):
        each_invest_captical = 100
        last_idx = 0
        date_list = [self.dts[0]]
        year_length = 5
        while last_idx < len(start_signal_list):
            d0 = start_signal_list[last_idx]
            d1 = end_signal_list[last_idx]
            while ((d1 - d0).days < 365 * year_length) and (last_idx < len(start_signal_list)):
                last_idx += 1
                if last_idx < len(start_signal_list):
                    d1 = end_signal_list[last_idx]
                else:
                    break
            last_idx += 1
            date_list.append(d0 - datetime.timedelta(1))
            date_list.append(d1 + datetime.timedelta(1))
        df_res = []
        for idx, _dt in enumerate(date_list[:-1]):
            dt =  date_list[date_list.index(_dt) + 1]
            _dt_ = _dt - datetime.timedelta(days=1)
            dt_ = dt + datetime.timedelta(days=1)
            start_signal_dts = [dt_i for dt_i in start_signal_list if (dt_i >= _dt) and (dt_i <= dt)]
            end_signal_dts = [dt_i for dt_i in end_signal_list if (dt_i >= _dt) and (dt_i <= dt)]   
            res = []
            for dt_1, dt_2 in zip(start_signal_dts,end_signal_dts):
                start_price = self.index_price.loc[dt_1,'close']
                end_price = self.index_price.loc[dt_2,'close']
                ret = (start_price - end_price) / start_price
                dic = {
                    'start_date':dt_1,
                    'end_date':dt_2,
                    'start_price':start_price,
                    'end_price':end_price,
                    'ret':ret,
                    'win':ret>0,
                    'amount': (ret+1)*each_invest_captical
                }
                res.append(dic)
            _df_i = pd.DataFrame(res)
            red_start_date = [i.start_date for i in _df_i.itertuples() if i.ret >0 ]
            green_start_date = [i.start_date for i in _df_i.itertuples() if i.ret <= 0]
            red_end_date = [i.end_date for i in _df_i.itertuples() if i.ret >0 ]
            green_end_date = [i.end_date for i in _df_i.itertuples() if i.ret <= 0]
            df_res.append(_df_i)
            if is_plot_type_1:
                _index_price = self.index_price[['close',line_1,line_2]].loc[_dt_:dt_].copy()
                _index_price[['close']].plot.line(figsize=(16,8), fontsize=15,linewidth=2, zorder=1)
                success_c = 'red'
                fail_c = 'limegreen'
                size = 250
                up_loc = 1.03
                low_loc = 0.97
                plt.scatter(x=red_start_date,y=_index_price[['close']].loc[red_start_date] * up_loc, c=success_c, marker='$1$', s = size, zorder=5)
                plt.scatter(x=green_start_date,y=_index_price[['close']].loc[green_start_date] * low_loc, c=fail_c, marker='$1$', s = size, zorder=5)
                plt.scatter(x=red_end_date,y=_index_price[['close']].loc[red_end_date] * up_loc, c=success_c, marker='$2$', s = size, zorder=5)
                plt.scatter(x=green_end_date,y=_index_price[['close']].loc[green_end_date] * low_loc, c=fail_c, marker='$2$', s = size, zorder=5)
                plt.plot(_index_price.index, _index_price[line_1], c='gold',linewidth=1.5, zorder=2, label=line_1)
                plt.plot(_index_price.index, _index_price[line_2], c='lightgray',linewidth=1.5, zorder=3,label=line_2)
                try:
                    _win_rate = round(_df_i.win.sum() / _df_i.shape[0] * 100,1)
                    plt.title(f'{self.index_id} {dt.year} top win rate {_win_rate}%', fontsize=20)
                except:
                    plt.title(f'{self.index_id} {dt.year}', fontsize=20)
                plt.legend(fontsize=15)
                plt.grid()
                plt.show()
            elif is_plot_type_2:
                _line = 't_stats'
                _index_price = self.index_price[['close',line_2,_line]].loc[_dt_:dt_].copy()
                success_c = 'red'
                fail_c = 'limegreen'
                size = 250
                up_loc = 1.03
                low_loc = 0.97
                fig, ax1 = plt.subplots(figsize=(16,8))
                ax1.set_xlabel('date', fontsize=15)
                ax1.set_ylabel('price', fontsize=15)
                ax1.plot(_index_price.index, _index_price.close, label='close')
                ax1.plot(_index_price.index, _index_price[line_2], label=line_2)
                plt.scatter(x=red_start_date,y=_index_price[['close']].loc[red_start_date] * up_loc, c=success_c, marker='$1$', s = size, zorder=5)
                plt.scatter(x=green_start_date,y=_index_price[['close']].loc[green_start_date] * low_loc, c=fail_c, marker='$1$', s = size, zorder=5)
                plt.scatter(x=red_end_date,y=_index_price[['close']].loc[red_end_date] * up_loc, c=success_c, marker='$2$', s = size, zorder=5)
                plt.scatter(x=green_end_date,y=_index_price[['close']].loc[green_end_date] * low_loc, c=fail_c, marker='$2$', s = size, zorder=5)
                plt.yticks(fontsize=14)
                plt.xticks(fontsize=14)
                plt.legend(fontsize=18)
                ax2 = ax1.twinx() 
                color = 'gold'
                ax2.set_ylabel(_line,fontsize=15) 
                ax2.plot(_index_price.index, _index_price[_line], label=_line, color = color)
                try:
                    _win_rate = round(_df_i.win.sum() / _df_i.shape[0] * 100,1)
                    plt.title(f'{self.index_id} {dt.year} top win rate {_win_rate}%', fontsize=20)
                except:
                    plt.title(f'{self.index_id} {dt.year}', fontsize=20)
                plt.yticks(fontsize=14)
                plt.legend(fontsize=18)
                plt.grid()
                plt.show()
        df_total = pd.concat(df_res, axis=0)
        return df_total

    def consecutive_analysis(self, df, direction='loss'):
        res_list = []
        tmp_list = []
        for r in df.itertuples():
            if direction == 'loss':
                if r.ret <= 0:
                    tmp_list.append({
                        'start_date':r.start_date,
                        'end_date':r.end_date,
                        'ret':r.ret,
                    })
                if r.ret > 0 and len(tmp_list) > 0:
                    res_list.append(tmp_list)
                    tmp_list = []
            else:
                if r.ret >= 0:
                    tmp_list.append({
                        'start_date':r.start_date,
                        'end_date':r.end_date,
                        'ret':r.ret,
                    })
                if r.ret < 0 and len(tmp_list) > 0:
                    res_list.append(tmp_list)
                    tmp_list = []

        consecutive_numbers = max([len(i) for i in res_list])
        length_dic = []
        _res_list = []
        for i in res_list:
            dic = {}
            dic['start_date'] = i[0]['start_date']
            dic['end_date'] = i[-1]['end_date']
            dic['day_length'] = (dic['end_date'] - dic['start_date']).days
            dic['max_diff'] = sum([_i['ret'] for _i in i])
            length_dic.append(dic)
            _res_list.append(dic['max_diff'])
        if direction == 'loss':
            result = [i for i in length_dic if i['max_diff'] == min(_res_list)][0]
        else:
            result = [i for i in length_dic if i['max_diff'] == max(_res_list)][0]
        result['consecutive_numbers'] = consecutive_numbers
        return result

    def asset_constancy_analysis(self):
        index_close = self.index_price[['close']]
        index_close = index_close.reset_index().rename(columns={'index':'datetime'})
        index_close['year_month'] = index_close.datetime.map(lambda x: f'{x.year}_{x.month}' )
        index_close = index_close.set_index('year_month')
        index_list = sorted(index_close.index.unique().tolist())
        res = []
        for index_i in index_list:
            _df = index_close.loc[index_i]
            if _df.shape[0] < 5:
                continue
            else:
                trade_year = _df.shape[0] / self.YEAR
                annualized_ret = np.exp(np.log(_df['close'].values[-1]/_df['close'].values[0])/trade_year ) - 1
                annualized_vol = (_df.close/_df.close.shift(1)).std(ddof=1) * np.sqrt(self.YEAR)
                sharpe = (annualized_ret - self.RISK_FEE_RATE) / annualized_vol
                dic = {'datetime':index_i,'sharpe':sharpe}
                res.append(dic)
        sharpe_result = pd.DataFrame(res)
        result = []
        for lag_m in range(1,61):
            y = sharpe_result.sharpe.shift(-lag_m).dropna()
            x = sharpe_result.loc[:y.shape[0]-1].sharpe
            est = sm.OLS(y, sm.add_constant(x, prepend=False)).fit()
            p = est.params.sharpe
            result.append({'lag':lag_m,'显著性':p})
        pd.DataFrame(result).set_index('lag').plot.bar(figsize=(16,8), fontsize=15, rot=0)
        plt.title(f'{self.index_id}业绩持续性',fontsize=25)
        plt.legend(fontsize=20)
        plt.xlabel('lag', fontsize=18)
        plt.show()
    
    def get_backtest_result(self, df):
        year_lens = len(list(set([i.year for i in self.dts])))
        date_list = [(r.end_date - r.start_date).days for r in df.itertuples()] 
        stats_res = {}
        stats_res['asset'] = self.index_id
        stats_res['start_date'] = self.index_price.index.tolist()[0]
        stats_res['end_date'] = self.index_price.index.tolist()[-1]
        stats_res['trade_num'] = df.shape[0]
        stats_res['win_trade_num'] = sum(df['win'] * 1)
        stats_res['loss_trade_num'] = df.shape[0] - sum(df['win'] * 1)
        stats_res['stop_earning_num'] = sum(df['ret'] < -0.15)
        stats_res['averager_holding_periods'] = int(np.mean(date_list))
        stats_res['max_holding_periods'] = int(np.max(date_list))
        stats_res['min_holding_periods'] = int(np.min(date_list))
        stats_res['max_earn_single_trade'] = df['ret'].max() 
        stats_res['max_loss_single_trade'] = df['ret'].min() 
        stats_res['earn_sum'] = df[df['ret'] > 0].ret.sum()
        stats_res['loss_sum'] = df[df['ret'] < 0].ret.sum()
        stats_res['earn_loss_rate'] = - stats_res['earn_sum'] / stats_res['loss_sum'] 
        stats_res['total_win_rate'] = stats_res['win_trade_num'] / (stats_res['win_trade_num'] + stats_res['loss_trade_num'])
        stats_res['num_per_year'] = stats_res['trade_num'] / year_lens
        stats_res['total_ret'] = df.amount.sum() / (df.shape[0] * 100) - 1
        stats_res['ret_per_trade'] = stats_res['total_ret'] / df.shape[0]
        lose_result = self.consecutive_analysis(df, direction='loss')
        stats_res['consecutive_loss'] = lose_result['consecutive_numbers']
        stats_res['consecutive_loss_start_date'] = lose_result['start_date']
        stats_res['consecutive_loss_end_date'] = lose_result['end_date']
        stats_res['max_consecutive_loss'] = lose_result['max_diff']
        win_result = self.consecutive_analysis(df, direction='win')
        stats_res['consecutive_win'] = win_result['consecutive_numbers']
        stats_res['consecutive_win_start_date'] = win_result['start_date']
        stats_res['consecutive_win_end_date'] = win_result['end_date']
        stats_res['max_consecutive_earn'] = win_result['max_diff']

        int_list = ['trade_num',
                    'win_trade_num',
                    'loss_trade_num',
                    'averager_holding_periods',
                    'max_holding_periods',
                    'min_holding_periods',
                    'stop_earning_num',
                    'consecutive_loss',
                    'consecutive_win']

        rate_list = ['earn_loss_rate',
                    'total_win_rate',
                    'total_ret',
                    'max_earn_single_trade',
                    'max_loss_single_trade',
                    'max_consecutive_loss',
                    'max_consecutive_earn']

        float_list = ['earn_sum','loss_sum','num_per_year']

        bp_list = ['ret_per_trade']

        for i in int_list:
            stats_res[i] = str(int(stats_res[i]))
        for i in rate_list:
            stats_res[i] = str(round((stats_res[i] * 100), 2)) + '%'

        for i in float_list:
            stats_res[i] = str(round((stats_res[i]), 3)) 

        for i in bp_list:
            stats_res[i] = str(round((stats_res[i] * 10000), 1)) +'bp'
        
        dic = {
            'asset':'资产', 
            'start_date':'回测开始日', 
            'end_date':'回测结束日', 
            'trade_num':'交易次数', 
            'win_trade_num':'盈利交易次数',
            'loss_trade_num':'亏损交易次数', 
            'stop_earning_num':'止损交易次数', 
            'averager_holding_periods':'平均开仓周期', 
            'num_per_year':'平均年开仓次数',
            'max_earn_single_trade':'最大单笔盈利',
            'max_loss_single_trade':'最大单笔亏损', 
            'max_holding_periods':'最大开仓天数', 
            'min_holding_periods':'最低开仓天数',
            'earn_sum':'盈利总额', 
            'loss_sum':'亏损总额', 
            'earn_loss_rate':'盈亏比',
            'total_win_rate':'总胜率', 
            'total_ret':'总收益', 
            'ret_per_trade':'每单平均收益',
            'consecutive_loss':'最大连续亏损交易次数',
            'consecutive_win':'最大连续盈利交易次数',
            'consecutive_loss_start_date':'最大连续亏损开始日',
            'consecutive_loss_end_date':'最大连续亏损结束日',
            'consecutive_win_start_date':'最大连续盈利开始日',
            'consecutive_win_end_date':'最大连续盈利结束日',
            'max_consecutive_loss':'最大连续亏损占单次开仓比例',
            'max_consecutive_earn':'最大连续盈利占单次开仓比例',
        }
        result = pd.DataFrame([stats_res], index=['回测记录']).rename(columns = dic)
        result = result.drop(['盈利总额','亏损总额','盈亏比'], axis=1)
        
        return result.T


if __name__ == "__main__":
    '''
    self = TrendStrategy()
    self.init()
    self.asset_constancy_analysis()

    strategy 1  未优化
    标普500过去12个月的价格均线和月底价格作比较，每个月根据信号来测试。
    如果月底标普500的价格高于过去12个月的均价（包含当月），则持有标普；否则卖出标普
    (月度计算)
    df = self.index_price.copy()
    df.index = pd.to_datetime(df.index)
    df = df[['close']].resample('M').last().copy()
    df.index = pd.Series(df.index).dt.date
    df = df.reset_index().copy()
    index_list = self.index_price.index.values
    real_index = []
    for r in df.itertuples():
        real_index.append(index_list[index_list <= r.index].tolist()[-1])
    df.index = real_index
    df['ma_1y'] = df[['close']].rolling(window=12).mean()
    df['top_fac'] = TrendCalculator.cross_down(df,'close','ma_1y')
    df['bottom_fac'] = TrendCalculator.cross_up(df,'close','ma_1y')

    start_signal_list, end_signal_list = self.make_trade_signal(df=df, start_fac='top_fac', end_fac='bottom_fac')
    df = self.plot_signal_point(start_signal_list, end_signal_list, 'ma_1w', 'ma_1y',is_plot_type_1=True)
    result = self.get_backtest_result(df)
    
    
    strategy 2  未优化
    标普500过去12个月的总回报。如果标普过去12个月的总回报大于0，则继续持有，否则卖出 (月度计算)
    
    df = self.index_price.copy()
    df.index = pd.to_datetime(df.index)
    df = df[['close']].resample('M').last().copy()
    df.index = pd.Series(df.index).dt.date
    df = df.reset_index().copy()
    index_list = self.index_price.index.values
    real_index = []
    for r in df.itertuples():
        real_index.append(index_list[index_list <= r.index].tolist()[-1])
    df.index = real_index
    df['top_fac'] = df['close'].pct_change(12) > 0
    df['bottom_fac'] = df['close'].pct_change(12) < 0
    start_signal_list, end_signal_list = self.make_trade_signal(df=self.index_price, start_fac='top_fac', end_fac='bottom_fac')
    df = self.plot_signal_point(start_signal_list, end_signal_list, 'ma_1w', 'ma_1y', is_plot_type_1=True)
    result = self.get_backtest_result(df)


    strategy 3 未优化
    标普500过去12个月的总回报。如果标普过去12个月的总回报大于0，则继续持有，否则卖出 (日度计算)|
    self.index_price['top_fac'] = self.index_price['close'].pct_change(self.YEAR) > 0
    self.index_price['bottom_fac'] = self.index_price['close'].pct_change(self.YEAR) < 0
    start_signal_list, end_signal_list = self.make_trade_signal(df=self.index_price, start_fac='top_fac', end_fac='bottom_fac')
    df = self.plot_signal_point(start_signal_list, end_signal_list, 'ma_1w', 'ma_1y',is_plot_type_1=True)
    result = self.get_backtest_result(df)

    strategy 4 增加因子做筛选 微调
    计算其过去12个月的日收益率的 Newey-West t统计量 日收益对时序做回归
    开仓条件:
        t统计量小于-0.8，收盘价 低于一年均线 0.02，6个月rsi 小于 35
    平仓条件
        t统计量大于-0.2

    t_stats = []
    for i in self.index_price.index.tolist():
        _df = self.index_price.loc[:i,'ret'].dropna()
        if _df.shape[0] < 242:
            t_stats.append(0)
        else:
            F_tau = _df.values.tolist()[-self.YEAR:]
            tau = [i + 1 for i in range(self.YEAR)]
            est = sm.OLS(F_tau, sm.add_constant(tau, prepend=False)).fit()
            t_stats.append(est.tvalues[0])

    self.index_price['t_stats'] = t_stats
    t_start  = -0.8
    t_end = -0.25
    m_y1_diff = -0.02
    rsi = 35
    
    self.index_price['top_fac'] = (self.index_price['t_stats'] < t_start) & \
                              (self.index_price['1m_y1_diff'] < m_y1_diff) & \
                              (self.index_price['rsi'] < rsi)
                             
    self.index_price['bottom_fac'] = self.index_price['t_stats'] > t_end
    start_signal_list, end_signal_list = self.make_trade_signal(df=self.index_price, start_fac='top_fac', end_fac='bottom_fac')
    df = self.plot_signal_point(start_signal_list, end_signal_list, 'ma_1w', 'ma_1y', is_plot_type_1=True, is_plot_type_2=False)
    test = self.get_backtest_result(df)
    '''