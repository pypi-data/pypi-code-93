import pandas as pd
import datetime
from ...wrapper.mysql import RawDatabaseConnector, BasicDatabaseConnector
from ...view.raw_models import *
from ...view.basic_models import *
from .derived_data_helper import DerivedDataHelper
from ..raw.raw_data_helper import RawDataHelper
from ..basic.basic_data_helper import BasicDataHelper
from ...api.raw import RawDataApi

class ManagerInfoProcessor:
    '''
    wind基金经理数据比较全 含离职基金经理数据
    东财只含当前基金经理数据
    用wind数据做历史， 用东财数据做更新。对比wind和东财历史数据，解决差异，区分历史和需要更新的数据
    '''

    DEFAULT_DATE = datetime.date(2040,1,1)

    def __init__(self):
        self._raw_api = RawDataApi()
        self.derived_helper = DerivedDataHelper()
        self.basic_helper = BasicDataHelper()

    def init(self):
        #load data
        with RawDatabaseConnector().managed_session() as quant_session:
            _query = quant_session.query(WindFundManager)
            self.wind_manager_df = pd.read_sql(_query.statement, _query.session.bind)

        self.raw_fund_nav: pd.DataFrame = self._raw_api.get_em_fund_nav(columns=('ADJUSTEDNAV',))
        self.raw_fund_nav = self.raw_fund_nav.pivot_table(index='DATES', columns='CODES', values='ADJUSTEDNAV').fillna(method='ffill')

        with BasicDatabaseConnector().managed_session() as quant_session:
            _query = quant_session.query(MngInfo)
            self.manager_df = pd.read_sql(_query.statement, _query.session.bind) 

            _query = quant_session.query(FundInfo)
            self.fund_info = pd.read_sql(_query.statement, _query.session.bind) 

        # 没有基金复用的基金id
        l = self.fund_info.order_book_id.tolist()
        s = list(set(l))
        self.only_1_list = [i for i in s if l.count(i) == 1]

    def wind_fund_nav_begin_date(self, wind_id):
        # 找到基金净值开始日期
        _dt = self.raw_fund_nav[wind_id].dropna().index[0]
        return _dt

    def to_date(self, str_date):
        # 转换wind F_INFO_MANAGER_STARTDATE str ——> datetime
        # 如果为空， 用最新数据填充
        if str_date is not None:
            return datetime.datetime.strptime(str_date, '%Y%m%d').date()
        else:
            return datetime.datetime.today().date()

    def history_data_process(self): 
        # 处理第一步
        #wind F_INFO_MANAGER_STARTDATE 为空，表示公布发布了，但是在获取数据的时刻 2020，6，10左右 基金还为成立，先考虑F_INFO_MANAGER_STARTDATE 不为空的基金数据

        self.w1 =  self.wind_manager_df[~self.wind_manager_df['F_INFO_MANAGER_STARTDATE'].isnull()].copy()
        self.w1['fund_id'] = self.w1.apply(
            lambda x: self.basic_helper._get_fund_id_from_order_book_id(x.F_INFO_WINDCODE.replace('!','.').split('.')[0], self.to_date(x.F_INFO_MANAGER_STARTDATE)), axis=1
        )
        self.w1['F_INFO_MANAGER_STARTDATE'] =  self.w1['F_INFO_MANAGER_STARTDATE'].map(lambda x : datetime.datetime.strptime(x, '%Y%m%d').date() )

        # 东财和万得匹配基金经理名 基金id 和起始日时，起始日会有差别， 人工排除
        ## wind 对的
        wind_right_case = [
            ['杨建华', '200002!0', datetime.date(2009, 8, 24)], # 查过简历 wind对
            ['莫海波', '519193!0', datetime.date(2019, 3, 23)], # 查过基金招募说明 wind 对
            ['刘铭', '004612!0', datetime.date(2018, 11, 10)],  # 查过简历 wind对
            ['刘铭', '004613!0', datetime.date(2018, 11, 10)],  # 查过简历 wind对   
            ['陈薪羽', '007885!0', datetime.date(2020, 1, 4)],  # 查过基金招募说明 wind 对
            ['陈薪羽', '007886!0', datetime.date(2020, 1, 4)],  # 查过基金招募说明 wind 对
            ['吴卫东', '008218!0', datetime.date(2019, 11, 18)], # 查过基金招募说明 wind 对
            ['吴卫东', '008220!0', datetime.date(2019, 11, 18)]  # 查过基金招募说明 wind 对
        ]

        ## 东财对的，基金经理都没有离职情况，只需要改wind起始日就可以
        em_right_case = [
            ['杨谷', '320003!0', datetime.date(2006, 2, 22)], # 查过简历 东财对
            ['王超', '002344!0', datetime.date(2016, 5, 11)], # 查过基金招募说明 东财对
            ['张韵', '002457!0', datetime.date(2016, 3, 1)], # 查过基金招募说明 东财 对
            ['周博洋', '005817!0', datetime.date(2018, 4, 20)],# 查过基金招募说明 东财 对
            ['张航', '005018!0', datetime.date(2019, 9, 16)], # 查过简历 东财对
        ]

        # wind 对华裔人名 不加空格， 东财加
        no_space_name = ['TIAN HUAN']

        # 东财名字 对应wind是中文
        name_replace = {
            'Zhang Phoebe':'张蓓蓓'
        }

        self.no_pair_case = [] # 逐条校验过 85条数据 都是wind没有字条，不是数据不一致导致匹配不上的数据
        for r in self.manager_df.itertuples():
            # 通过 经理名字 基金id 基金经理开始工作时间 3者匹配， 如果1对1， 完美
            # 但是发现两个数据原 经理工作的起始日子错位一天 比如 '徐荔蓉', '450001!0'
            # 匹配逻辑放宽至起始日 在2天以内

            # 东财对于外籍华人 会用拼音加中文表示 比如WEIDONG WU(吴卫东)
            # wind 对某些拼音人名不加 空格 比如 TIAN HUAN
            if '(' in r.mng_name:
                mng_name = r.mng_name.split('(')[1].split(')')[0]
            else:
                mng_name = r.mng_name
                
            if mng_name in no_space_name:
                mng_name = mng_name.replace(' ', '')
            
            if mng_name in name_replace:
                mng_name = name_replace[mng_name]
            
            order_book_id = r.fund_id.replace('!','.').split('.')[0]
            
            if order_book_id not in self.only_1_list:
                continue
            
            # 用东财数据替换wind
            case = [mng_name, r.fund_id, r.start_date]
            if case in em_right_case:
                self.w1.loc[(self.w1['F_INFO_FUNDMANAGER'] == mng_name) \
                            &(self.w1['fund_id'] == r.fund_id),'F_INFO_MANAGER_STARTDATE'] = r.start_date
                continue

            if case in wind_right_case:
                continue
                
            _df = self.w1[(self.w1['F_INFO_FUNDMANAGER'] == mng_name) \
                &(self.w1['fund_id'] == r.fund_id) \
                &(self.w1['F_INFO_MANAGER_STARTDATE'] >= (r.start_date - datetime.timedelta(2))) \
                &(self.w1['F_INFO_MANAGER_STARTDATE'] <= (r.start_date + datetime.timedelta(2)))]
            if _df.shape[0] == 1:
                continue
            else:
                # 没有1对1匹配 放开起始日限制，重新匹配
                em_case = self.manager_df[ (self.manager_df['mng_name'] == mng_name) & \
                    (self.manager_df['fund_id'] == r.fund_id) & \
                    (self.manager_df['start_date'] == r.start_date) ]
            
                wind_case = self.w1[(self.w1['F_INFO_FUNDMANAGER'] == mng_name) \
                    &(self.w1['fund_id'] == r.fund_id)]

                # 1对1 匹配
                if em_case.shape[0] == 1 and wind_case.shape[0] == 1:
                    wind_id = wind_case.F_INFO_WINDCODE.values[0]
                    nav_start_date = self.wind_fund_nav_begin_date(wind_id)
                    
                    # 如果净值开始时间晚于 两个数据基金经理开始时间， 不认为是错误
                    if (nav_start_date >= em_case.start_date.values[0]) and (nav_start_date >= wind_case.F_INFO_MANAGER_STARTDATE.values[0]):
                        continue
                
                self.no_pair_case.append([r.mng_name, r.fund_id, r.start_date])
                
    def history_data_process_dlc(self):
        # 处理第二步
        # 跑完 self.history_data_process 有一些东财未配对的数据
        # 现在处理这些未配对的数据 和 wind 起始时间未空的数据， 合并重复项
        self.w2 =  self.wind_manager_df[self.wind_manager_df['F_INFO_MANAGER_STARTDATE'].isnull()].copy()
        self.w2['fund_id'] = self.w2.apply(
            lambda x: self.basic_helper._get_fund_id_from_order_book_id(x.F_INFO_WINDCODE.replace('!','.').split('.')[0], datetime.date(2020,9,1)), axis=1
        )
        self.new_case = []
        for case_i in self.no_pair_case:
            mng_name = case_i[0]
            fund_id = case_i[1]
            wind_id = fund_id.split('!')[0] +'.OF'
            start_date = case_i[2]
            _df = self.w2[(self.w2['F_INFO_FUNDMANAGER'] == mng_name) & (self.w2['F_INFO_WINDCODE'] == wind_id)]
            # 东财数据新的数据 匹配到wind的历史数据， 更新fund_id 和 基金经理开始任职时间
            if _df.shape[0] == 1:
                self.w2.loc[(self.w2['F_INFO_FUNDMANAGER'] == mng_name) \
                            &(self.w2['F_INFO_WINDCODE'] == wind_id),'F_INFO_MANAGER_STARTDATE'] = start_date
                self.w2.loc[(self.w2['F_INFO_FUNDMANAGER'] == mng_name) \
                            &(self.w2['F_INFO_WINDCODE'] == wind_id),'fund_id'] = fund_id
            else:
                # 找不到到对应数据，船新基金经理数据
                self.new_case.append(case_i)
    
    def existed_mng_id_date_process(self):
        # 处理第三步
        # 如果new_case里数据 基金经理信息 在wind里已有基金id， 用基金id填充
        self.history_data = pd.concat([self.w1,self.w2]).copy()
        self.existed_person_info = []
        self.new_person_info = []
        for case_i in self.new_case:
            mng_name = case_i[0]
            fund_id = case_i[1]
            wind_id = fund_id.split('!')[0] +'.OF'
            start_date = case_i[2]
            mng_info = self.manager_df[(self.manager_df['fund_id'] == fund_id) & (self.manager_df['mng_name'] == mng_name)].copy()
            resume = mng_info.resume.values[0]
            
            # 看是否同名经理 同名人任职过的基金公司名字是否在当前字条的工作经历中 如果是复用基金经理id
            company_now = self.fund_info[self.fund_info['fund_id'] == fund_id].company_id.values[0]
            same_mng_name_fund_ids = fund_list = self.history_data[self.history_data['F_INFO_FUNDMANAGER'] == mng_name].dropna(subset=['fund_id']).fund_id
            if len(same_mng_name_fund_ids) > 0:
                company_list = list(set(self.fund_info[self.fund_info['fund_id'].isin(fund_list)].company_id))
                is_same_person = False
                _fund_id = ''
                for company_i in company_list:
                    if company_i in resume:
                        is_same_person = True
                        company_stayed = company_i
                if is_same_person:
                    stayed_fund_ids = self.fund_info[(self.fund_info['fund_id'].isin(fund_list)) & (self.fund_info['company_id'] == company_stayed )].fund_id.tolist()
                    mng_id = self.history_data[(self.history_data['F_INFO_FUNDMANAGER'] == mng_name) & (self.history_data['fund_id'] == stayed_fund_ids[0])].F_INFO_FUNDMANAGER_ID.values[0]
                    mng_info['F_INFO_FUNDMANAGER_ID'] = mng_id
                    self.existed_person_info.append(mng_info)
                else:
                    self.new_person_info.append(mng_info)

    def make_new_manager_info(self):
        # TODO 用东财经理信息更新wind 会有重名基金经理id对照不上，两个数据源头的经理简历不一致 需要人工对照
        pass
        # 处理第四步
        # 不存在基金经理id的人造id
        # df = pd.concat(self.new_person_info,axis=0)
        # _df = df[['start_mng_date','mng_name']].drop_duplicates().reset_index(drop=True)
        # _df['F_INFO_FUNDMANAGER_ID'] = _df.index
        # _df['F_INFO_FUNDMANAGER_ID'] = _df['F_INFO_FUNDMANAGER_ID'].map(lambda x: f'mngid_{x+1}')
        # mng_id_df = _df.set_index(['start_mng_date','mng_name'])
        # df['F_INFO_FUNDMANAGER_ID'] = df.apply(lambda x: mng_id_df.loc[x.start_mng_date, x.mng_name], axis=1)
        # self.new_id_mng = df.copy()
        # self.old_id_mng = pd.concat(self.existed_person_info,axis=0)
        # self.new_data = pd.concat([self.new_id_mng,self.old_id_mng])

    def change_date(self, x):
        if x is not None:
            return datetime.datetime.strptime(x, '%Y%m%d').date()
        return x

    def unify_columns(self):
        # 处理第五步
        # 融合成新数据格式
        self.new_data['end_date'] = None

        col_dict = {
            'F_INFO_FUNDMANAGER_ID':'mng_id',
            'F_INFO_FUNDMANAGER':'mng_name',
            'F_INFO_MANAGER_GENDER':'gender',
            'F_INFO_MANAGER_BIRTHYEAR':'birth_year',
            'F_INFO_MANAGER_EDUCATION':'education',
            'F_INFO_MANAGER_NATIONALITY':'nationality',
            'F_INFO_MANAGER_RESUME':'resume',
            'F_INFO_MANAGER_STARTDATE':'start_date',
            'F_INFO_MANAGER_LEAVEDATE':'end_date',
        }

        wind_columns = ['F_INFO_FUNDMANAGER_ID',
                        'fund_id',
                        'F_INFO_FUNDMANAGER',
                        'F_INFO_MANAGER_GENDER',
                        'F_INFO_MANAGER_BIRTHYEAR',
                        'F_INFO_MANAGER_EDUCATION',
                        'F_INFO_MANAGER_NATIONALITY',
                        'F_INFO_MANAGER_RESUME',
                        'F_INFO_MANAGER_STARTDATE',
                        'F_INFO_MANAGER_LEAVEDATE']
        df_1 = self.history_data[wind_columns].rename(columns=col_dict).copy()
        df_1['gender'] = df_1['gender'].replace('m','男').replace('f','女')
        df_1['end_date'] = df_1['end_date'].map(lambda x: self.change_date(x) )

        em_columns = ['F_INFO_FUNDMANAGER_ID',
                    'fund_id',
                    'mng_name',
                    'gender',
                    'birth_year',
                    'education',
                    'nationality',
                    'resume',
                    'start_date',
                    'end_date']
        df_2 = self.new_data[em_columns].rename(columns=col_dict).copy()
        self.result = pd.concat([df_1,df_2])
        self.result['start_date'] = self.result['start_date'].fillna(self.DEFAULT_DATE)
        self.result['end_date'] = self.result['end_date'].fillna(self.DEFAULT_DATE)
        self.result['fund_id'] = self.result['fund_id'].fillna('not_exist') # TODO update basic.fund_info if too many not_exist existed 
        self.result = pd.merge(self.result, self.fund_info[['fund_id','company_id']], on='fund_id')
        res = []
        company_s = df.company_id.tolist()
        for i in company_s:
            i = i.replace('管理有限公司','').replace('管理有限责任公司','').replace('股份有限公司','').replace('有限公司','')
            res.append(i)
        self.result.company_id = res

if __name__ == "__main__":
    self = ManagerInfoProcessor()
    self.init()
    self.history_data_process()
    self.history_data_process_dlc()
    self.existed_mng_id_date_process()
    self.make_new_manager_info()
    self.unify_columns()
    self.derived_helper._upload_derived(self.result.drop_duplicates(), 'manager_info')