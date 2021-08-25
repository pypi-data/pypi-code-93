from __future__ import absolute_import
from __future__ import unicode_literals

import requests
from minio import Minio
from laipvt.interface.middlewareinterface import MiddlewareInterface
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.handler.middlewarehandler import MinioConfigHandler
from laipvt.sysutil.template import FileTemplate
from laipvt.sysutil.util import path_join, log, status_me


class MinioController(MiddlewareInterface):
    def __init__(self, result: CheckResultHandler, handler: MinioConfigHandler, template: str):
        super(MinioController, self).__init__(result, handler, template)
        self.minio_cfg = MinioConfigHandler().get_config_with_check_result()
        self.minio_nginx_tmp = path_join("/tmp", "nginx-minio.conf")
        self.minio_nginx_template = path_join(self.template, "nginx-minio.tmpl")
        self.minio_nginx_file = path_join(self.deploy_dir, "nginx/http/nginx-minio.conf")
        self.minio_cfg["minio"]["ipaddress"] = self.handler.cfg["ipaddress"]

    def _proxy_on_nginx(self):
        log.info("渲染 Nginx 代理配置文件")
        FileTemplate(self.minio_cfg, self.minio_nginx_template, self.minio_nginx_tmp).fill()
        self.update_nginx_config()
        self.generate_docker_compose_file(self.minio_cfg)

    def _create_bucket(self, bucket: str):
        log.info("创建 bucket")
        try:
            self.endpoint = "{}:{}".format(self.minio_cfg["minio"]["lb"], self.minio_cfg["minio"]["nginx_proxy_port"])
            cli = Minio(
                self.endpoint,
                self.minio_cfg["minio"]["username"],
                self.minio_cfg["minio"]["password"],
                secure=False
            )
            if not cli.bucket_exists(bucket):
                cli.make_bucket(bucket)
                return True
        except Exception as e:
            log.error(e)
            log.error("Minio 创建bucket失败")
            exit(2)

    def check(self):
        super().wait_for_service_start()
        for ip in self.master_server:
            try:
                log.info("检查 {IP}:{PORT} 上的 Minio 健康性...".format(IP=ip.ipaddress, PORT=self.minio_cfg["minio"]["port"]))
                requests.get(
                    "http://{IP}:{PORT}/minio/health/live".format(
                        IP=ip.ipaddress, PORT=self.minio_cfg["minio"]["port"]
                    )
                )
                log.info("Minio 连接检查通过")
            except Exception as e:
                log.error(e)
                log.error("{IP}:{PORT} 上的 Minio 服务异常".format(IP=ip.ipaddress,PORT=self.minio_cfg["minio"]["port"]))
                exit(2)

    @status_me("middleware")
    def deploy_minio(self):
        if self.check_is_deploy(self.minio_cfg):
            self._proxy_on_nginx()
            self.send_docker_compose_file()
            self.start()
            self.check()
            self._create_bucket("mysql-backup")

    def deploy(self):
        self.deploy_minio()
