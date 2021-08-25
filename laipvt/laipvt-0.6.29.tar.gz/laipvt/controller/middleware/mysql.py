from __future__ import absolute_import
from __future__ import unicode_literals
from laipvt.interface.middlewareinterface import MiddlewareInterface
from laipvt.handler.middlewarehandler import MysqlConfigHandler, MinioConfigHandler
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.sysutil.template import FileTemplate
from laipvt.sysutil.util import walk_sql_path, path_join, log, ssh_obj, status_me
from laipvt.model.sql import SqlModule
from laipvt.model.server import ServerModel
from laipvt.sysutil.conf import YamlConfig
from laipvt.sysutil.gvalue import LAIPVT_BASE_DIR


class MysqlController(MiddlewareInterface):
    def __init__(self, result: CheckResultHandler, handler: MysqlConfigHandler, template: str):
        super(MysqlController, self).__init__(result, handler, template)
        self.mysql_cfg = YamlConfig(path_join(LAIPVT_BASE_DIR, "middleware"), suffix="yaml").read_dir()
        self.mysql_cfg["mysql"] = MysqlConfigHandler().get_config_with_check_result()["mysql"]
        self.user = self.mysql_cfg["mysql"]["username"]
        self.password = self.mysql_cfg["mysql"]["password"]
        self.port = int(self.mysql_cfg["mysql"]["port"])
        self.master_host = self.master_server[0].ipaddress
        self.mysql_nginx_tmp = path_join("/tmp", "nginx-mysql.conf")
        self.proxysql_conf_tmp = path_join("/tmp", "proxysql.cnf")
        self.proxysql_conf_template = path_join(self.template, "proxysql.cnf")
        self.mysql_nginx_template = path_join(self.template, "nginx-mysql.tmpl")
        self.proxysql_conf_file = path_join(self.base_dir, "conf", "proxysql.cnf")
        self.template_file_name = ("mysql_master.cnf", "mysql_slave1.cnf", "mysql_slave2.cnf")
        self.mysql_config_file = path_join(self.base_dir, "conf", "{}.conf".format(self.middleware_name))
        self.template_sql = path_join(self.template, "mgr_init")
        self.template_sql_name = ("fill_slave_join_mgr.sql", "fill_create_mgr.sql", "fill_proxysql_join_mgr.sql")
        self.mysql_service_file_template = path_join(self.template, "mysql_service.tmpl")
        self.mysql_service_file_dest = path_join("/tmp", "mysql_service.yaml")
        self.mysql_service_file_remote = path_join(self.base_dir, "svc", "mysql_service.yaml")
        if self.mysql_cfg["mysql"]["is_deploy"]:
            self.mysql_cfg["mysql"]["ipaddress"] = self.handler.cfg["ipaddress"]
        self.mysql_cfg["minio"]["ipaddress"] = self.handler.cfg["ipaddress"]
        self.mysql_cfg["mysql"]["data_dir"] = path_join(self.base_dir, "data/mysql")
        self.backup_conf_template = path_join(self.template, "backup.cnf")
        self.backup_conf_tmp = path_join("/tmp", "backup.cnf")
        self.backup_conf_file = path_join(self.base_dir, "conf", "backup.conf")
        self.backup_sh_template = path_join(self.template, "backup.sh")
        self.backup_sh_file = path_join(self.base_dir, "backup.sh")

    def gen_proxy_sql_config(self):
        log.info("渲染分发Proxysql配置文件")
        server = ServerModel(self.master_server)
        try:
            FileTemplate(self.mysql_cfg, self.proxysql_conf_template, self.proxysql_conf_tmp).fill()
            server.send_file(self.proxysql_conf_tmp, self.proxysql_conf_file)
        except Exception as e:
            log.error(e)
            exit()
        finally:
            server.close()

    def _fill_init_sql(self):
        if self.mysql_cfg["is_standalone"]:
            return
        for file in self.template_sql_name:
            sql_file = path_join(self.template_sql, file)
            FileTemplate(self.mysql_cfg, sql_file, sql_file.replace("fill_", "")).fill()
        self.gen_proxy_sql_config()
        self._proxy_on_nginx()

    def _generic_config(self):
        log.info("渲染Mysql配置文件")
        if len(self.master_server) == 1:
            log.info("使用单机模式部署")
            self.mysql_cfg["is_standalone"] = True
        elif len(self.master_server) == 3:
            log.info("使用集群模式部署")
            self.mysql_cfg["is_standalone"] = False
        else:
            log.info("集群模式需要3台主机,请检查前置检查配置是否正确")
            exit(2)
        for num_id in range(len(self.master_server)):
            self.mysql_cfg["server_id"] = 100 + num_id
            src = path_join(self.template, self.template_file_name[num_id])
            dest = path_join("/tmp", self.template_file_name[num_id])
            FileTemplate(self.mysql_cfg, src, dest).fill()
            self.mysql_cfg["mysql"]["ip"] = self.master_server[num_id].ipaddress
            FileTemplate(self.mysql_cfg, self.backup_conf_template, self.backup_conf_tmp).fill()
            self.send_config_file(self.master_server[num_id], dest, self.mysql_config_file)
            self.send_config_file(self.master_server[num_id], self.backup_conf_tmp, self.backup_conf_file)
            self.send_config_file(self.master_server[num_id], self.backup_sh_template, self.backup_sh_file)
        self.generate_docker_compose_file(self.mysql_cfg)

    def _proxy_on_nginx(self):
        log.info("渲染Mysql代理配置文件")
        for num_id in range(len(self.master_server)):
            FileTemplate(self.mysql_cfg, self.mysql_nginx_template, self.mysql_nginx_tmp).fill()
        self.update_nginx_config()

    def _create_mgr_cluster(self):
        """
        构建mysqlmgr集群
        :return:
        """
        super().wait_for_service_start()
        if self.mysql_cfg["is_standalone"]:
            return True
        log.info("构建Proxysql MysqlMgr 集群")
        sql = SqlModule(host=self.master_host, port=self.port, user=self.user, passwd=self.password)
        sql.import_from_file(path_join(self.template, "mgr_init/create_mgr.sql"), file_eof=";" )
        sql.import_from_file(path_join(self.template, "mgr_init/view.sql"), file_eof="$$")

        log.info("Slave 节点加入mgr集群")
        for server in self.master_server[1:]:
            sql = SqlModule(host=server.ipaddress, port=self.port, user=self.user, passwd=self.password)
            sql.import_from_file(path_join(self.template, "mgr_init/slave_join_mgr.sql"), file_eof=";")

        log.info("Proxysql 添加mgr节点")
        sql = SqlModule(host=self.master_host, port=6032, user="cluster", passwd="123456", connect_timeout=5)
        sql.import_from_file(path_join(self.template, "mgr_init/proxysql_join_mgr.sql"), file_eof=";")

    def _check(self):
        super().wait_for_service_start()
        for server in self.master_server:
            if not self.mysql_cfg["is_standalone"]:
                self.port = int(self.mysql_cfg["mysql"]["proxysql_port"])
            try:
                log.info("检查 {IP}:{PORT} 上的 MySQL 健康性".format(IP=server.ipaddress, PORT=self.port))
                SqlModule(
                    host=server.ipaddress, port=self.port,
                    user=self.user, passwd=self.password,
                    db="test", charset='utf8'
                )
                self._read_write_test(server.ipaddress, self.port)
            except Exception as e:
                log.error(e)
                log.error("{IP}:{PORT} 上的 MySQL 服务异常".format(IP=server.ipaddress, PORT=self.port))
                exit(2)
        # if not self.handler.cfg["is_standalone"]:
        #     self._read_write_test(self.master_host, self.handler.cfg["mysql_load"]["nginx_proxy_port"])

    def _read_write_test(self, Ipaddress, Port):
        log.info("测试验证Mysql数据库读写")
        try:
            sql = SqlModule(host=Ipaddress, port=Port, user=self.user, passwd=self.password)
            sql.insert_sql("create table test.student (id int(10),name char(100),primary key (ID));")
            sql.insert_sql("insert into test.student (id,name)values(1,'Reading and writing tests');")
            sql.select("select * from test.student;")
            sql.insert_sql("drop table test.student;")
            log.info("Mysql {IP}:{PORT} 读写测试成功...".format(IP=Ipaddress, PORT=Port))

        except Exception as e:
            log.info("Mysql {IP}:{PORT} 读写测试失败...".format(IP=Ipaddress, PORT=Port))
            log.error(e)
            exit(2)

    def init(self, path):
        log.info(path)
        db_info = walk_sql_path(path)
        for db_name, sql_files in db_info.items():
            sql = SqlModule(host=self.master_host, port=self.port, user=self.user, passwd=self.password)
            create_db = "create database If Not Exists {db_name} DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_general_ci".format(
                db_name=db_name
            )
            sql.insert_sql(create_db)
            for sql_file in sql_files:
                sql = SqlModule(host=self.master_host, port=self.port, user=self.user, passwd=self.password, db=db_name)
                sql.import_from_file(sql_file, file_eof=";\n")

    def run_backup_crontab(self):
        log.info("配置Mysql 备份定时任务")
        self.crontab_task = "01 00 * * * sudo docker run --rm  " \
                            "-v {}:/mysql-backup  -v {}:/var/lib/mysql" \
                            " -v {}:/backup.sh -v {}:/backup.conf  {}:{}/middleware/mysql_xtrabackup:5.7.32 /bin/bash "\
                            "-c '/backup.sh /backup.conf /mysql-backup/backup.log &>> /mysql-backup/backup.log'"
        self.crontab_task = self.crontab_task.format(
            path_join(self.base_dir, "mysql-backup"),
            path_join(self.base_dir, "data/mysql"),
            self.backup_sh_file,
            self.backup_conf_file,
            self.mysql_cfg["mysql"]["harbor_ipaddress"],
            self.mysql_cfg["mysql"]["nginx_harbor_proxy_port"]
            )
        self.chmod_backupsh = "chmod +x {}".format(self.backup_sh_file)

        for server in self.master_server:
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            cmd_list = [self.chmod_backupsh,
                        "systemctl restart crond",
                        "echo \"{}\" >> /var/spool/cron/{}".format(self.crontab_task, server.username)]
            results = ssh_cli.run_cmdlist(cmd_list)
            if results[0]["code"] == 0 and results[1]["code"] == 0:
                log.info("{} Crontab 定时启动并配置成功".format(server.ipaddress))
            else:
                log.error(results[0]["stdout"])
                log.error(results[1]["stdout"])
                log.error("{} 主机 Crontab 配置失败".format(server.ipaddress))
                exit(2)

    def create_mysql_service_kubernetes(self):
        log.info("渲染初始化Mysql Service in Kubernetes")
        server = ServerModel(self.master_server)
        FileTemplate(self.mysql_cfg, self.mysql_service_file_template, self.mysql_service_file_dest).fill()
        server.send_file(self.mysql_service_file_dest, self.mysql_service_file_remote)

        log.info("在kubernetes集群内创建Mysql Service")
        cmd = "kubectl apply -f {}".format(self.mysql_service_file_remote)
        ssh_cli = ssh_obj(ip=self.master_server[0].ipaddress, user=self.master_server[0].username,
                          password=self.master_server[0].password, port=self.master_server[0].port)
        results = ssh_cli.run_cmd(cmd)
        if results["code"] != 0:
            log.error("kubernetes集群内创建Mysql Service失败:{} {}".format(results["stdout"], results["stderr"]))
            exit(2)

    @status_me("middleware")
    def deploy_mysql(self):
        if self.check_is_deploy(self.mysql_cfg):
            self._generic_config()
            self._fill_init_sql()
            self.send_docker_compose_file()
            self.start()
            self.run_backup_crontab()
            self._create_mgr_cluster()
            self._check()
            self.create_mysql_service_kubernetes()

    def deploy(self):
        self.deploy_mysql()
