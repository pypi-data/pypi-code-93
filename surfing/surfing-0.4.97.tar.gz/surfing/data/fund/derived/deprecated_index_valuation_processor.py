import pandas as pd
import numpy as np
from datetime import datetime
from datetime import date
import json
from ...wrapper.mysql import BasicDatabaseConnector, DerivedDatabaseConnector
from ...api.raw import RawDataApi
from ...api.basic import BasicDataApi

class IndexValuationProcessor():
    w1 = 5
    m1 = 20
    m3 = 60
    m6 = 121
    y1 = 242
    y3 = 242*2
    y5 = 242*5
    y10 = 242*10

    def __init__(self):
        self._raw_data_api = RawDataApi()
        self._basic_data_api = BasicDataApi()

    def upload_derived(self, df, table_name):
        df.to_sql(table_name, DerivedDatabaseConnector().get_engine(), index=False, if_exists='append')
    
    def alpha(self, fund_nav,d):
        return fund_nav['adjusted_net_value'] / fund_nav['adjusted_net_value'].shift(d)  - fund_nav['close'] / fund_nav['close'].shift(d)

    def index_return(self):
        #history
        index_df = self._basic_data_api.get_index_info()
        index_list = [i for o,i in zip(index_df['order_book_id'],index_df['index_id']) if '.' in o]
        for i in index_list:
            
            df =  self._basic_data_api.get_index_price([i])
            if df.empty:
                continue
            else:
                df['w1_ret'] = df['close'] / df['close'].shift(self.w1) -1
                df['m1_ret'] = df['close'] / df['close'].shift(self.m1) -1
                df['m3_ret'] = df['close'] / df['close'].shift(self.m3) -1
                df['m6_ret'] = df['close'] / df['close'].shift(self.m6) -1
                df['y1_ret'] = df['close'] / df['close'].shift(self.y1) -1
                df['y3_ret'] = df['close'] / df['close'].shift(self.y3) -1
                df['y5_ret'] = df['close'] / df['close'].shift(self.y5) -1
                df['y10_ret'] = df['close'] / df['close'].shift(self.y10) -1
                df['cumulative_ret'] = df['close'] / df['close'].values[0] -1
                res = []
                df = df.set_index('datetime')
                for i,d in zip(df.close, df.index):
                    begin_of_year = df.index[df.index >= date(d.year, 1, 1)].min()
                    res.append(i/df.loc[begin_of_year,'close'] - 1)
                df['this_y_ret'] = res
                df = df.drop(['id','volume','low','close','high','open','total_turnover','ret'], axis = 1)
                df['datetime'] = df.index
                self.upload_derived(df, 'index_return')
    
    def index_volatility(self):
        #history
        index_df = self._basic_data_api.get_index_info()
        index_list = index_df['index_id'].tolist()
        for i in index_list:
            df =  self._basic_data_api.get_index_price([i])
            if df.empty:
                continue
            else:
                df = df.set_index('datetime')
                df = df[['close']]
                df = pd.DataFrame(df['close'] / df['close'][0])
                df['w1_vol'] = df['close'].rolling(self.w1).std()
                df['m1_vol'] = df['close'].rolling(self.m1).std()
                df['m3_vol'] = df['close'].rolling(self.m3).std()
                df['m6_vol'] = df['close'].rolling(self.m6).std()
                df['y1_vol'] = df['close'].rolling(self.y1).std()
                df['y3_vol'] = df['close'].rolling(self.y3).std()
                df['y5_vol'] = df['close'].rolling(self.y5).std()
                df['y10_vol'] = df['close'].rolling(self.y10).std()

                cumu_vol = []
                this_y_vol = []
                for d in df.index:
                    begin_of_year = df.index[df.index >= date(d.year, 1, 1)].min()
                    this_y_vol.append(df.loc[begin_of_year:d,]['close'].std())
                    cumu_vol.append(df.loc[:d,]['close'].std())
                df['this_y_vol'] = this_y_vol
                df['cumulative_vol'] = cumu_vol
                df = df.drop(['close'], axis = 1)
                df['index_id'] = i
                df['datetime'] = df.index
                self.upload_derived(df, 'index_volatility')
    
    def fund_alpha(self):

        index_df = self._basic_data_api.get_index_info()
        fund_info = self._basic_data_api.get_fund_info()
        fund_dic = {f: i for f,i in zip(fund_info['fund_id'],fund_info['track_index']) if i != 'none'}
        for f,i in fund_dic.items():

            fund_nav = self._basic_data_api.get_fund_nav([f]).drop_duplicates(subset='datetime')
            index = self._basic_data_api.get_index_price([i])

            fund_nav = fund_nav[['adjusted_net_value','datetime']].set_index('datetime')
            index = index[['close','datetime']].set_index('datetime')
            fund_nav = fund_nav.join(index)

            fund_nav['fund_ret'] = fund_nav['adjusted_net_value']/ fund_nav['adjusted_net_value'].shift(1) - 1
            fund_nav['index_ret'] = fund_nav['close'] /  fund_nav['close'].shift(1) - 1 
            track_err = []
            this_y_alpha = []
            cumu_alpha = []
            for d in fund_nav.index:
                f_ret = fund_nav.loc[:d,'fund_ret']
                i_ret = fund_nav.loc[:d,'index_ret']
                t = fund_nav.index.tolist().index(d) +1
                track_err_i = np.sqrt(pow((f_ret - i_ret),2).sum() *self.y1/ t)
                track_err.append(track_err_i)

                begin_of_year = fund_nav.index[fund_nav.index >= date(d.year, 1, 1)].min()
                this_y_alpha_i = fund_nav.loc[d,'adjusted_net_value'] / fund_nav.loc[begin_of_year,'adjusted_net_value'] - fund_nav.loc[d,'close'] / fund_nav.loc[begin_of_year,'close']
                this_y_alpha.append(this_y_alpha_i)

                cumu_alpha_i = fund_nav.loc[d,'adjusted_net_value'] / fund_nav['adjusted_net_value'].values[0] - fund_nav.loc[d,'close'] / fund_nav['close'].values[0]
                cumu_alpha.append(cumu_alpha_i)

            fund_nav['track_err'] = track_err
            fund_nav['this_y_alpha'] = this_y_alpha
            fund_nav['cumulative_alpha'] = cumu_alpha

            fund_nav['w1_alpha'] = self.alpha(fund_nav,self.w1)
            fund_nav['m1_alpha'] = self.alpha(fund_nav,self.m1)
            fund_nav['m3_alpha'] = self.alpha(fund_nav,self.m3)
            fund_nav['m6_alpha'] = self.alpha(fund_nav,self.m6)
            fund_nav['y1_alpha'] = self.alpha(fund_nav,self.y1)
            fund_nav['y3_alpha'] = self.alpha(fund_nav,self.y3)
            fund_nav['y5_alpha'] = self.alpha(fund_nav,self.y5)
            fund_nav['y10_alpha'] = self.alpha(fund_nav,self.y10)
            fund_nav = fund_nav.drop(['adjusted_net_value','close','fund_ret','index_ret'], axis = 1)
            fund_nav['fund_id'] = f
            fund_nav['datetime'] = fund_nav.index
            self.upload_derived(fund_nav, 'fund_alpha')
            

    def index_valuation(self):
        index_df = self._basic_data_api.get_index_info()
        index_df = index_df[index_df['tag_method'] != 'none']
        index_df = index_df[index_df['order_book_id'] != 'not_available']
        index_df = index_df[index_df['order_book_id'].map(lambda x : '.' in x )]
        start_date = date(2010,1,1)
        index_result = []
        for i in index_df.to_dict('records'):
            index_res = {}
            index_id = i['index_id']
            index_weight = self._raw_data_api.get_rq_index_weight([index_id],start_date)
            print(index_id)
            # save index components weight
            res = {}
            stock_list = []
            for s,w,d  in zip(index_weight['stock_list'] , index_weight['weight_list'],index_weight['datetime']):
                s = json.loads(s)
                w = json.loads(w)
                res[d] = [{'stock_id':si , 'weights': wi} for si,wi in zip(s,w)]
                stock_list.extend(s)
            stock_list = list(set(stock_list))
            # if all components are not stock, next one 
            stock_list = [ _ for _ in stock_list if _[0] in ['0','3','6']]
            if len(stock_list) < 1:
                continue
                
            stock_val  = self._raw_data_api.get_rq_stock_valuation(stock_list,start_date)
            stock_val2 = self._raw_data_api.get_stock_fin_fac(stock_list,start_date)
            
            for d, ws in res.items():
                index_res[d] = {}
                stock_val_tmp = stock_val[stock_val['datetime'] == d].copy()
                stock_val_tmp2 = stock_val2[stock_val2['datetime'] == d].copy()
                
                if stock_val_tmp.empty:
                    break
                for index_i in ['pb_ratio_lf','pe_ratio_ttm','peg_ratio_ttm','dividend_yield_ttm']:
                
                    index_d_w = stock_val_tmp[['stock_id',index_i]].set_index('stock_id').join(pd.DataFrame(res[d]).set_index('stock_id'))
                    index_d_w = index_d_w.fillna(0)
                    index_res[d][index_i] =  (index_d_w[index_i] * index_d_w['weights']).sum()
                
                index_d_w = stock_val2[['stock_id','return_on_equity_ttm']].set_index('stock_id').join(pd.DataFrame(res[d]).set_index('stock_id'))
                index_d_w = index_d_w.fillna(0)
                index_res[d]['return_on_equity_ttm'] = (index_d_w['return_on_equity_ttm'] * index_d_w['weights']).sum()
                
                
            index_result_i = pd.DataFrame(index_res).T
            index_result_i['index_id'] = index_id
            index_result_i['pe_pct'] = index_result_i['pe_ratio_ttm'].rank(pct=True)
            index_result_i['pb_pct'] = index_result_i['pb_ratio_lf'].rank(pct=True)
            index_result_i = index_result_i.dropna().copy()
            index_i = index_result_i['index_id'].values[0]
            val_method = index_df[index_df['index_id'] == index_i]['tag_method'].values[0]
            if val_method == 'PE百分位':
                index_result_i['val_score'] = index_result_i['pe_pct'].copy()
            else:
                index_result_i['val_score'] = index_result_i['pb_pct'].copy()
            index_result_i['datetime'] = index_result_i.index
            index_result_i.columns = ['dy_ttm','pb_mrq','pe_ttm','peg_ttm','roe_ttm','index_id','pe_pct','pb_pct','val_score','datetime']
            self.upload_derived(index_result_i, 'index_valuation')
            print(index_id, 'finish')

if __name__ == '__main__':
    ivp = IndexValuationProcessor()
    ivp.index_valuation()