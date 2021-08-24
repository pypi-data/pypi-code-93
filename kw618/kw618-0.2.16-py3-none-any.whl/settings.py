
"""
    function: kw618在导入各种子模块之前, 需要设置的初始配置信息 (可用于子模块)
"""

# 导入常用的固定路径(多平台通用)
from kw618._file_path import *

import logging

# 1. 创建logger和handler
logger = logging.getLogger("logger")
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(filename=f"{FILE_PATH_FOR_HOME}/log/test.log")

# 2. 设置level
    # DEBUG, INFO, WARNING, ERROR, CRITICAL (分别是10, 20, 30, 40, 50)
logger.setLevel(logging.DEBUG) # 指的是: 最低能支持什么级别的打印输出
# logger.setLevel(logging.WARNING) # 指的是: 最低能支持什么级别的打印输出
stream_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.WARNING)

# 3. 设置log的输出格式
formatter = logging.Formatter("%(asctime)s [%(levelname)s]:  %(message)s") # 其他格式见上面的url
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 4. 把handler添加进logger
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

# =========================
# logger.setLevel(logging.INFO) # 如果想要让某个脚本运行时, console不打印debug信息, 则可以修改logger的级别












#
