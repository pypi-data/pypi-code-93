# -*- coding: utf-8 -*-

from phcli.ph_lmd.runtime.lambda_rt import LambdaRuntime


class NodejsRT(LambdaRuntime):
    __runtime_name = "nodejs"

    def pkg_layer(self, data):
        """
        组织 layer 的打包逻辑
        :param data
            :arg lib_path: 指定 nodejs 的 lib 位置
            :arg package_name: 打包的名称
        """

        self._package_cmds = [
            "rm -rf %s" % (data["lib_path"]),
            "npm install --production",
            "mkdir -p %s/%s/node_modules" % (self._package_root, self.__runtime_name),
            "cp -r %s/* %s/%s/node_modules/" % (data["lib_path"], self._package_root, self.__runtime_name),
            "cd %s && zip -r -q ../package.zip . && cd -" % self._package_root,
            "rm -rf %s" % self._package_root,
        ]

        self.package(data["package_name"])

    def pkg_code(self, data):
        """
        组织 code 的打包逻辑
        :param data
            :arg name: 项目名称
            :arg code_path: 需要打包的代码位置
            :arg package_name: 打包的名称
        """

        self._package_cmds = [
            "mkdir -p %s/%s" % (self._package_root, self.__runtime_name),
            "npm i",
            "npm run build",
        ]

        for path in data["code_path"].split(","):
            if path.endswith("/"):
                path = path[:-1]
            self._package_cmds.append("cp -r %s %s/%s/" % (path, self._package_root, self.__runtime_name))

        if "name" in data.keys():
            self._package_cmds.extend([
                "mv %s/%s/config/project/%s.yml %s/%s/config/server.yml" % (self._package_root, self.__runtime_name, data['name'], self._package_root, self.__runtime_name),
                "rm -rf %s/%s/config/project/" % (self._package_root, self.__runtime_name)
            ])

        self._package_cmds.extend([
            "cd %s/%s && zip -r -q ../../package.zip . && cd -" % (self._package_root, self.__runtime_name),
            "rm -rf %s" % self._package_root,
        ])

        self.package(data["package_name"])
