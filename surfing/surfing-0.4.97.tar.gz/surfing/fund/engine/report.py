import pandas as pd
import numpy as np
import datetime
import copy
from pprint import pprint 
import platform
import matplotlib as mpl
import json
import re
from collections import Counter
from .painter.asset_painter import AssetPainter
from .painter.fund_painter import FundPainter
from .painter.hybrid_painter import HybridPainter
from ...data.struct import AssetWeight, AssetPosition, AssetPrice, AssetValue
from .asset_helper import TAAHelper
from ...data.manager import DataManager
from ...data.manager.manager_fund import FundDataManager
from ...data.struct import FundTrade, TaaTunerParam, FundPosition, TAAParam
from .asset_helper import SAAHelper, TAAHelper, FAHelper, TAAStatusMode
from ...util.calculator import Calculator
from ...constant import IndClassType

CURRENT_PLATFORM = platform.system()
if CURRENT_PLATFORM == 'Darwin':
    mpl.rcParams['font.family'] = ['Heiti TC']
else:
    mpl.rcParams['font.family'] = ['STKaiti']

class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super(DatetimeEncoder, obj).default(obj)
        except TypeError:
            return str(obj)

class ReportHelper:
    
    '''
    save backtest history
    '''

    def __init__(self):
        pass

    def init(self): 
        pass

    def plot_init(self, dm, taa_helper=None, score_select=None):
        self.index_price = dm.get_index_price()
        self.fund_info = dm.get_fund_info()
        self.fund_nav = dm.dts.fund_nav
        self.fund_indicator = dm.dts.fund_indicator
        self.taa_params = taa_helper.params if isinstance(taa_helper, TAAHelper) else None
        self.index_pct = dm.dts.index_pct
        self.dts = dm.dts.trading_days.datetime
        self.fund_manager_info = dm.dts.fund_manager_info
        self.fund_score_dm = dm._score_manager.score_cache
        trade_list = []
        for d, trade_d in self.trade_history.items():
            trade_d = [_.__dict__ for _ in trade_d]
            trade_list.extend(trade_d)
        self.trade_df = pd.DataFrame(trade_list)
        if not self.trade_df.empty:
            self.trade_df['year'] = [_.year for _ in self.trade_df.trade_date]
        self.pct_df = dm.dts._index_pct_df
        self.score_select = score_select
        self.active_fund_info = dm.dts.active_fund_info
        self.fund_info = self.fund_info.set_index('fund_id')
        for r in self.active_fund_info.itertuples():
            self.fund_info.loc[r.fund_id,'index_id'] = r.index_id
        self.fund_info = self.fund_info.reset_index()

    def setup(self, saa:AssetWeight=None):
        self.saa_weight = saa.__dict__ if saa else None
        self.asset_cash_history = {}
        self.asset_position_history = {}
        self.asset_market_price_history = {}
        self.pending_trade_history = {}
        self.asset_weights_history = {}
        self.tactic_history = {}
        self.fund_position_history = {}
        self.trade_history = {}
        self.rebalance_date = []
        self.fund_cash_history = {}
        self.fund_marktet_price_history = {}
        self.fund_weights_history = {}
        self.fund_score = {}
        self.fund_score_raw = {}
        self.target_allocation = {}
        self._rebalance_details = []
        self._rebalance_history = []

    def update(self,dt:datetime, asset_cur_position:AssetPosition, asset_cur_price:AssetPrice, pend_trades:list, fund_cur_position:FundPosition, fund_nav:dict, traded_list:list, fund_score:dict, fund_score_raw:dict, target_allocation):   
        # 检查回测时使用
        self.asset_cash_history[dt] = asset_cur_position.cash##
        self.asset_position_history[dt] = asset_cur_position.__dict__##
        self.pending_trade_history[dt] = pend_trades##
        if fund_cur_position is not None:
            dic = {f : f_info.__dict__  for f, f_info in fund_cur_position.copy().funds.items()}
            for f, f_info in dic.items():
                f_info['price'] =  fund_nav[f]
            self.fund_position_history[dt] = dic     
            self.fund_cash_history[dt] = fund_cur_position.cash
            mv, fund_w = fund_cur_position.calc_mv_n_w(fund_navs=fund_nav)
            self.fund_marktet_price_history[dt] = mv
            self.fund_weights_history[dt] = { fund_id : w_i for fund_id, w_i in fund_w.items() if w_i > 0}
            self.fund_score[dt] = fund_score
            self.fund_score_raw[dt] = fund_score_raw

        self.asset_market_price_history[dt] = AssetValue(prices=asset_cur_price, positions=asset_cur_position).sum() 
        asset_w = AssetValue(prices=asset_cur_price, positions=asset_cur_position).get_weight().__dict__
        self.asset_weights_history[dt] = { index_id : w_i for index_id, w_i in asset_w.items() if w_i > 0}
        if traded_list is not None:
            if len(traded_list) > 0:
                self.rebalance_date.append(dt)
                self.trade_history[dt] = traded_list
        self.target_allocation[dt] = target_allocation
        
    def _calc_stat_yearly(self, mv_df):
        if not self.trade_df.empty:
            trade_df = self.trade_df.set_index(['year','trade_date'])
            trade_df = trade_df[trade_df['is_buy'] == True]
            trade_amount_year = trade_df.groupby('year').sum()
            mv_df = mv_df.reset_index()
            dates = mv_df['date'].values
            mv_df['year'] = [_.year for _ in mv_df.date]
            mv_df = mv_df.set_index(['year','date'])
            res = []
            for year in trade_amount_year.index:
                mv_year = mv_df.loc[year]
                dic = {
                    'year': year,
                    'yearly_amount': trade_amount_year.loc[year, 'amount'],
                    'year_begin_mv': mv_df.loc[year].iloc[0].mv,
                    'year_end_mv':mv_year.iloc[-1].mv,
                    'year_mdd':1 - (mv_year.mv / mv_year.mv.cummax()).min()
                    }
                res.append(dic)
            self.turnover_df = pd.DataFrame(res)
            self.turnover_df['turnover_rate_yearly'] = 100 * self.turnover_df['yearly_amount'] / self.turnover_df['year_begin_mv']
            self.turnover_df['year_ret'] = self.turnover_df.year_end_mv / self.turnover_df.year_begin_mv - 1
            self.turnover_rate_yearly_avg = self.turnover_df['turnover_rate_yearly'].sum() / (mv_df.index[-1][0] - mv_df.index[0][0] + 1)
            total_amount = self.trade_df[self.trade_df['is_buy'] == True].amount.sum()
            self.turnover_rate_amt_mv_gmean = Calculator.get_turnover_rate(dates=dates, values=mv_df.mv.values, total_amount=total_amount)
        else:
            self.turnover_df = pd.DataFrame()
            self.turnover_rate_yearly_avg = 0
            self.turnover_rate_amt_mv_gmean = 0

    def _calc_stat(self, df):
        res = Calculator.get_stat_result_from_df(df=df.reset_index(), date_column='date', value_column='mv')
        w = copy.deepcopy(self.saa_weight) if self.saa_weight else AssetWeight().__dict__ # asset weight float
        self._calc_stat_yearly(df)
        w['mdd'] = res.mdd #float
        w['annual_ret'] = res.annualized_ret #float
        w['ret_over_mdd'] = res.ret_over_mdd #float
        w['sharpe'] = res.sharpe #float 
        w['recent_1m_ret'] = res.recent_1m_ret #float
        w['recent_3m_ret'] = res.recent_3m_ret #float
        w['recent_6m_ret'] = res.recent_6m_ret #float
        w['recent_1y_ret'] = res.recent_y1_ret #float
        w['5_year_ret'] = res.recent_y5_ret #float
        w['3_year_ret'] = res.recent_y3_ret #float
        w['1_year_ret'] = res.recent_y1_ret #float
        w['annual_vol'] = res.annualized_vol #float
        w['mdd_d1'] = res.mdd_date1 #datetime
        w['mdd_d2'] = res.mdd_date2 #datetime
        w['turnover_rate_yearly_avg'] = self.turnover_rate_yearly_avg #float 两种算法的换手率结果很接近
        w['turnover_rate_amt_mv_gmean'] = self.turnover_rate_amt_mv_gmean #float
        w['start_date'] = res.start_date #datetime
        w['end_date'] = res.end_date #datetime
        if not self.trade_df.empty:
            w['total_fee_over_begin_mv'] = self.trade_df.commission.sum() / df.mv[0] #float
            w['total_commission'] = self.trade_df.commission.sum()
        else:
             w['total_fee_over_begin_mv'] = 0
             w['total_commission'] = 0
        w['rebalance_date'] = self.rebalance_date #list
        w['last_unit_nav'] = res.last_unit_nav
        w['last_mv_diff'] = res.last_mv_diff
        w['last_increase_rate'] = res.last_increase_rate
        w['market_value'] = df #dataframe
        w['rebalance_times'] = len(self.rebalance_date)
        w['recent_drawdown'] = res.recent_drawdown
        w['recent_mdd_date1'] = str(res.recent_mdd_date1) # str
        w['worst_3m_ret'] = res.worst_3m_ret
        w['worst_6m_ret'] = res.worst_6m_ret
        hold_days = self.rebalance_date + [df.index.values[-1]]
        index_list = df.index.tolist()
        result = {}
        for d in hold_days[:-1]:
            d1 = hold_days[hold_days.index(d) + 1]
            idx0 = index_list.index(d)
            idx1 = index_list.index(d1)
            result[d.strftime('%Y-%m-%d')] = (idx1 - idx0) / 242
        w['hold_years'] = result # dic
        return w

    def get_asset_stat(self):
        self.asset_mv = pd.DataFrame([ {'date':k, 'mv':v} for k,v in self.asset_market_price_history.items()]).set_index('date')
        w = self._calc_stat(self.asset_mv.copy())
        return w
    
    def save_asset_bk(self, json_name):
        dic = self.get_asset_stat()
        dic['market_value'] =  dic['market_value'].reset_index().to_dict('records')
        with open(f'{json_name}.json','w') as f:
            f.write(json.dumps(dic, cls=DatetimeEncoder))

    def get_fund_stat(self):
        if not self.fund_marktet_price_history:
            return None
            
        self.fund_mv = pd.DataFrame([ {'date':k, 'mv':v} for k,v in self.fund_marktet_price_history.items()]).set_index('date')
        w = self._calc_stat(self.fund_mv.copy())
        return w

    def get_last_position(self,asset_target,result,dm):
        last_date = list(self.fund_position_history.keys())[-1]
        last_rebalance_dt = max(list(result['hold_years'].keys()))
        last_rebalance_dt = pd.to_datetime(last_rebalance_dt).date()
        dic = self.fund_position_history[last_date]
        weight_dict = self.fund_weights_history[last_date]
        name_dict =  self.fund_info[['fund_id','desc_name']].set_index('fund_id').to_dict()['desc_name']
        dic_list = [v for k,v in dic.items() if v['volume'] > 0]
        pos_df = pd.DataFrame(dic_list).sort_values('index_id')[['fund_id','index_id']].set_index('fund_id')
        pos_df['weight'] = pos_df.index.map(lambda x : weight_dict[x])
        pos_df['desc_name'] = pos_df.index.map(lambda x : name_dict[x])
        pos_df.index.name = last_date
        pos_df = pos_df.sort_values('weight', ascending = False)
        recent_index_price = self.index_price.loc[last_rebalance_dt:]
        _index_price_recent_month_1 = recent_index_price / recent_index_price.iloc[0]
        dt = sorted(list(self.fund_score_dm.keys()))[-1]
        last_month_start_day = last_date - datetime.timedelta(days=31)
        last_month_start_day = self.dts[self.dts >= last_month_start_day].values[0]
        _index_price_recent_month = self.index_price.loc[last_month_start_day:]
        _index_ret_recent = _index_price_recent_month.iloc[-1] / _index_price_recent_month.iloc[0]
        fund_rank = []
        fund_rank_pct = []
        fund_vs_index_rate = {}
        _price_rate_list = []
        for i in pos_df.itertuples():
            _score_dict = self.fund_score_dm[dt][i.index_id][self.score_select[i.index_id]]
            _score_list = sorted(_score_dict.items(), key=lambda x:x[1], reverse=True)
            _fund_list = [i[0] for i in _score_list]
            rank_i = _fund_list.index(i.Index) + 1 if i.Index in _fund_list else 10000
            rank_pct = (_fund_list.index(i.Index) + 1) / len(_fund_list) if i.Index in _fund_list else 1
            fund_rank.append(rank_i)
            fund_rank_pct.append(rank_pct)
            _fund_nav_recent_month = self.fund_nav.loc[last_month_start_day:][self.fund_nav.columns.intersection(set(_fund_list))]
            _fund_ret_recent = _fund_nav_recent_month.iloc[-1] / _fund_nav_recent_month.iloc[0]
            r = np.mean([_fund_ret_recent >= _index_ret_recent[i.index_id]])
            fund_vs_index_rate[i.index_id] = r
            
            _fund_nav_recent_month = self.fund_nav.loc[last_rebalance_dt:][[i.Index]]
            _fund_nav_recent_month_1 = _fund_nav_recent_month.reindex(_index_price_recent_month_1.index.intersection(_fund_nav_recent_month.index))
            _fund_nav_recent_month_1 = _fund_nav_recent_month_1 / _fund_nav_recent_month_1.iloc[0]
            _fund_nav_recent_month_1 = _fund_nav_recent_month_1.div(_index_price_recent_month_1[i.index_id].values,axis=0)
            for fund_id in _fund_nav_recent_month_1:
                sr = _fund_nav_recent_month_1[fund_id]
                mdd_part =  sr / sr.rolling(window=sr.shape[0], min_periods=1).max()
                mdd = 1 - mdd_part.min()
                mdd_date2 = mdd_part.idxmin()
                mdd_date1 = sr[:mdd_date2].idxmax()
                mdd_lens = (mdd_date2-mdd_date1).days
                dic = {
                    'fund_id':fund_id,
                    'relative_mdd':mdd,
                    'relative_mdd_day_length':mdd_lens
                }
                _price_rate_list.append(dic)
            
        pos_df = pos_df.join(self.fund_info.set_index('fund_id')[['fund_manager']])
        pos_df.loc[:,'fund_rank'] = fund_rank
        pos_df.loc[:,'fund_rank_pct'] = fund_rank_pct
        #asset_target = self._prep_target_asset_allocation
        asset_target = {k: round(v,2) for k,v in asset_target.__dict__.items()}
        pos_df.index.name = 'fund_id'
        pos_df = pos_df.reset_index()
        cur_index_pos = pos_df[['index_id','weight']].groupby('index_id').sum().rename(columns={'weight':'cur_index_weight'})
        pos_df = pos_df.set_index('index_id').join(cur_index_pos,on='index_id').reset_index()
        pos_df.loc[:,'target_index_weight'] = pos_df.index_id.map(lambda x: asset_target[x])

        index_cur_mdd_dic = 1 - recent_index_price.iloc[0] / recent_index_price.max()
        pos_df.loc[:,'cur_index_mdd'] = pos_df.index_id.map(lambda x:index_cur_mdd_dic[x])
        recent_fund_nav = self.fund_nav[pos_df.fund_id.tolist()].loc[last_rebalance_dt:]
        fund_cur_mdd_dic = 1 - recent_fund_nav.iloc[0] / recent_fund_nav.max()
        pos_df.loc[:,'cur_fund_mdd'] = pos_df.fund_id.map(lambda x:fund_cur_mdd_dic[x])
        pos_df.loc[:,'fund_ex_index_ret_rate_recent_1m'] = pos_df.index_id.map(lambda x: fund_vs_index_rate[x])
        relative_mdd_detail = pd.DataFrame(_price_rate_list).set_index('fund_id')
        pos_df = pos_df.set_index('fund_id').join(relative_mdd_detail).reset_index()
        pos_df['index_weight_diff'] = abs(pos_df['target_index_weight'] - pos_df['cur_index_weight'])
        name_dic = {
            'fund_id':'基金id',
            'index_id':'指数id',
            'weight':'基金权重',
            'desc_name':'基金名称',
            'fund_manager':'基金经理',
            'fund_rank':'基金排名',
            'fund_rank_pct':'基金排名百分比',
            'cur_index_weight':'大类资产权重',
            'target_index_weight':'大类资产目标权重',
            'cur_index_mdd':'大类资产当前回撤',
            'cur_fund_mdd':'基金资产当前回撤',
            'fund_ex_index_ret_rate_recent_1m':'最近一月超越指数涨幅的基金数目比率',
            'relative_mdd':'价格比最大回撤',
            'relative_mdd_day_length':'价格比最大回撤持续自然日',
            'index_weight_diff':'大类资产偏移权重',
        }
        pct_cols = ['weight','fund_rank_pct','cur_index_weight','target_index_weight','cur_index_mdd','cur_fund_mdd','fund_ex_index_ret_rate_recent_1m','relative_mdd','index_weight_diff']
        for pct_col in pct_cols:
            pos_df[pct_col] = pos_df[pct_col].map(lambda x:str(round(x*100,1))+'%')
        fund_id_list = pos_df.fund_id.tolist()
        _df = dm.view_data(func_name='get_daily_fund_daily_result', fund_id_list=fund_id_list).rename(columns={'基金ID':'fund_id'}).set_index('fund_id')
        df_cols_order = ['fund_id','index_id', 'weight', 'desc_name', 'fund_manager',
                 'fund_rank', 'fund_rank_pct','cur_index_weight', 'target_index_weight','index_weight_diff',
                 'cur_index_mdd', 'cur_fund_mdd', 'fund_ex_index_ret_rate_recent_1m','relative_mdd', 'relative_mdd_day_length'
                ]
        pos_df = pos_df[df_cols_order]
        pos_df = pos_df.set_index('fund_id').join(_df).reset_index()
        return pos_df.rename(columns=name_dic)

    def get_last_target_fund_allocation(self, target_fund):
        dt = list(self.fund_position_history.keys())[-1]
        res = []
        fund_info_dic = self.fund_info[['fund_id','desc_name']].set_index('fund_id').to_dict()['desc_name']
        for fund_id, fund_w in target_fund.items():
            _score_dict = self.fund_score_dm[dt][fund_w.index_id][self.score_select[fund_w.index_id]]
            _score_list = sorted(_score_dict.items(), key=lambda x:x[1], reverse=True)
            _fund_list = [i[0] for i in _score_list]
            rank_i = _fund_list.index(fund_w.fund_id) + 1 if fund_w.fund_id in _fund_list else 10000
            dic = {'fund_id':fund_w.fund_id,
                'index_id':fund_w.index_id, 
                'weight':round(fund_w.fund_wgt,3),
                'desc_name':fund_info_dic[fund_w.fund_id],
                'rank':rank_i}
            res.append(dic)
        target_fund = pd.DataFrame(res).set_index('fund_id')
        target_fund = target_fund.join(self.fund_info.set_index('fund_id')[['fund_manager']])
        target_fund.index.name = list(self.fund_position_history.keys())[-1]
        return target_fund.sort_values('weight', ascending = False)[['index_id','weight','rank','desc_name','fund_manager']]

    def get_fund_trade(self):
        fsdf = self.fund_score.copy()
        fund_info_df = self.fund_info.copy().set_index('fund_id')
        fund_trade = []
        for d in self.trade_history:
            f_t = [ i.__dict__  for i in self.trade_history[d] if isinstance(i, FundTrade)]
            fund_trade.extend(f_t)
        if len(fund_trade) < 1:
            return pd.DataFrame()
        ft_res = []
        for ft in fund_trade:
            ft['desc_name'] = fund_info_df.loc[ft['fund_id'], 'desc_name']
            index_id = fund_info_df.loc[ft['fund_id'], 'index_id']
            try:
                score_dic = fsdf[ft['submit_date']][index_id][self.score_select[index_id]] 
                rank_list = sorted(score_dic.items(), key=lambda x:x[1], reverse=True)
                rank_list = [i[0] for i in rank_list]
                s = rank_list.index(ft['fund_id']) + 1
            except:
                s = np.nan
            ft['submit_d_score'] = s
            fund_id = ft['fund_id']
            submit_d = ft['submit_date']
            traded_d = ft['trade_date']
            ft['before_w']  = self.fund_weights_history[submit_d].get(fund_id,0)
            ft['after_w'] = self.fund_weights_history[traded_d].get(fund_id,0)
            ft_res.append(ft)
        df = pd.DataFrame(ft_res)
        df['before_w'] = df['before_w'].round(4)
        df['after_w'] = df['after_w'].round(4)
        # dts = df.submit_date.unique().tolist()
        # for dt in dts:
        #     _df = df[df['submit_date'] == dt]
        #     fund_id = _df.iloc[-1].fund_id
        #     df.loc[(df['submit_date'] == dt) & (df['fund_id'] == fund_id),'after_w'] = 1 - _df.iloc[:-1].after_w.sum()
        #     df.loc[(df['submit_date'] == dt) & (df['fund_id'] == fund_id),'before_w'] = 1 - _df.iloc[:-1].before_w.sum()
        return df

    @staticmethod
    def fund_rank_recent_analysis(dm, fund_id, score_select):
        score_dict = dm._score_manager.score_cache
        fund_info = dm.dts.fund_info
        fund_indicator = dm.dts.fund_indicator
        fund_nav = dm.dts.fund_nav
        index_price = dm.dts.index_price
        index_id = fund_info[fund_info['fund_id'] == fund_id].index_id.values[0]
        score_func = dm._score_manager.funcs[index_id][score_select[index_id]]
        return HybridPainter.fund_rank_recent_analysis(fund_id,index_id,score_dict,fund_info,fund_indicator,fund_nav,index_price,score_func,score_select)

    def get_asset_trade(self):
        asset_trade = []
        for d in self.trade_history:
            a_t = [ i.__dict__  for i in self.trade_history[d] if not isinstance(i, FundTrade)]
            asset_trade.extend(a_t) 
        res = []
        for dic in asset_trade: 
            index_id = dic['index_id']
            submit_d = dic['submit_date']
            traded_d = dic['trade_date']
            dic['before_w'] = self.asset_weights_history[submit_d].get(index_id, 0)
            dic['after_w'] = self.asset_weights_history[traded_d].get(index_id, 0)
            res.append(dic)
        df = pd.DataFrame(res)
        df['before_w'] = df['before_w'].round(4)
        df['after_w'] = df['after_w'].round(4)
        dts = df.submit_date.unique().tolist()
        for dt in dts:
            _df = df[df['submit_date'] == dt]
            index_id = _df.iloc[-1].index_id
            df.loc[(df['submit_date'] == dt) & (df['index_id'] == index_id),'after_w'] = 1 - _df.iloc[:-1].after_w.sum()
            df.loc[(df['submit_date'] == dt) & (df['index_id'] == index_id),'before_w'] = 1 - _df.iloc[:-1].before_w.sum()
        return df

    def get_fund_position(self):
        fund_pos = []
        for d in self.fund_position_history:
            for i in self.fund_position_history[d].values():
                if i['volume'] > 0:
                    i['datetime'] = d
                    fund_pos.append(i)
        return pd.DataFrame(fund_pos).sort_values('datetime')

    def get_index_fee_avg(self):
        self.index_fee = self.trade_df.copy()
        if self.index_fee.empty:
            self.index_fee_buy = pd.DataFrame()
            self.index_fee_sel = pd.DataFrame()
            self.index_fee_buy['fee_ratio_avg'] = 0
            self.index_fee_sel['fee_ratio_avg'] = 0
            self.index_fee['fee_ratio_avg'] = 0
        else:
            self.index_fee_buy = self.index_fee[self.index_fee.is_buy].groupby('index_id').sum()
            self.index_fee_sel = self.index_fee[np.logical_not(self.index_fee.is_buy)].groupby('index_id').sum()
            self.index_fee_buy['fee_ratio_avg'] = self.index_fee_buy.commission / self.index_fee_buy.amount
            self.index_fee_sel['fee_ratio_avg'] = self.index_fee_sel.commission / self.index_fee_sel.amount
            self.index_fee = self.index_fee.groupby('index_id').sum()
            self.index_fee['fee_ratio_avg'] = self.index_fee.commission / self.index_fee.amount

    def get_rebalance_detail(self):
        #rebalance_details = [i['rebalance_reason'][0]['rebalanace_reason'] for i in self._rebalance_details]
        #rebalance_details = dict(Counter(rebalance_details))
        trade_df = self.trade_df.copy()
        fund_mv = self.fund_mv.copy()
        result = self._calc_stat(fund_mv).copy()
        _rb_df = pd.DataFrame(self._rebalance_details)
        submit_date_to_trade_day = trade_df[['submit_date','trade_date']].set_index('submit_date').to_dict()['trade_date']
        turnover_df = trade_df[trade_df['is_buy'] == True].groupby('submit_date').sum()[['amount']].join(fund_mv).copy().reset_index()
        turnover_df['trade_date'] = turnover_df['submit_date'].map(lambda x : submit_date_to_trade_day[x])
        turnover_df = turnover_df[['amount','mv','trade_date']].set_index('trade_date')
        _rb_df['trade_date'] = _rb_df['datetime'].map(lambda x : submit_date_to_trade_day[x])
        _rb_df['rebalance reason'] = _rb_df['rebalance_reason'].map(lambda x : x[0]['rebalanace_reason'])
        _res = []
        for dic in _rb_df['rebalance_reason']:
            dic = dic[0]
            strs = [ f'{v} ' for k , v in dic.items() if k is not 'rebalanace_reason']
            strs = ''.join(strs)
            _res.append(strs)
        _rb_df['rebalance_detail'] = _res
        _rb_df = _rb_df[['trade_date','rebalance reason','rebalance_detail']].set_index('trade_date').copy()
        turnover_df['turnover'] = turnover_df['amount'] / turnover_df['mv']
        _df = pd.DataFrame([{'trade_date':d,'hold_year':l} for d,l in result['hold_years'].items()]).set_index('trade_date')
        _df.index = pd.to_datetime(_df.index)
        turnover_df = turnover_df.join(_df).join(_rb_df).copy()
        return turnover_df[['turnover','hold_year','rebalance reason','rebalance_detail']]

    def backtest_asset_plot(self):
        bt_type = 'asset'
        print(f'{bt_type} report')
        w = self.get_asset_stat()
        del w['market_value']
        pprint(w)
        AssetPainter.plot_asset_weights(self.asset_weights_history, self.saa_weight)
        HybridPainter.plot_market_value(self.asset_mv, bt_type, self.index_price, self.saa_weight, w)
        AssetPainter.plot_asset_mdd_period(self.asset_mv, self.saa_weight, self.index_price, self.asset_weights_history)
        AssetPainter.plot_asset_mdd_amount(self.asset_mv, self.index_price, self.asset_position_history)

    def backtest_fund_plot(self):
        bt_type = 'fund'
        print(f'{bt_type} report')
        w = self.get_fund_stat()
        mv = w['market_value'].copy()
        del w['market_value']
        pprint(w)
        w['market_value'] = mv
        self.get_index_fee_avg()
        #FundPainter.plot_fund_weights(self.fund_weights_history, self.fund_cash_history, self.fund_marktet_price_history, self.saa_weight)
        HybridPainter.plot_market_value_with_mdd_analysis(self.fund_mv, bt_type, self.index_price, self.saa_weight, w)
        FundPainter.plot_fund_mdd_periods(self.fund_mv, self.fund_weights_history, self.fund_nav, self.fund_info)
        FundPainter.plot_fund_mdd_amounts(self.fund_mv, self.fund_nav, self.fund_info, self.fund_position_history.copy())
        FundPainter.plot_fund_alpha(self.fund_nav, self.fund_info, self.index_price, self.fund_position_history.copy(), w)
        #FundPainter.plot_mv_on_each_asset(self.fund_nav, self.fund_info, self.index_price, self.fund_position_history.copy(), w)
        #HybridPainter.plot_asset_fund_mv_diff(self.asset_mv, self.fund_mv)
        # if not self.index_fee.empty:
        #     FundPainter.plot_index_fund_fee(self.index_fee)
        # if not self.turnover_df.empty:
        #     FundPainter.plot_fund_ret_each_year(self.turnover_df, w['mdd'], w['annual_ret'] )
        #     FundPainter.plot_turnover_rate_each_year(self.turnover_df, self.turnover_rate_yearly_avg)

    def singel_index_plot(self):
        w = self.get_fund_stat()
        HybridPainter.plot_market_value_with_mdd_analysis(self.fund_mv, 'fund', self.index_price, self.saa_weight, w)
        FundPainter.plot_fund_mdd_periods(self.fund_mv, self.fund_weights_history, self.fund_nav, self.fund_info)
        FundPainter.plot_fund_alpha(self.fund_nav, self.fund_info, self.index_price, self.fund_position_history.copy(), w)

    def asset_price_ratio(self):    
        fund_trade = self.get_fund_trade()
        return HybridPainter.plot_asset_price_ratio(self.fund_nav, self.fund_info, self.index_price, self.fund_score_dm, self.get_fund_stat(), self.dts, self.saa_weight, fund_trade, self.score_select)
        
    def plot_whole(self):
        self.backtest_fund_plot()
        self.backtest_asset_plot()
        
    def _plot_fund_score(self, asset, is_tuning):
        FundPainter.plot_fund_score(self.fund_mv, 
                                    self.fund_weights_history, 
                                    self.trade_history,
                                    self.index_price, 
                                    self.asset_weights_history,
                                    self.fund_info,
                                    self.fund_nav,
                                    self.fund_score,
                                    self.fund_score_raw,
                                    self.fund_indicator,
                                    asset,
                                    is_tuning,
                                    self.score_select,
                                    )
   
    def _index_pct_plot(self, index_id:str, saa_mv:pd.DataFrame, taa_mv:pd.DataFrame):
        pct = TaaTunerParam.POOL[index_id]
        index_pct = self.index_pct.xs(index_id, level=1, drop_level=True)[[pct]].rename(columns={pct:index_id})
        AssetPainter.plot_taa_analysis(saa_mv, taa_mv, index_id, index_pct, self.taa_params, self.index_price)
        
    def _plot_taa_saa(self, saa_mv, taa_mv, index_id):
        pct = TaaTunerParam.POOL[index_id]
        index_pct = self.index_pct.xs(index_id, level=1, drop_level=True)[[pct]].rename(columns={pct:index_id})
        AssetPainter.plot_asset_taa_saa(saa_mv, taa_mv, index_id, index_pct)
       
    def save_fund_bk_data(self, csv_title:str='check'):
        self.fund_mv.to_csv(csv_title + '_fund_mv.csv')
        self.get_fund_trade().to_csv(csv_title + '_fund_trade.csv')
        self.get_fund_position().to_csv(csv_title + '_fund_pos.csv')
        pd.DataFrame(self.asset_position_history).T.to_csv(csv_title + '_asset_pos.csv')
        if hasattr(self, 'asset_mv'):
            self.asset_mv.to_csv(csv_title + '_asset_mv.csv')
        self.get_asset_trade().to_csv(csv_title + '_asset_trade.csv')
    
    def update_rebalance_detail(self, dt, rebalance_reason, trigger_detail):
        if bool(rebalance_reason):
            self._rebalance_details.append({'datetime':dt,'rebalance_reason':rebalance_reason})
        self._rebalance_history.append({'datetime':dt,'rebalance_reason':trigger_detail})

    def plot_taa_pct_df(self, dt):
        res = []
        _res = []
        index_val_selected = list(TaaTunerParam.INDEX_PCT_SELECTED.keys())
        for index_id, pct_data in TaaTunerParam.POOL.items():
            _df = self.pct_df.loc[index_id][['datetime'] + index_val_selected].rename(columns=TaaTunerParam.INDEX_PCT_SELECTED)
            _df = _df[['datetime',pct_data]].reset_index().pivot_table(index='datetime', columns='index_id',values=pct_data)
            res.append(_df)
            index_val_name = TaaTunerParam.PCT_PAIR[index_id]
            _df = self.pct_df.loc[index_id][['datetime',index_val_name]].reset_index()
            _df = _df.pivot_table(index='datetime',columns='index_id')[index_val_name]
            _res.append(_df)
        pct_df = pd.concat(res, axis=1, sort=True)

        index_val_df = pd.concat(_res, axis=1, sort=True)
        index_val_dic = {k : f'{k}_{v}' for k,v in TaaTunerParam.PCT_PAIR.items()}
        index_val_df = index_val_df.loc[dt:].rename(columns=index_val_dic)
        df = pct_df.loc[dt:].ffill()
        HybridPainter.plot_taa_detail(df, '指数估值分位数')
        HybridPainter.plot_taa_detail(index_val_df, '指数估值')
        
    @staticmethod
    def get_taa_result(index_id:str, start_date:datetime.date, end_date:datetime.date, taaParam:TAAParam, dm:FundDataManager):
        taa_helper = TAAHelper(taa_params=taaParam)
        _dts = dm.get_trading_days()
        dts = _dts[(_dts.datetime >= start_date) & (_dts.datetime <= end_date)].datetime 
        fake_weight = AssetWeight(**{index_id:1})
        for dt in dts:
            asset_pct = dm.get_index_pcts_df(dt)
            taa_helper.on_price(dt=dt, asset_price=None, cur_saa=fake_weight, asset_pct=asset_pct, select_val={},score_dict={})
        df = pd.DataFrame(taa_helper.tactic_history).T.dropna()
        df['last_date'] = df.index.to_series().shift(1)
        con = df[index_id] != df[index_id].shift(1)
        df_diff_part = df[con].copy()
        df_diff_part = df_diff_part.reset_index().rename(columns={'index':'begin_date'})
        next_date = df_diff_part['last_date'].shift(-1).tolist()
        next_date[-1] = df.index.values[-1]
        df_diff_part['end_date'] = next_date
        df_result = df_diff_part[df_diff_part[index_id] != TAAStatusMode.NORMAL][['begin_date','end_date',index_id]]
        df_result = df_result.rename(columns = {index_id:'status'})
        return df_result.to_dict('records') 

    def get_date_score(self, datetime:datetime.date):
        fund_score = self.fund_score[datetime]
        fund_score_raw = self.fund_score_raw[datetime]
        desc_name_dic = self.fund_info[['fund_id','desc_name']].set_index('fund_id').to_dict()['desc_name']
        res = []
        for index_id, score_dic in fund_score.items():
            for fund_id, fund_s in score_dic.items():
                dic = {
                    'index_id' : index_id,
                    'fund_id': fund_id,
                    'desc_name':desc_name_dic[fund_id],
                    'score':fund_s,
                    'raw_score':fund_score_raw[index_id][fund_id],
                }
                res.append(dic)
        return pd.DataFrame(res).sort_values(['index_id','score'],ascending=[True,False]).set_index('index_id')

    def get_mdd_recover_stats(self):
        fund_mv = pd.DataFrame([ {'date':k, 'mv':v} for k,v in self.fund_marktet_price_history.items()]).set_index('date')
        res = Calculator.get_mdd_recover_result(fund_mv)
        return res

    def get_mdd_stats(self):
        fund_mv = pd.DataFrame([ {'date':k, 'mv':v} for k,v in self.fund_marktet_price_history.items()]).set_index('date')
        res = Calculator.get_mdd_result(fund_mv)
        return res

    @staticmethod
    def plot_fund_score(fund_id:str='200002!0',begin_date:datetime.date=datetime.date(2015,1,1),dm:FundDataManager=None):
        FundPainter.plot_fund_rank(score_dic=dm._score_manager.score_cache,
                                   fund_info=dm.dts.fund_info,
                                   fund_id=fund_id,
                                   begin_date=begin_date,
                                   fund_index_map=dm.dts.fund_index_map)

    @staticmethod
    def indicator_score_d(begin_d:datetime.date, fund_list:list, direction:str, m:FundDataManager):
        indicator_1 = m.dts.fund_indicator[(m.dts.fund_indicator.fund_id.isin(fund_list)) &
                            (m.dts.fund_indicator.datetime == begin_d)]
        indicator_1 = indicator_1[['fund_id','alpha','beta','track_err','fee_rate','index_id']].rename(columns={'alpha':f'{direction}_alpha',
                                                                                                            'beta':f'{direction}_beta',
                                                                                                            'track_err':f'{direction}_track_err'})
        indicator_1 = indicator_1.set_index('fund_id')
        score_day_dic = m._score_manager.score_cache[begin_d]
        fund_ranks = {}
        for index_id, score_dic in score_day_dic.items():
            _rank = sorted(score_dic.items(), key=lambda x:x[1], reverse=True)
            fund_rank = [i[0] for i in _rank]
            fund_ranks[index_id] = fund_rank
        rank_result = []
        for r in indicator_1.itertuples():
            try:
                rank_result.append(fund_ranks[r.index_id].index(r.Index) + 1)   
            except:
                rank_result.append(10000)
        indicator_1.loc[:,f'{direction}_rank'] = rank_result
        return indicator_1
     
    @staticmethod
    def fund_trade_result(_bk_class,_bk_result,m):
        _dts = m.dts.trading_days.datetime.tolist()
        rebalance_date = _bk_result['rebalance_date']
        begin_date = rebalance_date[0]
        mv_df = _bk_result['market_value']
        rebalance_list = [begin_date] + [i for i in rebalance_date if i > begin_date] + [mv_df.index[-1]]
        fund_info_dic = m.dts.fund_info[['fund_id','desc_name']].set_index('fund_id').to_dict()['desc_name']
        df_list = []
        for i in range(len(rebalance_list)-1):
            begin_d = rebalance_list[i]
            end_d = rebalance_list[i+1]
            score_day_1 = _dts[_dts.index(begin_d) -1]
            score_day_2 = _dts[_dts.index(end_d) -1]
            pos_dic = _bk_class._report_helper.fund_position_history[begin_d]
            res = []
            for fund_id, fund_pos_i in pos_dic.items():
                if fund_pos_i['volume'] > 1:
                    res.append({
                        'fund_id':fund_pos_i['fund_id'],
                        'volume':fund_pos_i['volume'],
                        'price1':fund_pos_i['price'],
                        'index_id':fund_pos_i['index_id'],
                    })
            pos_i_df = pd.DataFrame(res)
            pos_i_df.loc[:,'price2'] = pos_i_df['fund_id'].map(lambda x : m.dts.fund_nav.loc[end_d,x])
            pos_i_df['amount'] = pos_i_df['volume'] * pos_i_df['price1']
            pos_i_df['weight'] = pos_i_df['amount'] / pos_i_df['amount'].sum()
            pos_i_df.loc[:,'desc_name'] = pos_i_df['fund_id'].map(lambda x: fund_info_dic[x])
            pos_i_df['fund_ret_rate'] = (pos_i_df['price2'] / pos_i_df['price1']) - 1
            pos_i_df['fund_return'] = pos_i_df['fund_ret_rate'] * pos_i_df['weight'] 
            pos_i_df_show = pos_i_df[['fund_id','desc_name','index_id','weight','fund_ret_rate','fund_return']]
            pos_i_df_show = pos_i_df_show.sort_values('fund_return', ascending=False)
            fund_list = pos_i_df_show.fund_id.tolist()
            pos_i_df_show = pos_i_df_show.set_index('fund_id')
            indicator_1 = ReportHelper.indicator_score_d(score_day_1, fund_list, 'buy', m)
            indicator_2 = ReportHelper.indicator_score_d(score_day_2, fund_list, 'sell', m)
            pos_i_df_show = pos_i_df_show.join(indicator_1[['buy_alpha','buy_beta','buy_track_err','fee_rate','buy_rank']]).join(indicator_2[['sell_alpha','sell_beta','sell_track_err','sell_rank']])
            pos_i_df_show = pos_i_df_show.reset_index()
            pos_i_df_show.index.name = f'{begin_d}~{end_d}'
            pos_i_df_show.loc[:,'buy_signal_date'] = begin_d
            pos_i_df_show.loc[:,'sell_signal_date'] = end_d
            df_list.append(pos_i_df_show)
        return pd.concat(df_list)

    @staticmethod
    def recent_week_return(pos_df,fund_result,weight_df,saa,mv_df,m,benchmark,end_date=None,begin_date=None,port_id='',fund_info=None):
        # 把买卖交易费平滑打入净值中
        def _index_price_ratio_item(index_ratio_res, d1, d2, is_buy_fee, is_sell_fee):
            _index_ratio_res = []
            for index_id, fund_list in index_ratio_res.items():
                _nav = m.dts.fund_nav[fund_list].loc[d1:d2]
                if is_buy_fee:
                    for fund_id in _nav:
                        fund_i_fee = buy_dic.get(fund_id,0)
                        fee_discount_l = np.linspace(1,1-fund_i_fee,_nav.shape[0])
                        _nav[fund_id] = _nav[fund_id] * fee_discount_l
                if is_sell_fee:
                    for fund_id in _nav:
                        fund_i_fee = sell_dic.get(fund_id,0)
                        fee_discount_l = np.linspace(1,1-fund_i_fee,_nav.shape[0])
                        _nav[fund_id] = _nav[fund_id] * fee_discount_l
                _nav['index_price'] = m.dts.index_price.loc[d1:d2,index_id]
                _nav = _nav/_nav.iloc[0]
                _nav['mean'] = _nav.mean(axis=1)
                _nav.loc[:,index_id] = _nav['mean'] / _nav['index_price']
                _index_ratio_res.append(_nav[[index_id]].copy())   
            res_df = pd.concat(_index_ratio_res, sort=True, axis=1)
            return res_df

        def _ret_item(begin_date, today, is_buy_fee, is_sell_fee):
            _fund_list = list(weight_df[begin_date].keys())
            _nav = m.dts.fund_nav[_fund_list].loc[begin_date:today]
            fund_ret = _nav.iloc[-1] / _nav.iloc[0] - 1
            ret_df = pd.DataFrame(fund_ret)
            if 0 not in ret_df.columns:
                return None
            ret_df = ret_df.rename(columns={0:'ret'})
            res = []
            for k,w in weight_df[begin_date].items():
                res.append({'fund_id':k,'weight':w})
            _weight_df = pd.DataFrame(res).set_index('fund_id')
            res_df = ret_df.join(_weight_df)
            res_df.loc[:,'rets'] = res_df['ret'] * res_df['weight']
            res_df.loc[:,'begin_date'] = begin_date
            res_df.loc[:,'end_date'] = today
            return res_df

        buy_dic = (fund_info[['fund_id','purchase_fee']].set_index('fund_id') * 0.15).to_dict()['purchase_fee']
        sell_dic = fund_info[['fund_id','redeem_fee']].set_index('fund_id').to_dict()['redeem_fee']
        index_price = m.dts.index_price
        if end_date is None:
            today = datetime.date.today()
        else:
            today = end_date
        if begin_date is None:
            begin_date =  today - datetime.timedelta(days=today.weekday())
        dt_df = m.dts.trading_days.copy().set_index('datetime')
        begin_date = dt_df.loc[:begin_date].index[-1]
        trading_days = sorted(list(set(m.dts.trading_days.datetime) & set(mv_df.index)))
        mv_df = mv_df.loc[begin_date:].reindex(trading_days)
        stats = Calculator.get_stat_result_from_df(df=mv_df.dropna().reset_index(), date_column='date', value_column='mv')
        annual_ret= round(stats.annualized_ret,3)
        mdd = round(stats.mdd,4)
        df_plot_i = mv_df.join(m.dts.index_price[[benchmark]]).loc[begin_date:today]
        df_plot_i = df_plot_i / df_plot_i.iloc[0]
        total_ret = int((stats.last_unit_nav - 1) * 10000)
        st = f'check period annual ret : {annual_ret} mdd : {mdd} total_ret {total_ret} bp'
        FundPainter.plot_recent_ret(df_plot_i,begin_date,today,st,port_id)
        _index_list = []
        for asset, w in saa.__dict__.items():
            if w > 0 and asset != 'cash':
                _index_list.append(asset)
        _index_price = index_price.loc[begin_date:today]
        _index_price = _index_price / _index_price.iloc[0]
        AssetPainter.plot_index_price_ratio(_index_price,'index_price')
        
        if begin_date >= fund_result['rebalance_date'][-1]:
            res_df = _ret_item(begin_date,today, False, False)
        else:
            date_list = [[begin_date,fund_result['rebalance_date'][-1]],[fund_result['rebalance_date'][-1],today]]
            _res_dt_df = []
            for idx,dl in enumerate(date_list):
                b1 = dl[0]
                b2 = dl[1]
                fund_res = _ret_item(b1, b2, False, False)
                if fund_res is not None:
                    _res_dt_df.append(fund_res)
            res_df = pd.concat(_res_dt_df, axis=0, sort=True)
        #res_df.loc[:,'rets'] = res_df['ret'] * res_df['weight']
        res_df = res_df.sort_values('rets',ascending=False)
        res_df['_rets'] = res_df['rets']
        res_df.loc[:,'rets'] = [str(int(i*10000))+'BP' for i in res_df.loc[:,'rets']]
        desc_dic = fund_info[['fund_id','desc_name']].set_index('fund_id').to_dict()['desc_name']
        index_dic = fund_info[['fund_id','index_id']].set_index('fund_id').to_dict()['index_id']
        res_df['desc_name'] = res_df.index.map(lambda x : desc_dic[x])
        res_df['index_id'] = res_df.index.map(lambda x : index_dic[x])        
        if begin_date > fund_result['rebalance_date'][-1]:
            d1 = begin_date
            d2 = today
            index_ratio_res = {}
            _fund_list = list(weight_df[begin_date].keys())
            for fund_id in _fund_list:
                _index_id = index_dic[fund_id]
                if _index_id not in index_ratio_res:
                    index_ratio_res[_index_id] = [fund_id]
                else:
                    index_ratio_res[_index_id].append(fund_id)
            res_index_df = _index_price_ratio_item(index_ratio_res, d1, d2, False, False)
        else:
            date_list = [[begin_date,fund_result['rebalance_date'][-1]],[fund_result['rebalance_date'][-1],today]]
            _res_df = []
            for idx,dl in enumerate(date_list):
                b1 = dl[0]
                b2 = dl[1]
                _res = {}
                for fund_id, fund_pos_i in pos_df[b1].items():
                    if fund_pos_i['volume'] > 1:
                        if fund_pos_i['index_id'] not in _res:
                            _res[fund_pos_i['index_id']] = [fund_pos_i['fund_id']]
                        else:
                            _res[fund_pos_i['index_id']].append(fund_pos_i['fund_id'])
                if idx == 0:
                    _df = _index_price_ratio_item(_res, b1, b2, False, True)
                elif idx == 1:
                    _df = _index_price_ratio_item(_res, b1, b2, True, False)
                _res_df.append(_df)
            df_1 = _res_df[0]
            df_2 = _res_df[1]
            df_2 = df_1.iloc[-1] * df_2
            res_index_df = df_1.iloc[:-1].append(df_2, sort=True)
       
        res_df = res_df.rename(columns={'ret':'fund_ret'})
        res_tmp = res_df[['_rets','index_id']].groupby('index_id').sum()[['_rets']]
        w = (res_tmp*10000).round(1).to_dict()['_rets']
        st = [ f'{k} :{v}BP ' for k, v in w.items()]
        st = ''.join(st)
        AssetPainter.plot_index_price_ratio(res_index_df.dropna(),'price_ratio',st)
        res_df['fund_ret'] = res_df.fund_ret.map(lambda x: str(round(x*100,2)) +'%')
        res_df['weight'] = res_df.weight.map(lambda x: str(round(x*100,2)) +'%')
        res_df = res_df[['begin_date','end_date','desc_name','index_id','fund_ret','weight','rets']]
        fund_id_list = res_df.index.tolist()
        _df = m.view_data(func_name='get_daily_fund_daily_result', fund_id_list=fund_id_list).rename(columns={'基金ID':'fund_id'}).set_index('fund_id')
        res_df = res_df.join(_df)
        return res_df

    @staticmethod
    def rolling_analysis(rolling_year, index_id, m, mv_df, fund_annual_ret, ret_list=[]):
        if '沪深300' in mv_df:
            mv_df = mv_df.drop('沪深300', axis=1)
        mv_df = mv_df.join(m.dts.index_price[[index_id]])
        mv_df = mv_df / mv_df.shift(1)
        annual_ret = (mv_df.rolling(window=242*rolling_year).agg(lambda x : x.prod() - 1))/rolling_year
        FundPainter.plot_rolling_analysis(annual_ret,fund_annual_ret,rolling_year,index_id,ret_list)
     
    @staticmethod
    def regular_rebalance_in_index_strategy(m, begin_date,end_date,index_id,rebalance_year,top_funds):
        dts = m.dts.trading_days.datetime
        fund_score_dic = m._score_manager.score_cache
        fund_info = m.dts.fund_info
        index_price = m.dts.index_price
        fund_nav = m.dts.fund_nav
        result_df, pos_df = HybridPainter.regular_rebalance_in_index_strategy(begin_date,end_date,index_id,rebalance_year,top_funds,dts,fund_score_dic,fund_info,index_price,fund_nav)
        return result_df, pos_df

    @staticmethod
    def mining_fac_importances(m,start_date,end_date,index_id,top_num,wind_class_2):
        '''
        index_id = 'csi500'
        start_date = datetime.date(2020,1,1)
        end_date = datetime.date(2020,8,10)
        top_num = 5
        wind_class_2 = ['被动指数型基金']
        ReportHelper.mining_fac_importances(m,start_date,end_date,index_id,top_num,wind_class_2)
        '''
        _dts = m.dts.trading_days.datetime
        _dts = _dts[(_dts >= start_date) & (_dts <= end_date)]
        _start_date = _dts.iloc[0]
        _end_date = _dts.iloc[-1]
        fund_info = m.dts.fund_info
        _fund_list = fund_info[(fund_info['index_id'] == index_id) & fund_info['wind_class_2'].isin(wind_class_2)].fund_id.tolist()
        _index_fund_pack = m.dts.index_fund_indicator_pack.loc[index_id].loc[_start_date:_end_date]
        _dts = _index_fund_pack.index.get_level_values(0).tolist()
        _col1 = m.dts.fund_nav.columns.tolist()
        fl = [i for i in _fund_list if i in _col1]
        _fund_nav = m.dts.fund_nav[fl].loc[_start_date:_end_date].dropna(axis=1)
        top_funds = (_fund_nav.iloc[-1] / _fund_nav.iloc[0]).sort_values(ascending=False).index.tolist()
        indicator_existed_fund = _index_fund_pack.loc[_start_date].index.tolist()
        top_funds = [i for i in top_funds if i in indicator_existed_fund][:top_num]
        cur_d = _index_fund_pack.loc[_start_date]
        cur_d_sta = cur_d.apply(lambda x: (x - x.mean() + 1e-6)/ (x.std() + 1e-6), axis=0)
        cur_d_sta['beta'] = cur_d['beta']
        cur_d_sta['year_length'] = cur_d['year_length']
        cur_d = cur_d_sta
        return pd.DataFrame(cur_d.rank(pct=True).loc[top_funds].mean(axis=0)).rename(columns={0:'rank'}).sort_values('rank',ascending=False)

    @staticmethod
    def samp_period_fund_compare_in_index(index_id,score_select,m,begin_date,today,res_df):
        # 同期 同板块下跑赢指数基金和持仓基金对比
        index_price = m.dts.index_price
        fund_nav = m.dts.fund_nav
        fund_info = m.dts.fund_info
        active_fund_info = m.dts.active_fund_info
        index_info = m.dts.index_info
        fund_size = m.dts.fund_size
        _index_price = index_price.loc[begin_date:today]
        _index_price = _index_price / _index_price.iloc[0]
        last_day = _index_price.index.values[-1]
        _index_ret = pd.DataFrame(data=(_index_price.iloc[-1] / 1 - 1).rename('index_ret'))
        index_ret = _index_ret.loc[index_id].values[0]
        score_dic = m._score_manager.score_cache[last_day][index_id][score_select.__dict__[index_id]]
        score_list = sorted(score_dic.items(), key=lambda x:x[1], reverse=True)
        score_list = [i[0] for i in score_list]
        fund_list = score_list[:int(len(score_list)/2)]
        #fund_list = m._score_manager.score_cache[last_day][index_id][score_select.__dict__[index_id]]
        fund_score = score_select.__dict__[index_id]
        if fund_score == 'active':
            fund_pool = m.dts.all_fund_list
            fund_pool = active_fund_info[(active_fund_info.fund_id.isin(fund_pool)) & (active_fund_info.index_id == index_id)].fund_id.tolist()
        else:
            fund_pool = m.dts.fund_list
            fund_pool = fund_info[(fund_info.fund_id.isin(fund_pool)) & (fund_info.index_id == index_id)].fund_id.tolist()
        fund_list = [i for i in fund_list if i in fund_pool]
        fund_list = fund_info[(fund_info.fund_id.isin(fund_list)) & (fund_info.end_date == datetime.date(2040,12,31))].fund_id.tolist()
        fund_nav_week = fund_nav.loc[begin_date: last_day][fund_list]
        fund_ret = pd.DataFrame(data = (fund_nav_week.iloc[-1] / fund_nav_week.iloc[0] - 1), columns=['ret'])
        top_fund_list = fund_ret[fund_ret.ret > index_ret].sort_values('ret',ascending=False).head(6).index.tolist()
        pos_funds = res_df[res_df.index_id==index_id].index.tolist()
        top_fund_list = list(set(top_fund_list).union(set(pos_funds)))
        price_df = _index_price[[index_id]].join(fund_nav_week[fund_nav_week.columns.intersection(set(top_fund_list))])
        price_df = price_df / price_df.iloc[0]
        name_dict = fund_info.set_index('fund_id').to_dict()['desc_name']
        name_dict.update(index_info.set_index('index_id').to_dict()['desc_name'])
        price_df = price_df.rename(columns=name_dict)
        indicator = m.dts.index_fund_indicator_pack.loc[index_id].loc[last_day].loc[top_fund_list][['alpha','beta','track_err']].reset_index()
        indicator.loc[:,'rank'] = indicator.fund_id.map(lambda x :score_list.index(x) + 1)
        indicator['desc_name'] = indicator.fund_id.map(name_dict)
        indicator = pd.merge(indicator,fund_ret, on='fund_id')
        indicator = indicator.sort_values('ret',ascending=False)
        indicator['ret'] = indicator.ret.map(lambda x: str(round(x*10000,1))+'BP')        
        fund_info['trim_name'] = fund_info.desc_name.map(lambda x : re.subn(r'[ABCDEFR]{1,2}(\(人民币\)|\(美元现汇\)|\(美元现钞\)|1|2|3)?$', '', x)[0])
        trim_name_df = fund_info.set_index('fund_id')[['trim_name']]
        fund_id_df = fund_info.set_index('trim_name')[['fund_id']]
        fund_size = fund_size.tail(1).T
        fund_size.columns = ['fund_size']
        fund_size = fund_size.join(trim_name_df).groupby('trim_name').sum()
        fund_size = fund_size.join(fund_id_df).set_index('fund_id')
        indicator = indicator.set_index('fund_id').join(fund_size).reset_index()
        indicator['fund_size'] = indicator.fund_size.map(lambda x: str(round(x/1e8,1)) + '亿')
        indicator['alpha'] = indicator.alpha.map(lambda x: round(x,3))
        indicator['beta'] = indicator.beta.map(lambda x: round(x,3))
        indicator['track_err'] = indicator.track_err.map(lambda x: round(x,3))
        FundPainter.plot_legend_aside(price_df)
        return indicator

    @staticmethod
    def port_penetraded_analysis(m, fund_type,res_df):
        # 组合持仓穿透分析
        fund_info = m.dts.fund_info
        fund_list = res_df.index.tolist()
        
        stock_weights = DataManager.basic_data(func_name=f'get_fund_hold_{fund_type}_latest', fund_list = fund_list)
        res_df['weight'] = res_df['weight'].map(lambda x : float(x[:-1]))
        stock_weights = stock_weights.set_index('fund_id').drop(columns=['datetime','_update_time'])
        weight_list = [i for i in stock_weights if 'weight' in i]
        for r in stock_weights.iterrows():
            fund_id = r[0]
            fund_weight = res_df.loc[fund_id, 'weight'] /100
            for weight_i in weight_list:
                stock_weights.loc[fund_id, weight_i] = stock_weights.loc[fund_id, weight_i] / 100 * fund_weight
        _df = stock_weights.join(res_df)
        stock_weights = _df[~_df.index_id.isin(['mmf','sp500rmb'])]
        _res = []
        for r in stock_weights.iterrows():
            fund_id = r[0]
            for i in range(1,11):
                dic = {
                    'fund_id' : fund_id,
                    f'{fund_type}_name':r[1][f'rank{i}_{fund_type}'],
                    f'{fund_type}_weight':r[1][f'rank{i}_{fund_type}weight'], 
                }
                _res.append(dic)
        _df_before_agg = pd.DataFrame(_res)
        _df_before_agg = pd.merge(_df_before_agg,fund_info[['fund_id','desc_name']],on='fund_id')
        if fund_type == 'bond':
            _df_before_agg = _df_before_agg.dropna(subset=['bond_name'])
            rule = '[a-zA-Z0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+'
            _df_before_agg['subject'] = _df_before_agg.bond_name.map(lambda x: re.sub(rule, '', x) )
            _df_before_agg = _df_before_agg.rename(columns={'bond_name':'bond_full_name'})
            bond_info = DataManager.raw_data(func_name='get_em_bond_info')
            bond_info['subject'] = bond_info.name.map(lambda x: re.sub(rule, '', x))
            stock_info = DataManager.raw_data(func_name='get_em_stock_info')
            conv_bond_info = DataManager.raw_data(func_name='get_em_conv_bond_info')
            conv_bond_info['subject'] = conv_bond_info.CBNAME.map(lambda x: re.sub(rule, '', x))
            _df_before_agg = _df_before_agg.rename(columns={'bond_name':'bond_full_name','bond_short_name':'bond_name'})
            _df_before_agg = _df_before_agg[['subject','bond_weight','desc_name','bond_full_name']].groupby('subject').agg({'bond_weight':'sum',
                                                                         'desc_name':lambda x: x.tolist(),
                                                                         'bond_full_name':lambda x: x.tolist()})
            _df_before_agg = _df_before_agg.join(bond_info[['subject','em2_type']].set_index('subject'))
            _df_before_agg['desc_name'] = _df_before_agg.desc_name.map(lambda x : list(set(x))) 
            _df_before_agg = _df_before_agg.reset_index().drop_duplicates('subject').set_index('subject')  
            _df_before_agg = _df_before_agg.join(bond_info[['subject','is_city_bond']].sort_values('subject',ascending=False).drop_duplicates(subset=['subject']).set_index('subject'))
            _df_before_agg = _df_before_agg.join(bond_info[['subject','cbl2_type']].drop_duplicates(subset=['subject']).set_index('subject'))
        else:
            _df_before_agg = _df_before_agg.groupby(f'{fund_type}_name').agg({'desc_name':lambda x: x.tolist(),f'{fund_type}_weight':'sum'})

        _sum = _df_before_agg[f'{fund_type}_weight'].sum()
        _df_before_agg[f'{fund_type}_weight'] = _df_before_agg[f'{fund_type}_weight'] / _sum
        _df_before_agg = _df_before_agg.sort_values(f'{fund_type}_weight',ascending=False)


        if fund_type == 'stock':      
            _df_before_agg[f'{fund_type}_weight'] = _df_before_agg[f'{fund_type}_weight'].map(lambda x : str(round(100*x,1))+'%')
            stock_info = DataManager.raw_data(func_name='get_em_stock_info')
            industry_info = DataManager.raw_data(func_name='get_em_industry_info')
            industry_info = industry_info[industry_info.ind_class_type == IndClassType.SWI1]
            stock_info.loc[:,'sw_indus_1'] = stock_info.bl_sws_ind_code.map(lambda x: x.split('-')[0] if x is not None else None)
            _df1 = stock_info[['stock_id','name','sw_indus_1']]
            _df2 = industry_info[['em_id','ind_name']].rename(columns={'em_id':'sw_indus_1'})
            stock_info = pd.merge(_df1,_df2,on='sw_indus_1')
            _df_before_agg = _df_before_agg.join(stock_info.set_index('name')[['ind_name']]).reset_index().set_index(['ind_name','stock_name'])
            return _df_before_agg, pd.DataFrame()
        else:
            # part1 利率债 政策
            _df_before_agg.loc[:,'group_name'] = ''
            part_1 = _df_before_agg[_df_before_agg.em2_type == '政策银行债'].copy()
            part_1.loc[:,'group_name'] = '1.利率债'
            # part2 城投债
            part_2 = _df_before_agg[(_df_before_agg.em2_type != '政策银行债') & (_df_before_agg.is_city_bond == 1)].copy()
            part_2.loc[:,'group_name'] = '2.城投债'
            # part3 可转债
            part_3 = _df_before_agg[_df_before_agg.index.str.contains('转债')].join(conv_bond_info[['subject','CBSTOCKCODE','CBSTOCKNAME']].set_index('subject')).copy()
            part_3.loc[:,'group_name'] = '3.可转债'
            part_3.loc[:,'em2_type'] = '可转债'
            part_3 = part_3.rename(columns={'CBSTOCKCODE':'stock_id','CBSTOCKNAME':'stock_name'})
            # part4 其他企业信用债 a股企业债， 其他企业债
            part_4 = _df_before_agg[(_df_before_agg.is_city_bond != 1)&(_df_before_agg.em2_type != '政策银行债')&(~_df_before_agg.index.str.contains('转债'))].copy()
            part_4.loc[:,'stock_id'] = ''
            part_4.loc[:,'stock_name'] = ''
            for r in part_4.iterrows():
                subject_name = r[0]
                try:
                    _df = stock_info[stock_info['name'].str.contains(subject_name)]
                    if _df.shape[0] >= 1:
                        part_4.loc[subject_name,'stock_id'] = _df.stock_id.values[0]
                        part_4.loc[subject_name,'stock_name'] = _df.name.values[0]
                        part_4.loc[subject_name,'group_name'] = '4.a股企业债'
                    else:
                        part_4.loc[subject_name,'group_name'] = '5.其他企业债'
                except:
                    part_4.loc[subject_name,'group_name'] = '5.其他企业债'
            cols = ['group_name','bond_weight','subject','fund_name','bond_full_name','em2_type','cbl2_type','is_city_bond','stock_id','stock_name']
            result = pd.concat([part_1,part_2,part_3,part_4]).reset_index().rename(columns={'desc_name':'fund_name'})[cols].sort_values(by=['group_name','bond_weight'],ascending=[1,0])
            result2 = (result[['em2_type','bond_weight']].groupby('em2_type').sum() * 100).round(2).sort_values('bond_weight',ascending=False)
            result2 = result2.astype('str') + '%'
            result[f'{fund_type}_weight'] = result[f'{fund_type}_weight'].map(lambda x : str(round(100*x,1))+'%')
            return result, result2

    @staticmethod
    def port_penetraded_asset_weight(res_df, m, saa):
        res_df['weight'] = res_df.weight.map(lambda x: float(x[:-1]))
        fund_id_list = res_df.index.tolist()

        pos_weight = DataManager.basic_data(func_name=f'get_fund_hold_asset_latest', fund_list = fund_id_list)
        fund_info = m.dts.fund_info
        pos_weight = pos_weight.set_index('fund_id')[['stock_nav_ratio','bond_nav_ratio','cash_nav_ratio','other_nav_ratio']].fillna(0)
        pos_weight = pos_weight.rename(columns={'stock_nav_ratio':'stock',
                                         'bond_nav_ratio':'bond',
                                        'cash_nav_ratio':'cash',
                                        'other_nav_ratio':'other'})
        pos_stats = pos_weight.T.mul(res_df['weight'].T)
        df_weight = pd.DataFrame(pos_stats.T.sum() / pos_stats.T.sum().sum(), columns=['weights'])
        pos_weight = pos_weight.join(fund_info[['fund_id','desc_name','wind_class_2']].set_index('fund_id')).reset_index().set_index(['fund_id','desc_name'])
        for col in ['stock','bond','cash','other']:
            pos_weight[col] = pos_weight[col].map(lambda x : str(round(x,1)) + '%')
        
        saa_df = pd.DataFrame([saa.__dict__],index=['weights']).replace(0,np.nan).dropna(axis=1).T
        AssetPainter.double_pie_chart(df_weight,saa_df)
        return pos_weight.sort_values('wind_class_2')

    def real_port_hold(self, check_date, port_name, m):
        port_hold = {}
        port_hold['稳健'] = {
            'datetime':datetime.date(2020,11,23),
            'position':[
                    {
                        'fund_id':'000860!0',
                        'weight':0.085,
                    },
                    {
                        'fund_id':'001931!0',
                        'weight':0.085,
                    },
                    {
                        'fund_id':'003042!0',
                        'weight':0.085,
                    },
                    {
                        'fund_id':'003999!0',
                        'weight':0.165,
                    },
                    {
                        'fund_id':'004449!0',
                        'weight':0.085,
                    },
                    {
                        'fund_id':'005893!0',
                        'weight':0.165,
                    },
                    {
                        'fund_id':'007333!0',
                        'weight':0.165,
                    },
                    {
                        'fund_id':'009404!0',
                        'weight':0.165,
                    },
            ]
        }

        port_hold['进取'] = {
            'datetime':datetime.date(2020,7,17),
            'position':[
                    {
                        'fund_id':'161125!0',
                        'weight':0.025,
                    },
                    {
                        'fund_id':'164210!0',
                        'weight':0.125,
                    },
                    {
                        'fund_id':'673101!0',
                        'weight':0.04,
                    },
                    {
                        'fund_id':'000217!0',
                        'weight':0.05,
                    },
                    {
                        'fund_id':'000509!0',
                        'weight':0.01,
                    },
                    {
                        'fund_id':'000917!0',
                        'weight':0.10,
                    },
                    {
                        'fund_id':'002671!0',
                        'weight':0.04,
                    },
                    {
                        'fund_id':'002963!0',
                        'weight':0.05,
                    },
                    {
                        'fund_id':'004603!0',
                        'weight':0.125,
                    },
                    {
                        'fund_id':'005480!0',
                        'weight':0.125,
                    },
                    {
                        'fund_id':'006075!0',
                        'weight':0.025,
                    },
                    {
                        'fund_id':'006730!0',
                        'weight':0.04,
                    },
                    {
                        'fund_id':'006760!0',
                        'weight':0.125,
                    },
                    {
                        'fund_id':'006928!0',
                        'weight':0.04,
                    },
                    {
                        'fund_id':'007404!0',
                        'weight':0.04,
                    },
                    {
                        'fund_id':'008779!0',
                        'weight':0.04,
                    },
            ]
        }

        port_hold['激进'] = {
            'datetime':datetime.date(2021,1,12),
            'position':[
                    {
                        'fund_id':'160424!0',
                        'weight':0.04,
                    },
                    {
                        'fund_id':'673101!0',
                        'weight':0.05,
                    },
                    {
                        'fund_id':'003999!0',
                        'weight':0.09,
                    },
                    {
                        'fund_id':'004449!0',
                        'weight':0.095,
                    },
                    {
                        'fund_id':'006075!0',
                        'weight':0.05,
                    },
                    {
                        'fund_id':'006730!0',
                        'weight':0.05,
                    },
                    {
                        'fund_id':'007333!0',
                        'weight':0.094,
                    },
                    {
                        'fund_id':'007404!0',
                        'weight':0.05,
                    },
                    {
                        'fund_id':'007465!0',
                        'weight':0.04,
                    },
                    {
                        'fund_id':'007795!0',
                        'weight':0.05,
                    },
                    {
                        'fund_id':'000701!0',
                        'weight':0.055,
                    },
                    {
                        'fund_id':'000931!0',
                        'weight':0.09,
                    },
                    {
                        'fund_id':'007045!0',
                        'weight':0.05,
                    },
                    {
                        'fund_id':'007386!0',
                        'weight':0.05,
                    },
                    {
                        'fund_id':'007448!0',
                        'weight':0.05,
                    },
                    {
                        'fund_id':'007829!0',
                        'weight':0.096,
                    },
            ]
        }

        port_hold['年方二十'] = {
            'datetime':datetime.date(2021,2,4),
            'position':[
                    {
                        'fund_id':'160424!0',
                        'weight':0.05,
                    },
                    {
                        'fund_id':'202308!0',
                        'weight':0.15,
                    },
                    {
                        'fund_id':'001681!0',
                        'weight':0.073,
                    },
                    {
                        'fund_id':'003291!0',
                        'weight':0.116,
                    },
                    {
                        'fund_id':'006075!0',
                        'weight':0.025,
                    },
                    {
                        'fund_id':'006649!0',
                        'weight':0.072,
                    },
                    {
                        'fund_id':'007063!0',
                        'weight':0.082,
                    },
                    {
                        'fund_id':'007581!0',
                        'weight':0.123,
                    },
                    {
                        'fund_id':'007722!0',
                        'weight':0.025,
                    },
                    {
                        'fund_id':'004951!0',
                        'weight':0.073,
                    },
                    {
                        'fund_id':'005091!0',
                        'weight':0.105,
                    },
                    {
                        'fund_id':'005223!0',
                        'weight':0.106,
                    },
            ]
        }
        fund_weight = pd.DataFrame(port_hold[port_name]['position']).set_index('fund_id')
        start_date = port_hold[port_name]['datetime']
        fund_nav = m.basic_data(func_name='get_fund_nav_with_date', fund_list=fund_weight.index.tolist(), start_date=start_date)
        fund_nav = fund_nav.pivot_table(index='datetime',values='adjusted_net_value',columns='fund_id').ffill()
        _fund_nav = fund_nav / fund_nav.iloc[0]
        _fund_nav = _fund_nav * fund_weight.to_dict()['weight']
        mv_df = pd.DataFrame(_fund_nav.loc[check_date:].sum(axis=1),columns=['mv'])
        mv_df = mv_df.join(m.dts.index_price['hs300']).ffill().bfill()
        mv_df = mv_df / mv_df.iloc[0]
        
        stats = Calculator.get_stat_result_from_df(df=mv_df.reset_index(), date_column='datetime', value_column='mv')
        annual_ret= round(stats.annualized_ret,3)
        mdd = round(stats.mdd,4)
        total_ret = int((stats.last_unit_nav - 1) * 10000)
        st = f'check period annual ret : {annual_ret} mdd : {mdd} total_ret {total_ret} bp'

        port_bp_dict = round((mv_df.iloc[-1] - 1) * 10000, 1).to_dict()
        bt_dict = ((fund_nav.iloc[-1] / fund_nav.loc[check_date]) - 1)*10000 
        _dict = bt_dict * _fund_nav.loc[check_date]
        _dict = _dict.round(1).to_dict()
        _dict = {k: str(v)+'bp' for k, v in _dict.items()}
        today = datetime.date.today()
        mv_df = mv_df.drop_duplicates('hs300')
        FundPainter.plot_recent_ret(mv_df,check_date,today,st,port_name+' 盈米')
        df = pd.DataFrame([_dict],index=['rets']).T
        index_dic = m.dts.fund_index_map
        index_dic['009404!0'] = 'national_debt'
        index_dic['000701!0'] = 'mmf'
        index_dic['001681!0'] = 'csi500'
        index_dic['003291!0'] = 'hs300'
        index_dic['007581!0'] = 'hs300'
        df.loc[:,'begin_date'] = check_date
        df.loc[:,'end_date'] = _fund_nav.index[-1]
        df.loc[:,'desc_name'] = df.index.map(m.dts.fund_info.set_index('fund_id')['desc_name'])
        df.loc[:,'fund_ret'] = (bt_dict / 100).round(2)
        df.loc[:,'index_id'] = df.index.map(index_dic)
        df.loc[:,'weight'] = df.index.map(_fund_nav.loc[check_date])
        df = df.sort_values(by='fund_ret',ascending=False)
        df['rets'] = df['fund_ret'] * df['weight']
        df['fund_ret'] = [str(i) + '%' for i in df['fund_ret']]
        df['weight'] = [str(round((i*100),2)) + '%' for i in df['weight']]
        df['rets'] = [str(int(i*100)) + 'BP' for i in df['rets']]
        df = df[['begin_date','end_date','desc_name','index_id','fund_ret','weight','rets']]
        fund_id_list = df.index.tolist()
        _df = m.view_data(func_name='get_daily_fund_daily_result', fund_id_list=fund_id_list).rename(columns={'基金ID':'fund_id'}).set_index('fund_id')
        df = df.join(_df)
        return df

    def get_diff_between_position(self, df1, df2):
        _df1 = df1[['rets']].rename(columns={'rets':'理论收益'}).reset_index()
        _df1 = _df1[~_df1.index.duplicated(keep='first')]
        _df2 = df2[['rets']].reset_index().rename(columns={'rets':'盈米收益','index':'fund_id'})
        _df2 = _df2[~_df2.index.duplicated(keep='first')]
        df_combine = _df1.merge(_df2, on='fund_id',how='outer').fillna(0)
        desc_df = df1[['desc_name']].append(df2[['desc_name']]).drop_duplicates()
        index_df = df1[['index_id']].append(df2[['index_id']])
        df_combine = df_combine.set_index('fund_id').join(desc_df).join(index_df)
        return df_combine

    def bk_trade_history_to_fof_system(self, m, port_name, saa):
        df = self.get_fund_trade()
        fund_weights_df = self.fund_weights_history
        trade_date_list = sorted(df.trade_date.unique().tolist())
        asset_desc_dic = {
            'hs300':'沪深300',
            'csi500':'中证500',
            'gem':'创业板',
            'mmf':'货基',
            'national_debt':'国债',
            'sp500rmb':'标普',
            'gold':'黄金',
        }

        index_id_list = df.index_id.unique().tolist()
        fund_desc_dic = m.dts.fund_info.set_index('fund_id')['desc_name'].to_dict()
        fund_index_dic = df[['fund_id','index_id']].drop_duplicates().set_index('fund_id')['index_id']
        index_desc_dic = m.dts.index_info.set_index('index_id')['desc_name'].to_dict()
        benchmark_id_info = {asset_desc_dic[index_id]: index_id for index_id in index_id_list}

        trade_history = []
        for dt in trade_date_list:
            dic = {
                'datetime':str(dt),
                'fund_weight':[],
            }
            fund_weight_dic = fund_weights_df[dt]
            for fund_id, w in fund_weight_dic.items():
                if round(w,3) == 0:
                    continue
                _dic = {
                    'fund_id':fund_id,
                    'weight':round(w,3),
                    'fund_type':asset_desc_dic[fund_index_dic[fund_id]],
                    'fund_name':fund_desc_dic[fund_id],
                }
                dic['fund_weight'].append(_dic)
            trade_history.append(dic)

        benchmark_list = []
        for asset_name, index_id in benchmark_id_info.items():
            dic = {
                'asset_name':asset_name,
                'index_name':index_desc_dic[index_id],
                'index_id':index_id,
                'weight':saa.__dict__[index_id],
            }
            benchmark_list.append(dic)
        data_result = {
            'trade_history':trade_history,
            'benchmark_info':benchmark_list,
            'portfolio_name':port_name,
        }
        with open(f'{port_name}.json','w',encoding='utf-8') as f:
            f.write(json.dumps(data_result,ensure_ascii=False))
        return data_result