from __future__ import absolute_import
from __future__ import unicode_literals
import os
from laipvt.interface.middlewareinterface import MiddlewareInterface
from laipvt.handler.middlewarehandler import NginxConfigHandler
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.sysutil.template import FileTemplate
from laipvt.sysutil.util import path_join, log, status_me, ssh_obj
from laipvt.model.cmd import ComposeModel
from laipvt.sysutil.gvalue import CERTS_PATH



class NginxController(MiddlewareInterface):
    def __init__(self, result: CheckResultHandler, handler: NginxConfigHandler, template: str):
        super(NginxController, self).__init__(result, handler, template)

        self.nginx_conf_tmp = path_join("/tmp", "nginx.conf")
        self.nginx_conf_template = path_join(self.template, "config.tmpl")
        self.nginx_conf_file = path_join(self.base_dir, "nginx.conf")
        self.apiserver_conf_tmp = path_join("/tmp", "apiserver.conf")
        self.apiserver_conf_template = path_join(self.template, "tcp/apiserver.conf")
        self.apiserver_conf_file = path_join(self.base_dir, "tcp/apiserver.conf")
        self.apiserver_cluster_conf_template = path_join(self.template, "tcp/apiserver_cluster.conf")
        self.nginx_cfg = NginxConfigHandler().get_config_with_check_result()
        self.nginx_cfg["nginx"]["ipaddress"] = self.handler.cfg["ipaddress"]
        self.nginx_cfg.update(self.check_result.__dict__)
        # if self.nginx_cfg["config"]["deploy_https"]:
        #     if self.nginx_cfg["config"]["self_signed_ca"]:
        #         self.nginx_cfg["config"]["cert_path"] = os.path.dirname(SERVER_SECURE_KEY)
        #     else:
        #         self.nginx_cfg["config"]["cert_path"] = os.path.dirname(self.nginx_cfg["config"]["ca_key_path"])

    def _generic_config(self):
        if self.nginx_cfg["config"]["deploy_https"]:
            if self.nginx_cfg["config"]["self_signed_ca"]:
                self.nginx_cfg["config"]["cert_path"] = CERTS_PATH
                self._send_https_ca_file()
            else:
                self.nginx_cfg["config"]["cert_path"] = os.path.dirname(self.nginx_cfg["config"]["ca_key_path"])

        log.info("渲染nginx配置文件")
        for num_id in range(len(self.all_server)):
            FileTemplate(self.nginx_cfg, self.nginx_conf_template, self.nginx_conf_tmp).fill()
            FileTemplate(self.nginx_cfg, self.apiserver_conf_template, self.apiserver_conf_tmp).fill()
            self.send_config_file(self.all_server[num_id], self.nginx_conf_tmp, self.nginx_conf_file)
            self.send_config_file(self.all_server[num_id], self.apiserver_conf_tmp, self.apiserver_conf_file)
        self.generate_docker_compose_file(self.nginx_cfg)

    def _send_docker_compose_file(self):
        for server in self.all_server:
            log.info("分发%s docker-compose配置文件至 %s" % (self.middleware_name, server.ipaddress))
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            try:
                ssh_cli.put(self.docker_compose_file_tmp, self.docker_compose_file)
            except Exception as e:
                log.error(e)
                exit(2)
            finally:
                ssh_cli.close()

    def _send_https_ca_file(self):
        for server in self.all_server:
            log.info("分发%s https证书文件至 %s" % (self.middleware_name, server.ipaddress))
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            try:
                ssh_cli.put("/tmp/certs", CERTS_PATH)

            except Exception as e:
                log.error(e)
                exit(2)
            finally:
                ssh_cli.close()

    def renew_apiserver_config(self):
        log.info("将k8s master节点渲染到apiserver配置文件中")
        for num_id in range(len(self.all_server)):
            FileTemplate(self.nginx_cfg, self.apiserver_cluster_conf_template, self.apiserver_conf_tmp).fill()
            self.send_config_file(self.all_server[num_id], self.apiserver_conf_tmp, self.apiserver_conf_file)
            self._restart()

    def _check(self):
        super().wait_for_service_start()
        port = self.nginx_cfg["nginx"]["k8s_proxy_port"]
        for server in self.master_server:
            res = self.check_port(server.ipaddress, port)
            if res:
                log.info("机器:{} Nginx代理端口:{}访问正常".format(server.ipaddress, port))
            else:
                log.error("机器:{} Nginx代理端口:{}访问异常".format(server.ipaddress, port))
                exit(2)

    def _start(self):
        compose_cmd = ComposeModel(self.docker_compose_file)
        for server in self.all_server:
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

    def _restart(self):
        compose_cmd = ComposeModel(self.docker_compose_file)
        for server in self.all_server:
            log.info("启动 %s %s服务" % (server.ipaddress, self.middleware_name))
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            try:
                res = ssh_cli.run_cmd(compose_cmd.restart())
                if res["code"] != 0:
                    log.error("启动 %s: %s服务失败.错误原因: %s %s" %
                              (server.ipaddress, self.middleware_name, res["stderr"], res["stdout"]))
                    exit(2)
            except Exception as e:
                log.error(e)
                exit(2)
            finally:
                ssh_cli.close()

    @status_me("basesystem")
    def install_nginx(self):
        self._generic_config()
        self._send_docker_compose_file()
        self._start()
        self._check()
