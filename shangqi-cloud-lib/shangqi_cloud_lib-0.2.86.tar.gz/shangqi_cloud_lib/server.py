# -*- coding: utf-8 -*-
from typing import Optional

import tornado.ioloop
import tornado.web
import tornado.httpserver
import os
import importlib

import logging

from shangqi_cloud_lib.utils.FileUtil import read_yaml

import shangqi_cloud_lib.context as context
from shangqi_cloud_lib.context import config
# CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
import shangqi_cloud_lib.router as router


# 自动导入Handler
def auto_import(path, pkg_name):
    dynamic_handler_names = os.listdir(path)
    for handler_name in dynamic_handler_names:
        full_file = os.path.join(path, handler_name)
        if os.path.isdir(full_file):
            auto_import(os.path.join(path, handler_name), ".".join([pkg_name, handler_name]))
        if os.path.isfile(full_file) and handler_name.endswith(".py"):
            importlib.import_module("{}.{}".format(pkg_name, handler_name.replace(".py", "")))


def set_cfg(cfg):
    config_dict = {}
    if isinstance(cfg, str):
        config_dict = read_yaml(cfg)
    elif isinstance(cfg, dict):
        config_dict.update(cfg)
    elif str(type(cfg)) == '<class \'module\'>':
        for name in dir(cfg):
            if name.startswith("__"):
                continue
            if name not in config.keys():
                continue
            val = getattr(cfg, name)
            val_type = str(type(val))
            if val_type in ["<class 'module'>", "<class 'function'>", "<class 'type'>"]:
                continue
            config_dict[name] = val
    config.update(**config_dict)


# 应用实例
class WebServer:
    def __init__(self, cfg, post_init=None):
        set_cfg(cfg)
        self.context = context
        auto_import(config.handler_path, config.handler_path.replace(config.project_path, '')[1:])
        self.settings = {
            "static_path": config.static_path,
            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
            "cookie_secret": config.cookie_secret,
            "debug": True,
            "db":config.db
        }
        self.app = tornado.web.Application(
            router.router,
            **self.settings,
            autoreload=True
        )
        self.server = tornado.httpserver.HTTPServer(self.app, max_buffer_size=500 * 1024 * 1024)  # 500M
        self.init_log()
        if post_init:
            if isinstance(post_init, list):
                for func in post_init:
                    func()
            else:
                post_init()

    @staticmethod
    def init_log():
        log_config = {
            "level": 20,
            "format": "%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s"
        }

        logging.basicConfig(
            **log_config
        )

    def start(self, num_processes: Optional[int] = 1, max_restarts: int = None):
        self.server.listen(config.server_port)
        self.server.start(num_processes, max_restarts)
        logging.info(f"start server port : {config.server_port}")
        tornado.ioloop.IOLoop.current().start()
