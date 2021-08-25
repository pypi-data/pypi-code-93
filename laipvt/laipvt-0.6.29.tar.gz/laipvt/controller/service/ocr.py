from __future__ import absolute_import
from __future__ import unicode_literals

import os
from laipvt.interface.middlewareinterface import MiddlewareInterface
from laipvt.handler.middlewarehandler import OcrConfigHandler
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.sysutil.util import path_join, log, ssh_obj
from laipvt.model.cmd import DockerImageModel, ComposeModel
from laipvt.sysutil.template import FileTemplate
from laipvt.sysutil.command import RESTART_LICSERVER


class OcrController(MiddlewareInterface):
    def __init__(self, service_path: object, result: CheckResultHandler, handler: OcrConfigHandler, template: str):
        super(OcrController, self).__init__(result, handler, template)
        self.project = "mage"
        self.service_path = service_path
        self.harbor_cfg = self.handler.get_all_config_with_check_result()
        try:
            harbor_ip = self.harbor_cfg["harbor"]["ipaddress"][0]
        except IndexError:
            harbor_ip = self.check_result.servers.get_role_ip("harbor")[0]
        self.registry_hub = "{}:{}".format(harbor_ip, self.harbor_cfg["harbor"]["http_port"])
        self.deploy_service_list = self.service_path.config.services

    def push_images(self):
        for image in os.listdir(self.service_path.images):
            image_path = path_join(self.service_path.images, image)
            log.info("将镜像push到私有仓库: {}".format(image_path))
            # print(image_path)
            docker = DockerImageModel(image=image_path, project=self.project, repo=self.registry_hub)
            docker.run()

    def start_licserver(self, renew=False, **kwargs):
        licserver = self.servers.get_role_obj("licserver")[0]
        log.info("分发授权文件文件至 %s:/etc/intsig/licServer.lic" % licserver.ipaddress )
        ssh_cli = ssh_obj(ip=licserver.ipaddress, user=licserver.username, password=licserver.password, port=licserver.port)
        try:
            if renew:
                lcs_file_path = kwargs.get("license_file")
            else:
                lcs_file_path = self.service_path.license_file

            ssh_cli.put(lcs_file_path, "/etc/intsig/licServer.lic")
            cmd = RESTART_LICSERVER
            ssh_cli.run_cmd(cmd)
        except Exception as e:
            log.error(e)
            exit(2)
        finally:
            ssh_cli.close()

    def generate_data(self, module_name: str) -> dict:
        data = {}
        data["name"] = module_name
        data["image_name"] = path_join(self.registry_hub, self.project, module_name)
        data["port"] = self.handler.get_ocr_module_port(module_name)
        log.info("获取{}的端口号为{}".format(data['name'], data['port']))
        data["machine_type"] = "gpu" if self.service_path.config.require_tfserver else "cpu"
        return data

    def generate_docker_compose_file_ocr(self, module_name: str, data_dict: dict) -> bool:
        log.info("渲染%s docker-compose配置文件" % module_name)
        compose_tmp = path_join("/tmp", "docker-compose-{}.yaml".format(module_name))
        FileTemplate(data_dict, path_join(self.template, "docker-compose.tmpl"), compose_tmp).fill()
        return compose_tmp if os.path.isfile(compose_tmp) else False

    def deploy(self, server, compose_file_local, compose_file_remote):
        compose_cmd = ComposeModel(compose_file_remote)
        ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password,
                          port=server.port)
        try:
            log.info("发送配置文件{}到服务器{}".format(compose_file_local, server.ipaddress))
            ssh_cli.put(compose_file_local, compose_file_remote)
            log.info("启动服务{}".format(compose_cmd.up()))
            ssh_cli.run_cmd(compose_cmd.up())
        except Exception as e:
            log.error(e)
            exit(2)
        finally:
            ssh_cli.close()

    def deploy_ocr_module(self):
        server = self.servers.get_role_obj("licserver")[0]
        for module in self.deploy_service_list:
            compose_file_remote = path_join(self.check_result.deploy_dir, module, "docker-compose.yaml")
            data = self.generate_data(module)
            compose_file = self.generate_docker_compose_file_ocr(module, data)
            log.info("开始部署ocr 模型 {}".format(module))
            self.deploy(server, compose_file, compose_file_remote)

    def restart_ocr_module(self):
        server = self.servers.get_role_obj("licserver")[0]
        for module in self.deploy_service_list:
            compose_file_remote = path_join(self.check_result.deploy_dir, module, "docker-compose.yaml")
            compose_cmd = ComposeModel(compose_file_remote)
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username,
                              password=server.password, port=server.port)
            try:
                log.info("重新启动服务{}".format(compose_cmd.restart()))
                ssh_cli.run_cmd(compose_cmd.restart())
            except Exception as e:
                log.error(e)
                exit(2)
            finally:
                ssh_cli.close()

    def renew_license(self, license_file):
        self.start_licserver(renew=True, license_file=license_file)
        self.restart_ocr_module()

    def run(self):
        self.push_images()
        self.start_licserver()
        self.deploy_ocr_module()

