# -*- coding: utf-8 -*-

from abc import abstractmethod
import os

from phcli.ph_logs.phLogs.ph_logs import phlogger
from phcli.ph_errs.ph_err import PhException


class LambdaRuntime(object):
    """
    封装 AWS Lambda 各个运行时的的常规操作和抽象方法
    """

    _package_root = ".package"
    _package_cmds = []

    @abstractmethod
    def pkg_layer(self, data):
        pass

    @abstractmethod
    def pkg_code(self, data):
        pass

    def package(self, package_name):
        """
        执行打包逻辑
        :param package_name 打包的名称
        """

        if not isinstance(self._package_cmds, list):
            raise PhException('Expected an list')

        self._package_cmds.extend([
            "mv package.zip %s" % package_name,
        ])

        try:
            for cmd in self._package_cmds:
                phlogger.info("正在执行: " + cmd + " ")
                os.system(cmd)
        except Exception as ex:
            phlogger.error(ex)
