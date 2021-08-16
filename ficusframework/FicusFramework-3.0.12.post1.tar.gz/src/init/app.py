import logging
import sys

from flask import Flask
from flask_cors import *

import config
from config import annotation
from discovery import discovery_service_proxy

# 开始使用异步服务器启动 TODO 发现异步在message消息的情况下会异常退出,先不使用
# import gevent.monkey
# gevent.monkey.patch_all()

log = logging.getLogger('Ficus')

log.info("=======服务启动开始======")
app = Flask(__name__)
# 解决flask中文乱码
app.config['JSON_AS_ASCII'] = False
# 设置跨域
CORS(app, supports_credentials=True)

# 读取本地配置文件
from config.BootstrapPropertyLoader import load_properties_after_started, init_from_yaml_property, \
    init_from_environ_property, init_profile_from_environ_property

# 先从环境变量中获取profile
init_profile_from_environ_property()

init_from_yaml_property(sys.argv[0])
# 尝试从环境变量中获取 bootstrap里面的信息
init_from_environ_property()

log.info("服务启动,完成本地yaml配置文件读取")

# 注册信息到注册中心中
discovery_service_proxy().registry(server=config.eureka_default_zone,
                                   app_name=config.application_name,
                                   # 当前组件的主机名，可选参数，如果不填写会自动计算一个，如果服务和 eureka 服务器部署在同一台机器，请必须填写，否则会计算出 127.0.0.1
                                   instance_host=config.server_ip or config.find_host_ip(),
                                   instance_port=config.server_port or 5000,
                                   status_page_url="/actuator/info",
                                   health_check_url="/actuator/health",
                                   renewal_interval_in_secs=4,
                                   duration_in_secs=12)

log.info("服务启动,完成注册中心注册及心跳")

load_properties_after_started(sys.argv[0])

log.info("服务启动,完成配置中心配置文件读取")

# 这一行不能去掉,目的是引入flask的endpoints,并且位置需要在 app = Flask(__name__) 后面
# 引入views
from remote import remote

app.register_blueprint(remote, url_prefix='/')

log.info("服务启动,完成flask框架启动")

# 先加载registry.yml
import registry

registry.load_registry_properties(sys.argv[0], "registry.yml")
registry.load_algorithm_properties(sys.argv[0], "algorithms.yml")

# 加载规则引擎的配置
from rule_engine import RuleEngineInitialize

RuleEngineInitialize.initialize_from_remote()
log.info("服务启动,完成规则引擎的初始化")

# 加载Celery的框架东西
# 获取远程配置中的配置项.判断是否有规则引擎相关的配置
try:
    if annotation.get_value("${celery.enable:false}"):
        import cloudcelery

        log.info("服务启动,完成celery的预启动")
except:
    # 无所谓
    pass

# 预先加载根目录下的这个模块,这样才能在程序启动后,自动注册执行器
try:
    import handlers
except Exception as e:
    log.error(f"加载执行器实例错误:{str(e)}")
    exit(-1)  # 程序直接退出
log.info("服务启动,完成处理器的预加载")

# 程序启动后,判断是否需要注册执行器
from registry import LoadOnRegistryLoader, LoadOnAlgorithmLoader

LoadOnRegistryLoader.registry_after_started()
LoadOnAlgorithmLoader.registry_after_started()

log.info("服务启动,完成处理器的注册")

from schedule.utils.log.TaskLogCleanScheduler import TaskLogCleanScheduler

log_cleaner = TaskLogCleanScheduler()
log_cleaner.start()
log.info("服务启动,完成日期清理线程的启动")

log.info(f"服务启动:{config.server_ip or config.find_host_ip()}:{config.server_port or 5000}")
log.info("======服务启动完毕======")

from multiprocessing import Process


class CeleryProcess(Process):  # 继承Process类
    def __init__(self, name):
        super(CeleryProcess, self).__init__()
        self.name = name

    def run(self):
        import uuid
        argv = [
            'worker',
            '--loglevel=DEBUG',
            f'--hostname={config.actor_name}@{uuid.uuid4()}'
        ]
        import cloudcelery
        cloudcelery.celery.worker_main(argv)


def run_flask(celery_able=False):
    """
    单独启动flask
    :return:
    """
    if not celery_able:
        # 在非celery环境中,需要在主进程上启动监控
        # 这里要提前获取一次,便于提前加载和开启数据库连接以及FD的变化监听
        from factdatasource import FactDatasourceProxyService
        FactDatasourceProxyService.fd_client_proxy()
        log.info("服务启动,完成FD服务加载")

    from config import server_port
    from gevent import pywsgi
    # import gevent.monkey
    # gevent.monkey.patch_all()
    server = pywsgi.WSGIServer(('0.0.0.0', server_port), app)
    server.serve_forever()


def run_flask_with_celery():
    """
    启动flask和celery
    :return:
    """
    p2 = CeleryProcess('Celery')
    p2.start()

    run_flask(True)
    p2.join()


def run_with_auto_select():
    if annotation.get_value("${celery.enable:false}"):
        run_flask_with_celery()
    else:
        run_flask(False)
