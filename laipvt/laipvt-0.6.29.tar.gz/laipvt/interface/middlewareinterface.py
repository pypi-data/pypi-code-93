from __future__ import absolute_import
from __future__ import unicode_literals

import time
import os
import socket

from laipvt.handler.middlewarehandler import MiddlewareConfigHandler, HarborConfigHandler
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.model.cmd import ComposeModel
from laipvt.sysutil.util import path_join, ssh_obj,log
from laipvt.sysutil.gvalue import CHECK_INTERVAL
from laipvt.sysutil.template import FileTemplate
from laipvt.sysutil.command import RM, MKDIR_DIR, CHMOD_777

class MiddlewareInterface():
    def __init__(self, result: CheckResultHandler, handler: MiddlewareConfigHandler, template: str):
        self.check_result = result
        self.handler = handler
        self.template = template

        self.deploy_dir = self.check_result.deploy_dir
        self.middleware_name = self.handler.get_value("name")
        self.check_interval = CHECK_INTERVAL
        self.compose_template = path_join(self.template, "{}.tmpl".format(self.middleware_name))
        self.nginx_template = path_join(self.template, "nginx-{}.tmpl".format(self.middleware_name))
        self.servers = self.check_result.servers
        self.server_list = self.servers.get_role_ip("master")
        self.master_server = self.servers.get_role_obj("master")
        self.harbor_server = self.servers.get_role_obj("harbor")
        self.handler.set("ipaddress", self.server_list)
        self.all_server = self.servers.get()
        self.base_dir = path_join(self.deploy_dir, self.middleware_name)
        self.docker_compose_file_tmp = path_join("/tmp", "docker-compose-{}.yaml".format(self.middleware_name))
        self.nginx_config_tmp = path_join("/tmp", "nginx-{}.conf".format(self.middleware_name))

        self.docker_compose_file = path_join(self.base_dir, "docker-compose.yml")
        self.nginx_config_file = path_join(self.deploy_dir, "nginx", self.handler.get_proxy_type(), "{}.conf".format(self.middleware_name))
        self.nginx_compose_file = path_join(self.deploy_dir, "nginx", "docker-compose.yml")
        self.harbor_cfg = HarborConfigHandler().load()
        self.handler.set("harbor_http_port", self.harbor_cfg["harbor"]["http_port"])
        self.handler.set("harbor_ipaddress", [self.harbor_server[0].ipaddress, ])

    def info(self):
        return self.handler.cfg

    def wait_for_service_start(self):
        time.sleep(self.check_interval)

    def check_is_deploy(self, cfg):
        return False if cfg[self.middleware_name]["is_deploy"] == False else True

    def generate_docker_compose_file(self, data_dict) -> bool:
        log.info("渲染%s docker-compose配置文件" % self.middleware_name)
        FileTemplate(data_dict, self.compose_template, self.docker_compose_file_tmp).fill()
        return True if os.path.isfile(self.docker_compose_file_tmp) else False

    def send_docker_compose_file(self):
        for server in self.master_server:
            log.info("分发%s docker-compose配置文件至 %s" % (self.middleware_name, server.ipaddress))
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            try:
                ssh_cli.put(self.docker_compose_file_tmp, self.docker_compose_file)
            except Exception as e:
                log.error(e)
                exit(2)
            finally:
                ssh_cli.close()

    def send_docker_compose_file_hosts(self, host):
        log.info("分发%s docker-compose配置文件至 %s:%s" % (self.middleware_name, host.ipaddress, self.docker_compose_file))
        ssh_cli = ssh_obj(ip=host.ipaddress, user=host.username, password=host.password, port=host.port)
        try:
            ssh_cli.put(self.docker_compose_file_tmp, self.docker_compose_file)
        except Exception as e:
            log.error(e)
            exit(2)
        finally:
            ssh_cli.close()

    def send_config_file(self, server, src, dest, ignore=''):
        log.info("分发配置文件{} 到 {}:{}".format(src, server.ipaddress, dest))
        ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
        try:
            ssh_cli.put(src, dest, ignore)
        except Exception as e:
            log.error(e)
            exit(2)
        finally:
            ssh_cli.close()

    def send_docker_compose_file_hosts(self, host):
        """aa"""
        log.info("分发%s docker-compose配置文件至 %s:%s" % (self.middleware_name, host.ipaddress, self.docker_compose_file))
        ssh_cli = ssh_obj(ip=host.ipaddress, user=host.username, password=host.password, port=host.port)
        try:
            ssh_cli.put(self.docker_compose_file_tmp, self.docker_compose_file)
        except Exception as e:
            log.error(e)
            exit(2)
        finally:
            ssh_cli.close()

    def start(self):
        compose_cmd = ComposeModel(self.docker_compose_file)
        for server in self.master_server:
            log.info("启动 %s %s服务" % (server.ipaddress, self.middleware_name))
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            try:
                res = ssh_cli.run_cmd(compose_cmd.up())
                if res["code"] != 0:
                    log.error("启动 %s: %s服务失败.错误原因: %s %s" % (server.ipaddress, self.middleware_name, res["stderr"], res["stdout"]))
                    exit(2)
            except Exception as e:
                log.error(e)
                exit(2)
            finally:
                ssh_cli.close()

    def restart(self):
        compose_cmd = ComposeModel(self.docker_compose_file)
        for server in self.master_server:
            log.info("启动 %s %s服务" % (server.ipaddress, self.middleware_name))
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            try:
                res = ssh_cli.run_cmd(compose_cmd.restart())
                if res["code"] != 0:
                    log.error("启动 %s: %s服务失败.错误原因: %s %s" % (
                    server.ipaddress, self.middleware_name, res["stderr"], res["stdout"]))
                    exit(2)
            except Exception as e:
                log.error(e)
                exit(2)
            finally:
                ssh_cli.close()

    def reset(self):
        compose_cmd = ComposeModel(self.docker_compose_file)
        for server in self.master_server:
            log.info("重新加载 %s %s服务" % (server.ipaddress, self.middleware_name))
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            try:
                res = ssh_cli.run_cmd(compose_cmd.down())
                res = ssh_cli.run_cmd(compose_cmd.up())
                if res["code"] != 0:
                    log.error("重启 %s: %s服务失败.错误原因: %s %s" % (
                    server.ipaddress, self.middleware_name, res["stderr"], res["stdout"]))
                    exit(2)
            except Exception as e:
                log.error(e)
                exit(2)
            finally:
                ssh_cli.close()

    def create_logs_dir(self, log_path):
        log.info("创建服务日志目录及授权:{}".format(log_path))
        cmd = [
            MKDIR_DIR.format(log_path),
            CHMOD_777.format(log_path)
        ]
        for server in self.master_server:
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username,
                              password=server.password, port=server.port)
            ssh_cli.run_cmdlist(cmd)

    def check(self) -> bool:
        pass

    def check_port(self, ip, port):
        try:
            if int(port) > 65536:
                return False
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = s.connect_ex((ip, port))
                if result == 0:
                    return True
                s.close()
        except Exception as e:
            log.error(e)
            return False

    def init(self, path) -> bool:
        FileTemplate(self.handler.cfg, self.nginx_template, self.nginx_config_tmp).fill()
        return True if os.path.isfile(self.nginx_config_tmp) else False

    def update_nginx_config(self):
        compose_cmd = ComposeModel(self.nginx_compose_file)
        for server in self.master_server:
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            try:
                ssh_cli.put(self.nginx_config_tmp, self.nginx_config_file)
                ssh_cli.run_cmd(compose_cmd.restart())
            except Exception as e:
                log.error(e)
                exit(2)
            finally:
                ssh_cli.close()

    def remove(self):
        compose_cmd = ComposeModel(self.docker_compose_file)
        for server in self.master_server:
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            try:
                ssh_cli.run_cmd(compose_cmd.down())
                ssh_cli.run_cmd(RM.format(self.base_dir))
            except Exception as e:
                log.error(e)
                exit(2)
            finally:
                ssh_cli.close()

    def run(self):
        self.generate_docker_compose_file()
        self.send_docker_compose_file()
        self.start()
        self.check()
        self.update_nginx_config()
