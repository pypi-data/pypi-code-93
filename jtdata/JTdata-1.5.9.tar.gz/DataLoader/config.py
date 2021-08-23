
import os
import platform
from datetime import datetime

if(platform.system()=='Windows'):
    print('Windows系统')
    data_path = os.path.join("Z:\\","qtDOperation","Jtjjdata","data")
    # data_path = r"D:\VS-Code-python\TLik\data"
elif platform.system()=='Linux':
    print('Linux系统')
    data_path = os.path.join("/mnt/z/","qtDOperation","Jtjjdata","data")
    

provider_config = {
    "TDP": "TradeDayInfoProvider",
    "BP": "LocalPorvider",
    "IdxSP": "LocalIndexStatusProvider",
    "InstSP": "LocalInstStatusProvider",
    "InduSP": "LocalIndustryMemberProvider",
    "FRP": "LoacalFincReportsProvider",
    "FuRP": "LoacalFundReportsProvider",
    "CDP": "LoacalConsusProvider"
}

stk_uiverse = { "sz380":'000009.SH',  # 上证380
                "sz50" :'000016.SH',  # 上证50
                "zz1000":'000852.SH',  # 中证1000
                "zz100":'000903.SH',  # 中证100
                "zz200":'000904.SH',  # 中证200
                "zz500":'000905.SH',  # 中证500
                "zz800":'000906.SH',  # 中证800
                "zxidx":'399005.SZ',  # 中小板指
                "cyidx":'399006.SZ',  # 创业板指
                "sz300":'399007.SZ',  # 深圳300
                "zx300":'399008.SZ',  # 中小300
                "hs300":'399300.SZ',  # 沪深300
                "zzall":'399985.SZ'}  # 中证全指

defualt_start_date = 20070104
defualt_end_date = int(datetime.now().strftime("%Y%m%d"))