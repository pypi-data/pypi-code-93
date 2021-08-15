from eagle.eagle_heart.data_classes import StockDataBuilder, StockGroupDataBuilder
from eagle.paw import *

vn30_tickers = list_stock_from_group("vn30")
print(vn30_tickers)

all_data = get_cophieu68_data()
all_data = reformat_data(all_data, source='COPHIEU68')

stock_data_builders = []
for ticker in vn30_tickers:
    print(ticker)
    data = extract_stock_from_cophieu68(all_data, ticker)
    stock_data_builder = StockDataBuilder(data, ticker)
    stock_data_builder.present()
    stock_data_builders.append(stock_data_builder)

stock_group_data_builders = StockGroupDataBuilder(stock_data_builders)
stock_group_data_builders.present()
stock_group_data_builders.to_csv("pnl_VN30.csv")


## test single
# ticker = "VRE"
# data = extract_stock_from_cophieu68(all_data, ticker)
# print(data)
# stock_data_builder = StockDataBuilder(data, ticker)
# stock_data_builder.present()
# stock_data_builder.to_csv("pnl_VRE.csv")
