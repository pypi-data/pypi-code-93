from kw618 import *

pd.set_option('display.float_format',lambda x : '%.4f' % x) # 所有数值列都保留3位小数来呈现
pd.set_option('display.max_columns', None)

ba = BinanceAccount(settings=LSH_BINANCE_SETTING)
df = ba.get_maxProfit_df()
print(df[:50])
# print(df[50:100])










#
