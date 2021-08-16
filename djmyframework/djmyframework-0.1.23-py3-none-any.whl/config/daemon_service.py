# coding=utf-8
# 启动守护进程


# supervisord 管理设置 http://supervisord.org/configuration.html
INET_HTTP_SERVER_LISTEN = '0.0.0.0:19001'
INET_HTTP_SERVER_USERNAME = 'admin'
INET_HTTP_SERVER_PASSWORD = 'P@ssword'

DAEMON_SERVICE_MAP = {
        # "statistic"  : {"command": "python -u manage.py StatisticCron -c", "remark": "统计后台服务"},
        "ldap"       : dict(command="python3 -u manage.py ldap_server -p 13891",remark="ldap 服务器", off=True),
        "redis": dict(command="redis-server configfile/redis.conf", remark="redis 服务器", off=True),
        "asgi"       : dict(
                command="gunicorn asgi -c config/gunicorn_config.py -k uvicorn.workers.UvicornWorker --access-logfile - --error-logfile - ",
                stopsignal='TERM',
                remark="gunicorn asgi 服务"),

        "wsgi"       : dict(command="gunicorn wsgi -c config/gunicorn_config.py --access-logfile - --error-logfile - ",
                            stopsignal='TERM',
                            remark="gunicorn wsgi 服务", off=False),
        "celery_work": dict(command="celery -A config.celery_app worker -l info -E -c 2 -O fair  --purge ", # 在守护进程启动之前清除所有等待的任务,防止定时任务积压
                            stopsignal='TERM',
                            remark="Celery 工作服务", off=False, environment='DJANGO_ENV = "prod"'),
        "celery_beat": dict(command="celery -A config.celery_app beat -l info -S django",
                            stopsignal='TERM',
                            remark="Celery 定时任务", off=False, environment='DJANGO_ENV = "prod"'),
        "celery_flower": dict(command="celery -A config.celery_app flower -l info",
                            stopsignal='TERM',
                            remark="Celery 任务监控", off=True, environment='DJANGO_ENV = "prod"'),
}
