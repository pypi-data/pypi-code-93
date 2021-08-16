import datetime
import pandas as pd
import numpy as np
import traceback
from typing import List, Dict
from ...api.raw import RawDataApi
from ..raw.raw_data_helper import RawDataHelper
from ....data.view.raw_models import QSOverseaFundCurMdd, QSOverseaFundMonthlyRet, QSOverseaFundIndicator, QSOverseaFundRadarScore, QSOverseaFundPeriodRet, OSFundRet, QSFundRecentRet
from ....util.calculator_item import CalculatorBase

# TODO 按照一只美股持仓基金和中国股票持仓基金跑流程
TEST_CODE = ['HKAACE01','HKAAVP'] # 净值分析 持仓分析 选用的基金id
TEST_CODE_COMPARE = ['MXAPJ', 'MXWD', 'MXCNANM', 'RIY'] # 因子计算截面对比 选用的指数id


class OverseaFundNavAnalysis:

    # 对每个基金类别统计,按照数量和含义人工汇总
    FUND_GROUP = {
        'stock':['股票基金','指数基金 - 股票'],
        'fix_rate':['定息基金','指数基金 - 定息'],
        'mix':['均衡基金','混合资产基金'],
        'other':['另类基金'],
        'mmf':['货币市场基金'],
      }
    
    # 统计每类基金类别下最普遍基准作为默认基准
    DEFAULT_BENCHMARK = {
        '股票基金':'MXAPJ',
        '定息基金':'JPEIGLBL',
        '均衡基金':'MXAPJ',
        '另类基金':'mmf',
        '混合资产基金':'SHSZ300',
        '指数基金 - 股票':'MXAPJ',
        '指数基金 - 定息':'JPEIGLBL',
        '货币市场基金':'mmf',
    }

    # 资产基准
    ASSET_BENCHMARK = {
        'us_stock': 'RIY',      # 罗素1000指数
        'us_bond': 'LUACTRUU',  # Bloomberg Barclays US Corporate Total Return Value Unhedged USD
        'ap_stock': 'MXAP', # MSCI AC Asia ex Japan Net Total Return USD Index
        'ap_bond': 'JPEIJACC',  # J.P. Morgan Asia Credit Index Core
    }

    NOT_CONSIDER_TYPE = ['指数基金']

    def __init__(self, data_helper: RawDataHelper):
        self._data_helper = data_helper
        self._raw_api = RawDataApi()

    def init(self, end_date=str):
        fund_info = self._raw_api.get_over_sea_fund_info()
        fund_benchmark = self._raw_api.get_over_sea_fund_benchmarks()
        self.fund_info = pd.merge(fund_info, fund_benchmark[['benchmark_final','industry_1','industry_2','isin_code']], on='isin_code').set_index('codes')    
        self.fund_info = self.fund_info[~self.fund_info.fund_type.isin(self.NOT_CONSIDER_TYPE)]
        for fund_type, benchmark in self.DEFAULT_BENCHMARK.items():
            fund_list = self.fund_info[(self.fund_info['fund_type'] == fund_type) & (self.fund_info.benchmark_final.isnull())].index.tolist()
            self.fund_info.loc[fund_list,'benchmark_final'] = benchmark
        self._fund_nav = self._raw_api.get_oversea_fund_nav(end_date=end_date).drop(columns=['_update_time'],errors='ignore')
        self.fund_nav = self._fund_nav.pivot_table(index='datetime',columns='codes',values='nav').replace(0,np.nan).ffill()
        self.fund_nav_adj = self._raw_api.get_oversea_fund_nav_adj(end_date=end_date)
        self.fund_nav_adj = self.fund_nav_adj.pivot_table(index='datetime',columns='codes',values='nav').replace(0,np.nan).ffill()
        self.index_price = self._raw_api.get_oversea_index_price(end_date=end_date)        
        self.index_price = self.index_price.pivot_table(index='datetime',columns='codes',values='close').replace(0,np.nan).ffill()
        self.get_new_fund_benchmark()

    def get_new_fund_benchmark(self):
        # 由于数据更新 当前把基金分四类设置基准
        us_stock_fund_list = self.fund_info[(self.fund_info.area.isin(['环球','美国'])) 
                      &(self.fund_info.industry_1 == 'Equity Fund')].index.tolist()
        us_bond_fund_list = self.fund_info[(self.fund_info.area == '美国')&(self.fund_info.industry_1 == 'Debt Fund')].index.tolist()
        ap_stock_fund_list = self.fund_info[((self.fund_info.area == '亚洲 (包括日本)')|(self.fund_info.area == '亚洲 (日本除外)'))&(self.fund_info.industry_1 == 'Equity Fund')].index.tolist()
        ap_bond_fund_list = self.fund_info[((self.fund_info.area == '亚洲 (包括日本)')|(self.fund_info.area == '亚洲 (日本除外)')) & (self.fund_info.industry_1 == 'Debt Fund')].index.tolist()


        l = us_stock_fund_list+us_bond_fund_list+ap_stock_fund_list+ap_bond_fund_list
        fl = self.fund_info.index.tolist()
        fls = [i for i in fl if i not in l]

        _fund_info = self.fund_info.loc[fls]
        cl = _fund_info[_fund_info.fund_type == '股票基金'].area.unique().tolist()
        asian_country = ['泰国', '日本', '大中华', '新兴市场', '中国','新兴市场','中国A股','香港','印尼','台湾', '印度','印尼','中国及印度','越南', '菲律宾','前沿市場','马来西亚及新加坡','韩国',
        '新加坡']
        all_country = [i for i in cl if i not in asian_country]
        ap_stock_fund_list.extend(_fund_info[(_fund_info.fund_type == '股票基金') & (_fund_info.area.isin(asian_country))].index.tolist())
        us_stock_fund_list.extend(_fund_info[(_fund_info.fund_type == '股票基金') & (_fund_info.area.isin(all_country))].index.tolist())

        cl = _fund_info[_fund_info.fund_type != '股票基金'].area.unique().tolist()
        asian_country = ['中国A股','大中华','亚洲 (日本除外)','香港','新兴市场','中国','印度']
        all_country = [i for i in cl if i not in asian_country]
        us_bond_fund_list.extend(_fund_info[(_fund_info.fund_type != '股票基金') & (_fund_info.area.isin(all_country))].index.tolist())
        ap_bond_fund_list.extend(_fund_info[(_fund_info.fund_type != '股票基金') & (_fund_info.area.isin(asian_country))].index.tolist())

        benchmark_dic = {
            'us_stock':us_stock_fund_list,
            'us_bond':us_bond_fund_list,
            'ap_stock':ap_stock_fund_list,
            'ap_bond':ap_bond_fund_list,
        }
        fund_benchmark = {}
        for asset_id, fund_list in benchmark_dic.items():
            for fund_id in fund_list:
                fund_benchmark[fund_id] = asset_id
        self.fund_benchmark_dic = fund_benchmark


    def get_update_date(self, df_new, df_old, dt_col='datetime'): # dt_col in other db maybe report_date
        codes_list = df_new.codes.unique().tolist()
        res = []
        for code_i in codes_list:
            exsited_dt = df_old[df_old.codes == code_i]
            if exsited_dt.empty:
                continue
            exsited_dt = pd.to_datetime(exsited_dt.datetime.values[-1]).date()
            _df = df_new[(df_new.codes == code_i)&(df_new.datetime > exsited_dt)]
            # idx = codes_list.index(code_i)
            # if idx % 50 == 0:
            #     print(idx)
            res.append(_df)
        return pd.concat(res)

    def rolling_cur_mdd(self, x):
        if pd.isnull(x).all():
            return np.nan
        x_max = np.fmax.accumulate(x, axis=0)
        return -(1 - np.nanmin(x[-1] / x_max))

    def period_ret_calc(self, df, rule='1M'):
        df = df.set_axis(pd.to_datetime(df.index), inplace=False).resample(rule).last()
        df.index = [i.date() for i in df.index]
        df.index.name = 'date'
        fund_id = df.columns.tolist()[0]
        df.columns=['ret']
        df = df.pct_change(1).reset_index()
        if rule == '1M':
            df.date = [i.year * 100 + i.month for i in df.date]
        else:
            df.date = [i.year for i in df.date]
        df.loc[:,'codes'] = fund_id
        return df.dropna(axis=0)

    def process_fund_ret(self):
        failed_tasks: List[str] = []
        try:
            _df = self.fund_nav.pct_change(1).iloc[1:] * 100
            _df = pd.DataFrame(_df.stack())
            _df.columns=['ret']
            _df = _df.reset_index()
            self._data_helper._upload_raw(_df, OSFundRet.__table__.name,to_truncate=True)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(f'oversea_fund_ret')
        return failed_tasks
        
    def process_current_mdd(self):
        failed_tasks: List[str] = []
        try:
            _df = (self.fund_nav / self.fund_nav.cummax()) - 1
            _df = pd.DataFrame(_df.stack())
            _df.columns=['current_mdd']
            _df = _df.reset_index()
            _df = _df[_df.datetime >= datetime.date(2021,1,1)]
            end_date = self.fund_nav.index[-1]
            existed_start_date = end_date - datetime.timedelta(days=30)
            exsited_data = self._raw_api.get_oversea_fund_cur_mdd(start_date = str(existed_start_date))
            _df = self.get_update_date(df_new=_df, df_old=exsited_data, dt_col='datetime')
            self._data_helper._upload_raw(_df, QSOverseaFundCurMdd.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(f'oversea_current_mdd')
        return failed_tasks

    def process_monthly_ret(self):
        failed_tasks: List[str] = []
        try:
            _df = self.fund_nav.set_axis(pd.to_datetime(self.fund_nav.index), inplace=False).resample('1M').last()
            _df.index = [i.date() for i in _df.index]
            _df.index.name = 'datetime'
            _df = _df.pct_change(1)
            _df = pd.DataFrame(_df.stack())
            _df.columns=['monthly_ret']
            _df = _df.reset_index()
            _df = _df.replace(np.Inf,np.nan).replace(-np.Inf,np.nan)
            self._data_helper._upload_raw(_df, QSOverseaFundMonthlyRet.__table__.name, to_truncate=True)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(f'oversea_monthly_ret')
        return failed_tasks

    def process_indicators(self):

        dic = {
            'cumu_ret':'累计收益',
            'annual_ret':'年化收益',
            'annual_vol':'年化波动',
            'sharpe':'夏普',
            'recent_1w_ret':'最近一个周收益',
            'recent_1m_ret':'最近一个月收益',
            'recent_3m_ret':'最近三个月收益',
            'recent_6m_ret':'最近六个月收益',
            'recent_1y_ret':'最近一年收益',
            'recent_3y_ret':'最近三年收益',
            'recent_5y_ret':'最近五年收益',
            'worst_3m_ret':'最差三个月收益',
            'worst_6m_ret':'最差六个月收益',
            'last_mv_diff':'最新涨跌幅',
            'last_increase_rate':'最新涨跌',
            'recent_drawdown':'当前回撤',
            'recent_mdd_date1':'当前回撤开始时间',
            'recent_mdd_lens':'当前回撤持续天数',
            'mdd':'最大回撤',
            'mdd_date1':'最大回撤开始日',
            'mdd_date2':'最大回撤结束日',
            'mdd_lens':'最大回撤持续天数',
            'calmar':'卡玛比率',
            'downside_risk':'下行风险',
            'sortino':'索提诺',
            'var':'风险价值',
            'ervar':'风险价值调整比',
            'skew':'偏度',
            'kurtosis':'峰度',
            'alpha_cl':'选股收益',
            'beta_cl':'择时收益',
            'beta_bear':'熊市beta', 
            'beta_bull':'牛市beta',
            'excess_ret':'相对收益',
            'win_rate':'胜率',
            'corr':'相关性',
            'track_err':'跟踪误差',
            'info':'信息比率',
            'alpha':'alpha',
            'beta':'beta',
            'treynor':'特雷诺',
            'not_system_risk':'非系统性风险',
            'cvar':'条件风险价值',
            'up_capture':'上行捕捉率',
            'down_capture':'下行捕捉率',
            'excess_ret_cotinue':'超额收益持续性',
            'continue_value_m':'业绩持续性',
        }

        failed_tasks: List[str] = []
        try:
            res = []
            monthly_indicator = []
            daily_indicator = ['start_date','end_date','trade_year','last_unit_nav','cumu_ret','annual_ret','annual_vol','sharpe','recent_1w_ret','recent_1m_ret','recent_3m_ret','recent_6m_ret','recent_1y_ret','recent_3y_ret','recent_5y_ret','worst_3m_ret','worst_6m_ret','last_mv_diff','last_increase_rate','recent_drawdown','recent_mdd_date1','recent_mdd_lens','mdd','mdd_date1','mdd_date2','mdd_lens']
            fund_list = self.fund_info.index.tolist()
            for fund_id in fund_list:
                if fund_id in ['HKATAF01','HKJFCNG'] or fund_id not in self.fund_nav:
                    continue
                fund_nav_i = self.fund_nav[[fund_id]]
                fund_nav_adj_i = self.fund_nav_adj[[fund_id]]
                benchmark_id = self.fund_info.loc[fund_id].benchmark_final
                #benchmark_id = self.ASSET_BENCHMARK[self.fund_benchmark_dic[fund_id]]
                
                if not benchmark_id in self.index_price or benchmark_id in ['USC0TR03','G0O1','I02885JP']:
                    benchmark_id = self.DEFAULT_BENCHMARK[self.fund_info.loc[fund_id,'fund_type']]
                fund_nav_i = fund_nav_i.join(self.index_price[benchmark_id]).ffill().dropna()
                fund_nav_i.columns = ['fund','benchmark']
                fund_nav_adj_i = fund_nav_adj_i.join(self.index_price[benchmark_id]).ffill().dropna()
                fund_nav_adj_i.columns = ['fund','benchmark']
                last_day = fund_nav_i.index.values[-1]
                # 不同年度
                for year in [1,3,5]:
                    b_d = last_day - datetime.timedelta(days=365*year)
                    _fund_nav_i = fund_nav_i.loc[b_d:]
                    _fund_nav_adj_i = fund_nav_adj_i.loc[b_d:]
                    if _fund_nav_i.fund.pct_change().std() < 0.0005:
                        continue
                    res_i_m = CalculatorBase.get_stat_result(
                            dates = _fund_nav_adj_i.index.values,
                            values = _fund_nav_adj_i.fund.values,
                            risk_free_rate=0.015,
                            frequency='1M',
                            ret_method='pct_ret',
                            benchmark_values=_fund_nav_adj_i.benchmark.values,
                        )
                    res_i_d = CalculatorBase.get_stat_result(
                                    dates = _fund_nav_i.index.values,
                                    values = _fund_nav_i.fund.values,
                                    risk_free_rate=0.015,
                                    frequency='1D',
                                    ret_method='pct_ret',
                                    benchmark_values=_fund_nav_i.benchmark.values,
                                )
                    _df_i_daily = pd.DataFrame([res_i_d])
                    _df_i_monthly = pd.DataFrame([res_i_m])
                    # 日度和月度结合
                    if monthly_indicator == []:
                        monthly_indicator = [i for i in _df_i_daily.columns if i not in daily_indicator]
                    _df_i = pd.concat([_df_i_daily[daily_indicator], _df_i_monthly[monthly_indicator]],axis=1)
                    _df_i.loc[:,'codes'] = fund_id
                    _df_i.loc[:,'data_cycle'] = year
                    res.append(_df_i)
                idx = fund_list.index(fund_id)
                print(f'fund {fund_id} {idx + 1}')
            _df = pd.concat(res)
            _df = _df.drop(columns=['start_date']).rename(columns={'end_date':'datetime'})
            _df = _df.replace(np.Inf,np.nan).replace(-np.Inf,np.nan)
            total_columns = list(QSOverseaFundIndicator.__table__.columns.keys())
            _df = _df[_df.columns.intersection(total_columns)]
            self._data_helper._upload_raw(_df, QSOverseaFundIndicator.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(f'oversea_indicators')
        return failed_tasks

    def process_radar_score(self):
        failed_tasks: List[str] = []
        try:
            indicator_df = self._raw_api.get_qs_fund_indicator()
            dt = indicator_df.datetime.unique().tolist()[0]
            dic = {
                    'annual_ret':'ret_ability',
                    'annual_vol':'risk_ability',
                    'up_capture':'bull_ability',
                    'down_capture':'bear_ability',
                    'alpha':'alpha_ability',
                    'mdd':'drawdown_ability',}
            indicator_df = indicator_df[indicator_df.data_cycle == 3].drop(columns=['data_cycle']).set_index('codes')
            _df = indicator_df.copy()
            _df = _df[list(dic.keys())].rename(columns=dic)
            _df['risk_ability'] = - _df['risk_ability']
            _df['bear_ability'] = - _df['bear_ability']
            _df['drawdown_ability'] = - _df['drawdown_ability']
            _df = _df.rank(pct=True)
            _df['total_score'] = _df.mean(axis=1).rank(pct=True)
            _df = (_df / 0.2).apply(np.ceil)
            _df = _df.reset_index()
            _df.loc[:,'datetime'] = dt
            type_dic = {}
            for group_id, fund_types in self.FUND_GROUP.items():
                fund_list = self.fund_info[self.fund_info.fund_type.isin(fund_types)].index.tolist()
                for i in fund_list:
                    type_dic[i] = fund_types[0]
            _df.loc[:,'fund_type'] = _df.codes.map(lambda x:type_dic[x])
            type_dic = {
                'ret_ability':int,
                'risk_ability':int,
                'bull_ability':int,
                'bear_ability':int,
                'alpha_ability':int,
                'drawdown_ability':int,
                'total_score':int,
            }
            _df = _df.astype(type_dic)
            self._data_helper._upload_raw(_df, QSOverseaFundRadarScore.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(f'oversea_radar_score')
        return failed_tasks
    
    def process_period_ret(self):
        failed_tasks: List[str] = []
        try:
            res = []
            for fund_id in self.fund_nav:
                fund_nav_i = self.fund_nav[[fund_id]]
                # monthly
                res_monthly = self.period_ret_calc(fund_nav_i, rule='1M')
                # yearly
                res_yearly = self.period_ret_calc(fund_nav_i, rule='1Y')
                res.append(res_monthly)
                res.append(res_yearly)
            df = pd.concat(res, axis=0)
            self._data_helper._upload_raw(df, QSOverseaFundPeriodRet.__table__.name, to_truncate=True)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(f'oversea_period_ret')
        return failed_tasks

    def process_recent_ret(self):
        failed_tasks: List[str] = []
        try:
            res = []
            end_date = self.fund_nav.index[-1]
            for fund_id in self.fund_nav:
                nav = self._fund_nav[self._fund_nav.codes == fund_id].set_index('datetime')[['nav']].dropna()
                ret_i = CalculatorBase.calc_recent_ret(dates=nav.index,values=nav.nav.values)
                ret_i['datetime'] = end_date
                ret_i['codes'] = fund_id
                res.append(ret_i)
            df = pd.DataFrame(res)
            df = df.replace(np.Inf,np.nan).replace(-np.Inf, np.nan)
            df = df.replace(np.Inf,np.nan).replace(-np.Inf, np.nan)
            total_columns = list(QSFundRecentRet.__table__.columns.keys())
            df = df[df.columns.intersection(total_columns)]
            self._data_helper._upload_raw(df, QSFundRecentRet.__table__.name, to_truncate=True)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(f'oversea_recent_ret')
        return failed_tasks

    def daily_process(self, end_date):
        self.init(end_date)
        failed_tasks = []
        failed_tasks.extend(self.process_fund_ret())
        #failed_tasks.extend(self.process_current_mdd())
        failed_tasks.extend(self.process_monthly_ret())
        failed_tasks.extend(self.process_period_ret())
        failed_tasks.extend(self.process_recent_ret())
        return failed_tasks

    def weekly_process(self, end_date):
        self.init(end_date)
        failed_tasks = []
        failed_tasks.extend(self.process_indicators())
        failed_tasks.extend(self.process_radar_score())
        return failed_tasks