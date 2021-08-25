from __future__ import absolute_import
from __future__ import unicode_literals

from functools import reduce
from laipvt.sysutil.util import get_yaml_obj, get_json_obj, get_yaml_config, to_object
from laipvt.handler import ListHandler, DictHandler
from laipvt.sysutil.relation import service_module_relation, machine_module_relation, get_module_key

class ProjectsHandler(ListHandler):
    def __init__(self, projects):
        super(ProjectsHandler, self).__init__(projects)
        self.mage = self.check("mage")
        self.commander = self.check("commander")
        self.wulai = self.check("wulai")

class RoleHandler(ListHandler):
    def __init__(self, role):
        super(RoleHandler, self).__init__(role)
        self.master = self.check("master")
        self.node = self.check("node")
        self.harbor = self.check("harbor")
        self.licserver = self.check("licserver")

class ServerHandler(DictHandler):
    """返回服务器信息"""
    def __init__(self, server):
        super(ServerHandler, self).__init__(server)
        self.ipaddress = self.d.ipaddress
        self.username = self.d.username
        self.password = self.d.password
        self.port = self.d.port
        self.role = RoleHandler(self.d.role)

class ServersHandler(ListHandler):
    """返回服务器列表"""
    def __init__(self, servers):
        super(ServersHandler, self).__init__(servers)
        try:
            self.servers = self.get()
        except KeyError:
            self.servers = to_object(self.l)

    def get(self) -> list:
        """

        :return: list[ServerHandler]
        """
        l = []
        for server in self.l:
            l.append(ServerHandler(server))
        return l

    def get_role_ip(self, role: str) -> list:
        """根据角色获取匹配该角色的ip地址列表"""
        l = []
        for server in self.servers:
            if server.role.check(role):
                l.append(server.ipaddress)
        return l

    def get_all_ip(self) -> list:
        """根据角色获取匹配该角色的ip地址列表"""
        l = []
        for server in self.servers:
            l.append(server.ipaddress)
        return l

    def get_role_obj(self, role: str) -> list:
        l = []
        for server in self.servers:
            if server.role.check(role):
                l.append(server)
        return l

    def search_server(self, key: str, value: str) -> list:
        l = []
        for server in self.servers:
            if server.__dict__[key] == value:
                l.append(server)
        return l

class CheckResultHandler():
    def __init__(self, config_file: str):
        self.config = get_yaml_obj(config_file)
        self.deploy_dir = self.config.deploy_dir
        self.lb = self.config.lb
        self.deploy_projects = ProjectsHandler(self.config.deploy_projects)
        self.servers = ServersHandler(self.config.servers)
        self.licserver = self.config.licserver

class DeployServiceHandler():
    """
    处理要部署的项目，返回字典
    service: 自研的项目
    ocr: ocr相关
    """
    def __init__(self, deploy_service: list):
        res = []
        for id in deploy_service:
            if id in service_module_relation["ocr_standard"]:
                res.append("ocr_standard")
            elif id in service_module_relation["ocr"]:
                res.append("ocr")
            else:
                res.append(get_module_key(id))
            # for srv in service_module_relation:
            #     if int(id) in service_module_relation[srv]:
            #         res.append(srv)
        self.service_id = deploy_service
        self.service_list = reduce(lambda x, y: x if y in x else x + [y], [[], ] + res)

    def get(self) -> list:
        return self.service_list

    def parse(self, l: list) -> dict:
        cpu_list = []
        gpu_list = []
        for id in l:
            if id in machine_module_relation['cpu']:
                cpu_list.append(id)
            elif id in machine_module_relation['gpu']:
                gpu_list.append(id)
        return {
            "cpu": cpu_list,
            "gpu": gpu_list
        }

class PvtAdminConfigHandler():
    """解析私有部署授权平台传递配置
    {
        "code_version": 01,
        "deploy_type": simple/ha
        "project_name": "项目名称",
        "project_id": "abcde",
        "start_time": 1606199550,
        "end_time": 1608791570,
        "license_file_name": "abcde.lcs",
        "deploy_service": [0, 1, 2, 3, 4, 5]
    }
    {
            "commander": ["commander"],
            "mage": ["mage", "nlp", "captcha", "laiye_ocr", "hehe_ocr"],
            "wulai": ["wulai"],
            "laiye_ocr"li: ["laiye_document_cpu", "laiye_document_gpu", "laiye_table_cpu", "laiye_table_gpu"],
            "hehe_ocr": ["hehe_document_cpu", "hehe_document_gpu", "hehe_table_cpu", "hehe_table_gpu"],
    }
    """
    def __init__(self, config: str):
        self.config = get_json_obj(config)
        self.code_version = self.config.code_version
        self.project_name = self.config.project_name
        self.project_id = self.config.project_id
        self.license_file_name = self.config.license_file_name
        self.service_list = DeployServiceHandler(self.config.deploy_service)
        try:
            self.siber_tags = self.config.siber_tags
        except Exception:
            pass


class ServiceConfigHandler:
    """
    middleware:
      - mysql
      - redis
      - minio
    services:
      document-mining-backend:
        - document-mining-rpc
        - document-mining-auth
        - document-mining-openapi
      file-analyze:
        - file-analyze
      ocr-server-dispatch:
        - ocr-server-dispatch
    """
    def __init__(self, conf: str):
        self.conf = get_yaml_config(conf)
        self.middleware = self.conf.get("middleware", [])
        self.services = self.conf.get("services", [])
        self.tag = self.conf.get("tag", "")
        self.cfg = to_object({})
        self.buckets = self.conf.get("buckets", [])
        self.require_tfserver = self.conf.get("require_tfserver", False)
        self.machine_type = self.conf.get("machine_type", "cpu")

    def get_process(self, service: str) -> list:
        return self.services.get(service)
