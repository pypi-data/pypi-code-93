
import traceback

from .basic_data_part1 import BasicDataPart1
from .basic_data_part2_fund_ret import BasicFundRet
from .style_analysis_data import StockFactor
from .basic_data_helper import BasicDataHelper
from .barra_cne5_factor_data import BarraCNE5FactorData


class BasicDataProcessor(object):
    def __init__(self):
        self._data_helper = BasicDataHelper()
        self.basic_data_part1 = BasicDataPart1(self._data_helper)
        self.basic_fund_ret = BasicFundRet(self._data_helper)
        self._style_analysis = StockFactor(self._data_helper)
        self._barra_cne5_factor = BarraCNE5FactorData(self._data_helper)

    def process_all(self, start_date, end_date):
        failed_tasks = []

        try:
            failed_tasks.extend(self.basic_data_part1.process_all(start_date, end_date))
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('unknown in basic_data_part1')

        try:
            failed_tasks.extend(self.basic_fund_ret.process_all(end_date))
            failed_tasks.extend(self._style_analysis.process_all(start_date, end_date))
            failed_tasks.extend(self._barra_cne5_factor.process_all(start_date, end_date))
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('unknown in other basic_data')

        return failed_tasks

    def get_updated_count(self):
        return self._data_helper._updated_count

    def process_not_trading_day(self, start_date, end_date):
        failed_tasks = []

        try:
            failed_tasks.extend(self.basic_data_part1.process_not_trading_day(start_date, end_date))
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('unknown in basic_data_part1')

        return failed_tasks


if __name__ == "__main__":
    BasicDataProcessor().process_all('20200813', '20200813')
