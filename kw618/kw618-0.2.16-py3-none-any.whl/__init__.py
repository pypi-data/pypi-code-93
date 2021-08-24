"""
    导入顺序:
        0. 版本信息
        1. 常用固定路径
        2. 第三方依赖库
        3. 本pkg下的各个子包/子模块的所有全局namespace
        4. 添加外部脚本的常用路径到"默认搜索路径"
        5. 生成常用变量


    设计哲学:
        1. 注重internal结构: kw618的顶层namespace中, 会把所有子包中常用函数/类导入进来
        2. 不关心external环境: 很多在MyCode中可重复利用的脚本暂时不导入到本模块中.(用到时,自行导入)
           (但会提前加入"默认搜索路径", 可以方便任意路径导入函数/类)
        3. kw618会有两种形式存在:
            一是:本地编辑的代码
                主要应用场景: 本地. 优势:在本地可以快速调整, 快速响应
            二是:pypi服务器存储的已更新上传的代码
                主要应用场景: 阿里云服务器端(remote).
                    劣势:
                        1. 每次更新代码后都要更新上传pypi比较麻烦;(但毕竟remote, 在github上更新也挺麻烦)
                            (需要写一个shell脚本自动化更新上传)
                        2. 每次上传到pypi后, 需要在remote端重新更新kw618库  (pypi网络延迟比git可能更慢.)
                        eg代码:
                            python setup.py sdist bdist_wheel
                            twine upload dist/*
                            pip3 install --upgrade kw618
                            pip install -i https://pypi.org/simple  kw618 0.0.5  # 临时使用官方pypi源作为pip的下载源
                    优势: 比github上的版本控制要容易(0.0.4是完全覆盖0.0.3, 而不需要自己处理版本之间diff的问题)


    notes:
        1. 后续想把ziru除名! (ziru应该放在MyCode中的Libs中) (任何与代码有关的资源最好也放在这个目录中,便于调用)
            (巨型log除外) (巨型log会导致git版本控制的内容巨大)
        2. pandas 底下的包和模块绝对不能有"from kw618 import *"/ "import kw618"
            导入kw618只能在外部代码调用kw618库时候出现!! (内部代码不能使用, 否则会导致"循环导入")
            如果在某个脚本中需要"全平台通用路径":
                目前: from kw618._file_path import *
                        (此处以kw618打头, 不知道会不会存在循环导入的问题)
                        (pandas底下的core.frame模块也需要导入core.dtypes.common.is_dict_like)


    from kw618 import *
    (所需内存: 100mb)

"""

# 库包版本相关
from kw618._version import (
    __name__, __description__, __version__, __author__,
)


# 导入常用的固定路径(多平台通用)
from kw618._file_path import *

# 导入一些初始配置信息 (在kw618内的各种子模块都可能需要用到的信息) // 直接导入在子模块中不能使用, 还需要在子模块中单独导入...
from kw618.settings import *

# kw618库包中需要用到的所有第三方库 (这里是py脚本中使用import时候的名字, 与setup.py中的库名会有部分差异)
hard_dependencies = (
    # requests相关
    "sys", "os", "retry", "traceback", "pysnooper", "user_agent", "random", "requests",
    "threading", "multiprocessing", "scrapy", "urllib", "smtplib", "uuid", "email", "execjs",
    "copy", "exchangelib", "urllib3", "selenium",
    # pandas相关
    "numpy", "pandas", "math", "collections", "pymongo", "warnings",
    # pymongo相关
    "re", "json", "time", "pymongo", "redis",
    # pymysql相关
    "pymysql",
    # 定时任务相关
    "schedule", "csv",
    # python通用utils相关
    "functools",
    # 加密相关 (与setup.py中的库名会有部分差异)
    "Crypto",
    )

# 判断依赖包是否存在
missing_dependencies = []
for dependency in hard_dependencies:
    try:
        if dependency == "numpy":  # 1. 使用语句的方式import
            import numpy as np
        elif dependency == "pandas":
            import pandas as pd
        elif dependency == "warnings":
            import warnings
            warnings.filterwarnings("ignore")
        else:
            # __import__(dependency)  # 2. 使用函数方式import: 可以用str类型作为参数传入
            exec("import {}".format(dependency))
    except ImportError as e:
        missing_dependencies.append("{0}: {1}".format(dependency, str(e)))
if missing_dependencies:
    raise ImportError(
        "无法导入所需依赖包:\n" + "\n".join(missing_dependencies)
    )
del hard_dependencies, dependency, missing_dependencies



# 导入所有模块中的所有全局变量/函数/类
# (这些都是"kw618"这个 package namespace 底下的 API )
    ## 1. 第三方库封装模块
        ##### (pandas的__init__.py 中 即使要全部导入也是一个个导,不会使用*)
from kw618.k_pandas.utils_pandas import *
from kw618.k_pandas.utils_finance import *
from kw618.k_pymongo.utils_pymongo import *
from kw618.k_pymongo.utils_redis import *
# from kw618.k_pymongo.utils_redis import KwRedis as R
R = KwRedis()
from kw618.k_pymysql.utils_pymysql import *
from kw618.k_python.utils_python import *
from kw618.k_python.utils_img import *
# from kw618.k_requests import *
from kw618.k_requests.utils_requests import *
from kw618.k_requests.my_cookies import *
from kw618.k_requests.ocr import *
from kw618.k_requests.wyy import *
from kw618.k_requests.robust import *
# from kw618.k_finance.utils_quant import *
# from kw618.k_finance.quant_strategy import *
# from kw618.k_finance.quant_hc import *
# from kw618.k_finance.vnpy import *
# from kw618.k_finance.Arbitrage.binance_gateway import *
# from kw618.k_finance.Arbitrage.getData import *
# from kw618.k_finance.Arbitrage.calData import *
# from kw618.k_finance.Arbitrage.sendOrder import *
from kw618.k_finance.Arbitrage.sendOrder_simply import *

    ## 2. 工作相关模块
"把工作相关的模块在kw618中废除了!! 移至MyCode中的Libs中"
    ## 3. 添加常用本地路径到默认搜索路径
    ## 不直接导入函数/变量
    ## (会将 MyCode 目录下的重要文件夹添加到 python_path中)
    ## (当项目变得庞大了, 可能会出现同名Crawler项目, 需要单独在各自项目中添加) <toggle>
if os.path.exists(f"{FILE_PATH_FOR_MYCODE}"):
    sys.path.append(f"{FILE_PATH_FOR_MYCODE}")
    sys.path.append(f"{FILE_PATH_FOR_MYCODE}/BusinessProj")
    sys.path.append(f"{FILE_PATH_FOR_MYCODE}/PersonalProj")
"如果这里把Ziru的项目添加到python_path中, 容易在导入时候出现命名空间混乱!"
"(建议Ziru项目: 使用Ziru.Projects... 之类的绝对导入方式)"
# if os.path.exists(f"{FILE_PATH_FOR_ZIRU_CODE}"):
#     sys.path.append(f"{FILE_PATH_FOR_ZIRU_CODE}")
#     sys.path.append(f"{FILE_PATH_FOR_ZIRU_CODE}/Projects")
#     sys.path.append(f"{FILE_PATH_FOR_ZIRU_CODE}/Utils")
"又存在循环调用, 比较头疼....可能需要一个中间中转的脚本...api.py??"
"//k200215:为避免循环导入, 这里只添加默认搜索路径, 不直接在本模块导入函数和变量"



"导入通用变量/常量"
    ## 1. pandas
today_obj = pd.to_datetime("today")
today_date = today_obj.strftime("%Y-%m-%d") # 转成“2019-02-28”这样的str形式
this_time = today_obj.strftime("%X") # 转成“2019-02-28”这样的str形式
yesterday_obj = today_obj - pd.to_timedelta("1 d")
yesterday_date = yesterday_obj.strftime("%Y-%m-%d") # 转成“20190228”这样的str形式
df = pd.DataFrame({
        "key":["A", "B", "C", "A", "B", "C", "B", "A"],
        "data1":np.random.randint(5, 8, 8),
        "data2":np.random.randint(6, 9, 8),
        "data3":np.random.randint(1, 10, 8),
        "data4":range(8),
        },
        columns=["key", "data1", "data2", "data3", "data4"]
    )
df1 = pd.DataFrame({"col x":["class 1", "class 2", "class 3", "class 4"], "col y":["cat 1", "cat 2", "cat 3", "cal 4"]})

    # 只有kw618为本地项目的时候, 才有这些'测试'功能
if kw618_pkg == "Local":
    # 以后尽量避免用csv来获取'测试数据', 使用pandas创建'随机数据'更加科学
    df2 = import_data(in_file_path=f"{FILE_PATH_FOR_KW618}/k_pandas/df_test.csv")
    df3 = import_data(in_file_path=f"{FILE_PATH_FOR_KW618}/k_pandas/df_test2.csv") # 这里的kw618路径是动态的 (_file_path.py文件会自动寻址)




    ## 2. pymongo
        # [注意: pymongo的连接是'惰性连接', 当你真正展开它的生成器的时候, 才会真的进行连接操作. 有点像'列表生成式'的感觉] [pymysql会提前报错]
        # [所以, 即使远程mongo服务端没开, 在导入kw618时候并不能发现]
try:
        # 本地和remote的mongo我都没设置密码 //k0403: 被黑客黑了,必须添加密码!!
            # 1. 本地mongo
    client = pymongo.MongoClient(f'mongodb://kerwin:kw618@{HOST}:27017/')
    db = client["zufang_001"]
            # 2. 远程mongo
            # 把其他机子(包括docker)中的remote_db, 都设成阿里云服务器的地址
    if socket.gethostname() != "remote":
        remote_client = pymongo.MongoClient(f'mongodb://kerwin:kw618@{REMOTE_HOST}:27017/')
        remote_db = remote_client["zufang_001"]
except:
    print(k_tb(10))  ## except中, 可以呈现详细的报错信息
    print(
        "\n\n[kk警告]:  本地似乎没有mongo数据库, 建议正确安装mongo\n"
    )


# # mysql基本没用, 但是每次 from kw618 import * 时候, 都要等那么久, 很没有价值 [暂时先关掉吧, 完全不影响]
# # ====================================
#     # 3. mysql
#         # 1. 本地 mysql
# try:
#     conn = pymysql.connect(
#         host="localhost",
#         port=3306,
#         user="root",
#         password="kw618",
#         database="mysql",
#         charset="utf8")
#     cursor = conn.cursor(cursor=pymysql.cursors.DictCursor) # 每一行doc以字典形式呈现结果集, 如:{k1:v1, k2:v2, k3:v3}
#             ### pandas专用引擎
#             ### pd.to_sql()时候的con参数, 必须要使用这个engine, 而不能使用pymysql中的conn...!!
#     engine = create_engine('mysql+pymysql://root:kw618@localhost:3306/ttt_db?charset=utf8')
# except:
#     print(k_tb(10))  ## except中, 可以呈现详细的报错信息
#     print(
#         "\n\n[kk警告]:  本地似乎没有 mysql 数据库, 建议正确安装mysql\n"
#     )
#
#         # 2. 远程 mysql
# try:
#     if socket.gethostname() != "remote":
#         # pymysql
#         remote_conn = pymysql.connect(
#             host="120.55.63.193",
#             port=3306,
#             user="root",
#             password="kw618",
#             database="mysql",
#             charset="utf8"
#             )
#         remote_cursor = remote_conn.cursor(cursor=pymysql.cursors.DictCursor) # 每一行doc以字典形式呈现结果集, 如:{k1:v1, k2:v2, k3:v3}
#         # pandas专用引擎
#         remote_engine = create_engine('mysql+pymysql://root:kw618@120.55.63.193:3306/ttt_db?charset=utf8')
# except:
#     print(k_tb(10))  ## except中, 可以呈现详细的报错信息
#     print(
#         "\n\n[kk警告]:  远程似乎没有开启 mysql 服务, 建议正确开启mysql\n"
#     )




    ## 4. redis
r = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True) # 连接0号数据库
r0 = r
r1 = redis.StrictRedis(host="localhost", port=6379, db=1, decode_responses=True) # 连接1号数据库
r2 = redis.StrictRedis(host="localhost", port=6379, db=2, decode_responses=True) # 连接2号数据库
r9 = redis.StrictRedis(host="localhost", port=6379, db=9, decode_responses=True) # 连接9号数据库 (用做测试库!)

    ## 5. requests
req = myRequest().req



    ## 6. python 常用数据结构
d = {1:9, 2:88, 7:4, 99:3, "name":"kerwin", "age":26}
od = collections.OrderedDict(d)
lst = [1, 2, 3, 4, 5, 6, 7, 8]
obj = [{3:3, 4:4, 5:{2:4, 4:9}}, 111, 333, [{3:4}, 4, 5, [3, 4]]]





























##
