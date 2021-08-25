from __future__ import absolute_import
from __future__ import unicode_literals

import os
import time
from laipvt.handler.confighandler import CheckResultHandler, ServerHandler
from laipvt.handler.packagehandler import KubePackageHandler
from laipvt.handler.kubehandler import KubeConfigHandler
from laipvt.sysutil.util import path_join, ssh_obj, log, status_me

from laipvt.sysutil.template import FileTemplate
from laipvt.model.cmd import KubeModel
from laipvt.sysutil.command import BASH_RUN, CP_KUBEADM, KUBE_INIT, CREATE_KUBE_DIR, CP_KUBE_CONFIG, \
    KUBECTL_COMPLETION, KUBECTL_APPLY, KUBEADM_TOKEN_CREATE, TAR_KUBE_CRETS, UNTAR_KUBE_CRETS, ADD_MASTER_SUFFIX, \
    TAINT_MASTER, HELM_PATH, TILLER_PATH, TILLER_SERVICE_PATH, CHMOD_EXECUTE, SYSTEMCTL_DAEMON_RELOAD, SYSTEMCTL_START, \
    SYSTEMCTL_ENABLE, ISTIOCTL_PATH, ISTIOCTL_INSTALL, CHECK_ISTIO


class KubeInterface:
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

        self.master = result.servers.get_role_obj("master")[0]
        self.master_servers = result.servers.get_role_obj("master")
        self.all_servers = result.servers.get_role_obj("master")
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

    @status_me("basesystem")
    def add_hosts(self):
        self._generate_file(template_file=self.hosts_file_template, dest_file=self.hosts_file)
        self._send_file(self.hosts_file, "/etc/hosts")

    @status_me("basesystem")
    def install_rpms(self):
        self._send_file(self.info["k8s-rpms"], path_join(self.base_dir, "k8s-rpms"))
        cmd_list = [
            # "rpm -ivUh {}/*.rpm --force --nodeps".format(path_join(self.base_dir, "k8s-rpms")),
            CP_KUBEADM.format(path_join(self.base_dir, "k8s-rpms"))
        ]
        for server in self.servers:
            log.info("{} 替换kubeadm执行文件".format(server.ipaddress))
            self._exec_command_to_host(cmd=cmd_list, server=server, check_res=False)

    @status_me("basesystem")
    def system_prepare(self):
        self._generate_file(template_file=self.system_init_template, dest_file=self.system_init_file)
        self._send_file(self.system_init_file, path_join(self.base_dir, "init_env.sh"))
        cmd = BASH_RUN.format(path_join(self.base_dir, "init_env.sh"))
        for server in self.servers:
            log.info("{}执行初始化脚本{}".format(server.ipaddress, path_join(self.base_dir, "init_env.sh")))
            self._exec_command_to_host(cmd=cmd, server=server)

    @status_me("basesystem")
    def init_primary_master(self):
        log.info("初始化master主节点")
        self._generate_file(template_file=self.kube_admin_file_template, dest_file=self.kube_admin_file)
        self._send_file(self.kube_admin_file, path_join(self.base_dir, "admin.conf"))
        cmd = KUBE_INIT.format(path_join(self.base_dir, "admin.conf"))
        self._exec_command_to_host(cmd=cmd, server=self.master)
        # cmd = [
        #     CREATE_KUBE_DIR,
        #     CP_KUBE_CONFIG
        # ]
        # self._exec_command_to_host(cmd=cmd, server=self.master)

    def cp_kube_config(self):
        log.info("拷贝kubectl config文件")
        cmd = [
            CREATE_KUBE_DIR,
            CP_KUBE_CONFIG
        ]
        for server in self.all_servers:
            self._exec_command_to_host(cmd=cmd, server=server, check_res=False)

    @status_me("basesystem")
    def kube_completion(self):
        log.info("k8s命令自动补全")
        cmd = KUBECTL_COMPLETION
        self._exec_command_to_host(cmd=cmd, server=self.master)

    @status_me("basesystem")
    def install_network_plugin(self):
        log.info("部署flannel网络插件")
        self._generate_file(template_file=self.flannel_template, dest_file=self.flannel_file)
        self._send_file(self.flannel_file, path_join(self.base_dir, "kube-flannel.yaml"))
        cmd = KUBECTL_APPLY.format(path_join(self.base_dir, "kube-flannel.yaml"))
        self._exec_command_to_host(cmd=cmd, server=self.master)

    def get_kube_admin_join_command(self) -> str:
        cmd = KUBEADM_TOKEN_CREATE.format(path_join(self.base_dir, "admin.conf"))
        res = self._exec_command_to_host(cmd=cmd, server=self.master)

        if res["code"] == 0 and "kubeadm join" in res["stdout"]:
            return res["stdout"].strip().split("\n")[-1]
        else:
            raise Exception("生成Node节点join命令失败：\n {} {}".format(res["stdout"], res["stderr"]))

    @status_me("basesystem")
    def join_master(self):
        # 1、连接master-01，打包需要拷贝的证书配置，拉到本地
        log.info("将master-01 kubernetes证书拉回本地，发送至其余master节点")
        cmd = TAR_KUBE_CRETS.format(self.remote_pki_path)
        self._exec_command_to_host(cmd=cmd, server=self.master)
        self._get_file(src=self.remote_pki_path, dest=path_join(self.local_tmp, self.pki_tar_name), server=self.master)

        other_masters = []
        for server in self.master_servers:
            if server.ipaddress != self.master.ipaddress:
                other_masters.append(server)

        join_cmd = self.get_kube_admin_join_command()
        for i, server in enumerate(other_masters):
            log.info("将kubernetes证书，发送至master节点{},并解压".format(server.ipaddress))
            self._send_file(src=path_join(self.local_tmp, self.pki_tar_name), dest=self.remote_pki_path)
            cmd = UNTAR_KUBE_CRETS.format(self.remote_pki_path)
            self._exec_command_to_host(cmd=cmd, server=server)

            log.info("加入{}master节点".format(server.ipaddress))
            node_name = "master-0{}".format(i + 2)
            cmd = ADD_MASTER_SUFFIX.format(join_cmd, node_name)
            self._exec_command_to_host(cmd=cmd, server=server)

    @status_me("basesystem")
    def join_node(self):
        # for i, server in enumerate(self.result.servers.get_role_obj("node")): # 4
        #     if server.ipaddress in self.result.servers.get_role_ip("master"): # 3
        #         log.info("master")
        #         node_name = "master-0{}".format(i + 1)
        #         cmd = TAINT_MASTER.format(node_name)
        #         self._exec_command_to_host(cmd=cmd, server=self.master)
        #     else:
        #         cmd = self.get_kube_admin_join_command()
        #         self._exec_command_to_host(cmd=cmd, server=server)

        node = list(set(self.result.servers.get_role_ip("node")) - set(self.result.servers.get_role_ip("master")))
        if len(node) <= 3:
            for i, server in enumerate(self.result.servers.get_role_obj("master")):
                node_name = "master-0{}".format(i + 1)
                cmd = TAINT_MASTER.format(node_name)
                self._exec_command_to_host(cmd=cmd, server=self.master)
        if len(node) > 0:
            for server in self.result.servers.get_role_obj("node"):
                if server.ipaddress in node:
                    cmd = self.get_kube_admin_join_command()
                    self._exec_command_to_host(cmd=cmd, server=server)

    def check_cluster_status(self) -> bool:
        kube = KubeModel()
        status = kube.get_node_status()
        print(status)
        for i in status:
            if i["node_status"] != "Ready":
                return False
        return True

    @status_me("basesystem")
    def install_helm(self):
        self._send_file(src=path_join(self.info.plugin.helm, "bin/helm"), dest=HELM_PATH)
        self._send_file(src=path_join(self.info.plugin.helm, "bin/tiller"), dest=TILLER_PATH)
        self._send_file(
            src=path_join(self.info.plugin.helm, "service/tiller.service"),
            dest=TILLER_SERVICE_PATH
        )
        cmd_list = [
            CHMOD_EXECUTE.format(HELM_PATH), CHMOD_EXECUTE.format(TILLER_PATH),
            SYSTEMCTL_DAEMON_RELOAD, SYSTEMCTL_START.format("tiller.service"), SYSTEMCTL_ENABLE.format("tiller.service")
        ]
        self._exec_command_to_host(cmd=cmd_list, server=self.master, check_res=True)

    @status_me("basesystem")
    def install_istio(self):
        self._send_file(src=path_join(self.info.plugin.istio, "bin/istioctl"), dest=ISTIOCTL_PATH)

        self._generate_file(template_file=self.istio_template, dest_file=self.istio_file)
        istio_remote_file = path_join(self.base_dir, "istio-private-deploy.yaml")
        self._send_file(src=self.istio_file, dest=istio_remote_file)

        cmd = CHMOD_EXECUTE.format(ISTIOCTL_PATH)
        self._exec_command_to_host(cmd=cmd, server=self.master, check_res=True)

        log.info("安装Istio")
        install_cmd = ISTIOCTL_INSTALL.format(path_join(self.base_dir, "istio-private-deploy.yaml"))
        self._exec_command_to_host(cmd=install_cmd, server=self.master, check_res=True)

        log.info("检查Istio")
        time.sleep(30)
        check_cmd = CHECK_ISTIO
        res = self._exec_command_to_host(cmd=check_cmd, server=self.master, check_res=True)
        try:
            if int(res["stdout"]) != 21:
                log.error("Istio CRDs 非21个，错误退出")
                exit(2)
        except Exception:
            log.error("Istio CRDs非21个，错误退出:{} {}".format(res["stdout"], res["stderr"]))
            exit(2)
