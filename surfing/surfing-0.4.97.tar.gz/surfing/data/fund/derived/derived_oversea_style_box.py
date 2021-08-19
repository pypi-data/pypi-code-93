import datetime
import pandas as pd
import numpy as np
from ...api.raw import RawDataApi
from ..raw.raw_data_helper import RawDataHelper
from ....data.view.raw_models import QSFundStyleBox
from ....util.calculator_item import CalculatorBase

class OverseaFundStyleBox:

    DEFAULT_START_DATE = '2018-01-01'
    HK_CH_EXCHANGE_RATE = 0.8
    US_CH_EXCHANGE_RATE = 6.5

    def __init__(self, data_helper: RawDataHelper):
        self._data_helper = data_helper
        self._raw_api = RawDataApi()

    def init(self):
        self.fund_info = self._raw_api.get_over_sea_fund_info()
        self.fund_pos = self._raw_api.get_fund_hold_top10_pos()
        #ch_equity_list, us_equity_list, hk_equity_list = self.get_stock_list(self.fund_pos)
        self.ch_stock_fin = self._raw_api.get_em_stock_fin_fac()
        hm_stock_fin = self.process_fin_fac(self._raw_api.get_os_stock_fin_fac())
        self.us_stock_fin = hm_stock_fin[~hm_stock_fin.stock_id.str.contains('\.HK')]
        self.hk_stock_fin = hm_stock_fin[hm_stock_fin.stock_id.str.contains('\.HK')]

        # 股价
        self.ch_stock_price = self._raw_api.get_em_stock_price(start_date=self.DEFAULT_START_DATE, columns=['close']).set_index(['stock_id', 'datetime'])
        self.hk_stock_price = self._raw_api.get_em_hk_stock_price(start_date=self.DEFAULT_START_DATE).replace(0,np.nan).ffill()
        self.us_stock_price = self._raw_api.get_em_us_stock_price(start_date=self.DEFAULT_START_DATE).replace(0,np.nan).ffill()
        dic = {'CODES':'stock_id','DATES':'datetime','CLOSE':'close'}
        self.hk_stock_price = self.hk_stock_price.rename(columns=dic).pivot_table(index='datetime',columns='stock_id',values='close')
        self.us_stock_price = self.us_stock_price.rename(columns=dic).pivot_table(index='datetime',columns='stock_id',values='close')
        self.ch_stock_price = self.ch_stock_price.reset_index().pivot_table(index='datetime',columns='stock_id',values='close')

        # 市值
        self.cap = self.process_cap()

    def process_fin_fac(self, df):
        td = pd.to_datetime(df.report_date)
        td = [i.date() for i in td]
        df.report_date = td
        return df.rename(columns={'report_date':'datetime','stock_code':'stock_id'})

    def us_stock_index_map(self, df):
        df.columns = [i.split('.')[0]+' '+'US Equity' for i in df.columns]
        return df

    def hk_stock_index_map(self, df):
        df.columns = [i.split('.')[0].lstrip('0')+' '+'HK Equity' for i in df.columns]
        return df

    def ch_stock_index_map(self, df):
        df.columns = [i.split('.')[0]+' '+'CH Equity' for i in df.columns]
        return df
    
    #  overall value score 
    def process_cap(self):
         # 总股本 部分中概股总市值用abs 计算 abs 和 流通股有的差距100倍 比如PTR，不统一，这里选择直接用市值
        ch_total_share = self._raw_api.get_em_daily_info(start_date=self.DEFAULT_START_DATE, columns=['total_share']).pivot_table(index='datetime', columns='stock_id', values='total_share')
        hk_cap = self.hk_stock_fin.pivot_table(index='datetime', columns='stock_id', values='indicator_18').ffill().iloc[-1]
        us_cap = self.us_stock_fin.pivot_table(index='datetime', columns='stock_id', values='indicator_18').ffill().iloc[-1]

        self.ch_cap = pd.DataFrame(ch_total_share.iloc[-1] * self.ch_stock_price.iloc[-1])
        self.ch_cap.columns = ['cap']
        self.us_cap = pd.DataFrame(us_cap * self.US_CH_EXCHANGE_RATE)
        self.us_cap.columns = ['cap']
        self.hk_cap = pd.DataFrame(hk_cap * self.HK_CH_EXCHANGE_RATE)
        self.hk_cap.columns = ['cap']
        return pd.concat([self.ch_cap, self.us_cap, self.hk_cap])

    def process_ep(self):
        ch_ep = self.ch_stock_fin.pivot(index='datetime', columns='stock_id', values='np_ttmrp').ffill().iloc[-1]
        ch_ep = pd.DataFrame(ch_ep / self.ch_cap.cap)
        ch_ep.columns = ['ep']
        us_ep = self.us_stock_fin.pivot(index='datetime', columns='stock_id', values='indicator_3').ffill().iloc[-1]
        us_ep = pd.DataFrame(us_ep / self.us_cap.cap * self.US_CH_EXCHANGE_RATE)
        us_ep.columns = ['ep']
        hk_ep = self.hk_stock_fin.pivot(index='datetime', columns='stock_id', values='indicator_3').ffill().iloc[-1]
        hk_ep = pd.DataFrame(hk_ep / self.hk_cap.cap * self.HK_CH_EXCHANGE_RATE)
        hk_ep.columns = ['ep']
        return pd.concat([ch_ep,us_ep,hk_ep]).dropna().rank(pct=True) * 100

    def process_bp(self):
        ch_bp = self.ch_stock_fin.pivot(index='datetime', columns='stock_id', values='balance_statement_74').ffill().iloc[-1]
        ch_bp = pd.DataFrame(ch_bp / self.ch_cap.cap)
        ch_bp.columns = ['bp']
        us_bp = self.us_stock_fin.pivot(index='datetime', columns='stock_id', values='indicator_4').ffill().iloc[-1] / self.us_stock_price.iloc[-1]
        us_bp = pd.DataFrame(us_bp)
        us_bp.columns = ['bp']
        hk_bp = self.hk_stock_fin.pivot(index='datetime', columns='stock_id', values='indicator_4').ffill().iloc[-1] / self.hk_stock_price.iloc[-1]
        hk_bp = pd.DataFrame(hk_bp)
        hk_bp.columns = ['bp']
        return pd.concat([ch_bp,us_bp,hk_bp]).dropna().rank(pct=True) * 100

    def process_rp(self):
        ch_rp = self.ch_stock_fin.pivot(index='datetime', columns='stock_id', values='or_ttmr').ffill().iloc[-1]
        ch_rp = pd.DataFrame(ch_rp / self.ch_cap.cap)
        ch_rp.columns = ['rp']
        us_rp = self.us_stock_fin.pivot(index='datetime', columns='stock_id', values='indicator_13').ffill().iloc[-1] / self.us_stock_price.iloc[-1]
        us_rp = pd.DataFrame(us_rp)
        us_rp.columns = ['rp']
        hk_rp = self.hk_stock_fin.pivot(index='datetime', columns='stock_id', values='indicator_13').ffill().iloc[-1] / self.hk_stock_price.iloc[-1]
        hk_rp = pd.DataFrame(hk_rp)
        hk_rp.columns = ['rp']
        return pd.concat([ch_rp,us_rp,hk_rp]).dropna().rank(pct=True) * 100

    def process_cp(self):
        ch_cp = self.ch_stock_fin.pivot(index='datetime', columns='stock_id', values='cfo_ttmr').ffill().iloc[-1]
        ch_cp = pd.DataFrame(ch_cp / self.ch_cap.cap)
        ch_cp.columns = ['cp']
        us_cp = self.us_stock_fin.pivot(index='datetime', columns='stock_id', values='indicator_11').ffill().iloc[-1] / self.us_stock_price.iloc[-1]
        us_cp = pd.DataFrame(us_cp)
        us_cp.columns = ['cp']
        hk_cp = self.hk_stock_fin.pivot(index='datetime', columns='stock_id', values='indicator_11').ffill().iloc[-1] / self.hk_stock_price.iloc[-1]
        hk_cp = pd.DataFrame(hk_cp)
        hk_cp.columns = ['cp']
        return pd.concat([ch_cp,us_cp,hk_cp]).dropna().rank(pct=True) * 100
    
    # overall growth score 近似用每股数据的变化率做
    def process_er(self):
        ch_er = self.ch_stock_fin.pivot(index='datetime', columns='stock_id', values='np_ttmrp').ffill().pct_change(1).mean().dropna()
        ch_er = pd.DataFrame(ch_er)
        ch_er.columns = ['er']
        us_er = self.us_stock_fin.pivot(index='datetime', columns='stock_id', values='indicator_3').ffill().pct_change(1).mean()
        us_er = pd.DataFrame(us_er)
        us_er.columns = ['er']
        hk_er = self.hk_stock_fin.pivot(index='datetime', columns='stock_id', values='indicator_13').ffill().pct_change(1).mean()
        hk_er = pd.DataFrame(hk_er)
        hk_er.columns = ['er']
        return pd.concat([ch_er,us_er,hk_er]).dropna().rank(pct=True) * 100

    def process_br(self):
        ch_br = self.ch_stock_fin.pivot(index='datetime', columns='stock_id', values='balance_statement_74').ffill().pct_change(1).mean().dropna()
        ch_br = pd.DataFrame(ch_br)
        ch_br.columns = ['br']
        us_br = self.us_stock_fin.pivot(index='datetime', columns='stock_id', values='indicator_4').ffill().pct_change(1).mean()
        us_br = pd.DataFrame(us_br)
        us_br.columns = ['br']
        hk_br = self.hk_stock_fin.pivot(index='datetime', columns='stock_id', values='indicator_4').ffill().pct_change(1).mean()
        hk_br = pd.DataFrame(hk_br)
        hk_br.columns = ['br']
        return pd.concat([ch_br,us_br,hk_br]).dropna().rank(pct=True) * 100

    def process_rr(self):
        ch_rr = self.ch_stock_fin.pivot(index='datetime', columns='stock_id', values='or_ttmr').ffill().pct_change(1).mean().dropna()
        ch_rr = pd.DataFrame(ch_rr / self.ch_cap.cap)
        ch_rr.columns = ['rr']
        us_rr = self.us_stock_fin.pivot(index='datetime', columns='stock_id', values='indicator_13').ffill().pct_change(1).mean().dropna()
        us_rr = pd.DataFrame(us_rr)
        us_rr.columns = ['rr']
        hk_rr = self.hk_stock_fin.pivot(index='datetime', columns='stock_id', values='indicator_13').ffill().pct_change(1).mean().dropna()
        hk_rr = pd.DataFrame(hk_rr)
        hk_rr.columns = ['rr']
        return pd.concat([ch_rr,us_rr,hk_rr]).dropna().rank(pct=True) * 100

    def process_cr(self):
        ch_cr = self.ch_stock_fin.pivot(index='datetime', columns='stock_id', values='cfo_ttmr').ffill().pct_change(1).mean().dropna()
        ch_cr = pd.DataFrame(ch_cr / self.ch_cap.cap)
        ch_cr.columns = ['cr']
        us_cr = self.us_stock_fin.pivot(index='datetime', columns='stock_id', values='indicator_11').ffill().pct_change(1).mean().dropna()
        us_cr = pd.DataFrame(us_cr)
        us_cr.columns = ['cr']
        hk_cr = self.hk_stock_fin.pivot(index='datetime', columns='stock_id', values='indicator_11').ffill().pct_change(1).mean().dropna()
        hk_cr = pd.DataFrame(hk_cr)
        hk_cr.columns = ['cr']
        return pd.concat([ch_cr,us_cr,hk_cr]).dropna().rank(pct=True) * 100

    def calculate_stock_score(self):
        # overall value score
        ep = self.process_ep()
        bp = self.process_bp()
        rp = self.process_rp()
        cp = self.process_cp()

        # overall growth score
        er = self.process_er()
        br = self.process_br()
        rr = self.process_rr()
        cr = self.process_cr()

        # value core growth
        score = pd.concat([ep,bp,rp,cp,er,br,rr,cr], axis=1)
        score.loc[:,'ovs'] = score.ep * 0.5 + (score.bp + score.rp + score.cp) / 6
        score.loc[:,'ogs'] = (score.er + score.br + score.rr + score.cr) / 4
        score.loc[:,'vcg'] = score.ogs - score.ovs
        return score

    def process_stock_style(self):
        score = self.calculate_stock_score()
        capsum = self.cap.dropna().sort_values(by='cap',ascending=False).cumsum()
        capt = capsum / capsum.iloc[-1]
        self.big_cap_stock = capt[capt.cap < 0.7].index
        self.mid_cap_stock = capt[np.logical_and(capt.cap  >= 0.7, capt.cap  <= 0.9)].index
        self.small_cap_stock = capt[capt.cap  > 0.9].index
        self.big_vcg = score.loc[score.index.intersection(self.big_cap_stock),'vcg']
        self.mid_vcg = score.loc[score.index.intersection(self.mid_cap_stock),'vcg']
        self.small_vcg = score.loc[score.index.intersection(self.small_cap_stock),'vcg']
        LMT = self.cap.loc[self.mid_cap_stock[0],'cap']
        MST = self.cap.loc[self.mid_cap_stock[-1],'cap']
        res = []
        for stock_id in score.dropna(subset=['vcg']).index:
            y_raw = 100 * (1 + (np.log(self.cap.loc[stock_id,'cap']) - np.log(MST)))/(np.log(LMT) - np.log(MST))
            if y_raw > 200:
                x_raw = 100 * (1 + (score.loc[stock_id,'vcg'] - self.big_vcg.quantile(1 / 3)) / (self.big_vcg.quantile(2 / 3) - self.big_vcg.quantile(1 / 3)))
            elif y_raw < 100:
                x_raw = 100 * (1 + (score.loc[stock_id,'vcg'] - self.small_vcg.quantile(1 / 3)) / (self.small_vcg.quantile(2 / 3) - self.small_vcg.quantile(1 / 3)))
            else:
                x_raw = 100 * (1 + (score.loc[stock_id,'vcg'] - self.mid_vcg.quantile(1 / 3)) / (self.mid_vcg.quantile(2 / 3) - self.mid_vcg.quantile(1 / 3)))
            dic = {
                'stock_id':stock_id,
                'x':x_raw,
                'y':y_raw,
            }
            res.append(dic)
        df = pd.DataFrame(res).set_index('stock_id')
        # 统一股票代码
        res = []
        for i in df.index:
            mkt = i.split('.')[-1]
            if mkt in ['SH','SZ']:
                i = i.split('.')[0] + ' CH Equity'
            elif mkt == 'HK':
                i = i.split('.')[0].lstrip('0')+' HK Equity'
            else:
                i = i.split('.')[0].lstrip('0')+' US Equity'
            res.append(i)
        df.index = res
        return df

    def process_fund_style(self):
        stock_style = self.process_stock_style()
        cols_id = []
        cols_w = []
        for i in range(1,11,1):
            cols_id.append(f'pos_{i}')
            cols_w.append(f'pos_{i}_w')
        res = []
        for fund_id in self.fund_pos.codes:
            _df = self.fund_pos[self.fund_pos.codes == fund_id]
            asset_list = _df[cols_id].values[0].tolist()
            equity_list = [i.split(' ')[-1] for i in asset_list if i is not None]
            if equity_list.count('Equity') < 5:
                continue
            else:
                _df_T = _df.T
                _df_T.columns = [0]
                asset_list = _df_T.loc[cols_id][0].tolist()
                asset_w_list = _df_T.loc[cols_w][0].tolist()
                df_w = pd.DataFrame({'stock_id':asset_list,'stock_w':asset_w_list}).set_index('stock_id')
                df_w = df_w.join(stock_style).dropna()
                x = (df_w.stock_w * df_w.x).sum() / df_w.stock_w.sum()
                y = (df_w.stock_w * df_w.y).sum() / df_w.stock_w.sum()
                dic = {
                    'codes':fund_id,
                    'x':x,
                    'y':y,
                    'datetime':_df.report_date.values[0],
                }
                res.append(dic)
        df_result = pd.DataFrame(res)
        return df_result.dropna()

    def process(self):
        self.result = self.process_fund_style()
        self._data_helper._upload_raw(self.result, QSFundStyleBox.__table__.name)