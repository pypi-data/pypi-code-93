# -*- coding: utf-8 -*-
"""爬虫配置文件"""
import os


# MYSQL
MYSQL_IP = "localhost"
MYSQL_PORT = 3306
MYSQL_DB = "feapder"
MYSQL_USER_NAME = "feapder"
MYSQL_USER_PASS = "feapder123"

# REDIS
# IP:PORT
REDISDB_IP_PORTS = "localhost:6379"
REDISDB_USER_PASS = ""
REDISDB_DB = 0

ITEM_PIPELINES = [
    "pipelines.Pipeline",
    # "feapder.pipelines.mysql_pipeline.MysqlPipeline",
    # "feapder.pipelines.mongo_pipeline.MongoPipeline",
]

# # 爬虫相关
# # COLLECTOR
COLLECTOR_SLEEP_TIME = 1 # 从任务队列中获取任务到内存队列的间隔
COLLECTOR_TASK_COUNT = 100 # 每次获取任务数量
#
# # SPIDER
SPIDER_THREAD_COUNT = 1 # 爬虫并发数
# SPIDER_SLEEP_TIME = 0 # 下载时间间隔（解析完一个response后休眠时间）
# SPIDER_MAX_RETRY_TIMES = 100 # 每个请求最大重试次数

# # 重新尝试失败的requests 当requests重试次数超过允许的最大重试次数算失败
# RETRY_FAILED_REQUESTS = False
# # request 超时时间，超过这个时间重新做（不是网络请求的超时时间）单位秒
# REQUEST_LOST_TIMEOUT = 600  # 10分钟
# # 保存失败的request
# SAVE_FAILED_REQUEST = True
#
# # 下载缓存 利用redis缓存，由于内存小，所以仅供测试时使用
# RESPONSE_CACHED_ENABLE = False  # 是否启用下载缓存 成本高的数据或容易变需求的数据，建议设置为True
# RESPONSE_CACHED_EXPIRE_TIME = 3600  # 缓存时间 秒
# RESPONSE_CACHED_USED = False  # 是否使用缓存 补采数据时可设置为True
#
# WARNING_FAILED_COUNT = 1000  # 任务失败数 超过WARNING_FAILED_COUNT则报警
#
# # 爬虫初始化工作
# # 爬虫是否常驻
# KEEP_ALIVE = True
#
# # 设置代理
# PROXY_EXTRACT_API = None  # 代理提取API ，返回的代理分割符为\r\n
# PROXY_ENABLE = True
#
# # 随机headers
# RANDOM_HEADERS = True
# # requests 使用session
# USE_SESSION = False
#
# # 去重
# ITEM_FILTER_ENABLE = False # item 去重
# REQUEST_FILTER_ENABLE = False # request 去重
#
EXPORT_DATA_MAX_FAILED_TIMES = 1 # 导出数据时最大的失败次数，包括保存和更新，超过这个次数报警
EXPORT_DATA_MAX_RETRY_TIMES = 1 # 导出数据时最大的重试次数，包括保存和更新，超过这个次数则放弃重试
# # 报警
DINGDING_WARNING_URL = "https://oapi.dingtalk.com/robot/send?access_token=1c1906f63aeed6cadddf45dbf95856515891e437e6b2e78058ff8564405002ef"  # 钉钉机器人api
DINGDING_WARNING_PHONE = "13811037553"  # 报警人 支持列表，可指定多个
WARNING_INTERVAL = 3600
# EMAIL_SENDER = "feapder@163.com"  # 发件人
# EMAIL_PASSWORD = "YPVZHXFVVDPCJGTH"  # 授权码
# EMAIL_RECEIVER = "564773807@qq.com"  # 收件人 支持列表，可指定多个
# # 时间间隔
# WARNING_INTERVAL = 3600  # 相同报警的报警时间间隔，防止刷屏
# WARNING_LEVEL = "DEBUG"  # 报警级别， DEBUG / ERROR
# EMAIL_SMTPSERVER="smtp.163.com"
# LINGXI_TOKEN = "" # 灵犀报警token
#
# LOG_NAME = os.path.basename(os.getcwd())
# LOG_PATH = "log/%s.log" % LOG_NAME  # log存储路径
# LOG_LEVEL = "DEBUG"
# LOG_IS_WRITE_TO_FILE = False
# OTHERS_LOG_LEVAL = "ERROR"  # 第三方库的log等级

INFLUXDB_HOST = os.getenv("INFLUXDB_HOST", "localhost")
INFLUXDB_PORT = int(os.getenv("INFLUXDB_PORT", 8086))
INFLUXDB_UDP_PORT = int(os.getenv("INFLUXDB_UDP_PORT", 8089))
INFLUXDB_USER = "root"
INFLUXDB_PASSWORD = "root"
INFLUXDB_DATABASE = "feapder"
# 监控数据存储的表名，爬虫管理系统上会以task_id命名
INFLUXDB_MEASUREMENT = "task_23"
METRICS_OTHER_ARGS = dict(retention_policy_duration="180d", emit_interval=60, debug=True)