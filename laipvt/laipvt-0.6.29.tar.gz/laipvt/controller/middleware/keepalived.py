from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.interface.middlewareinterface import MiddlewareInterface
from laipvt.handler.middlewarehandler import KeepalivedConfigHandler
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.sysutil.template import FileTemplate
from laipvt.sysutil.util import path_join, ssh_obj, log, status_me

class KeepalivedController(MiddlewareInterface):
    def __init__(self, result: CheckResultHandler, handler: KeepalivedConfigHandler, template: str):
        super(KeepalivedController, self).__init__(result, handler, template)
        self.conf_template = path_join(self.template, "keepalived.conf")
        self.template_file_name = ("keepalived_master.conf", "keepalived_slave1.conf", "keepalived_slave2.conf")
        self.keepalived_config_file = path_join(self.base_dir, "conf", "{}.conf".format(self.middleware_name))
        self.keepalived_cfg = KeepalivedConfigHandler().get_config_with_check_result()
        self.keepalived_cfg["keepalived"]["ipaddress"] = self.handler.cfg["ipaddress"]

    def _generic_config(self):
        log.info("渲染 Keepalived 配置文件")
        for num_id, server in enumerate(self.master_server):
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            cmd = "ifconfig |grep {}  -B 1|grep -Po '^.*(?=:)'".format(server.ipaddress)
            results = ssh_cli.run_cmd(cmd)
            self.keepalived_cfg["keepalived"]["network_name"] = results["stdout"].split()[0]
            src = path_join(self.template, self.template_file_name[num_id])
            dest = path_join("/tmp", self.template_file_name[num_id])
            FileTemplate(self.keepalived_cfg, src, dest).fill()
            self.send_config_file(self.master_server[num_id], dest, self.keepalived_config_file)
            self.generate_docker_compose_file(self.keepalived_cfg)

    @status_me("middleware")
    def deploy_keepalived(self):
        self._generic_config()
        self.send_docker_compose_file()
        self.start()

