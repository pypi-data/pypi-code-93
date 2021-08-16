import pandas as pd
import traceback
from sqlalchemy import distinct, func
from ..derived.fund_manager_processor_advanced import ManagerProcessorDev
from ...wrapper.mysql import ViewDatabaseConnector
from ...view.view_models import ManagerInfoCollection, FundManagerDailyCollection
from ...manager import DataManager
from .__init__ import mng_best_uri, mng_s3_uri

class ManagerDailyCollectionProcessor:

    def __init__(self):
        self.classfy_helper = ManagerProcessorDev

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

    def cal(self):
        fund_manager_info = DataManager.derived_data(func_name='get_fund_manager_info')
        mng_best_fund = pd.read_parquet(mng_best_uri)
        manager_indicator = pd.read_parquet(mng_s3_uri)
        fund_info = DataManager.basic_data(func_name='get_fund_info')
        fund_manager_info = pd.merge(fund_manager_info, fund_info[['fund_id','desc_name','wind_class_1','wind_class_2']], on='fund_id')

        # 代表作逻辑较严格，对离职经理和新晋经理不评价，这里用终止日，起始日排序选出最近存续的基金作为代表作
        fund_type_dic = {}
        for fund_type, class_list in self.classfy_helper.FUND_CLASSIFIER.items():
            for class_i in class_list:
                fund_type_dic[class_i] = fund_type
        fund_manager_info.loc[:,'fund_type'] = fund_manager_info.wind_class_2.map(lambda x: fund_type_dic.get(x,'stock'))

        result = []
        last_date = mng_best_fund.index[-1]
        for fund_type in self.classfy_helper.FUND_CLASSIFIER:
            mng_info_i = fund_manager_info[fund_manager_info.fund_type == fund_type].copy()
            mng_info_i.loc[:,'best_fund'] = mng_info_i.mng_id.map(lambda x: mng_best_fund.loc[last_date,fund_type].get(x))
            no_best_fund_mng_id = mng_info_i[mng_info_i.best_fund.isnull()].mng_id.unique().tolist()
            mng_info_i = mng_info_i.set_index('mng_id')
            for mng_id in no_best_fund_mng_id:
                _df = mng_info_i.loc[[mng_id]]
                best_fund = _df.sort_values(['end_date','start_date'], ascending=[False, True]).fund_id[0]
                mng_info_i.loc[mng_id,'best_fund'] = best_fund
            mng_info_i = mng_info_i.reset_index()
            result.append(mng_info_i)
        result_df = pd.concat(result).drop(columns=['_update_time'])
        _df1 = manager_indicator.set_index(['mng_id','fund_type'])
        _df2 = result_df.set_index(['mng_id','fund_type'])[['best_fund']]
        df = _df1.join(_df2).reset_index()

        _df_all = df[df.best_fund.isnull()].copy()
        _df_existed = df[~df.best_fund.isnull()].copy()
        for r in _df_all.itertuples():
            _df = fund_manager_info[(fund_manager_info.mng_id == r.mng_id)]
            best_fund = _df.sort_values(['end_date','start_date'], ascending=[False, True]).fund_id.values[0]
            _df_all.loc[r.Index,'best_fund'] = best_fund
        df = pd.concat([_df_all,_df_existed])

        replace_dic = {
            'mdd~history_daily':'mdd_history_daily',
            'annual_ret~history_m':'annual_ret_history_m',
            'mdd~5y_m':'mdd_5y_m',
            'annual_ret~5y_m':'annual_ret_5y_m',
            'mdd~3y_m':'mdd_3y_m',
            'annual_ret~3y_m':'annual_ret_3y_m',
            'mdd~1y_m':'mdd_1y_m',
            'annual_ret~1y_m':'annual_ret_1y_m'}
        
        col_dic = {
            'mng_id':'基金经理id',
            'name':'姓名',
            'fund_type':'基金类型',
            'mdd_history_daily':'历史最大回撤',
            'annual_ret_history_m':'历史年化收益',
            'total_score':'经理总分',
            'ret_ability':'收益能力',
            'risk_ability':'抗风险能力',
            'select_time':'择时能力',
            'select_stock':'选股能力',
            'stable_ability':'稳定能力',
            'experience':'经验能力',
            'mdd_5y_m':'近五年最大回撤',
            'annual_ret_5y_m':'近五年年化收益',
            'mdd_3y_m':'近三年最大回撤',
            'annual_ret_3y_m':'近三年年化收益',
            'mdd_1y_m':'近一年最大回撤',
            'annual_ret_1y_m':'近一年年化收益',
            'trading_days':'从业天数',
            'best_fund':'代表作品',
            'company_id':'基金公司',
        }
        self.result = df.rename(columns=replace_dic)[list(col_dic.keys())]
        self.result = self.result.drop_duplicates(subset=['mng_id','fund_type'])

    def insert(self):
        self.append_data(FundManagerDailyCollection.__tablename__, self.result)

    def collection_daily(self):
        try:
            self.cal()
            self.insert()
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def process(self):
        failed_tasks = []
        if not self.collection_daily():
            failed_tasks.append('fund_manager_daily_collection')
        return failed_tasks

class ManagerInfoCollectionProcessor:

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

    def collection_daily(self):
        mng_info = [
            {
                'mng_id':'16E872',
                'mng_name':'萧楠',
                'introduction':'消费之王，坚守价值投资，屡获奖项',
                'fund_type': 'stock',
            },
            {
                'mng_id':'170F31',
                'mng_name':'谢治宇',
                'introduction':'自下而上精选个股，行业均衡，成长投资，代表作7年6倍',
                'fund_type': 'stock',
            },
            {
                'mng_id':'7CABBB',
                'mng_name':'袁芳',
                'introduction':'擅长行业消费+科技，风格均衡，高换手分散持股',
                'fund_type': 'stock',
            },
            {
                'mng_id':'17109A',
                'mng_name':'曲扬',
                'introduction':'投资风格以稳健著称，获得第七届英华奖五年期股票投资最佳基金经理奖项',
                'fund_type': 'stock',
            },
            {
                'mng_id':'16E885',
                'mng_name':'张坤',
                'introduction':'收益优秀，8年6倍，700亿规模',
                'fund_type': 'stock',
            },
            {
                'mng_id':'7C3A95',
                'mng_name':'杨浩',
                'introduction':'TMT行业有着深入的研究，交银三剑客',
                'fund_type': 'stock',
            },
            {
                'mng_id':'7B55CF',
                'mng_name':'谭小兵',
                'introduction':'任职四年半回报230%',
                'fund_type': 'stock',
            },
            {
                'mng_id':'18377A',
                'mng_name':'王君正',
                'introduction':'通过稳健的投资框架，获得过金牛奖、明星基金奖和金基金奖共6座，业内少有的大满贯基金经理',
                'fund_type': 'stock',
            },
            {
                'mng_id':'7BE82B',
                'mng_name':'何帅',
                'introduction':'绝对收益；成长价值；性价比为王；长期优异；交银三剑客',
                'fund_type': 'stock',
            },
            {
                'mng_id':'78F3D1',
                'mng_name':'孙伟',
                'introduction':'连续5年金牛奖，全市场获此荣誉的基金经理仅3人三次获得明星基金奖',
                'fund_type': 'stock',
            },
            {
                'mng_id':'19A22E',
                'mng_name':'张清华',
                'introduction':'股债双修研究深入，择时能力突出',
                'fund_type': 'bond',
            },
            {
                'mng_id':'01109',
                'mng_name':'桂跃强',
                'introduction':'股债配置能力强，投资权益的风格就属于稳健型，擅长使用权益类资产进行稳定增强',
                'fund_type': 'bond',
            },
            {
                'mng_id':'4F9879',
                'mng_name':'姚秋',
                'introduction':'股债全能的投资界“名将”，宏观层面把握机会，追求长期稳健回报资产配置能力出色',
                'fund_type': 'bond',
            },
            {
                'mng_id':'4F9865',
                'mng_name':'张雅君',
                'introduction':'金牛债券基金经理，同类产品连续六年正收益，金牛基金、明星基金，五星债券基金',
                'fund_type': 'bond',
            },
            {
                'mng_id':'C3B3E7',
                'mng_name':'蒋利娟',
                'introduction':'第六届中国基金业英华奖三年期纯债投资最佳基金经理、泰康资产公募事业部固收投资负责人',
                'fund_type': 'bond',
            },
            {
                'mng_id':'00707',
                'mng_name':'苏玉平',
                'introduction':'五年期二级债最佳基金经理奖”，连续三年在英华奖评选中榜上有名',
                'fund_type': 'bond',
            },
            {
                'mng_id':'17036A',
                'mng_name':'于泽雨',
                'introduction':'2019年金牛奖最佳人气金牛基金经理得主、擅长分析基本面 擅长长周期操作',
                'fund_type': 'bond',
            },
            {
                'mng_id':'7A8375',
                'mng_name':'张雪',
                'introduction':'擅长使用久期择时，杠杆择时，注重风险调整后收益，夏普比率2.58',
                'fund_type': 'bond',
            },
            {
                'mng_id':'B9F063',
                'mng_name':'邬传雁',
                'introduction':'现任泓德基金副总经理。风格稳健型，股债研究均深入，擅长股债择时，权益类增强',
                'fund_type': 'bond',
            },
            {
                'mng_id':'00524',
                'mng_name':'李建',
                'introduction':'擅长股债择时和大类资产配置，严控回撤同时实现长期正收益的灵活配置型代表',
                'fund_type': 'stock',
            },
            {
                'mng_id':'7BEBB3',
                'mng_name':'刘博',
                'introduction':'选股能力出色，风险敞口低，近两年表现出色，任职年化收益45.39%。',
                'fund_type': 'stock',
            },
            {
                'mng_id':'16094C',
                'mng_name':'庄园',
                'introduction':'灵活配置股债，回撤控制和收益能力出色，获债券型优胜金牛基金等高含金量奖项',
                'fund_type': 'stock',
            },
            {
                'mng_id':'164E99',
                'mng_name':'宋炳珅',
                'introduction':'8次获得金牛奖，代表作年化收益7.63%，回撤控制在5.05%水平。工银瑞信“固收+”王牌团队成员',
                'fund_type': 'bond',
            },
        ]        
        self.result = pd.DataFrame(mng_info)

    def insert(self):
        self.append_data(ManagerInfoCollection.__tablename__, self.result)