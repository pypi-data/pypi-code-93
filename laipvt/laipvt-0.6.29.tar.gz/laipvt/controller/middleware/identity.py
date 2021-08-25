from __future__ import absolute_import
from __future__ import unicode_literals

import requests
from laipvt.interface.middlewareinterface import MiddlewareInterface
from laipvt.handler.middlewarehandler import IdentityConfigHandler
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.sysutil.template import FileTemplate
from laipvt.sysutil.util import path_join, log, status_me, walk_sql_path
from laipvt.sysutil.conf import YamlConfig
from laipvt.sysutil.gvalue import LAIPVT_BASE_DIR
from laipvt.model.sql import SqlModule
from laipvt.sysutil.command import CREATE_DB
from laipvt.sysutil.util import get_yaml_config


class IdentityController(MiddlewareInterface):
    def __init__(self, result: CheckResultHandler, handler: IdentityConfigHandler, template: str):
        super(IdentityController, self).__init__(result, handler, template)
        self.identity_conf_tmp = path_join("/tmp", "appsettings.json")
        self.identity_conf_template = path_join(self.template, "config.tmpl")
        self.identity_conf_file = path_join(self.base_dir, "config/appsettings.json")
        self.identity_nginx_tmp = path_join("/tmp", "nginx-identity.conf")
        self.identity_nginx_template = path_join(self.template, "nginx-identity.tmpl")
        self.identity_sql_template = path_join(self.template, "identity_sqls")
        self.log_path = path_join(self.base_dir, "logs")
        self.identity_sql_file = path_join(self.base_dir)
        self.identity = IdentityConfigHandler()
        self.cfg = YamlConfig(path_join(LAIPVT_BASE_DIR, "middleware"), suffix="yaml").read_dir()
        self.cfg["identity"] = self.identity.get_config_with_check_result()["identity"]
        self.cfg["identity"]["userstore"] = "Express"
        self.cfg["identity"]["ipaddress"] = self.handler.cfg["ipaddress"]
        # self.cfg["redis"]["ipaddress"] = self.handler.cfg["ipaddress"]
        self.user = self.cfg["mysql"]["username"]
        self.password = self.cfg["mysql"]["password"]
        self.port = int(self.cfg["mysql"]["port"])
        self.cfg.update(self.check_result.__dict__)
    def _generic_config(self):
        log.info("渲染 identity 配置文件")
        if self.cfg["mysql"]["is_deploy"]:
            self.cfg["mysql"]["ipaddress"] = self.handler.cfg["ipaddress"]
        if self.cfg["redis"]["is_deploy"]:
            self.cfg["redis"]["ipaddress"] = self.handler.cfg["ipaddress"]
        self.cfg['is_standalone'] = False
        if len(self.cfg["mysql"]["ipaddress"]) == 1:
            self.cfg['is_standalone'] = True
        for num_id in range(len(self.master_server)):
            self.cfg["localhost"] = self.master_server[num_id].ipaddress
            FileTemplate(self.cfg, self.identity_conf_template, self.identity_conf_tmp).fill()
            self.send_config_file(self.master_server[num_id], self.identity_conf_tmp, self.identity_conf_file)
            self.send_config_file(self.master_server[num_id], self.identity_sql_template, self.identity_sql_file)
        self.generate_docker_compose_file(self.cfg)

    def _proxy_on_nginx(self):
        log.info("渲染 nginx identity 代理配置文件")
        FileTemplate(self.cfg, self.identity_nginx_template, self.identity_nginx_tmp).fill()
        self.update_nginx_config()

    def _check(self):
        super().wait_for_service_start()
        for i in range(len(self.master_server)):
            try:
                log.info("检查 {IP}:{PORT} 上的 Identity 健康性...".format(IP=self.master_server[i].ipaddress, PORT=self.cfg["identity"]["nginx_proxy_port"]))
                requests.get(
                    "http://{IP}:{PORT}".format(
                        IP=self.master_server[i].ipaddress, PORT=self.cfg["identity"]["nginx_proxy_port"]
                    )
                )
                log.info("Identity检查通过")
            except Exception as e:
                log.error(e)
                log.error("{IP} 上的 Identity 服务异常".format(IP=self.master_server[i].ipaddress))
                exit(2)

    def init_mysql(self):
        if not self.cfg["mysql"]["is_deploy"]:
            self.master_host = self.cfg["mysql"]["ipaddress"][0]
        else:
            self.cfg["mysql"]["ipaddress"] = self.handler.cfg["ipaddress"][0]
            self.master_host = self.cfg["mysql"]["ipaddress"]
        log.info("初始化mysql identity数据表")
        db_info = walk_sql_path(path_join(self.template, "identity_sqls"))
        sql = SqlModule(host=self.master_host, port=self.port, user=self.user, passwd=self.password)
        for db_name, sql_files in db_info.items():
            create_db = CREATE_DB.format(db_name=db_name)
            sql.insert_sql(create_db)
            sql.use_db(db_name)
            for sql_file in sql_files:
                sql.import_from_file(sql_file, file_eof=";\n")
        self.create_logs_dir(self.log_path)

    @status_me("middleware")
    def deploy_identity(self):
        self._generic_config()
        self._proxy_on_nginx()
        self.send_docker_compose_file()
        self.init_mysql()
        self.start()
        self._check()

    @status_me("middleware")
    def update_identity_config(self):
        self.cfg["identity"]["userstore"] = "Commander"
        self._generic_config()
        self.send_docker_compose_file()
        self.restart()

    def deploy(self):
        self.deploy_identity()
