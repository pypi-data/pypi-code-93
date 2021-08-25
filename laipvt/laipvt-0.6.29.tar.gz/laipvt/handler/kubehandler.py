from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.handler.confighandler import CheckResultHandler
from laipvt.handler.middlewarehandler import HarborConfigHandler
from laipvt.sysutil.util import path_join


class KubeConfigHandler(object):
    def __init__(self, check_result: CheckResultHandler, *args, **kwargs):
        """
        初始化k8s的配置类
        :param check_result:
        :param args:
        :param kwargs:  subnet, version, network_plugin
        """
        # self.first_master = check_result.servers.get_role_ip("master")[0]
        self.first_master = check_result.servers.get_role_ip("harbor")[0]

        self.apiserver_porxy_port = "6443"
        self.apiserver_proxy_address = "127.0.0.1"
        self.lb_proxy_port = "6444"
        self.version = kwargs.get("version", "v1.18.12")

        # self.harbor_endpoint = "{}:{}".format(check_result.servers.get_role_ip("harbor")[0], 8888)
        self.harbor_cfg = HarborConfigHandler().get_config_with_check_result()
        self.harbor_endpoint = "{}:{}".format(self.harbor_cfg["harbor"]["lb"], self.harbor_cfg["harbor"]["nginx_harbor_proxy_port"])
        self.image_repo = path_join(self.harbor_endpoint, "base_system")
        self.subnet = kwargs.get("subnet", "10.244.0.0/16")

        self.ip_list = []
        self.ip_list.append(check_result.lb)

        self.harbor_list = check_result.servers.get_role_ip("harbor")
        self.master_list = check_result.servers.get_role_ip("master")
        self.node_list = check_result.servers.get_role_ip("node")
        self.others_master_list = sorted(list(set(self.master_list) ^ set(self.harbor_list)))

        self.ip_list += self.master_list
        self.ip_list += self.node_list
        self.ip_list = list(set(self.ip_list))

        self.network_plugin = kwargs.get("network_plugin", "flannel")

    def get(self) -> dict:
        return self.__dict__


"""
# cat admin.tmpl
apiVersion: kubeadm.k8s.io/v1beta2
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: {{ first_master }}
  bindPort: {{ apiserver_porxy_port }}
nodeRegistration:
  criSocket: /var/run/dockershim.sock
  name: master-01
  taints:
  - effect: NoSchedule
    key: node-role.kubernetes.io/master
---
apiServer:
  certSANs:
    - 127.0.0.1 {% for key in ip_list %}
    - {{ key }}{% endfor %}
  timeoutForControlPlane: 4m0s
apiVersion: kubeadm.k8s.io/v1beta2
certificatesDir: /etc/kubernetes/pki
clusterName: kubernetes
controlPlaneEndpoint: "{{ apiserver_proxy_address }}:{{ nginx_proxy_port }}"

controllerManager: {}
dns:
  type: CoreDNS
etcd:
  local:
    dataDir: /var/lib/etcd
imageRepository: {{ image_repo }}
kind: ClusterConfiguration
kubernetesVersion: v1.18.12
networking:
  dnsDomain: cluster.local
  serviceSubnet: 10.96.0.0/12
  podSubnet: "{{ subnet }}"
scheduler: {}
---
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: ipvs
"""