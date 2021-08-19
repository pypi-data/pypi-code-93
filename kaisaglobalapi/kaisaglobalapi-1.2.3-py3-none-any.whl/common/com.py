# -*- coding:utf-8 -*-

# ===================================================================
# This file is used to store all paths and URLs in the interface document
# KaisaGlobal rights are reserved.
# ===================================================================


"""
This code provide utils function for KaisaGlobal-Open.
developed by KaisaGlobal quant team.
2021.03.02
"""
appendIpAddress = "192.168.1.1"
# appendIpAddress = None
OPENIP = '120.78.227.40'
OPENPORT = 28880
PHONEMODEL = 'Windows 10'
PLATFORM = 'Windows'
SRVTYPE = 'open'
EP = ''
SYSVERSION = '1.3.0'

##########################################
#### pro
# REAL ENV.
KAISA_ROOT_URL_REAL = "kgl.jt00000.com"

KAISA_ROOT_URL = KAISA_ROOT_URL_REAL
##########################################

# KAISA_ROOT_URL = KAISA_ROOT_URL_SIM
KAISA_ROOT_URL_API = "openapi.jt00000.com"

# # AUTHENTICA_URL = "https://openapi.jt00000.com"

## pro
CRYPTO_RSA_URL = "https://__kaisarooturl__/kgl-third-authorization/crypto/key/RSA"

## pro
AUTHENTICA_URL = "https://__kaisarooturl__/kgl-third-authorization/oauth/token"

## userid-pro
AU_USERID_URL = 'https://__kaisarooturl__/kgl-user-center/userRegInfo/selectLoginUserInfo'
QUOTE_URL = "https://kgl.jt00000.com/hq"

REST_DATA_HOST = "https://__kaisarooturl__/dzApp/dzHttpApi"

TRADE_CRYPTO_RSA_URL = "https://__kaisarooturl__/kgl-trade-service/crypto/key/RSA"
ClientByMobile_URL = "https://__kaisarooturl__/kgl-user-center/userOaccAccount/selectClientIdByMobile"
REST_HOST = "https://__kaisarooturl__/kgl-trade-service"
WEBSOCKET_TRADE_HOST = "wss://__kaisarooturl__/kgl-trade-push-service/ws"

openapi_scope = "wthk"
openapi_scope = "read"

# 港股tick历史数据URL
HK_STOCK_TICK_POST_URL = 'https://__kaisarooturl__/kgl-stock-support-provider/stock/quote/tickHistory/v2'
# 港股KLine历史数据URL
HK_STOCK_KLINE_POST_URL = 'https://__kaisarooturl__/kgl-stock-support-provider/quoteInfo/kLineHistory/v2'
# 港股盘口十档历史数据URL
HK_STOCK_LEVEL2_10_ORDER_URL = 'https://__kaisarooturl__/kgl-stock-support-provider/quoteInfo/orderBuySellHisList/v2'
# 港股经纪人历史数据URL
HK_STOCK_BROKER_URL = 'https://__kaisarooturl__/kgl-stock-support-provider/quoteInfo/brokerHisList/v2'


# 基础财务指标URL, Post
BASIC_FIN_POST_URL = "https://__kaisarooturl__/kgl-glidata-center/stockReport/finReport"
# 衍生财务指标URL，Post
EX_FIN_POST_URL = "http://__kaisarooturl__/kgl-stock-front-stoacq/openapi/financial/factor"
# 基础/衍生技术面因子URL，Post
BE_TECH_POST_URL = "http://__kaisarooturl__/kgl-stock-front-stoacq/openapi/stock/techindex"

START_PUSH = 200
STOP_PUSH = 201
SYNCHRONIZE_PUSH = 250
QUERY_HISTORY = 36
QUERY_CONTRACT = 52
ON_TICK = 251
ON_MARKETDATA = 153
PING = 2
PONG = 3
LOGIN = 10
HKSE_MARKET = 2002

CREATION = 101
UPDATE = 102
TRADE = 103
CANCELLATION = 104
ACCOUT = 106
POSITION = 105


#########################公共Error返回值
PUB_SMALLENDDATE_ERROR = '您好,检测到end_date比start_date要小哟,请修正后重新请求数据!'
PUB_DATENONE_ERROR = '您好,检测到end_date和start_date都为None,请修正后重新请求数据!'
PUB_WRONG_MSG_ERROR = "您好!您输入的参数有误, 请纠正后重新输入!"
PUB_ONLY_LIST_TYPE_ERROR = '请传入list类型的code_list字段'
PUB_WRONG_DATE_AROUND_ERROR = '您好, 检测到时间区间的存在问题, 导致取到的数据为空, 请修改时间后重新请求数据.'
PUB_HELLO = '您好'
PUB_SOR = '抱歉'
#########################公共Error返回值



############################ KaisaHistQuoteData接口
########################### 一般常量
QUOTE_TYPE_DICT_ORI = {"1m": 1, "3m": 2, "5m": 3, "10m": 4, "15m": 5, "30m": 6, "1h": 7, "2h": 8, "4h": 9,
                       "1d": 10, "5d": 11, "1w": 12, "1M": 13, "1q": 14, "1y": 15}
ORI_DATA_TYPE_LIST = ['Kline', 'ticker', 'broker', 'level10']
HistQuote_MARKET_DICT = {1: 'CN', 2: 'HK', 3: 'US'}
K_QUOTE_TYPE_DICT = {"1m": 1, "1d": 10}
Quote_MARKET_DICT = {1: 'CN', 2: 'HK', 3: 'US'}
FRE_PRE_DICT = {'pre': '1', 'post': '2', 'None': '0'}

## 订阅的数据类型
SUB_QUOTE_TYPE = {'SUB_TYPE_NONE': 0, 'QUOTE': 1, 'TICK': 2, 'BROKER': 3, 'ORDER': 4}
QUOTE = 1   ## 盘口行情数据
TICK = 2    ## 逐笔行情数据
BROKERS = 3  ## 经纪商行情数据
LEVEL_ORDER = 4   ## 盘口十档行情数据
ALLDATAIDLIST=[1, 2, 3, 4]
PROTODATADIC = {1: 'QUOTE', 2: 'TICK', 3: 'BROKER', 4: 'ORDER'}
#################################################

KLINE = 'Kline'
KLINE_ORI_COLS = ['assetId', 'open', 'low', 'high', 'close', 'volume', 'amount', 'timestamp']
KLINE_RES_COLS = ['code', 'open', 'high', 'low', 'close', 'volume', 'money', 'trading_day']
KLINE_TIMESTAMP = 'timestamp'
KLINE_TRADEDATE = 'trading_day'
TICKER = 'ticker'
TICKER_ORI_COLS = ['assetId', 'now', 'curVolume', 'amount', 'tickFlag', 'tickVi', 'quoteTime']
TICKER_RES_COLS = ['code', 'last_price', 'volume', 'money', 'tick_order_type', 'tick_trade_type', 'quote_time']
BROKER = 'broker'
BROKER_ORI_COLS = ['assetId', 'brokerIdList', 'flag', 'level', 'brokerTime']
BROKER_RES_COLS = ['code', 'broker_id_list', 'direction', 'level', 'broker_time']
LEVEL10 = 'level10'
LEVEL10_ORI_COLS = ['assetId', 'price', 'flag', 'volume', 'brokerCount', 'level', 'quoteTime']
LEVEL10_RES_COLS = ['code', 'price', 'direction', 'volume', 'broker_count', 'level', 'quote_time']

############################ KaisaHistQuoteData接口里的Error异常备注##############################
MORECODES_ERROR = "您好, ticker接口限定每次只能拉取一个合约的数据, 请修改(如: code_list=['00700'])参数后重新请求!"
LOSSCODES_ERROR = '您好, 请填写您要获取数据的合约代码!'
ONLY_HK_MARKET_ERROR = '您好,接口暂时不提供美股/A股的数据哟,我们会马不停蹄的加班,尽快把数据补全!'
DATETYPE_ERROR = "您好, 请正确填写您要提取数据的参数, 如: data_type='Kline'"
OUTDATEFOR10_ERROR = '您好,单只股票,接口一次最多只能提供10年的数据哟,如果需要更多的数据,请分段获取!'
OUTDATEFOR1MON_ERROR = '您好,多只股票,接口一次最多只能提供1个月的数据哟,如果需要更多的数据,请分段获取!'
WRIONGUNIT_ERROR = "您好, 检测到您填写的unit参数不在允许范围内,参考:unit: '1m' or '1d'!"
FRE_ERROR = "您好, 请正确填写是否复权参数, 如: fre='pre'"
ONEDAYUPDATE_ERROR = '接口一次最多只能提供1个交易日的数据哟,如果需要更多的数据,请分段获取!'
#FIN_DATENONE_ERROR = '您好,检测到end_date和start_date都是None,请修正后重新请求数据!'

############################ KaisaHistQuoteData接口里的Error异常备注##############################

######################### KaisaHistQuoteData接口


############################ KaisaFinaData接口备注##############################
########################### 一般常量
FIN_MARKET_TYPE_DICT = {1: 'chn', 2: 'hkg', 3: 'usa'}
BASE_FACE = 'baseFace'
PROFIT = 'profit'
CASHFLOW = 'cashFlow'
OPERATION = 'operation'
DEBTPAY = 'debtPay'
GROWTH = 'growth'


############################ KaisaFinaData接口里的Error异常备注##############################
FIN_NOE_CODE_ERROR = '您好,该财务数据接口只允许获取单个合约的数据喔'
FIN_LOSS_CODE_ERROR = '您好, 请填写code字段！'

############################ KaisaFinaData接口里的Error异常备注##############################


############################ KaisaFinaData接口备注##############################


############################ KaisaTechData接口备注##############################

############################ KaisaTechData接口ERROR##############################
TECH_ONLY_DAY_DATA_ERROR = '您好,接口暂时不提供日级别以外的数据哟,我们会马不停蹄的加班,尽快把分钟、周和月级别的数据补全!'
TECH_ONLY_1_YEAR_DATA_ERROR = '您好,技术指标接口一次最多只能提供1年的数据哟,如果需要更多的数据,请分段获取!'
############################ KaisaTechData接口ERROR##############################

############################ KaisaTechData接口备注##############################