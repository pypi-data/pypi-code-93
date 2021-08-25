from __future__ import absolute_import
from __future__ import unicode_literals

import re
import time
import requests
from requests.auth import HTTPBasicAuth
from laipvt.interface.middlewareinterface import MiddlewareInterface
from laipvt.handler.middlewarehandler import EsConfigHandler
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.sysutil.template import FileTemplate
from laipvt.sysutil.util import path_join, log, status_me


class EsController(MiddlewareInterface):
    def __init__(self, result: CheckResultHandler, handler: EsConfigHandler, template: str):
        super(EsController, self).__init__(result, handler, template)
        self.es_conf_tmp = path_join("/tmp", "elasticsearch.yml")
        self.es_conf_template = path_join(self.template, "config.tmpl")
        self.es_conf_file = path_join(self.base_dir, "conf", "elasticsearch.yml")
        self.auth_conf_tmp = path_join("/tmp", "readonlyrest.yml")
        self.auth_conf_template = path_join(self.template, "readonlyrest.yml")
        self.auth_conf_file = path_join(self.base_dir, "conf", "readonlyrest.yml")
        self.pligins = path_join(self.template, "plugins")
        self.pligins_tmp = path_join(self.base_dir, "elasticsearch")
        self.es_cfg = EsConfigHandler().get_config_with_check_result()
        self.http_port = self.es_cfg["elasticsearch"]["http_port"]
        self.password = self.es_cfg["elasticsearch"]["password"]
        self.es_cfg["elasticsearch"]["ipaddress"] = self.handler.cfg["ipaddress"]

    def _generic_config(self):
        log.info("渲染 Elasticsearch 认证配置文件")
        for num_id in range(len(self.master_server)):
            self.es_cfg["elasticsearch"]["host_name"] = "saas-es-0%s" % (num_id + 1)
            self.es_cfg["elasticsearch"]["master_node"] = "saas-es-01"
            self.es_cfg["ip"] = self.master_server[num_id].ipaddress
            log.info("渲染 Elasticsearch 配置文件")
            FileTemplate(self.es_cfg, self.es_conf_template, self.es_conf_tmp).fill()
            FileTemplate(self.es_cfg, self.auth_conf_template, self.auth_conf_tmp).fill()

            self.send_config_file(self.master_server[num_id], self.es_conf_tmp, self.es_conf_file)
            self.send_config_file(self.master_server[num_id], self.auth_conf_tmp, self.auth_conf_file)
            self.send_config_file(self.master_server[num_id], self.pligins, self.pligins_tmp)
            self.generate_docker_compose_file(self.es_cfg)

    def _check(self):
        time.sleep(60)
        for i in self.master_server:
            try:
                url = "http://{IP}:{PORT}/_cat/health".format(
                    IP=i.ipaddress, PORT=self.http_port
                )
                log.info("检查 {}:{} 上的 Elasticsearch 健康性".format(i.ipaddress, self.http_port))
                result = requests.get(url,  auth=HTTPBasicAuth('admin', '{}'.format(
                    self.password))).content.decode("utf-8")

                if re.search("green", result):
                    # log.info("Elasticsearch 检查通过")
                    self._read_write_test(i.ipaddress, self.http_port)
                else:
                    log.error("{IP} 上的 Elasticsearch 服务异常".format(IP=i.ipaddress))
                    log.error("错误日志: {}".format(result))
                    exit(2)
            except Exception as e:
                log.error(e)
                log.error("{IP} 上的 Elasticsearch 服务异常".format(IP=i.ipaddress))
                exit()

    def _read_write_test(self, ipaddress, port):
        try:
            headers = {"Content-Type": "application/json"}
            create_index = "http://{IP}:{PORT}/laiye_test/_doc/1".format(IP=ipaddress, PORT=port)
            delete_index = "http://{IP}:{PORT}/laiye_test".format(IP=ipaddress, PORT=port)
            data_dit = {"name": "laiye", "age": "5"}
            auth = HTTPBasicAuth('admin', '{}'.format(self.password))

            requests.post(url=create_index, json=data_dit,  headers=headers, auth=auth)
            log.info("Elasticsearch 测试数据插入成功")
            requests.delete(url=delete_index, auth=auth)
        except Exception as e:
            log.error(e)
            exit(2)

    @status_me("middleware")
    def deploy_es(self):
        if self.check_is_deploy(self.es_cfg):
            self._generic_config()
            self.send_docker_compose_file()
            self.start()
            self._check()

    def deploy(self):
        self.deploy_es()
