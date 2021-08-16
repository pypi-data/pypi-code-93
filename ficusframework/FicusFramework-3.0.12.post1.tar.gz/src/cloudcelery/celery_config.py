#-*-coding=utf-8-*-
from __future__ import absolute_import

# 中间件
#BROKER_URL = 'redis://localhost:6379/0'
# BROKER_URL = 'amqp://admin:admin@172.16.148.211:5672'

# 结果存储
#CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
# CELERY_RESULT_BACKEND = 'db+mysql://root:@localhost:3306/celery'

# 任务队列的名字
#CELERY_DEFAULT_QUEUE = '20013'

# 不提前缓存4个任务,收一个任务,做一个任务
CELERYD_PREFETCH_MULTIPLIER = 1

# 延迟进行ACK的确认,只有当任务结束(成功/失败)后,再进行ACK的确认.这样做的目的是避免执行器进行 PREFETCH.在我们的场景里面预取问题很大
CELERY_ACKS_LATE = True

# CELERYD_CONCURRENCY = 1     # 并发任务数

# 记录任务的开始状态 否则就只有PENDING状态.   并且这个状态只任务结束24小时内有效.
CELERY_TRACK_STARTED = True

CELERY_TASK_SEND_SENT_EVENT = True

CELERY_SEND_EVENTS =True

# 忽略执行的结果(不能配置成True,否则获取不了状态和结果)
CELERY_IGNORE_RESULT = False

# 异步任务
CELERY_IMPORTS = (
    "cloudcelery.CeleryOnRequest"
)