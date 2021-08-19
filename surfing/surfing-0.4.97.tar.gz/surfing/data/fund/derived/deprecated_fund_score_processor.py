from ...manager.manager_fund import FundDataManager
from ...manager.score import FundScoreManager
from ...struct import AssetWeight, FundScoreHelper
from ...wrapper.mysql import DerivedDatabaseConnector
from ...view.derived_models import FundScore
import pandas as pd
import traceback
import datetime

class FundScoreProcessor(object):

    def __init__(self, data_helper):
        self._data_helper = data_helper

    def init(self, start_time, end_time):
        self._dm = FundDataManager(start_time=start_time, end_time=end_time, score_manager=FundScoreManager())
        self._dm.init()
        self.index_tag = FundScoreHelper()
        self.index_list = list(AssetWeight.__dataclass_fields__.keys())

        start_date_dt = datetime.datetime.strptime(start_time, '%Y%m%d').date()
        end_date_dt = datetime.datetime.strptime(end_time, '%Y%m%d').date()
        self.date_list = self._dm.dts.fund_indicator.datetime
        self.date_list = self.date_list[(self.date_list >= start_date_dt) & (self.date_list <= end_date_dt)]
        self.date_list = sorted(list(set(self.date_list)))
        self.desc_dic = self._dm.dts.fund_info[['fund_id','desc_name']].set_index('fund_id').to_dict('index')

    def calculate_score(self):
        res = []
        for dt in self.date_list:
            for index_id in self.index_list:
                try:
                    res_i, _ = self._dm.get_fund_score(dt, index_id)
                    if res_i:
                        for fund_id, score_i in res_i.items():
                            dic = {
                                'fund_id':fund_id,
                                'score':score_i,
                                'datetime':dt,
                                'index_id':index_id
                            }
                            res.append(dic)
                except:
                    continue
        score_df = pd.DataFrame(res)
        score_df['tag_name'] = score_df['index_id'].map(lambda x: self.index_tag.get(x))
        score_df.drop(['index_id'], axis=1, inplace=True)
        score_df['is_full'] = 1
        score_df['tag_type'] = 1
        score_df['tag_method'] = 'm0'
        score_df['score_method'] = 9
        score_df['desc_name'] = score_df['fund_id'].map(lambda x: self.desc_dic[x]['desc_name'])
        self._data_helper._upload_derived(score_df, FundScore.__table__.name)

    def process(self, start_date, end_date):
        failed_tasks = []
        try:
            self.init(start_date, end_date)
            self.calculate_score()
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('fund_score')

        return failed_tasks
