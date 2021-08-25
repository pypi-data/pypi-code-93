from __future__ import absolute_import
from __future__ import unicode_literals
import os
from redis.sentinel import Sentinel
from laipvt.model.cmd import DockerImageModel
from laipvt.model.harbor import HarborModel
from laipvt.handler.confighandler import CheckResultHandler, ServerHandler
from laipvt.handler.middlewarehandler import HarborConfigHandler
from laipvt.sysutil.template import FileTemplate
from laipvt.sysutil.util import path_join, log, ssh_obj, to_object, walk_sql_path
from laipvt.handler.middlewarehandler import MiddlewareConfigHandler
from laipvt.model.cmd import ComposeModel
from laipvt.model.sql import SqlModule
from laipvt.model.server import runcmd
from laipvt.sysutil.command import CREATE_NS, ISTIO_INJECTION_NS, KUBECTL_APPLY, MKDIR_DIR, CHMOD_777, \
    HELM_LIST, HELM_INSTALL, CREATE_DB, INIT_IDENTITY_USER, HELM_INSTALL_TF_SERVICE, HELM_UPGRADE_INSTALL


class ServiceInterface:
    def __init__(self, check_result: CheckResultHandler, service_path):
        """
        check_result: 对象，前置检查结果
        service_path: 对象，服务进程详情
        """
        self.check_result = check_result
        self.service_path = service_path

        self.middleware_servers = self.check_result.servers
        self.middleware_server_list = self.middleware_servers.get_role_ip("master")

        self.middleware_cfg = to_object(MiddlewareConfigHandler("mysql").get_all_config_with_check_result())
        for k, v in self.middleware_cfg.items():
            if not self.middleware_cfg[k]["ipaddress"]:
                self.middleware_cfg[k]["ipaddress"] = self.middleware_server_list
        self.middleware_cfg.update(self.check_result.__dict__)

        self.servers = check_result.servers.get()
        self.service_info = service_path.config
        self.private_deploy_version = self.service_info.tag

        self.templates_dir = self.service_path.templates
        self.data_dir = self.service_path.data
        self.deploy_dir = self.check_result.deploy_dir

        self.service_charts_remote = path_join(self.deploy_dir, "charts")
        self.harbor_cfg = HarborConfigHandler().get_config_with_check_result()
        try:
            harbor_ip = self.harbor_cfg["harbor"]["lb"]
        except IndexError:
            harbor_ip = self.check_result.servers.get_role_ip("harbor")[0]
        self.registry_hub = "{}:{}".format(harbor_ip, self.harbor_cfg["harbor"]["nginx_harbor_proxy_port"])

        self.etcd_servers = self.check_result.servers.get_role_ip("master")
        self.etcd_endpoint = "\,".join(
            ["{}:{}".format(server, self.middleware_cfg.etcd.http_port) for server in self.etcd_servers]
        )

        self.env_k8s_config_src = path_join(self.templates_dir, "env_k8s_config")
        self.env_k8s_config_dest = path_join(self.templates_dir, "env_k8s_config_dest")
        self.env_k8s_config_remote = path_join(self.deploy_dir, "env_k8s_config_dest")

        self.nginx_compose_file = path_join(self.deploy_dir, "nginx", "docker-compose.yml")

        self.servers = self.check_result.servers.get()
        self.middleware_cfg["k8s_hosts"] = [x.ipaddress for x in self.servers]
        self.master_hosts = self.check_result.servers.get_role_obj("master")
        self.middleware_cfg["k8s_masters"] = [x.ipaddress for x in self.master_hosts]

        self.replicas = 1
        self.nodes = self.check_result.servers.get_role_obj("node")
        self.master_host = self.check_result.servers.get_role_obj("master")[0]
        self.harbor_hosts = self.check_result.servers.get_role_obj("harbor")

        self.rabbitmq_init_file_template_path = path_join(self.templates_dir, "init_rabbitmq.tmpl")
        self.rabbitmq_init_file_path = path_join(self.templates_dir, "init_rabbitmq.sh")

        self.redis_init_file_template_path = path_join(self.templates_dir, "init_redis.tmpl")
        self.redis_init_file_path = path_join(self.templates_dir, "init_redis.sh")

    def push_images(self, project):
        harbor = HarborModel(username="admin", host=self.registry_hub, password=self.middleware_cfg["harbor"]["password"])
        if project not in harbor.list_project():
            harbor.create_project(project)
        for image in os.listdir(self.service_path.images):
            image_path = path_join(self.service_path.images, image)
            log.info("将镜像push到私有仓库: {}".format(image_path))
            # print(image_path)
            docker = DockerImageModel(image=image_path, project=project, repo=self.registry_hub)
            docker.run()

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

    def _exec_command_to_host(self, cmd, server: ServerHandler, check_res=True) -> dict:
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

    def _create_namespace(self, namespaces, istio_injection_namespaces=""):
        if namespaces:
            for ns in namespaces:
                log.info("创建namespace: {}".format(ns))
                cmd = CREATE_NS.format(ns)
                self._exec_command_to_host(cmd=cmd, server=self.master_host, check_res=False)
        if istio_injection_namespaces:
            for ns in istio_injection_namespaces:
                inject_cmd = ISTIO_INJECTION_NS.format(ns)
                self._exec_command_to_host(cmd=inject_cmd, server=self.master_host, check_res=False)

    def deploy_istio(self):
        # 渲染istio配置
        FileTemplate(
            self.middleware_cfg,
            path_join(self.env_k8s_config_src, "istio"),
            path_join(self.env_k8s_config_dest, "istio")
        ).fill()
        self._send_file(src=self.env_k8s_config_dest, dest=self.env_k8s_config_remote)
        cmd = KUBECTL_APPLY.format(path_join(self.env_k8s_config_remote, "istio"))
        self._exec_command_to_host(cmd=cmd, server=self.master_host)

    def _create_logs_dir(self, project):
        log_path = os.path.join(self.deploy_dir, "Logs", project)
        log.info("创建服务日志目录:{}".format(log_path))
        cmd = [
            MKDIR_DIR.format(log_path),
            CHMOD_777.format(log_path)
        ]
        for server in self.servers:
            self._exec_command_to_host(cmd=cmd, server=server)

    def start_service(self, project, version):
        self._send_file(src=self.service_path.charts, dest=self.service_charts_remote)
        for service, processes in self.service_path.config.services.items():
            for process in processes:
                log.info("{}开始部署".format(process))

                check_cmd = HELM_LIST.format(
                    process, process
                )
                check_results = self._exec_command_to_host(cmd=check_cmd, server=self.master_host, check_res=False)
                if check_results["code"] == 0:
                    log.warning("{} helm部署记录中已经存在，不做更新，如需要更新，可以先行删除".format(process))

                else:
                    self._create_logs_dir(service)
                    file_path = os.path.join(self.service_charts_remote, process)
                    # print(file_path)
                    cmd = HELM_INSTALL.format(
                        process=process, replicas=self.replicas,
                        registry_hub=path_join(self.registry_hub, project),
                        image_name=process, image_tag=version,
                        pvt_work_dir=self.deploy_dir,
                        etcd_endpoint=self.etcd_endpoint,
                        file_path=file_path)

                    self._exec_command_to_host(cmd=cmd, server=self.master_host)

    def upgrade_service(self, project):
        for service, processes in self.service_path.config.services.items():
            for process in processes:
                log.info("{}开始部署".format(process))
                self._create_logs_dir(service)
                file_path = os.path.join(self.service_path.charts, process)
                # print(file_path)
                cmd = HELM_UPGRADE_INSTALL.format(
                    process=process, replicas=self.replicas,
                    registry_hub=path_join(self.registry_hub, project),
                    image_name=process, image_tag=self.private_deploy_version,
                    pvt_work_dir=self.deploy_dir,
                    etcd_endpoint=self.etcd_endpoint,
                    file_path=file_path)
                self._exec_command_to_host(cmd=cmd, server=self.master_host)

    def proxy_on_nginx(self, nginx_template, nginx_tmp, nginx_file_remote):
        log.info("渲染nginx代理配置文件: {} -- > {}".format(nginx_template, nginx_tmp))
        FileTemplate(self.middleware_cfg, nginx_template, nginx_tmp).fill()
        self._send_file(src=nginx_tmp, dest=nginx_file_remote)
        compose_cmd = ComposeModel(self.nginx_compose_file)
        for server in self.servers:
            self._exec_command_to_host(cmd=compose_cmd.restart(), server=server, check_res=True)

    def init_mysql(self, sql_path):
        log.info(sql_path)
        db_info = walk_sql_path(sql_path)
        if self.middleware_cfg.mysql.is_deploy:
            mysql_host = self.master_host
        else:
            mysql_host = self.middleware_cfg.mysql.ipaddress[0]
        sql = SqlModule(host=mysql_host, port=int(self.middleware_cfg.mysql.port),
                        user=self.middleware_cfg.mysql.username, passwd=self.middleware_cfg.mysql.password)
        for db_name, sql_files in db_info.items():
            create_db = CREATE_DB.format(db_name=db_name)
            sql.insert_sql(create_db)
            sql.use_db(db_name)
            for sql_file in sql_files:
                sql.import_from_file(sql_file, file_eof=";\n")

    def init_rabbitmq(self):
        log.info("渲染初始化RabbitMQ脚本: {} -- > {}".format(
            self.rabbitmq_init_file_template_path,
            self.rabbitmq_init_file_path)
        )
        FileTemplate(self.middleware_cfg, self.rabbitmq_init_file_template_path, self.rabbitmq_init_file_path).fill()

        fp = open(self.rabbitmq_init_file_path)
        log.info("开始执行初始化RabbitMQ命令")

        for cmd in fp.readlines():
            if cmd.strip():
                log.info(cmd)
                code, res = runcmd(cmd)
                if code != 0:
                    log.error(res)
                    exit(2)

    def init_redis(self):
        if self.middleware_cfg["redis"]["is_deploy"]:
            # 如果是自建redis服务，连接哨兵服务器，获取master节点地址
            pool = []
            for host in self.middleware_servers.get_role_obj("master"):
                redis_endpoint = (host.ipaddress, self.middleware_cfg["redis"]["port_sentinel"])
                pool.append(redis_endpoint)
            sentinel = Sentinel(pool, socket_timeout=0.5)
            # 获取主服务器地址
            master_address = sentinel.discover_master(self.middleware_cfg.redis.master_name)[0]
            # server_object_list = self.check_result.servers.search_server(key="ipaddress", value=master)
            self.middleware_cfg["redis"]["master_address"] = master_address

        log.info("渲染初始化redis脚本: {} -- > {}".format(
            self.redis_init_file_template_path,
            self.redis_init_file_path)
        )
        FileTemplate(self.middleware_cfg, self.redis_init_file_template_path, self.redis_init_file_path).fill()

        fp = open(self.redis_init_file_path)
        log.info("开始执行初始化redis命令")

        for cmd in fp.readlines():
            if cmd.strip():
                log.info(cmd)
                code, res = runcmd(cmd)
                if code != 0:
                    log.error(res)
                    exit(2)

    def init_identity_user(self):
        init_user_cmd = INIT_IDENTITY_USER
        self._exec_command_to_host(cmd=init_user_cmd, server=self.servers[0], check_res=False)

    def deploy_tf_service(self, module_name, tf_image_name):
        # self._send_file(src=self.service_path.charts, dest=self.service_charts_remote)
        log.info("{}开始部署".format(module_name))
        check_cmd = HELM_LIST.format(
            module_name, module_name
        )
        check_results = self._exec_command_to_host(cmd=check_cmd, server=self.master_host, check_res=False)
        if check_results["code"] == 0:
            log.warning("{} helm部署记录中已经存在，不做更新，如需要更新，可以先行删除".format(module_name))

        else:
            file_path = os.path.join(self.service_charts_remote, module_name)
            # print(file_path)
            tag = "2.4.0-cpu" if self.service_path.config.machine_type == "cpu" else "2.4.0-gpu"
            cmd = HELM_INSTALL_TF_SERVICE.format(
                process=module_name, replicas=self.replicas,
                registry_hub=path_join(self.registry_hub, "middleware"),
                image_name=tf_image_name, image_tag=tag,
                pvt_work_dir=self.deploy_dir,
                etcd_endpoint=self.etcd_endpoint,
                file_path=file_path)

            self._exec_command_to_host(cmd=cmd, server=self.master_host)
