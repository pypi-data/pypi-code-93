
import traceback

from .compute_fund_daily_collection import FundDailyCollectionProcessor
from .compute_index_daily_collection import IndexDailyCollectionProcessor
from .compute_aic_daily_collection import AICDailyCollectionProcessor
from .compute_stock_ipo_collection import StockIpoCollectionProcessor, ConcBondIpoCollectionProcessor
from .compute_manager_info_collection import ManagerDailyCollectionProcessor
from .compute_hf_fund_daily_collection import HFFundDailyCollectionProcessor

class ViewDataProcessor(object):
    def __init__(self):
        self.fund_daily_collection_processor = FundDailyCollectionProcessor()
        self.index_daily_collection_processor = IndexDailyCollectionProcessor()
        self.aic_daily_collection_processor = AICDailyCollectionProcessor()
        self.stock_ipo_collection = StockIpoCollectionProcessor()
        self.conv_bond_ipo_collection = ConcBondIpoCollectionProcessor()
        self.manager_daily_collection = ManagerDailyCollectionProcessor()
        self.hf_fund_daily_collection = HFFundDailyCollectionProcessor()

    def process_all(self, start_date, end_date):
        failed_tasks = []
        try:
            failed_tasks.extend(self.fund_daily_collection_processor.process())
            failed_tasks.extend(self.index_daily_collection_processor.process())
            failed_tasks.extend(self.aic_daily_collection_processor.process())
            failed_tasks.extend(self.stock_ipo_collection.process())
            failed_tasks.extend(self.conv_bond_ipo_collection.process())
            failed_tasks.extend(self.manager_daily_collection.process())
            failed_tasks.extend(self.hf_fund_daily_collection.process())

        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('unknown in view_data_processor')
        return failed_tasks
