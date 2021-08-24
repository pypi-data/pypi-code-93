# -*- coding: utf-8 -*-

import os
import sys

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(r'../../'))

from hagworm.extend.logging import LogFileRotator
from hagworm.frame.tornado.base import Launcher

from routing import router
from setting import ConfigDynamic
from service.base import DataSource


def main():

    Launcher(
        router,
        ConfigDynamic.Port,
        process_num=ConfigDynamic.ProcessNum,
        on_startup=DataSource.initialize,
        on_shutdown=DataSource.release,
        debug=ConfigDynamic.Debug,
        gzip=ConfigDynamic.GZip,
        template_path=r'view',
        cookie_secret=ConfigDynamic.Secret,
        log_level=ConfigDynamic.LogLevel,
        log_file_path=ConfigDynamic.LogFilePath,
        log_file_rotation=LogFileRotator.make(ConfigDynamic.LogFileSplitSize, ConfigDynamic.LogFileSplitTime),
        log_file_retention=ConfigDynamic.LogFileBackups,
    ).start()


if __name__ == r'__main__':

    main()
