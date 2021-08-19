from enum import Enum
class condition(Enum):
 epsGrowth = "epsGrowth"
 listedShare = "listedShare"
 pe = "PE"
 peg = "PE/G"
 de = "de"
 interestBearingDebt = "interestBearingDebt" 
 cash = "cash"
 price = "price"
 equity = "equity"
 stockRepurchases = "stockRepurchases"
 cashPerShare = "cashPerShare"


class IndicatorIndustrial(Enum):
    NetProfit = "NetProfit"
    Sales = "Sales" 