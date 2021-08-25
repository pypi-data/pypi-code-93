from __future__ import absolute_import
from __future__ import unicode_literals

import os
import time

import requests
from minio import Minio

from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.model.sql import SqlModule
from laipvt.sysutil.command import COMMANDER_UPGRADE_INSTALL, CREATE_DB, HELM_INSTALL_COMMANDER, HELM_LIST
from laipvt.sysutil.util import log, path_join, status_me, walk_sql_path


class CommanderController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(CommanderController, self).__init__(check_result, service_path)
        self.namespaces = ["rpa", "proxy"]
        self.istio_injection_namespaces = ["rpa", "mid", ]
        self.project = "rpa"

        self.nginx_template = path_join(self.templates_dir, "nginx/http/nginx-commander.tmpl")
        self.nginx_tmp = path_join("/tmp", "nginx-commander.conf")
        self.nginx_file_remote = path_join(self.deploy_dir, "nginx/http/nginx-commander.conf")
        if self.middleware_cfg["mysql"]["is_deploy"]:
            self.mysql_host = "mysql.default.svc"
            self.mysql_port = 3306
        else:
            self.mysql_host = self.middleware_cfg["mysql"]["ipaddress"][0]
            self.mysql_port = self.middleware_cfg["mysql"]["port"]

        self.protocol = "https" if self.middleware_cfg["config"]["deploy_https"] else "http"
        self.tenant_url = "{protocol}://{host}:{port}".format(protocol=self.protocol,
                                                              host=self.middleware_cfg.nginx.lb,
                                                              port=self.middleware_cfg.nginx.commander_tenant_port)

    @status_me("commander")
    def init_commander_mysql(self):
        sql_path = self.service_path.sqls
        log.info(sql_path)
        db_info = walk_sql_path(sql_path)
        sql = SqlModule(host=self.middleware_cfg.mysql.ipaddress[0], port=int(self.middleware_cfg.mysql.port),
                        user=self.middleware_cfg.mysql.username, passwd=self.middleware_cfg.mysql.password)
        for db_name, sql_files in db_info.items():
            create_db = CREATE_DB.format(db_name=db_name)
            sql.insert_sql(create_db)
            sql.import_from_dir(db_name, path_join(sql_path, db_name))

    # sql.use_db(db_name)
    # for sql_file in sql_files:
    #    sql.import_from_file_commander(sql_file, file_eof=";")

    @status_me("commander")
    def push_commander_images(self):
        self.push_images(self.project)

    def start_service(self, project, version):
        self._send_file(src=self.service_path.charts, dest=self.service_charts_remote)
        for service, processes in self.service_path.config.services.items():
            for process in processes:
                log.info("{}开始部署".format(process))

                check_cmd = HELM_LIST.format(process, process)
                check_results = self._exec_command_to_host(cmd=check_cmd, server=self.servers[0], check_res=False)
                if check_results["code"] == 0:
                    log.warning("{} helm部署记录中已经存在，不做更新，如需要更新，可以先行删除".format(process))

                else:
                    self._create_logs_dir(service)
                    file_path = os.path.join(self.service_charts_remote, process)
                    # print(file_path)
                    if self.middleware_cfg["redis"]["is_deploy"]:
                        config_server = "\,".join(
                                [
                                        "{}:{}\,serviceName={}\,allowAdmin=true".format(
                                                server,
                                                self.middleware_cfg["redis"]["port_sentinel"],
                                                self.middleware_cfg["redis"]["master_name"]
                                        ) for server in self.middleware_servers.get_role_ip("master")
                                ]
                        )
                    else:
                        config_server = "{}:{}".format(self.middleware_cfg["redis"]["ipaddress"][0],
                                                       self.middleware_cfg["redis"]["port"])

                    oidc_authority = "{protocol}://{identity_lb}:{identity_port}".format(
                            protocol=self.protocol,
                            identity_lb=self.middleware_cfg["identity"]["lb"],
                            identity_port=self.middleware_cfg["identity"]["nginx_proxy_port"])

                    cmd = HELM_INSTALL_COMMANDER.format(
                            process=process, replicas=self.replicas,
                            registry_hub=path_join(self.registry_hub, project),
                            image_name=process, image_tag=version,
                            pvt_work_dir=self.deploy_dir,
                            config_server=config_server,
                            config_server_passwd=self.middleware_cfg["redis"]["password"],
                            mysql_host=self.mysql_host, mysql_port=self.mysql_port,
                            mysql_user=self.middleware_cfg["mysql"]["username"],
                            mysql_password=self.middleware_cfg["mysql"]["password"],
                            etcd_endpoint=self.etcd_endpoint, mysql_database="uibot_global",
                            mysql_charset="utf8mb4",
                            oidc_authority=oidc_authority,
                            oidc_secret="laiye",
                            file_path=file_path)

                    self._exec_command_to_host(cmd=cmd, server=self.servers[0])

    def upgrade_service(self, project):
        for service, processes in self.service_path.config.services.items():
            for process in processes:
                log.info("{}开始更新".format(process))
                self._create_logs_dir(service)
                file_path = os.path.join(self.service_path.charts, process)

                if self.middleware_cfg["redis"]["is_deploy"]:
                    config_server = "\,".join(
                            [
                                    "{}:{}\,serviceName={}\,allowAdmin=true".format(
                                            server,
                                            self.middleware_cfg["redis"]["port_sentinel"],
                                            self.middleware_cfg["redis"]["master_name"]
                                    ) for server in self.middleware_servers.get_role_ip("master")
                            ]
                    )
                else:
                    config_server = "{}:{}".format(self.middleware_cfg["redis"]["ipaddress"][0],
                                                   self.middleware_cfg["redis"]["port"])

                cmd = COMMANDER_UPGRADE_INSTALL.format(
                        process=process, replicas=self.replicas,
                        registry_hub=path_join(self.registry_hub, project),
                        image_name=process, image_tag=self.private_deploy_version,
                        pvt_work_dir=self.deploy_dir,
                        config_server=config_server,
                        config_server_passwd=self.middleware_cfg["redis"]["password"],
                        mysql_host=self.mysql_host, mysql_port=self.mysql_port,
                        mysql_user=self.middleware_cfg["mysql"]["username"],
                        mysql_password=self.middleware_cfg["mysql"]["password"],
                        etcd_endpoint=self.etcd_endpoint, mysql_database="uibot_global",
                        mysql_charset="utf8mb4",
                        oidc_authority="http://{}:{}".format(
                                self.middleware_cfg["identity"]["lb"],
                                self.middleware_cfg["identity"]["nginx_proxy_port"]),
                        oidc_secret="laiye",
                        file_path=file_path)

                self._exec_command_to_host(cmd=cmd, server=self.servers[0])

    @status_me("commander")
    def start_commander_service(self):
        self.start_service(project=self.project, version=self.private_deploy_version)

    @status_me("commander")
    def commander_proxy_on_nginx(self):
        self.proxy_on_nginx(self.nginx_template, self.nginx_tmp, self.nginx_file_remote)

    @status_me("commander")
    def create_namespace(self):
        self._create_namespace(
                namespaces=self.namespaces,
                istio_injection_namespaces=self.istio_injection_namespaces
        )

    @status_me("commander")
    def init_minio_data(self):
        for bucket in self.service_info.buckets:
            try:
                if self.middleware_cfg.minio.is_deploy:
                    endpoint = "{}:{}".format(self.middleware_cfg.minio.lb, self.middleware_cfg.minio.nginx_proxy_port)
                else:
                    endpoint = "{}:{}".format(self.middleware_cfg.minio.ipaddress[0], self.middleware_cfg.minio.port)
                cli = Minio(
                        endpoint,
                        self.middleware_cfg.minio.username,
                        self.middleware_cfg.minio.password,
                        secure=False
                )
                if not cli.bucket_exists(bucket):
                    cli.make_bucket(bucket)
            # policy_read_only = {
            #     "Version": "2012-10-17",
            #     "Statement": [
            #         {
            #             "Action": [
            #                 "s3:GetObject"
            #             ],
            #             "Effect": "Allow",
            #             "Principal": "*",
            #             "Resource": [
            #                 "arn:aws:s3:::{}/*".format(bucket)
            #             ],
            #             "Sid": ""
            #         }
            #     ]
            # }
            # cli.set_bucket_policy(bucket, json.dumps(policy_read_only))

            except Exception as e:
                log.error("Minio初始化数据失败:{}".format(e))
                exit(2)

    def login_tenant(self):
        log.info("登录租户管理平台")
        login_account_url = "{tenant_url}/api/tenant/account/getCurrentInfo".format(tenant_url=self.tenant_url)
        AccountResponse = requests.get(login_account_url)  # goto get the xsrf-token for post request.
        preCookies = AccountResponse.cookies  # include xsrf-token for future use.
        XsrfTOKEN = preCookies.get('XSRF-TOKEN')  # need this to header.
        loginHeaders = {
                'X-XSRF-TOKEN': XsrfTOKEN,
                'Referer':      self.tenant_url
        }
        data = {'userName': 'admin', 'password': '123456'}
        login_url = "{tenant_url}/api/global/account/webLogin".format(tenant_url=self.tenant_url)
        response = requests.post(login_url, json=data, headers=loginHeaders, cookies=preCookies,
                                 verify=False)
        auth_cookie = ''
        # print(response)
        ret = response.json()
        if ret['code'] == 0:
            auth_cookies = preCookies
            auth_cookies.set('GlobalUser', response.cookies.get('GlobalUser'))
            # f"GlobalUser={cookies.get('GlobalUser', None)}"
            # log.info(auth_cookies)
            log.info("Login succeed")
            return auth_cookies, loginHeaders
        else:
            log.error("Login error!")
            exit(2)

    def tenant_init_mysql(self, auth_cookies, login_headers):
        log.info("租户平台配置MySql数据库")
        db_mysql = {
                "name":     "mysql-1",
                "host":     self.mysql_host,
                "port":     self.mysql_port,
                "dbName":   "uibot_rpa",
                "userName": self.middleware_cfg.mysql.username,
                "password": self.middleware_cfg.mysql.password,
                "type":     "10"
        }
        mysql_url = "{tenant_url}/api/global/database/create".format(tenant_url=self.tenant_url)
        resp1 = requests.post(mysql_url, json=db_mysql, cookies=auth_cookies, headers=login_headers, verify=False)
        json_resp1 = resp1.json()
        if json_resp1['code'] == 0:
            log.info("配置MySQL数据库完成")
        else:
            log.error("配置MySQL数据库失败")
            exit(2)

    @status_me("commander")
    def init_tenant(self):
        counter = 0
        succeed = False
        # 重试 10 次，如果还是不成功就报错
        while not succeed and counter < 100:
            time.sleep(5)
            try:
                auth_cookies, loginHeaders = self.login_tenant()
                self.tenant_init_mysql(auth_cookies=auth_cookies, login_headers=loginHeaders)
                succeed = True
            except Exception as e:
                # log.error(e)
                succeed = False
                counter += 1
        if not succeed:
            log.error("登录租户系统失败，请检查容器是否启动。")
            exit(2)

    def run(self):
        self.init_commander_mysql()
        self.init_rabbitmq()
        self.init_minio_data()
        self.init_redis()
        self.create_namespace()
        self.push_commander_images()
        self.deploy_istio()
        self.start_commander_service()
        self.commander_proxy_on_nginx()
        self.init_tenant()

