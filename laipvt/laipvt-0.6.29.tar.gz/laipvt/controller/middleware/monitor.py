from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.interface.middlewareinterface import MiddlewareInterface
from laipvt.handler.middlewarehandler import MonitorConfigHandler
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.sysutil.template import FileTemplate
from laipvt.sysutil.util import path_join, log, status_me, ssh_obj

class MonitorController(MiddlewareInterface):
    def __init__(self, result: CheckResultHandler, handler: MonitorConfigHandler, template: str):
        super(MonitorController, self).__init__(result, handler, template)
        self.src_json = path_join(self.template, "json")
        self.dest_json = path_join(self.base_dir, "json")
        self.dashboards_conf_tmp = path_join("/tmp", "dashboards.yaml")
        self.dashboards_conf_file = path_join(self.base_dir, "conf", "dashboards.yaml")
        self.prometheus_tmp = path_join("/tmp", "prometheus.yaml")
        self.prometheus_file = path_join(self.base_dir, "conf", "prometheus.yaml")
        self.prometheus_istio_tempfile = path_join(self.template, "prometheus_istio.yaml")
        self.prometheus_istio_tmp = path_join("/tmp", "prometheus_istio.yaml")
        self.prometheus_istio_file = path_join(self.base_dir, "prometheus_istio.yaml")
        self.datasources_tmp = path_join("/tmp", "datasources.yaml")
        self.datasources_file = path_join(self.base_dir, "conf", "datasources.yaml")
        self.k8s_datasource_tmp = path_join("/tmp", "k8s_datasources.yaml")
        self.k8s_datasource_file = path_join(self.base_dir, "conf", "k8s_datasources.yaml")
        self.mysql_datasource_tmp = path_join("/tmp", "mysql_datasources.yaml")
        self.mysql_datasource_file = path_join(self.base_dir, "conf", "mysql_datasources.yaml")
        self.monitor_cfg = MonitorConfigHandler().get_all_config_with_check_result()
        self.monitor_cfg["monitor"] = MonitorConfigHandler().get_config_with_check_result()["monitor"]
        self.monitor_cfg["monitor"]["ipaddress"] = self.handler.cfg["ipaddress"]
        self.monitor_cfg["rabbitmq"]["ipaddress"] = self.handler.cfg["ipaddress"]
        self.monitor_cfg["redis"]["ipaddress"] = self.handler.cfg["ipaddress"]
        self.monitor_cfg["minio"]["ipaddress"] = self.handler.cfg["ipaddress"]
        self.monitor_cfg["mysql"]["ipaddress"] = self.handler.cfg["ipaddress"]
        self.monitor_cfg["elasticsearch"]["ipaddress"] = self.handler.cfg["ipaddress"]
        self.registry_hub = "{}:{}".format(self.monitor_cfg["monitor"]["harbor_ipaddress"],
                                           self.monitor_cfg["monitor"]["nginx_harbor_proxy_port"])
        self.servers = result.servers.get()
        
    def _generic_config(self):
        log.info("渲染 Monitor 配置文件")
        self.monitor_cfg["monitor"]["master"] = True
        FileTemplate(self.monitor_cfg, path_join(self.template, "config"), "/tmp").fill()
        FileTemplate(self.monitor_cfg, self.prometheus_istio_tempfile, self.prometheus_istio_tmp).fill()
        self.send_config_file(self.servers[0], self.dashboards_conf_tmp, self.dashboards_conf_file)
        self.send_config_file(self.servers[0], self.prometheus_tmp, self.prometheus_file)
        self.send_config_file(self.servers[0], self.datasources_tmp, self.datasources_file)
        self.send_config_file(self.servers[0], self.k8s_datasource_tmp, self.k8s_datasource_file)
        self.send_config_file(self.servers[0], self.mysql_datasource_tmp, self.mysql_datasource_file)
        self.send_config_file(self.servers[0], self.src_json, self.dest_json)
        self.send_config_file(self.servers[0], self.prometheus_istio_tmp, self.prometheus_istio_file)

        for server in self.servers:
            self.generate_docker_compose_file(self.monitor_cfg)
            self.monitor_cfg["monitor"]["master"] = False
            self.send_docker_compose_file_hosts(server)

    def _install_prometheus(self):
        log.info("安装 Prometheus")
        cmd = ["kubectl apply -f {}".format(path_join(self.base_dir, "prometheus_istio.yaml")),
               "helm --host=localhost:44134 install --name=k8s-metrics  --set replicaCount=1 \
               --set image.repository={}/middleware/kube-state-metrics --set image.tag=latest \
               {}".format(self.registry_hub, path_join(self.base_dir, 'kube-state-metrics'))]
        ssh_cli = ssh_obj(ip=self.harbor_server[0].ipaddress, user=self.harbor_server[0].username,
                          password=self.harbor_server[0].password, port=self.harbor_server[0].port)
        results = ssh_cli.run_cmdlist(cmd)
        if results[0]["code"] != 0 and results[1]["code"] != 0:
            log.error("监控prometheus安装失败".format(results["stdout"], results["stderr"]))
            exit(2)

    @status_me("middleware")
    def deploy_monitor(self):
        self._generic_config()
        self.start()
        self._install_prometheus()
