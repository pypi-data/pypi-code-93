import pandas as pd
import numpy as np
import json
import datetime
import re
from ...manager import DataManager
from ...wrapper.mysql import ViewDatabaseConnector
from ...view.view_models import FundRecommendationCollection
from .__init__ import mng_s3_uri, fund_s3_uri

EHR_PROBLEM_EKYWORDS = {
    'E': ['ETF', 'REITs', 'ESG', 'CES'],
    'H': ['H股', 'A-H50', '50AH', '中证AH'],
    'R': ['REITs'],
}

class FundRecommendationCollectionProcessor(object):

    def bench_parse(self, x):
        if x is None:
            return []
        bench_dic = json.loads(x)
        index_list = []
        for k,v in bench_dic.items():
            if k == '-1' or v < 0.4:
                continue
            if k == 'hs300' and v < 0.65:
                continue
            index_list.append(k)
        return index_list

    def append_data(self, table_name, data_append_directly_data_df):
        if not data_append_directly_data_df.empty:
            with ViewDatabaseConnector().managed_session() as mn_session:
                try:
                    mn_session.execute(f'TRUNCATE TABLE {table_name}')
                    mn_session.commit()
                except Exception as e:
                    print(f'Failed to truncate table {table_name} <err_msg> {e}')
            data_append_directly_data_df.to_sql(table_name, ViewDatabaseConnector().get_engine(), index = False, if_exists = 'append')
            print('新数据已插入')
        else:
            print('没有需要插入的新数据')
    
    def calc_whole_data(self):
        sector_info = DataManager.basic_data(func_name='get_sector_info')
        sector_fund = DataManager.basic_data(func_name='get_sector_index_info')
        fund_info = DataManager.basic_data(func_name='get_fund_info')
        index_info = DataManager.basic_data(func_name='get_index_info')
        benchmark_info = DataManager.basic_data(func_name='get_fund_benchmark')
        fund_ipo_stats = DataManager.basic_data(func_name='get_fund_ipo_stats')
        fund_open_info = DataManager.basic_data(func_name='get_fund_open_info')
        fund_status = DataManager.basic_data(func_name='get_fund_status')
        fund_conv_bond = DataManager.basic_data(func_name='get_fund_conv_stats')

        conv_bond_fund_list = fund_conv_bond[fund_conv_bond.conv_weights > 20].fund_id.tolist()
        abs_fund_ret_list = fund_info[fund_info.wind_class_2 == '股票多空'].fund_id.tolist()

        fund_info['trim_name'] = fund_info.desc_name.map(lambda x : re.subn(r'[ABCDEFR]{1,2}(\(人民币\)|\(美元现汇\)|\(美元现钞\)|1|2|3)?$', '', x)[0])
        self.not_include_in_market_fund_list = DataManager.basic_data(func_name='get_inside_market_funds').fund_id.tolist()
        not_include_close_fund_list = fund_open_info.fund_id.tolist()
        fund_info_money_fund = fund_info[fund_info.wind_class_2 == '货币市场型基金'].copy()
        self.not_include_no_buy_funds = fund_info_money_fund[ (fund_info_money_fund.desc_name.str.contains('B'))
                    | (fund_info_money_fund.desc_name.str.contains('C'))
                    | (fund_info_money_fund.desc_name.str.contains('D'))
                    | (fund_info_money_fund.desc_name.str.contains('E'))
                    | (fund_info_money_fund.desc_name.str.contains('F'))].fund_id.tolist()

        index_info = index_info.set_index('index_id')
        benchmark_info = benchmark_info[benchmark_info.index_text.notna()]
        benchmark_info.loc[:,'index_list'] = benchmark_info.benchmark_s_raw.map(lambda x : self.bench_parse(x))
        benchmark_info.loc[:,'index_name'] = benchmark_info.index_list.map(lambda x : index_info.loc[x].desc_name.tolist())
        sector_info = sector_info.set_index('sector_id')

        sector_fund = sector_fund.dropna(subset=['fund_id']).set_index('fund_id')
        fund_id_list = list(sector_fund.index.unique())
        res = []
        for fund_id in fund_id_list:
            _df = sector_fund.loc[[fund_id]]
            sector_list = list(_df.sector_id.dropna().unique())
            index_list = list(_df.index_id.unique())
            dic = {
                'fund_id': fund_id,
                'sector_list':sector_list,
                'sector_name':sector_info.loc[sector_info.index.intersection(sector_list)].sector_name.tolist()
            }
            res.append(dic)

        fund_ipo_stats = fund_ipo_stats.pivot_table(index='end_date', columns='fund_id', values='ipo_allocation_weight').fillna(0)
        fund_ipo_stats = fund_ipo_stats + fund_ipo_stats.shift(1).fillna(0) + fund_ipo_stats.shift(2).fillna(0) + fund_ipo_stats.shift(3).fillna(0)
        _df = fund_ipo_stats.tail(1).T
        _df.columns = ['ipo_weight']
        ipo_fund_list = _df[_df > 0.15].dropna().index.tolist()
            
        fund_info_part = fund_info[['fund_id','order_book_id','desc_name','company_id','wind_class_1','wind_class_2','risk_level']].set_index('fund_id')
        fund_info_part.loc[:,'is_ipo_fund'] = fund_info_part.index.isin(ipo_fund_list)
        sector_part = pd.DataFrame(res).set_index('fund_id')
        index_part = benchmark_info.set_index('fund_id')[['index_list','index_name']]

        fund_indicator_score = pd.read_parquet(fund_s3_uri)
        fund_info = fund_info[fund_info.fund_id.isin(fund_indicator_score.reset_index().dropna(subset=['total_score']).fund_id)]
        self.ehr_funds = []
        # 这里itertuples会比iterrows快1个数量级
        for r in fund_info[['desc_name', 'fund_id']].itertuples():
            for type_word, problem_words in EHR_PROBLEM_EKYWORDS.items():
                i = r.desc_name
                for problem_i in problem_words:
                    i = i.replace(problem_i, '')
                if type_word in i:
                    self.ehr_funds.append(r.fund_id)

        fund_info_no_money_fund = fund_info[fund_info.wind_class_2 != '货币市场型基金'].copy()
        fund_info_no_money_fund = fund_info_no_money_fund.groupby('trim_name').last()
        self.include_c_type = fund_info_no_money_fund.fund_id.tolist()
        
        
        fund_indicator_1 = fund_indicator_score[fund_indicator_score['fund_type'] != 'index']
        fund_indicator_2 = fund_indicator_score[fund_indicator_score.fund_type == 'index'].copy()
        #fund_indicator_2['ret_ability'] = fund_indicator_2.alpha_ability
        fund_indicator = pd.concat([fund_indicator_1,fund_indicator_2],axis=0)
        fund_indicator_part = fund_indicator[['mdd~history_daily','annual_ret~history_m','ret_ability','risk_ability','stable_ability','select_time','select_stock','mng_score','total_score','fund_type']]

        mng_info = DataManager.derived_data(func_name='get_fund_manager_info')
        mng_indicator_score = pd.read_parquet(mng_s3_uri)
        mng_part = mng_info[mng_info.end_date > datetime.datetime.now().date()].set_index('mng_id')[['fund_id']]
        mng_indicator_score = mng_indicator_score.join(mng_part, on='mng_id')
        mng_indicator_score_part = mng_indicator_score.rename(columns={'total_score':'mng_total_score'})[['mng_total_score','fund_id','mng_id','name','fund_type']].dropna(subset=['mng_total_score'])

        fund_type_list = list(fund_indicator_score.fund_type.unique())
        result = []
        fund_indicator_part = fund_indicator_part.drop(columns='mng_score')
        for fund_type in fund_type_list:
            _fund_indicator_part = fund_indicator_part[fund_indicator_part.fund_type == fund_type][['total_score']].reset_index().set_index('fund_id')
            _mng_indicator_part = mng_indicator_score_part[mng_indicator_score_part.fund_type == fund_type].set_index('fund_id')
            _fund_indicator_part = _fund_indicator_part.join(_mng_indicator_part)
            idx = _fund_indicator_part.groupby(['fund_id'], sort=False)['mng_total_score'].transform(max) == _fund_indicator_part.mng_total_score
            result.append(_fund_indicator_part[idx][['mng_id','name','mng_total_score']].rename(columns={'mng_total_score':'mng_score'}))
        final_df = fund_indicator_part.join(pd.concat(result)).reset_index().drop_duplicates(subset=['fund_id']).set_index('fund_id')
        final_df = final_df.join(fund_info_part).join(sector_part).join(index_part)
        for fund_id in final_df.index:
            try:
                index_list = sector_fund.loc[[fund_id]].index_id.dropna().unique().tolist()
                if '' in index_list:
                    index_list.remove('')
                append_list = [i for i in index_list if i not in final_df.loc[fund_id,'index_list']]
                final_df.loc[fund_id,'index_list'].extend(append_list)
            except:
                continue
        final_df = final_df.dropna(subset=['total_score'])
        final_df.sector_list = final_df.sector_list.map(lambda x : json.dumps(x))
        final_df.sector_name = final_df.sector_name.map(lambda x : json.dumps(x))
        final_df.index_list = final_df.index_list.map(lambda x : json.dumps(x))
        final_df.index_name = final_df.index_name.map(lambda x : json.dumps(x))
        final_df = final_df.rename(columns={'mdd~history_daily':'mdd','annual_ret~history_m':'annual_ret','name':'mng_name'})
        final_df = final_df.reset_index()
        final_df.loc[:,'is_abs_ret_fund'] = final_df.fund_id.isin(abs_fund_ret_list)
        final_df.loc[:,'is_conv_bond_fund'] = final_df.fund_id.isin(conv_bond_fund_list)
        return final_df
    
    def calc_filter(self, final_df):
        final_df = final_df[final_df.total_score >= 0]
        final_df_1 = final_df[final_df.wind_class_2 != '货币市场型基金']
        final_df_2 = final_df[final_df.wind_class_2 == '货币市场型基金']
        final_df_1 = final_df_1[ (final_df_1.fund_id.isin(self.include_c_type))
                                 & (~ final_df_1.fund_id.isin(self.not_include_in_market_fund_list))
                                 & (~ final_df_1.fund_id.isin(self.ehr_funds))]

        final_df_2 = final_df_2[(~ final_df_2.fund_id.isin(self.not_include_in_market_fund_list))
                                & (~ final_df_2.fund_id.isin(self.not_include_no_buy_funds))]
        final_df = pd.concat([final_df_1, final_df_2])
        fund_size = DataManager.basic_data(func_name='get_fund_size_range')
        fund_size_df = fund_size.pivot_table(columns='fund_id',index='datetime',values='size').tail(1).T
        fund_size_df.columns = ['size']
        big_funds = fund_size_df[fund_size_df['size'] > 1e8].index.tolist()                
        final_df = final_df.loc[final_df.fund_id.isin(big_funds)]
        return final_df

    def calc(self):
        final_df = self.calc_whole_data()
        self.result = self.calc_filter(final_df)

    def insert(self):
        self.append_data(FundRecommendationCollection.__tablename__, self.result)