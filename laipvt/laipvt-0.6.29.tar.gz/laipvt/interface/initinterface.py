from __future__ import absolute_import
from __future__ import unicode_literals

import os
import time
from laipvt.handler.confighandler import CheckResultHandler, ServerHandler
from laipvt.handler.packagehandler import KubePackageHandler
from laipvt.handler.kubehandler import KubeConfigHandler
from laipvt.sysutil.util import path_join, ssh_obj, log

from laipvt.sysutil.template import FileTemplate
from laipvt.model.cmd import KubeModel


class InitInterface:
    def __init__(self, result: CheckResultHandler, kube: KubePackageHandler.parse, *args, **kwargs):
        self.result = result
        self.kube_config = KubeConfigHandler(result, *args, **kwargs).get()
        self.info = kube
        self.base_dir = path_join(result.deploy_dir, "kubernetes")

        self.kube_admin_file_template = path_join(self.info.templates, "admin.tmpl")
        self.kube_admin_file = path_join(self.info.templates, "admin.conf")

        self.hosts_file_template = path_join(self.info.templates, "hosts.tmpl")
        self.hosts_file = path_join(self.info.templates, "hosts")

        self.system_init_template = path_join(self.info.templates, "init_env.tmpl")
        self.system_init_file = path_join(self.info.templates, "init_env.sh")

        self.flannel_template = path_join(self.info.templates, "kube-flannel.tmpl")
        self.flannel_file = path_join(self.info.templates, "kube-flannel.yaml")

        self.istio_template = path_join(self.info.plugin.istio, "service/istio-private-deploy.tmpl")
        self.istio_file = path_join(self.info.plugin.istio, "service/istio-private-deploy.yaml")

        self.local_tmp = path_join(os.path.dirname(self.info.templates), "tmp")

        self.master = result.servers.get_role_obj("harbor")[0]
        self.servers = result.servers.get()

        self.network_plugin_file = path_join(
            self.info.plugin.network,
            "{}.yaml".format(self.kube_config["network_plugin"])
        )

        self.pki_tar_name = "pki.tar.gz"
        self.remote_pki_path = path_join("/etc/kubernetes", self.pki_tar_name)
        self.kubeconfig_file = "/etc/kubernetes/admin.conf"
        self.kubeconfig_local = "~/.kube/config"

    def _exec_command_to_host(self, cmd, server: ServerHandler, check_res=True):
        log.info("主机 {} 执行命令: {}".format(server.ipaddress, cmd))
        if isinstance(cmd, list):
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            res_list = ssh_cli.run_cmdlist(cmd)
            ssh_cli.close()
            if check_res:
                for res in res_list:
                    if res["code"] != 0:
                        log.error("{} {}".format(res["stdout"], res["stderr"]))
                        exit(2)
            return res_list
        if isinstance(cmd, str):
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            res = ssh_cli.run_cmd(cmd)
            ssh_cli.close()
            if check_res:
                if res["code"] != 0:
                    log.error("{} {}".format(res["stdout"], res["stderr"]))
                    exit(2)
            return res
        else:
            log.error("{}传入命令格式存在错误".format(cmd))
            exit(2)

    def _generate_file(self, template_file, dest_file):
        log.info("渲染{}文件到{}".format(template_file, dest_file))
        FileTemplate(self.kube_config, template_file, dest_file).fill()
        if not os.path.isfile(dest_file):
            log.error("{}文件渲染失败，程序退出".format(template_file))
            exit(2)
        return True

    def _send_file(self, src, dest, role=""):
        l = []
        if role:
            for server in self.servers:
                if server.role.check(role):
                    l.append(server)
        else:
            l = self.servers
        for server in l:
            log.info("分发{}到{}:{}".format(src, server.ipaddress, dest))
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            try:
                ssh_cli.put(src, dest)
            except Exception as e:
                log.error(e)
                exit(2)
            finally:
                ssh_cli.close()

    def _get_file(self, src, dest, server: ServerHandler):
        log.info("拉取{}:{}到{}".format(server.ipaddress, src, dest))
        if not os.path.isdir(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))
        ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
        try:
            ssh_cli.get(src, dest)
        except Exception as e:
            log.error(e)
            exit(2)
        finally:
            ssh_cli.close()

    def add_hosts(self):
        self._generate_file(template_file=self.hosts_file_template, dest_file=self.hosts_file)
        self._send_file(self.hosts_file, "/etc/hosts")

    def install_rpms(self):
        self._send_file(self.info["k8s-rpms"], path_join(self.base_dir, "k8s-rpms"))
        cmd_list = [
            "rpm -ivUh {}/*.rpm --force --nodeps".format(path_join(self.base_dir, "k8s-rpms")),
            "unalias -a; cp -f {}/kubeadm /usr/bin/kubeadm".format(path_join(self.base_dir, "k8s-rpms"))
        ]
        for server in self.servers:
            log.info("{} 安装k8s离线包".format(server.ipaddress))
            self._exec_command_to_host(cmd=cmd_list, server=server, check_res=False)

    def system_prepare(self):
        self._generate_file(template_file=self.system_init_template, dest_file=self.system_init_file)
        self._send_file(self.system_init_file, path_join(self.base_dir, "init_env.sh"))
        cmd = "bash {}".format(path_join(self.base_dir, "init_env.sh"))
        for server in self.servers:
            log.info("{}执行初始化脚本{}".format(server.ipaddress, path_join(self.base_dir, "init_env.sh")))
            self._exec_command_to_host(cmd=cmd, server=server)

    def init_primary_master(self):
        log.info("初始化master主节点")
        self._generate_file(template_file=self.kube_admin_file_template, dest_file=self.kube_admin_file)
        self._send_file(self.kube_admin_file, path_join(self.base_dir, "admin.conf"))
        cmd = "kubeadm init --config {}".format(path_join(self.base_dir, "admin.conf"))
        self._exec_command_to_host(cmd=cmd, server=self.master)

        log.info("生成kubectl config文件")
        cmd = "mkdir ~/.kube;cp /etc/kubernetes/admin.conf ~/.kube/config"
        self._exec_command_to_host(cmd=cmd, server=self.master)

    def kube_completion(self):
        log.info("k8s命令自动补全")
        cmd = "echo 'source <(kubectl completion bash)' >> ~/.bashrc"
        self._exec_command_to_host(cmd=cmd, server=self.master)

    def install_network_plugin(self):
        log.info("部署flannel网络插件")
        self._generate_file(template_file=self.flannel_template, dest_file=self.flannel_file)
        self._send_file(self.flannel_file, path_join(self.base_dir, "kube-flannel.yaml"))
        cmd = "kubectl apply -f {}".format(path_join(self.base_dir, "kube-flannel.yaml"))
        self._exec_command_to_host(cmd=cmd, server=self.master)

    def get_kube_admin_join_command(self) -> str:
        cmd = "kubeadm token create --print-join-command --config {}".format(path_join(self.base_dir, "admin.conf"))
        res = self._exec_command_to_host(cmd=cmd, server=self.master)

        if res["code"] == 0 and "kubeadm join" in res["stdout"]:
            return res["stdout"].strip().split("\n")[-1]
        else:
            raise Exception("生成Node节点join命令失败：\n {} {}".format(res["stdout"], res["stderr"]))

    def join_master(self):
        # 1、连接master-01，打包需要拷贝的证书配置，拉到本地
        log.info("将master-01 kubernetes证书拉回本地，发送至其余master节点")
        cmd = """tar -C /etc/kubernetes -zcvf {} \
        admin.conf pki/ca.crt pki/ca.key pki/sa.key pki/sa.pub pki/front-proxy-ca.crt \
        pki/front-proxy-ca.key pki/etcd/ca.crt pki/etcd/ca.key""".format(self.remote_pki_path)
        self._exec_command_to_host(cmd=cmd, server=self.master)
        self._get_file(src=self.remote_pki_path, dest=path_join(self.local_tmp, self.pki_tar_name), server=self.master)

        other_masters = []
        for server in self.servers:
            if server.ipaddress != self.master.ipaddress:
                other_masters.append(server)

        join_cmd = self.get_kube_admin_join_command()
        for i, server in enumerate(other_masters):
            log.info("将kubernetes证书，发送至master节点{},并解压".format(server.ipaddress))
            self._send_file(src=path_join(self.local_tmp, self.pki_tar_name), dest=self.remote_pki_path)
            cmd = "tar -zxvf {} -C /etc/kubernetes/".format(self.remote_pki_path)
            self._exec_command_to_host(cmd=cmd, server=server)

            log.info("加入{}master节点".format(server.ipaddress))
            node_name = "master-0{}".format(i + 2)
            cmd = "{} --control-plane --node-name {}".format(join_cmd, node_name)
            self._exec_command_to_host(cmd=cmd, server=server)

    def join_node(self):
        for i, server in enumerate(self.result.servers.get_role_obj("node")):
            if server.ipaddress in self.result.servers.get_role_ip("master"):
                log.info("master")
                node_name = "master-0{}".format(i + 1)
                cmd = "kubectl taint nodes {} node-role.kubernetes.io/master-".format(node_name)
            else:
                cmd = self.get_kube_admin_join_command()
            self._exec_command_to_host(cmd=cmd, server=self.master)

    def check_cluster_status(self) -> bool:
        kube = KubeModel()
        status = kube.get_node_status()
        print(status)
        for i in status:
            if i["node_status"] != "Ready":
                return False
        return True

    def install_helm(self):
        self._send_file(src=path_join(self.info.plugin.helm, "bin/helm"), dest="/usr/bin/helm")
        self._send_file(src=path_join(self.info.plugin.helm, "bin/tiller"), dest="/usr/bin/tiller")
        self._send_file(
            src=path_join(self.info.plugin.helm, "service/tiller.service"),
            dest="/usr/lib/systemd/system/tiller.service"
        )
        cmd_list = [
            "chmod +x /usr/bin/helm", "chmod +x /usr/bin/tiller",
            "systemctl daemon-reload", "systemctl start tiller.service", "systemctl enable tiller.service"
        ]
        self._exec_command_to_host(cmd=cmd_list, server=self.master, check_res=True)

    def install_istio(self):
        self._send_file(src=path_join(self.info.plugin.istio, "bin/istioctl"), dest="/usr/bin/istioctl")

        self._generate_file(template_file=self.istio_template, dest_file=self.istio_file)
        istio_remote_file = path_join(self.base_dir, "istio-private-deploy.yaml")
        self._send_file(src=self.istio_file, dest=istio_remote_file)

        cmd = "chmod +x /usr/bin/istioctl && istioctl version || exit 2"
        self._exec_command_to_host(cmd=cmd, server=self.master, check_res=True)

        log.info("安装Istio")
        install_cmd = "istioctl install -f {}".format(
            path_join(self.base_dir, "istio-private-deploy.yaml")
        )
        self._exec_command_to_host(cmd=install_cmd, server=self.master, check_res=True)

        log.info("检查Istio")
        time.sleep(30)
        check_cmd = "kubectl get crds | grep 'istio.io' | wc -l"
        res = self._exec_command_to_host(cmd=check_cmd, server=self.master, check_res=True)
        try:
            if int(res["stdout"]) != 21:
                log.error("Istio CRDs 非21个，错误退出")
                exit(2)
        except Exception:
            log.error("Istio CRDs非21个，错误退出:{} {}".format(res["stdout"], res["stderr"]))
            exit(2)
