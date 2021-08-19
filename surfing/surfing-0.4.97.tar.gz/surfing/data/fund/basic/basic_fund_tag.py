
import datetime
import traceback
import json
import numpy as np
import pandas as pd
import re
from ...api.basic import BasicDataApi
from ...api.raw import RawDataApi
from ..raw.raw_data_helper import RawDataHelper
from .basic_data_helper import BasicDataHelper
from ...manager import DataManager
from ..derived.derived_indicators_processor_group_advanced import FundIndicatorProcessorGroup
from ....constant import IndClassType

class Data:
    
    pass

class FundTagProcessor:

    FUND_CLASSIFIER = {
        'stock': ['普通股票型基金', '偏股混合型基金', '平衡混合型基金', '灵活配置型基金'], 
        'index': ['被动指数型基金', '增强指数型基金'],
    }
    CONCEPT_GROUP_ID = ['dm_cpt_201223','dm_ind_201224']
    THRESHOLD = 0.2

    THRESHOLD_DICT = {
        '军工':0.2,
        '银行':0.2,
        '养老':0.19,
        '白酒':0.2,
        '5G':0.2,
        '芯片':0.2,
        '半导体':0.15,
        '券商':0.2,
        '医疗':0.15,
        '光伏':0.2,
        '新能源':0.2,
        '医美':0.13,
        '黄金':0.15,
        '农业':0.13,
        '食品饮料':0.2,
        '金融':0.2,
        '地产':0.15,
        '有色':0.15,
        '消费':0.2,
        '可选消费':0.18,
        '主要消费':0.2,
        '科技':0.2,
        '医药':0.15,
        '金融地产':0.2,
        }

    INDEX_FUND_RAW = {
        '白酒':['白酒'],
        '食品饮料':['食品'],
        '消费':['消费','可选'],
        '可选消费':['可选'],
        '主要消费':['消费'],
        '5G':['5G'],
        '半导体':['半导体'],
        '科技':['信息','科技','电信'],
        '光伏':['光伏'],
        '农业':['农业'],
        '新能源':['新能源'],
        '医药':['医药'],
        '医疗':['医疗'],
        '银行':['银行'],
        '券商':['非银'],
        '金融地产':['金融地产'],
        '金融':['金融'],
        '地产':['地产'],
        '有色':['有色'],
        '黄金':['黄金'],
        '军工':['军工'],
        '养老':['养老']
        }

    def __init__(self, data_helper:BasicDataHelper):
        self._data_helper = BasicDataHelper()
        self.config = FundIndicatorProcessorGroup
        self.data = Data()

    def data_prepare(self):
        today = datetime.datetime.now().date()
        md = today.strftime('%m%d')
        sentry_date = pd.Series(self.config.REPORT_DATE_LIST)
        sentry = sentry_date[sentry_date <= md]
        # 为半年报/年报发布预留一个季度的缓冲时间
        if sentry.empty:
            real_date = datetime.date(today.year - 1, 6, 30)
        elif len(sentry) <= 2:
            real_date = datetime.date(today.year - 1, 12, 31)
        else:
            real_date = datetime.date(today.year, 6, 30)

        self.data.fund_type_dic = {}
        for fund_type, wind_class_list in self.FUND_CLASSIFIER.items():
            for wind_class in wind_class_list:
                self.data.fund_type_dic[wind_class] = fund_type

        self.data.stock_info = DataManager.raw_data(func_name='get_em_stock_info')
        self.data.stock_info.loc[:,'sw_indus_1'] = self.data.stock_info.bl_sws_ind_code.map(lambda x: x.split('-')[0] if x is not None else None)
        
        self.data.industry_info = DataManager.raw_data(func_name='get_em_industry_info')
        self.data.industry_info = self.data.industry_info[self.data.industry_info.ind_class_type == IndClassType.SWI1]

        self.data.fund_info = DataManager.basic_data(func_name='get_fund_info')
        self.data.fund_info['fund_type'] = self.data.fund_info.wind_class_2.map(lambda x: self.data.fund_type_dic.get(x))
        self.data.stock_fund_list = self.data.fund_info[self.data.fund_info.fund_type == 'stock'].fund_id.tolist()
        self.data.index_fund_list = self.data.fund_info[self.data.fund_info.fund_type == 'index'].fund_id.tolist()
        
        self.data.fund_position = DataManager.basic_data(func_name=f'get_fund_hold_stock_latest', fund_list = self.data.stock_fund_list + self.data.index_fund_list ).set_index('fund_id')
        self.data.concept_data = DataManager.basic_data(func_name=f'get_fund_stock_concept', tag_group_id_list = self.CONCEPT_GROUP_ID)
        self.data.concept_data = self.data.concept_data[['stock_id','tag_name']].drop_duplicates().set_index('stock_id')
        self.fund_position_date_process()
        
        self.data.index_info = DataManager.basic_data(func_name='get_index_info')
        self.data.fund_benchmark = DataManager.basic_data(func_name='get_fund_benchmark')

    def fund_position_date_process(self):
        _res = []
        for r in self.data.fund_position.iterrows():
            fund_id = r[0]
            for i in range(1,11):
                dic = {
                    'fund_id' : fund_id,
                    'stock_id':r[1][f'rank{i}_stock_code'],
                    'stock_weight':r[1][f'rank{i}_stockweight'], 
                }
                _res.append(dic)
        self.data.fund_position = pd.DataFrame(_res).set_index('fund_id')
                
    def get_stocks_concept(self, stock_id):
        if stock_id in self.data.concept_data.index:
            return self.data.concept_data.loc[[stock_id]].tag_name.tolist()
        return []

    def get_fund_holdings(self, fund_id):
        if fund_id in self.data.fund_position.index:
            df = self.data.fund_position.loc[fund_id].copy()
            df.loc[:,'stock_weight'] = df.stock_weight / df.stock_weight.sum()
            df = df.set_index('stock_id').to_dict()['stock_weight']
            return df
        else:
            return None

    def calculate_fund_concept(self, fund_list):
        self.fund_concept_weight_dic = {}
        self.fund_concept_dic = {}
        for fund_id in fund_list:
            self.fund_concept_weight_dic[fund_id] = {}
            fund_weight_dic = self.get_fund_holdings(fund_id)
            if fund_weight_dic is None:
                continue
            for stock_id, stock_weight in fund_weight_dic.items():
                concept_list = self.get_stocks_concept(stock_id)
                for concept_i in concept_list:
                    if concept_i is not self.fund_concept_weight_dic[fund_id]:
                        self.fund_concept_weight_dic[fund_id][concept_i] = stock_weight
                    else:
                        self.fund_concept_weight_dic[fund_id][concept_i] += stock_weight
            self.fund_concept_dic[fund_id] = []
            for concept_i, weight_i in self.fund_concept_weight_dic[fund_id].items():
                threshold = self.THRESHOLD_DICT[concept_i]
                if weight_i >= threshold:
                    self.fund_concept_dic[fund_id].append(concept_i)

    def get_fund_concept_result(self):
        fund_concept = []
        for fund_id, concept_list in self.fund_concept_dic.items():
            if not concept_list == []:
                fund_concept.append({'fund_id':fund_id,'concept':concept_list})
        return pd.merge(pd.DataFrame(fund_concept),self.data.fund_info[['fund_id','desc_name']],on='fund_id')

    def get_fund_concept_weight_result(self):
        res = []
        for fund_id, concept_dic in self.fund_concept_weight_dic.items():
            for concept_i, weight_i in concept_dic.items():
                dic = {
                    'fund_id':fund_id,
                    'concept':concept_i,
                    'weight_i':weight_i,
                }
                res.append(dic) 
        return pd.DataFrame(res)

    def get_concept_id(self, tag_name, raw_concept_id):
        return f'{tag_name}@{str(raw_concept_id)}'

    def calculate_stock_fund_tag(self):
        
        fund_list = self.data.stock_fund_list
        self.calculate_fund_concept(fund_list)
        fund_concept_df = self.get_fund_concept_result()
        fund_concept_weight = self.get_fund_concept_weight_result()
        fund_concept_df = fund_concept_df[['fund_id','concept']].rename(columns={'concept':'tag_name'})
        fund_concept_df = fund_concept_df.explode('tag_name')
        return fund_concept_df

    def select_one_benchmark(self, x):
        if not x:
            return None
        x = json.loads(x)
        select = max(x, key=x.get)
        if x[select] >= 0.8:
            return select
        return None

    def calculate_index_fund_tag(self):
        df = self.data.fund_benchmark[self.data.fund_benchmark.fund_id.isin(self.data.index_fund_list)].copy()
        df.loc[:,'benchmark_id'] = df.benchmark_s_raw.map(lambda x:self.select_one_benchmark(x))
        df = df[['fund_id','index_text','benchmark_id']]
        _df = self.data.index_info[['index_id','desc_name']].rename(columns={'index_id':'benchmark_id'})
        df = pd.merge(df,_df, on='benchmark_id').rename(columns={'desc_name':'index_name'})
        df = pd.merge(df,self.data.fund_info[['fund_id','desc_name']], on='fund_id').rename(columns={'desc_name':'fund_name'})
        index_fund_rules = {}
        for k, vs in self.INDEX_FUND_RAW.items():
            for v in vs:
                if v not in index_fund_rules:
                    index_fund_rules[v] = []
                index_fund_rules[v].append(k)
        result = []
        for tag, tag_detail_list in index_fund_rules.items():
            _res = []
            for tag_i in tag_detail_list:
                _df_i = df[df.index_name.str.contains(tag)].copy()
                if _df_i.shape[0] >= 1:
                    _df_i.loc[:,'tag_name'] = tag_i
                    _res.append(_df_i)
            if _res == []:
                #print(tag)
                continue
            _df = pd.concat(_res).drop_duplicates()
            result.append(_df)
        df = pd.concat(result)[['fund_id','tag_name']]
        return df

    def make_concept_id(self):    
        tag_group_id = 'dm_fund_201224'
        stock_fund_concept_df = self.calculate_stock_fund_tag()
        index_fund_concept_df = self.calculate_index_fund_tag()
        fund_concept_df = pd.concat([stock_fund_concept_df,index_fund_concept_df],axis=0)

        tag_list = fund_concept_df.tag_name.unique().tolist()
        num = 1
        tag_dic = {}
        for tag_id in tag_list:
            tag_dic[tag_id] = self.get_concept_id(tag_group_id, num)
            num += 1
        fund_concept_df.loc[:,'tag_id'] = fund_concept_df.tag_name.map(lambda x: tag_dic[x])
        fund_concept_df.loc[:,'tag_group_id'] = tag_group_id
        name_dic = self.data.fund_info.set_index('fund_id').to_dict()['desc_name']
        name_to_id_dic = self.data.fund_info.set_index('desc_name').to_dict()['fund_id']
        tag_name_list = fund_concept_df.tag_name.unique().tolist()
        # 筛选类型
        result = []
        for tag_i in tag_name_list:
            df_tag_i = fund_concept_df[fund_concept_df.tag_name == tag_i].copy()
            df_tag_i.loc[:,'desc_name'] = df_tag_i.fund_id.map(lambda x : name_dic[x])
            delete_id_list = []
            fund_name_list = df_tag_i.desc_name.tolist()
            for r in df_tag_i.itertuples():
                desc_name = r.desc_name 
                fund_id = r.fund_id
                if 'B' in desc_name or 'C' in desc_name:
                    prefered_fund, count = re.subn(r'[BC]$', 'A', desc_name)
                    if count != 0 and prefered_fund in fund_name_list:
                        _fund_id = name_to_id_dic[prefered_fund]
                        print(f'[BC] {tag_i} remove {prefered_fund} keep {desc_name}')
                        delete_id_list.append(_fund_id)
                if 'H' in desc_name or 'E' in desc_name:
                    prefered_fund, count = re.subn(r'[HE]$', 'A', desc_name)
                    if count != 0 and prefered_fund in fund_name_list:
                        print(f'[EH] {tag_i} remove {desc_name} keep {prefered_fund}')
                        delete_id_list.append(r.fund_id)
            result.append(df_tag_i[~df_tag_i.fund_id.isin(delete_id_list)])
        
        df = pd.concat(result,axis=0)
        # 去掉剩下的 E H R I类
        EHR_PROBLEM_EKYWORDS = {
            'E': ['ETF', 'REITs', 'ESG', 'CES'],
            'H': ['H股', 'A-H50', '50AH', '中证AH'],
            'R': ['REITs'],
            'I': [],
        }
        ehr_funds = []
        for r in df[['desc_name', 'fund_id']].itertuples():
            for type_word, problem_words in EHR_PROBLEM_EKYWORDS.items():
                i = r.desc_name
                for problem_i in problem_words:
                    i = i.replace(problem_i, '')
                if type_word in i:
                    ehr_funds.append(r.fund_id)     
        
        df = df[~df['fund_id'].isin(ehr_funds)]
        self._data_helper._upload_basic(df, 'fund_tag')

    