from enum import Enum

from ctlml_commons.entity.focus.focus import Focus


class PeriodColumns(Enum):
    ID = 'id'
    LOW = 'low'
    HIGH = 'high'
    OPEN = 'open'
    CLOSE = 'close'
    WEIGHTED_AVERAGE = 'weightedAverage'
    VOLUME = 'volume'
    BASE_PRICE = 'basePrice'
    BASE_PRICE_BIN = 'basePriceBin'

    def __init__(self, column_name):
        self.column_name = column_name


class BinColumns(Enum):
    BIN_ID = 'binId'
    AGG_VOLUME = 'aggVolume'
    LAST_PREVIOUS_BIN_ID = 'recentStrongestBinId'
    CONTAINS_BUY_ORDER = 'containsBuyOrder'

    OLD_LAST_AGG_VOLUME = 'oldLastAggVolume'
    OLD_LAST_MAX_VOLUME = 'oldLastMaxVolume'
    OLD_LAST_BASE_PRICE = 'oldLastBasePrice'
    OLD_ONE_BEFORE_LAST_AGG_VOLUME = 'oldOneBeforeLastAggVolume'
    OLD_ONE_BEFORE_LAST_MAX_VOLUME = 'oldOneBeforeLastMaxVolume'
    OLD_PERIOD_START = 'oldPeriodStart'
    OLD_PERIOD_END = 'oldPeriodEnd'
    OLD_BASE_SCORE = 'oldBaseScore'

    NEW_LAST_AGG_VOLUME = 'newLastAggVolume'
    NEW_LAST_MAX_VOLUME = 'newLastMaxVolume'
    NEW_LAST_BASE_PRICE = 'newLastBasePrice'
    NEW_ONE_BEFORE_LAST_AGG_VOLUME = 'newOneBeforeLastAggVolume'
    NEW_ONE_BEFORE_LAST_MAX_VOLUME = 'newOneBeforeLastMaxVolume'
    NEW_PERIOD_START = 'newPeriodStart'
    NEW_PERIOD_END = 'newPeriodEnd'
    NEW_BASE_SCORE = 'newBaseScore'

    def __init__(self, column_name):
        self.column_name = column_name


class BrokenSupportsStrategy(Focus):
    pass


if __name__ == '__main__':
    p = PeriodColumns.WEIGHTED_AVERAGE
    print(p)
    print(p.column_name)

    print(BinColumns.CONTAINS_BUY_ORDER)
    print(BinColumns.CONTAINS_BUY_ORDER.column_name)
