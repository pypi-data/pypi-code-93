from .fund_derived_factors import *
from ...data.fund.derived.derived_data_helper import normalize, score_rescale

class ScoreCalculator:

    @staticmethod
    def fund_ability_factor_prepare(factor_list, wind_type_dict):
        dt = datetime.date(2012,1,1)
        result = []
        for fac_name in factor_list:
            obj = eval(fac_name)()
            fac = obj.get()
            fac = fac[fac.index > dt]
            fac.columns = pd.MultiIndex.from_product([[fac_name], fac.columns])
            result.append(fac)
            obj.clear(recursive=True)
        _factor = pd.concat(result, axis=1).stack()
        _factor = _factor.reset_index().dropna(subset=factor_list, how='all')
        fund_info = FundInfo().get()
        fund_type = ['stock','bond','index','QDII','mmf']
        wind_class_type = fund_info.set_index('fund_id')['wind_class_2']
        _factor = _factor.rename(columns={'level_1':'fund_id'})
        _factor.loc[:,'fund_type'] = _factor.fund_id.map(lambda x : wind_type_dict.get(wind_class_type.get(x),'stock'))
        _factor = _factor.set_index('datetime')
        return _factor

    @staticmethod
    def score_rescale(df):
        return df.rank(pct=True) * 100
    
    @staticmethod
    def process_score(df):
        df = df.reset_index().set_index('fund_id').drop(columns=['fund_type'])
        return df.rank(pct=True) * 100
    
    @staticmethod
    def calc_fund(df, fund_type, dt, calcu_score_fund):
        df = ScoreCalculator.process_score(df)
        if df is None:
            return None
        df = calcu_score_fund(df, fund_type)
        if df is None:
            return None
        df.loc[:,'fund_type'] = fund_type
        df.loc[:,'datetime'] = dt
        return df.dropna(subset=['fund_score'])

    @staticmethod
    def ability_calc(_factor, calcu_score_fund):
        date_list = sorted(_factor.index.unique().tolist())
        res = []
        lens_dt = len(date_list)
        fund_types = ['stock','bond','index','QDII','mmf']
        _t0 = time.time()
        for dt in date_list:
            df_dt = _factor.loc[dt].set_index('fund_type').copy()
            for fund_type in fund_types:
                try:
                    df_dt_fund_type = df_dt.loc[fund_type]
                except:
                    continue
                res.append(ScoreCalculator.calc_fund(df_dt_fund_type, fund_type, dt, calcu_score_fund))
            dt_idx = date_list.index(dt)
            if dt_idx % 100 == 0:
                _t1 = time.time()
                print(f'\t\tdt {dt} idx {dt_idx} total {lens_dt} cost {round(_t1 - _t0)}')
                _t0 = time.time()
        res = [i for i in res if i is not None]
        _factor = pd.concat(res, axis=0)
        _factor = _factor.reset_index().pivot_table(index='datetime',values='fund_score',columns='fund_id')
        return _factor

class MngScoreV1(Factor):
    # 雷达图基金评价 历史业绩为重

    def __init__(self):
        super().__init__(f_name='MngScoreV1', f_type=FundFactorType.DERIVED, f_level='score')
        self._deps.add(MngAnnualRetDailyHistory())
        self._deps.add(MngTotalRetDailyHistory())
        self._deps.add(MngMddDailyHistory())
        self._deps.add(MngAnnualVolDailyHistory())
        self._deps.add(MngDownsideStdDailyHistory())
        self._deps.add(MngFundTypeTradingDays())
        self._deps.add(MngFundSize())
        self._deps.add(MngClAlphaWeeklyHistory())
        self._deps.add(MngClBetaWeeklyHistory())

    def calc_mng(self, df, fund_type):
        if fund_type == 'stock':
            return self.score_mng_stock(df)
        if fund_type == 'bond':
            return self.score_mng_bond(df)
        if fund_type == 'index':
            return self.score_mng_index(df)
        if fund_type == 'QDII':
            return self.score_mng_qdii(df)
        if fund_type == 'mmf':
            return self.score_mng_mmf(df)
        
    def score_mng_stock(self, df):
        df.loc[:,'mng_ret_ability'] = score_rescale(0.4 * score_rescale(df['MngAnnualRetDailyHistory']) +0.6 * score_rescale(df['MngTotalRetDailyHistory']))
        df.loc[:,'mng_risk_ability'] = score_rescale(0.3 * score_rescale(-df['MngMddDailyHistory']) + 0.4 * score_rescale(-df['MngAnnualVolDailyHistory']) + 0.3 * score_rescale(-df['MngDownsideStdDailyHistory']))
        df.loc[:,'mng_select_stock'] =  score_rescale(normalize(df['MngClAlphaWeeklyHistory']))
        df.loc[:,'mng_select_time'] = score_rescale(normalize(df['MngClBetaWeeklyHistory']) )
        df.loc[:,'mng_experience'] = score_rescale( 0.8 *  score_rescale(df['MngFundTypeTradingDays']) + 0.2 * score_rescale(df['MngFundSize']))
        df.loc[:,'mng_score'] = score_rescale(df.loc[:,'mng_ret_ability'] + df.loc[:,'mng_risk_ability'] + df.loc[:,'mng_select_time'] + df.loc[:,'mng_select_stock'] + 1.5 * df.loc[:,'mng_experience'])
        return df[['mng_id','mng_ret_ability','mng_risk_ability','mng_select_time','mng_select_stock','mng_experience','mng_score']]

    def score_mng_bond(self, df):
        df.loc[:,'mng_ret_ability'] = score_rescale( 0.8 * score_rescale(df['MngAnnualRetDailyHistory']) + 0.2 * score_rescale(df['MngTotalRetDailyHistory']))
        df.loc[:,'mng_risk_ability'] = score_rescale(0.1 * score_rescale(-df['MngMddDailyHistory']) + 0.4 * score_rescale(-df['MngAnnualVolDailyHistory']) + 0.5 * score_rescale(-df['MngDownsideStdDailyHistory']))
        df.loc[:,'mng_select_stock'] =  score_rescale(normalize(df['MngClAlphaWeeklyHistory']))
        df.loc[:,'mng_select_time'] = score_rescale(normalize(df['MngClBetaWeeklyHistory']))
        df.loc[:,'mng_experience'] = score_rescale( 0.8 *  score_rescale(df['MngFundTypeTradingDays']) + 0.2 * score_rescale(df['MngFundSize']))
        df.loc[:,'mng_score'] = score_rescale(1.2 * df.loc[:,'mng_ret_ability'] +  df.loc[:,'mng_risk_ability'] + df.loc[:,'mng_select_time'] + df.loc[:,'mng_select_stock'] + 1.5 * df.loc[:,'mng_experience'])
        return df[['mng_id','mng_ret_ability','mng_risk_ability','mng_select_time','mng_select_stock','mng_experience','mng_score']]

    def score_mng_index(self, df):
        df.loc[:,'mng_ret_ability'] = score_rescale( 0.4 * score_rescale(df['MngAnnualRetDailyHistory']) + 0.6 * score_rescale(df['MngTotalRetDailyHistory']))
        df.loc[:,'mng_risk_ability'] = score_rescale(0.3 * score_rescale(-df['MngMddDailyHistory']) + 0.4 * score_rescale(-df['MngAnnualVolDailyHistory']) + 0.3 * score_rescale(-df['MngDownsideStdDailyHistory']))
        df.loc[:,'mng_experience'] = score_rescale( 0.4 *  score_rescale(df['MngFundTypeTradingDays']) + 0.6 * score_rescale(df['MngFundSize']))
        df.loc[:,'mng_score'] = score_rescale(df.loc[:,'mng_ret_ability'] + df.loc[:,'mng_risk_ability'] + 2 * df.loc[:,'mng_experience'] )
        return df[['mng_id','mng_ret_ability','mng_risk_ability','mng_experience','mng_score']]

    def score_mng_qdii(self, df):
        df.loc[:,'mng_ret_ability'] = score_rescale( 0.4 * score_rescale(df['MngAnnualRetDailyHistory']) + 0.6 * score_rescale(df['MngTotalRetDailyHistory']))
        df.loc[:,'mng_risk_ability'] = score_rescale(0.3 * score_rescale(-df['MngMddDailyHistory']) + 0.4 * score_rescale(-df['MngAnnualVolDailyHistory']) + 0.3 * score_rescale(-df['MngDownsideStdDailyHistory']))
        df.loc[:,'mng_experience'] = score_rescale( 0.8 *  score_rescale(df['MngFundTypeTradingDays']) + 0.2 * score_rescale(df['MngFundSize']))
        df.loc[:,'mng_score'] = score_rescale(df.loc[:,'mng_ret_ability'] + df.loc[:,'mng_risk_ability'] + 1.5 * df.loc[:,'mng_experience'])
        return df[['mng_id','mng_ret_ability','mng_risk_ability','mng_experience','mng_score']]

    def score_mng_mmf(self, df):
        df.loc[:,'mng_ret_ability'] = score_rescale(normalize(df['MngAnnualRetDailyHistory']))
        df.loc[:,'mng_experience'] = score_rescale( 0.8 *  score_rescale(df['MngFundTypeTradingDays']) + 0.2 * score_rescale(df['MngFundSize']))
        df.loc[:,'mng_score'] = score_rescale(df.loc[:,'mng_ret_ability'] + df.loc[:,'mng_experience'])
        return df[['mng_id','mng_ret_ability','mng_experience','mng_score']]

    def prepare(self):
        dt = datetime.date(2012,1,1)
        factor_list = [i.name for i in self._deps]
        result = []
        for fac_name in factor_list:
            obj = eval(fac_name)()
            fac = obj.get()
            fac = fac[fac.index > dt]
            fac.columns = pd.MultiIndex.from_product([[fac_name], fac.columns])
            result.append(fac)
            #obj.clear(recursive=True)
        _factor = pd.concat(result, axis=1).stack()
        _factor = _factor.reset_index().dropna(subset=factor_list, how='all').rename(columns={'level_1':'mng_id'})
        _factor.loc[:,'fund_type'] = _factor.mng_id.map(lambda x: x.split('_')[0])
        _factor = _factor.set_index(['datetime','fund_type'])
        return _factor

    def calc(self):
        _factor = self.prepare()
        fund_types = ['stock','bond','index','QDII','mmf']
        date_list = sorted(_factor.index.get_level_values(0).unique().tolist())
        result = []
        _t0 = time.time()
        for dt in date_list:
            #df_dt = self._factor.loc[dt]
            for fund_type in fund_types:
                df_i = _factor.loc[dt,fund_type].copy()
                df_i = self.calc_mng(df_i, fund_type)
                result.append(df_i)
            dt_idx = date_list.index(dt)
            if dt_idx % 100 == 0:
                print(f'dt {dt} idx {dt_idx}')
        _t1 = time.time()
        print(_t1 - _t0)
        self._factor = pd.concat(result).dropna(subset=['mng_score'])
        self._factor = self._factor.reset_index()
        self._factor = self._factor.set_index('datetime')
        td = self._factor.index.tolist()
        td = pd.to_datetime(td)
        td = [i.date() for i in td] 
        self._factor.index = td

    def append_update(self):
        _exsited_factor = self.get()
        fund_types = ['stock','bond','index','QDII','mmf']
        last_date = pd.to_datetime(_exsited_factor.index[-1]).date()
        _factor = self.prepare()
        date_list = sorted(_factor.index.get_level_values(0).unique().tolist())
        date_list = [pd.to_datetime(i).date() for i in date_list]
        date_list = [i for i in date_list if i > last_date]
        result = []
        if len(date_list)  == 0:
            return True
        for dt in date_list:
            for fund_type in fund_types:
                df_i = _factor.loc[dt,fund_type].copy()
                df_i = self.calc_mng(df_i, fund_type)
                result.append(df_i)
            dt_idx = date_list.index(dt)
        if len(result) == 0:
            return True
        self._factor = pd.concat(result).dropna(subset=['mng_score'])
        self._factor = self._factor.reset_index().set_index('datetime')
        self._factor = _exsited_factor.append(self._factor)
        td = self._factor.index.tolist()
        td = pd.to_datetime(td)
        td = [i.date() for i in td] 
        self._factor.index = td
        return self.save()

class FundMngScoreV1(Factor):

    def __init__(self):
        super().__init__(f_name='FundMngScoreV1', f_type=FundFactorType.DERIVED, f_level='score')
        self._deps.add(MngScoreV1())
        self._deps.add(FundManagerInfo())
        self._deps.add(FundNavDaily())
        self._deps.add(FundInfo())
   
    def prepare(self):
        total_score = MngScoreV1().get().reset_index()
        fund_manager_info = FundManagerInfo().get().set_index('fund_id')[['mng_id','start_date','end_date']]
        fund_nav = FundNavDaily().get()
        fund_info = FundInfo().get()
        type_list = ['stock','bond','index','QDII','mmf']
        manager_score = {}
        for type_i in type_list:
            _df = total_score[total_score['fund_type'] == type_i].reset_index().rename(columns={'index':'datetime'})
            _df = _df.pivot_table(index='datetime',columns='mng_id',values='mng_score')
            manager_score[type_i] = _df
        date_index = manager_score['stock'].index
        #date_index = [_.date() for _ in date_index]
        wind_class_dict = fund_info.set_index('fund_id').to_dict()['wind_class_2']
        return fund_manager_info, fund_nav, wind_class_dict, manager_score, date_index

    def loop_item(self, fund_id, wind_class_dict, fund_manager_info, manager_score, date_index):
        wind_type = wind_class_dict.get(fund_id)
        fund_type = Calculator.WIND_TYPE_DICT.get(wind_type, 'stock')
        if fund_id not in fund_manager_info.index:
            return None
        single_fund_info = fund_manager_info.loc[[fund_id]]
        result = []
        for row in single_fund_info.itertuples(index=False):
            mng_id = fund_type + '_' + row.mng_id
            if mng_id not in manager_score[fund_type]:
                continue
            data = (date_index >= row.start_date) & (date_index <= row.end_date)
            _manager_score = pd.Series(1, index=date_index[data], name=mng_id)
            _manager_score = _manager_score * manager_score[fund_type][mng_id]
            result.append(_manager_score)
        if result  == []:
            return None
        fund_manager_score_i = pd.concat(result,axis=1).max(axis=1)
        fund_manager_score_i.name = fund_id
        return fund_manager_score_i

    def calc(self):
        fund_manager_info, fund_nav, wind_class_dict, manager_score, date_index = self.prepare()
        score_result_total = []
        fund_list = fund_nav.columns.tolist()
        _t0 = time.time()
        for fund_id in fund_list:
            res_i = self.loop_item(fund_id, wind_class_dict, fund_manager_info, manager_score, date_index)
            if res_i is not None:
                score_result_total.append(res_i)
            idx = fund_list.index(fund_id)
            if idx % 1000 == 0:
                _t1 = time.time()
                #print(f'fund_id {fund_id} {idx} {len(fund_list)} cost { round(_t1 - _t0,2)}')
                _t0 = time.time()
        self._factor = pd.concat(score_result_total, axis=1)

class RetAbilityFundScore(Factor):

    def __init__(self):
        super().__init__(f_name='RetAbilityFundScore', f_type=FundFactorType.DERIVED, f_level='score')
        self._deps.add(AnnualRetDailyHistory())
        self._deps.add(TotalRetDailyHistory())
        self._deps.add(RecentMonthRet())

    @staticmethod
    def calcu_score_fund(df, fund_type):
        if fund_type in ['stock','index','QDII']:
            df.loc[:,'fund_score'] = ScoreCalculator.score_rescale(0.4 * df.AnnualRetDailyHistory + 0.6 * df.TotalRetDailyHistory)
        elif fund_type in ['bond']:
            df.loc[:,'fund_score'] = ScoreCalculator.score_rescale(0.8 * df.AnnualRetDailyHistory + 0.2 * df.TotalRetDailyHistory)
        elif fund_type in ['mmf']:
            df.loc[:,'fund_score'] = ScoreCalculator.score_rescale(df.RecentMonthRet)
        return df[['fund_score']]

    def calc(self):
        fund_list = [i.name for i in self._deps]
        factor = ScoreCalculator.fund_ability_factor_prepare(fund_list, Calculator.WIND_TYPE_DICT)
        self._factor = ScoreCalculator.ability_calc(factor, RetAbilityFundScore.calcu_score_fund)

class RiskAbilityFundScore(Factor):

    def __init__(self):
        super().__init__(f_name='RiskAbilityFundScore', f_type=FundFactorType.DERIVED, f_level='score')
        self._deps.add(MddDailyHistory())
        self._deps.add(AnnualVolDailyHistory())
        self._deps.add(DownsideStdDailyHistory())
        self._deps.add(FundPersonalHold())
        self._deps.add(FundSizeCombine())
        
    @staticmethod
    def calcu_score_fund(df, fund_type):
        if fund_type in ['stock','index','QDII','bond']:
            df.loc[:,'fund_score'] = ScoreCalculator.score_rescale(0.3 * df.MddDailyHistory + 0.4 * df.AnnualVolDailyHistory + 0.3 * df.DownsideStdDailyHistory)
        elif fund_type in ['mmf']:
            df.loc[:,'fund_score'] = ScoreCalculator.score_rescale(0.5 * df.FundPersonalHold + 0.5 * df.FundSizeCombine)
        return df[['fund_score']]

    def calc(self):
        fund_list = [i.name for i in self._deps]
        factor = ScoreCalculator.fund_ability_factor_prepare(fund_list, Calculator.WIND_TYPE_DICT)
        self._factor = ScoreCalculator.ability_calc(factor, RiskAbilityFundScore.calcu_score_fund)

class StableAbility(Factor):

    def __init__(self):
        super().__init__(f_name='StableAbility', f_type=FundFactorType.DERIVED, f_level='score')
        self._deps.add(TradeYear())
        self._deps.add(ContinueRegValue())
        self._deps.add(FundSizeCombine())

    @staticmethod
    def calcu_score_fund(df, fund_type):
        if fund_type in ['stock','index','QDII','bond']:
            df.loc[:,'fund_score'] = ScoreCalculator.score_rescale(0.4 * df.TradeYear + 0.4 * df.ContinueRegValue + 0.2 * df.FundSizeCombine)
        else:
            return None
        return df[['fund_score']]

    def calc(self):
        fund_list = [i.name for i in self._deps]
        factor = ScoreCalculator.fund_ability_factor_prepare(fund_list, Calculator.WIND_TYPE_DICT)
        self._factor = ScoreCalculator.ability_calc(factor, StableAbility.calcu_score_fund)

class SelectTimeAbility(Factor):

    def __init__(self):
        super().__init__(f_name='SelectTimeAbility', f_type=FundFactorType.DERIVED, f_level='score')
        self._deps.add(FundClBetaHistoryWeekly())
    
    @staticmethod
    def calcu_score_fund(df, fund_type):
        if fund_type in ['stock','QDII','index']:
            df.loc[:,'fund_score'] = ScoreCalculator.score_rescale(df.FundClBetaHistoryWeekly)
        else:
            return None
        return df[['fund_score']]

    def calc(self):
        fund_list = [i.name for i in self._deps]
        factor = ScoreCalculator.fund_ability_factor_prepare(fund_list, Calculator.WIND_TYPE_DICT)
        self._factor = ScoreCalculator.ability_calc(factor, SelectTimeAbility.calcu_score_fund)

class SelectStockAbility(Factor):

    def __init__(self):
        super().__init__(f_name='SelectStockAbility', f_type=FundFactorType.DERIVED, f_level='score')
        self._deps.add(FundClAlphaHistoryWeekly())

    @staticmethod
    def calcu_score_fund(df, fund_type):
        if fund_type in ['stock','QDII','index']:
            df.loc[:,'fund_score'] = ScoreCalculator.score_rescale(df.FundClAlphaHistoryWeekly)
        else:
            return None
        return df[['fund_score']]

    def calc(self):
        fund_list = [i.name for i in self._deps]
        factor = ScoreCalculator.fund_ability_factor_prepare(fund_list, Calculator.WIND_TYPE_DICT)
        self._factor = ScoreCalculator.ability_calc(factor, SelectStockAbility.calcu_score_fund)

class UpdateDerivedScoreStart:
    pass
