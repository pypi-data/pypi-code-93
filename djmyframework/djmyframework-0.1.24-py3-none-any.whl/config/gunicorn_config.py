# -*- coding: utf-8 -*-
# @Time    : 2019-02-27 12:16
# @Author  : xzr
# @File    : gunicorn_config.py
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : gunicorn配置
#

# http://docs.gunicorn.org/en/latest/settings.html#worker-connections
import multiprocessing

LOGS_DIR = 'logs'
loglevel = 'INFO'

bind = "0.0.0.0:8000"
# pidfile = "tmp/gunicorn.pid"

# 将stdout / stderr重定向到errorlog中的指定文件
capture_output = True
errorlog = '-'  # '"%s/gunicornd.log" % LOGS_DIR
accesslog = errorlog
# 通过启动脚本控制daemon模式,配合在supervisord监控
daemon = False
workers = multiprocessing.cpu_count() + 1

worker_class = 'sync'
threads = workers * 4

# worker_class = 'egg:meinheld#gunicorn_worker'

# use gunicorn asgi
# worker_class ='uvicorn.workers.UvicornWorker'
# worker_class ='uvicorn.workers.UvicornH11Worker'

max_requests = 10000
max_requests_jitter = 100

# https://stackoverflow.com/questions/27687867/is-there-a-way-to-log-python-print-statements-in-gunicorn
# enable_stdio_inheritance = True
raw_env = ["PYTHONUNBUFFERED=TRUE"]
