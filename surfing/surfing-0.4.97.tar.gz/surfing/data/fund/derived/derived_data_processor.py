
import datetime
from typing import List
import traceback
import pandas as pd

from .fund_indicator_processor import FundIndicatorProcessor
# from .derived_index_val import IndexValProcess
from .derived_index_val_long_term import IndexValProcessLongTerm
from .style_analysis_processor import StyleAnalysisProcessor
from .derived_data_helper import DerivedDataHelper
from .fund_indicator_processor_weekly import FundIndicatorProcessorWeekly
from .fund_indicator_processor_monthly import FundIndicatorProcessorMonthly
from .derived_indicators_processor_group import FundIndicatorProcessorGroup
from .derived_index_ret_vol import IndexIndicatorProcessor
from .derived_fund_aic import AIPProcess
from .derived_mng_fund_rank import FundManagerFundRankProcessor
from .derived_fund_alpha import FundAlphaProcessor
# from .derived_fund_score_extended import FundScoreExtendedProcess
from .derived_fund_score_group import FundScoreGroupProcess
from .derived_fund_score_group_v1 import FundScoreGroupV1Process
from .barra_cne5_factor_processor import BarraCNE5FactorProcessor
from .style_reg_processer import StyleBoxReg
from .style_box import StyleBoxGenerator
from .fund_manager_processor import ManagerProcessor
from .derived_top_manager_funds import TopManagerFundProcessor
from .derived_fund_industry_exposure import FundIndustryExposureProcess
from .third_party_portfolio.qieman import QiemanPortfolioProcessor
from .third_party_portfolio.danjuan import DanjuanPortfolioProcessor
from .third_party_portfolio.em import EmPortfolioProcessor
from .third_party_portfolio.gf_sec import GFSecPortfolioProcessor
from .third_party_portfolio.manually_crawled import ManuallyCrawledPortfolioProcessor
from .fund_manager_processor_advanced import ManagerProcessorDev
from .derived_oversea_nav_analysis import OverseaFundNavAnalysis
from ...api.basic import BasicDataApi
from ..raw.raw_data_helper import RawDataHelper


class DerivedDataProcessor:
    def __init__(self):
        self._data_helper = DerivedDataHelper()
        self._raw_data_helper = RawDataHelper()
        self.fund_indicator_processor = FundIndicatorProcessor(self._data_helper)
        self.fund_indicator_processor_weekly = FundIndicatorProcessorWeekly(self._data_helper)
        self.fund_indicator_processor_monthly = FundIndicatorProcessorMonthly(self._data_helper)
        self.fund_indicator_processor_group_1Y = FundIndicatorProcessorGroup(self._data_helper, 1)
        self.fund_indicator_processor_group_5Y = FundIndicatorProcessorGroup(self._data_helper, 5)
        self._manager_processor = ManagerProcessor(self._data_helper)
        # self.index_val_processor = IndexValProcess(self._data_helper)
        self.index_val_processor_long_term = IndexValProcessLongTerm(self._data_helper)
        self.index_indicator = IndexIndicatorProcessor(self._data_helper)
        self.fund_aip = AIPProcess(self._data_helper)
        # 这版基金评分先不用了，这里先注释掉
        # self._derived_fund_score_extended = FundScoreExtendedProcess(self._data_helper)
        self._derived_fund_score_group_v1_1Y = FundScoreGroupV1Process(self._data_helper, 1)
        self._derived_fund_score_group_v1_5Y = FundScoreGroupV1Process(self._data_helper, 5)
        self._derived_fund_score_group_1Y = FundScoreGroupProcess(self._data_helper, 1)
        self._derived_fund_score_group_5Y = FundScoreGroupProcess(self._data_helper, 5)
        self._barra_cne5_factor_processor = BarraCNE5FactorProcessor(self._data_helper)
        self._style_regression_processor = StyleBoxReg(self._data_helper)
        self._style_box_processor = StyleBoxGenerator(self._data_helper)
        self.style_analysis_processors: List[StyleAnalysisProcessor] = []
        self.mng_fund_rank = FundManagerFundRankProcessor(self._data_helper)
        self._fund_alpha_processor = FundAlphaProcessor(self._data_helper)
        self.top_manager_funds_processor = TopManagerFundProcessor(self._data_helper)
        self._fund_industry_exposure = FundIndustryExposureProcess(self._data_helper)
        # 暂时只算这三个universe
        for universe in ('hs300', 'csi800', 'all'):
            sap = StyleAnalysisProcessor(self._data_helper, universe)
            self.style_analysis_processors.append(sap)
        self._qieman_portfolio_processor = QiemanPortfolioProcessor(self._data_helper)
        self._danjuan_portfolio_processor = DanjuanPortfolioProcessor(self._data_helper)
        self._em_portfolio_processor = EmPortfolioProcessor(self._data_helper)
        self._gf_sec_portfolio_processor = GFSecPortfolioProcessor(self._data_helper)
        self._manually_crawled_portfolio_processor = ManuallyCrawledPortfolioProcessor(self._data_helper)
        self._manager_processor_dev = ManagerProcessorDev(self._data_helper)
        self._oversea_fund_nav_analysis = OverseaFundNavAnalysis(data_helper=self._raw_data_helper)

    def process_all(self, start_date, end_date):
        failed_tasks = []
        try:
            failed_tasks.extend(self.fund_indicator_processor.process(start_date, end_date))
            # failed_tasks.extend(self.index_val_processor.process(start_date, end_date))
            failed_tasks.extend(self.index_val_processor_long_term.process(start_date, end_date))
            failed_tasks.extend(self.index_indicator.process(end_date))
            failed_tasks.extend(self._manager_processor.process(end_date))
            failed_tasks.extend(self.fund_aip.process(start_date, end_date))
            failed_tasks.extend(self._barra_cne5_factor_processor.process(start_date, end_date))
            failed_tasks.extend(self._style_regression_processor.process(start_date, end_date))
            failed_tasks.extend(self._style_box_processor.process(start_date, end_date))
            failed_tasks.extend(self.mng_fund_rank.process(end_date))
            failed_tasks.extend(self._fund_alpha_processor.process(start_date, end_date))
            failed_tasks.extend(self.top_manager_funds_processor.process(start_date, end_date))
            for sap in self.style_analysis_processors:
                failed_tasks.extend(sap.process(start_date, end_date))
            failed_tasks.extend(self._qieman_portfolio_processor.process(end_date))
            failed_tasks.extend(self._danjuan_portfolio_processor.process(end_date))
            failed_tasks.extend(self._em_portfolio_processor.process(end_date))
            failed_tasks.extend(self._gf_sec_portfolio_processor.process(end_date))
            failed_tasks.extend(self._manually_crawled_portfolio_processor.process(end_date))
            failed_tasks.extend(self._oversea_fund_nav_analysis.daily_process(end_date))

            # 获取下一个交易日
            api = BasicDataApi()
            trading_day_df = api.get_trading_day_list(start_date=end_date)
            if trading_day_df.shape[0] <= 1:
                print(f'get trading days start with {end_date} failed')
                failed_tasks.append('get_trading_day for weekly/monthly indicator in derived')
            else:
                next_trading_day = trading_day_df.iloc[1, :].datetime
                print(f'got next trading day {next_trading_day}')
                end_date_dt = pd.to_datetime(end_date, infer_datetime_format=True).date()
                next_trading_dt = pd.to_datetime(next_trading_day, infer_datetime_format=True).date()
                if end_date_dt.weekday() < next_trading_dt.weekday() and next_trading_dt < end_date_dt + datetime.timedelta(weeks=1):
                    # 表明本周后边还有交易日，今天不需要更新
                    print(f'weekly indicator only update on the last day of week, not today {end_date_dt}')
                else:
                    failed_tasks.extend(self.fund_indicator_processor_weekly.process(start_date, end_date, end_date_dt))
                    # 分别用2年和5年的数据算一下
                    failed_tasks.extend(self.fund_indicator_processor_group_1Y.process(start_date, end_date, end_date_dt))
                    failed_tasks.extend(self.fund_indicator_processor_group_5Y.process(start_date, end_date, end_date_dt))
                    # failed_tasks.extend(self._derived_fund_score_extended.process(start_date, end_date, end_date_dt))
                    failed_tasks.extend(self._derived_fund_score_group_v1_1Y.process(start_date, end_date, end_date_dt))
                    failed_tasks.extend(self._derived_fund_score_group_v1_5Y.process(start_date, end_date, end_date_dt))
                    failed_tasks.extend(self._derived_fund_score_group_1Y.process(start_date, end_date, end_date_dt))
                    failed_tasks.extend(self._derived_fund_score_group_5Y.process(start_date, end_date, end_date_dt))
                    failed_tasks.extend(self._fund_industry_exposure.process(start_date, end_date, end_date_dt))
                    failed_tasks.extend(self._oversea_fund_nav_analysis.weekly_process(end_date))

                if end_date_dt.year == next_trading_dt.year and end_date_dt.month == next_trading_dt.month:
                    # 表明本月后边还有交易日，今天不需要更新
                    print(f'monthly indicator only update on the last day of month, not today {end_date_dt}')
                else:
                    failed_tasks.extend(self.fund_indicator_processor_monthly.process(start_date, end_date, end_date_dt))
                    failed_tasks.extend(self._manager_processor_dev.process(end_date))

        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('unknown in derived_data_processor')
        return failed_tasks

    def process_not_trading_day(self, start_date, end_date):
        failed_tasks = []
        try:
            failed_tasks.extend(self.index_val_processor_long_term.process(start_date, end_date))
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('unknown in derived_data_processor')
        return failed_tasks

    def get_updated_count(self):
        _dic = self._raw_data_helper._updated_count
        for k, v in _dic.items():
            self._data_helper._updated_count[k] = v
        return self._data_helper._updated_count


if __name__ == '__main__':
    ddp = DerivedDataProcessor()
    start_date = '20200820'
    end_date = '20200820'
    ddp.process_all(start_date, end_date)
    # ddp.fund_indicator_processor.process(start_date, end_date)
    # ddp.fund_score_processor.process(start_date, end_date)
    # import pandas as pd
    # date_list = pd.date_range(end='2010-05-31', periods=65, freq='M').sort_values(ascending=False).to_pydatetime()
    # for date in date_list:
    #     date = date.strftime('%Y%m%d')
    #     ddp.fund_indicator_processor_monthly.process(date, date)
