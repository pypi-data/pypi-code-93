# -*- coding: utf-8 -*-
from pkgutil import walk_packages
from importlib import import_module
from flask import Flask, request
from . import stacker, redis, db, celery, rq
from flask import _app_ctx_stack
from inspect import ismodule
from xloger.vendors import FlaskXLoger
from sys import exc_info
import inspect
# from deprecation import deprecated
import logging
import time

DEFAULT_APP_NAME = "application"

_vars = {"app": None, "config": {}, "db": None}


def get_exc_traceback(trace):
    if hasattr(trace, "tb_next") and trace.tb_next:
        return get_exc_traceback(trace.tb_next)

    trace = {
        "line": trace.tb_lineno,
        "file": inspect.getfile(trace.tb_frame)
    }
    return trace


def create_app(config, app_name=None):
    if app_name is None:
        app_name = DEFAULT_APP_NAME
        if isinstance(config, object):
            app_name = getattr(config, "APP_NAME", DEFAULT_APP_NAME)
        
    app = Flask(app_name)
    if config is None:
        return app
    _vars['app'] = app
    _app_ctx_stack.push(app.app_context())
    app.url_map.strict_slashes = app.config.get("URL_MAP_STRICT_SLASHES", False)
    configure_app(app, config)
    configure_db(app)
    configure_redis(app)
    # configure_celery(app)
    # configure_rq(app)
    # configure_models(app)
    FlaskXLoger(app, disabled=not app.config.get("XLOGER_ENABLED", False))
    #configure_blueprints(app)
    configure_handler(app)
    return app


def configure_handler(app):
    gunicorn_error_handlers = logging.getLogger('gunicorn.error').handlers
    app.logger.handlers.extend(gunicorn_error_handlers)

    @app.errorhandler(Exception)
    def server_internal_error(e):
        info = exc_info()
        message = e.__repr__()
        trace = get_exc_traceback(info[2])
        if app.config.get("DEBUG"):
            message = "%s in %s on line %d" % (message, trace['file'], trace['line'])
        app.logger.error(message)
        return message, 500


# ------------
# 应用配置文件
def configure_app(app, config=None):
    # config 不为空时覆盖配置
    if config is not None:
        app.config.from_object(config)
    # 映射配置
    _vars['config'] = app.config
    stacker['app'] = app


def configure_db(app):
    """
    数据库连接初始化

    :config SQLALCHEMY_POOL_RECYCLE: 连接池生命周期
    :config SQLALCHEMY_POOL_TIMEOUT: 连接池超时
    :config SQLALCHEMY_BINDS: 数据库连接配置, 可配置多个key=>value的配置

    :param app:
    :return:
    """
    app.config.setdefault("CACHE_LIFE_TIME", 600)
    db.init_app(app)


def configure_redis(app):
    """
    Redis 配置, 需要configs.py中的Redis参数

    :config REDIS: (host, port, database)

    :param app:
    :return:
    """
    max_connections = app.config.get("REDIS_MAX_CONNECTIONS", None)
    redis.init_app(app, max_connections=max_connections)


def configure_celery(app):
    celery.main = app.name
    celery.conf.update(app.config.get("CELERY", dict()))
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    app.celery = celery


def configure_rq(app):
    rq.init_app(app)


# def configure_clients(app):
#     try:
#         import clients
#     except ImportError:
#         return
#
#     for loader, name, is_pkg in walk_packages(clients.__path__):
#         import_module(clients.__name__ + '.' + name)
#         client_module = getattr(clients, name)
#         setattr(clients, name, getattr(client_module, name))


# 注册蓝图(Route)
def configure_blueprints(app):
    import blueprints

    @app.before_request
    def before_request():
        request.timestamp = time.time()

    prints = []
    for loader, name, is_pkg in walk_packages(blueprints.__path__):
        import_module(blueprints.__name__ + '.' + name)

    for name, blue in blueprints.__dict__.items():
        if not ismodule(blue):
            continue
        if hasattr(blue, "blueprint"):
            prints.append((blue.blueprint, getattr(blue, "url_prefix", None)))

    for blue, url_prefix in prints:
        app.register_blueprint(blue, url_prefix=url_prefix)


def configure_models(app):
    import models
    for loader, name, is_pkg in walk_packages(models.__path__):
        import_module(models.__name__ + '.' + name)
        module = getattr(models, name)
        model = getattr(module, name, None)
        if model is None:
            raise ImportError("class %s not found in %s" % (name, module.__file__))
        setattr(models, name, model)


# 获取app配置
def get_config():
    return _vars['config']


# 获取app配置
def get_app():
    return _vars['app']


def get_db():
    return db


# 多数据库时, 取到指定数据库连接
def get_db_engine(bind):
    db = get_db()
    app = get_app()
    return db.get_engine(app, bind)


# 初始化数据库
def init_db():
    """
    数据库初始化
    - 未创建表的模型会自动创建数据表
    - 已存在的表, 不会自动更新字段信息

    :return:
    """
    db = get_db()
    db.create_all()
