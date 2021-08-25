from __future__ import absolute_import
from __future__ import unicode_literals

import os
from laipvt.sysutil.util import path_join, run_local_cmd, to_object, status_me
from laipvt.helper.exception import Forbidden, HandlerError
from laipvt.helper.errors import PackageErrors, Error
from laipvt.handler.confighandler import PvtAdminConfigHandler, ServiceConfigHandler


"""
        目录结构
        授权id.tar.gz
          |- pvtadmin.json
          |- kubernetes.tar.gz
            |- templates/
              |- admin.tmpl
            |- plugin/
              |- network/
                  |- flannel.yaml
                  |- calico.yaml
              |- helm/
                  |- bin/
              |- istio/
                  |- bin/
                  |- istio.yaml
          |- middleware.tar.gz
            |- mysql/
                |- xxx.tmpl (docker-compose文件)
                |- nginx-xxx.tmpl
                |- config.tmpl
            |- redis/
            |- ...
          |- harbor.tar.gz
            |- install.sh
          |- mage.tar.gz
            |- config.yaml
            |- init/
              |- mysql/
            |- images/
              |- xxx.tar
            |- templates/
              |- xxx.conf
            |- charts/
          |- nlp.tar.gz
            |- config.yaml
            |- images
              |- xxx.tar
            |- data
              |- xxx
"""


class PackageHandler(object):
    def __init__(self, path: str, project_name: str):
        # 存放包的目录
        self.location = path
        self.project_name = project_name
        self.package_name = "{}.tar.gz".format(self.project_name)
        # 要部署的项目名称
        self.root_dir = path_join(self.location, self.project_name)
        self.pkg = path_join(self.location, self.package_name)

    def unpack(self, nozip=False) -> bool:
        cmd = "tar zxf {} -C {}".format(path_join(self.location, self.package_name), self.location)
        if nozip:
            cmd = "tar xf {} -C {}".format(path_join(self.location, self.package_name), self.location)
        res = run_local_cmd(cmd)
        if res.code == 0 and os.path.isdir(self.root_dir):
            return True
        raise HandlerError(PackageErrors().UNPACK_ERROR.format(res.stdout)) from None

    def pack(self, nozip=False) -> bool:
        cmd = "cd {} && tar zcvf {} {}".format(self.location, self.package_name, self.project_name)
        if nozip:
            cmd = "cd {} && tar cvf {} {}".format(self.location, self.package_name, self.project_name)
        res = run_local_cmd(cmd)
        if res.code == 0 and os.path.isdir(self.root_dir):
            return self.pkg
        raise HandlerError(PackageErrors().PACK_ERROR.format(res.stdout)) from None

    def must_in(self, name: str, path: str) -> str:
        if name in os.listdir(path):
            return path_join(path, name)
        raise Forbidden(PackageErrors().PACKAGE_ILLEGAL.format(name)) from None

    def parse(self):
        raise HandlerError(Error().UNIMPLEMENT_ERROR.format("PackageHandler.parse"))

    def get(self):
        self.unpack()
        return self.parse()


class DeployPackageHandler(PackageHandler):
    """
    解析abcdefghi.tar.gz
    """
    def __init__(self, path: str, apply_id: str):
        super(DeployPackageHandler, self).__init__(path, apply_id)
        if len(apply_id) != 9:
            raise Forbidden(PackageErrors().PROJECT_ID_INCORRECT)

    def unpack(self):
        super().unpack(nozip=True)

    def parse(self):
        admin_config = PvtAdminConfigHandler(path_join(self.root_dir, "pvtadmin.json"))
        deploy_projects = admin_config.service_list.get()
        service_list = []
        for s in deploy_projects:
            if s == "ocr":
                service_list.append(OcrPackageHandler(self.root_dir, s))
            else:
                service_list.append(ServicePackageHandler(self.root_dir, s))
        res = {
            "config": admin_config,
            "kubernetes": KubePackageHandler(self.root_dir),
            "middleware": MiddlewarePackageHandler(self.root_dir),
            "harbor": HarborPackageHandler(self.root_dir),
            "license": LicensePackageHandler(self.root_dir),
            "service": service_list
        }
        return to_object(res)


class KubePackageHandler(PackageHandler):
    def __init__(self, path: str):
        super(KubePackageHandler, self).__init__(path, "kubernetes")

    @status_me("basesystem")
    def kubernetes_unpack(self):
        cmd = "tar zxf {} -C {}".format(path_join(self.location, self.package_name), self.location)
        res = run_local_cmd(cmd)
        if res.code == 0 and os.path.isdir(self.root_dir):
            return True
        raise HandlerError(PackageErrors().UNPACK_ERROR.format(res.stdout)) from None

    def parse(self):
        res = {
            "templates": path_join(self.root_dir, "templates"),
            "plugin": {
                "network": path_join(self.root_dir, "plugin/network"),
                "helm": path_join(self.root_dir, "plugin/helm"),
                "istio": path_join(self.root_dir, "plugin/istio")
            },
            "k8s-rpms": path_join(self.root_dir, "k8s-rpms")
        }
        return to_object(res)


class MiddlewarePackageHandler(PackageHandler):
    def __init__(self, path: str):
        super(MiddlewarePackageHandler, self).__init__(path, "middleware")

    def parse(self):
        """
        返回中间件列表
        :return: ["mysql", "redis", "minio"]
        """
        middlewares = os.listdir(self.root_dir)
        res = {}
        for m in middlewares:
            res[m] = path_join(self.root_dir, m)
        return to_object(res)


class HarborPackageHandler(PackageHandler):
    def __init__(self, path: str):
        super(HarborPackageHandler, self).__init__(path, "harbor")

    def parse(self):
        res = {
            "harbor": self.root_dir
        }
        return to_object(res)


class LicensePackageHandler(PackageHandler):
    def __init__(self, path: str):
        super(LicensePackageHandler, self).__init__(path, "license")

    def parse(self):
        config_file = ServiceConfigHandler(path_join(self.root_dir, "config.yaml"))
        res = {
            "config": config_file,
            "images": path_join(self.root_dir, "images"),
            "charts": path_join(self.root_dir, "charts"),
            "templates": path_join(self.root_dir, "templates"),
            "sqls": path_join(self.root_dir, "sqls"),
            "siber_sqls": path_join(self.root_dir, "siber_sqls"),
            "identity_sqls": path_join(self.root_dir, "identity_sqls"),
            "data": path_join(self.root_dir, "data")
        }
        return to_object(res)


class ServicePackageHandler(PackageHandler):
    def __init__(self, path: str, name: str):
        super(ServicePackageHandler, self).__init__(path, name)

    def parse(self):
        config_file = ServiceConfigHandler(path_join(self.root_dir, "config.yaml"))
        res = {
            "config": config_file,
            "images": path_join(self.root_dir, "images"),
            "charts": path_join(self.root_dir, "charts"),
            "templates": path_join(self.root_dir, "templates"),
            "sqls": path_join(self.root_dir, "sqls"),
            "siber_sqls": path_join(self.root_dir, "data", "siber_sqls"),
            "siber_sqls_ok": path_join(self.root_dir, "data", "siber_sqls_ok"),
            "identity_sqls": path_join(self.root_dir, "identity_sqls"),
            "data": path_join(self.root_dir, "data")
        }
        return to_object(res)


class OcrPackageHandler(PackageHandler):
    def __init__(self, path: str, name: str):
        super(OcrPackageHandler, self).__init__(path, name)

    def parse(self):
        config_file = ServiceConfigHandler(path_join(self.root_dir, "config.yaml"))
        res = {
            "config": config_file,
            "images": path_join(self.root_dir, "images"),
            "charts": path_join(self.root_dir, "charts"),
            "templates": path_join(self.root_dir, "docker-compose.tmpl"),
            "license_file": path_join(self.root_dir, "data", "licServer.lic")
        }
        return to_object(res)
    
class PreCheckPackageHandler(PackageHandler):
    def __init__(self, path: str, name: str):
        super(PreCheckPackageHandler, self).__init__(path, name)

    def parse(self):
        res = {
            "checker": self.root_dir,
            "check_config": path_join(self.root_dir, "check_config.json")
        }
        return to_object(res)