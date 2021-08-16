# -*- coding: utf-8 -*-

from phcli.ph_lmd.runtime.lambda_rt import LambdaRuntime


class GoRT(LambdaRuntime):
    pass
    # __runtime_name = "golang"
    #
    # def pkg_layer(self, data):
    #     """
    #     组织 layer 的打包逻辑
    #     :param data
    #         :arg is_pipenv: 是否使用的 pipenv 构建的项目，默认为 False
    #         :arg lib_path: 仅当 is_pipenv = False 时有效，指定 python 的 lib 位置
    #         :arg package_name: 打包的名称
    #     """
    #
    #     self._package_cmds = [
    #         "mkdir -p %s/%s" % (self._package_root, self.__runtime_name),
    #         ]
    #
    #     if data.get("is_pipenv", False):
    #         self._package_cmds.extend([
    #             "pipenv lock -r | grep '==' | awk -F '==' '{print $1}' |" +
    #             "xargs -I '{}' cp -r ${VIRTUAL_ENV}/lib/python3.8/site-packages/{} %s/%s/" % (
    #                 self._package_root, self.__runtime_name),
    #             ])
    #     else:
    #         self._package_cmds.extend([
    #             "cp -r %s/* %s/%s/" % (data["lib_path"], self._package_root, self.__runtime_name),
    #             ])
    #
    #     self._package_cmds.extend([
    #         "cd %s && zip -r -q ../package.zip . && cd -" % self._package_root,
    #         "rm -rf %s" % self._package_root,
    #         ])
    #
    #     self.package(data["package_name"])
    #
    # def pkg_code(self, data):
    #     """
    #     组织 code 的打包逻辑
    #     :param data
    #         :arg code_path: 需要打包的代码位置
    #         :arg package_name: 打包的名称
    #     """
    #
    #     self._package_cmds = [
    #         "zip -r package.zip %s" % data["code_path"],
    #         ]
    #
    #     self.package(data["package_name"])
