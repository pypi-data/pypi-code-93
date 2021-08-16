import json
import traceback
from multiprocessing import Pool
from ...view.derived_models import FundManagerFundRank
from ...manager.manager_fund import *
from .derived_data_helper import DerivedDataHelper, FUND_CLASSIFIER
from ....resource.data_store import *


class FundManagerFundRankProcessor:

    def __init__(self, data_helper):
        self._data_helper = data_helper

    def init(self, dm=None, start_date='20191001', end_date='20200101'):
        # 借用dm处理数据表，不依赖输入时间
        if dm is None:
            self.dm = FundDataManager(start_time=start_date, end_time=end_date, score_manager=FundScoreManager())
            self.dm.init(score_pre_calc=False)
        else:
            self.dm = dm
        self.start_date = self.dm.start_date
        self.end_date = self.dm.end_date
        with BasicDatabaseConnector().managed_session() as quant_session:
            _fund_nav_query = quant_session.query(
                    FundNav.fund_id,
                    FundNav.adjusted_net_value,
                    FundNav.datetime
                ).filter(
                    FundNav.datetime >= self.start_date - datetime.timedelta(400),
                    FundNav.datetime <= self.end_date,
                )
            _nav_df = pd.read_sql(_fund_nav_query.statement, _fund_nav_query.session.bind)
            self.fund_nav = _nav_df.pivot_table(index='datetime', columns='fund_id', values='adjusted_net_value')
            self.fund_nav = self.fund_nav.fillna(method='ffill') + self.fund_nav.fillna(method='bfill') - self.fund_nav.fillna(method='bfill')
            # 对于单日上涨高于0.15的基金 收益改为0
            self.fund_ret = np.log(self.fund_nav).diff()
            self.fund_ret[self.fund_ret > 0.15] = 0
            self.fund_ret = self.fund_ret.rolling(242).sum()

        self.datelist = self.dm.dts.trading_days[(self.dm.dts.trading_days.datetime >= self.start_date) & (self.dm.dts.trading_days.datetime <= self.end_date)].datetime
        fund_id_list = self.dm.dts.fund_info[self.dm.dts.fund_info['wind_class_2'].isin(FUND_CLASSIFIER['stock'])].fund_id.tolist()
        self.fund_manager_info = self.dm.dts.fund_manager_info[self.dm.dts.fund_manager_info['fund_id'].isin(fund_id_list)]
        self.manager_list = self.fund_manager_info.index.unique().tolist()
        self.fund_id_list = self.fund_ret.columns.tolist()

    def loop_item(self, dt):
        try:
            _manager_detail = []
            _mng_info_dt = self.fund_manager_info[(self.fund_manager_info['start_date'] <= dt) & (self.fund_manager_info['end_date'] >= dt)]
            for manager_id in self.manager_list:
                if manager_id not in _mng_info_dt.index:
                    fund_list = []
                else:
                    mng_info_i = _mng_info_dt.loc[manager_id]
                    fund_list = mng_info_i.fund_id
                    fund_list = [fund_list] if isinstance(fund_list, str) else fund_list
                    fund_list = [i for i in self.dm.dts.all_fund_list if i in fund_list]
                    score_dic = self.fund_ret.loc[dt][fund_list].dropna()
                    if not score_dic.empty:
                        score_list = sorted(score_dic.items(), key=lambda x:x[1], reverse=True)
                        fund_list = [_[0] for _ in score_list]
                    else:
                        fund_list = []
                if len(fund_list) > 0:
                    dic = {
                        'mng_id':manager_id,
                        'fund_list':json.dumps(fund_list),
                        'datetime':dt
                    }
                    _manager_detail.append(dic)
            print(f' finish {dt}')
            return pd.DataFrame(_manager_detail)
        except:
            print(f'boom {dt} failed'  )
            return None

    def calc_history(self):
        date_list = self.datelist
        p = Pool()
        self.result = [i for i in p.imap_unordered(self.loop_item, date_list, 64)]
        self.result = [i for i in self.result if i is not None]
        p.close()
        p.join()
        self.result_df = pd.concat(self.result)
        self._data_helper._upload_derived(self.result_df, FundManagerFundRank.__table__.name)

    def calculate_update(self, dt):
        self.result_df = pd.concat([self.loop_item(dt)])

    def process(self, end_date):
        failed_tasks = []
        try:
            start_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d').date()
            end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d').date()
            start_date = start_date_dt - datetime.timedelta(days = 100) #做data manager 主要用信息表 需要季报数据 多load 100天
            start_date = datetime.datetime.strftime(start_date, '%Y%m%d')
            self.init(start_date=start_date, end_date=end_date)
            self.calculate_update(end_date_dt)
            self._data_helper._upload_derived(self.result_df, FundManagerFundRank.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('manager_fund_rank')
        return failed_tasks


if __name__ == "__main__":
    fmfr = FundManagerFundRankProcessor(DerivedDataHelper())
    fmfr.process('20210111')
