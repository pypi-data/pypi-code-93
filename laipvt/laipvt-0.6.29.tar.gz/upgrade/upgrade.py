from base import commander_config, mage_config, check_result, COMMANDER_APPSETTINGS_CONFIG, COMMANDER_APPSETTINGS
from laipvt.sysutil.util import run_local_cmd, to_object, log, path_join, write_to_file
from laipvt.model.sql import SqlModule
from laipvt.handler.middlewarehandler import MiddlewareConfigHandler, IdentityConfigHandler, HarborConfigHandler
from laipvt.handler.packagehandler import ServicePackageHandler
from laipvt.controller.middleware.identity import IdentityController
from laipvt.controller.service.license import LicenseController
from laipvt.controller.service.mage import MageController
from laipvt.controller.service.commander import CommanderController
from laipvt.controller.service.ocr_standard import OcrStandardController
import os


class UpgradeInterface():

    def __init__(self, proj, file_path, config):
        self.proj = proj
        self.cfg = to_object(config)
        self.middleware_server_list = check_result.servers.get_role_ip("master")
        self.middleware_cfg = to_object(MiddlewareConfigHandler("mysql").get_all_config_with_check_result())
        for k, v in self.middleware_cfg.items():
            if not self.middleware_cfg[k]["ipaddress"]:
                self.middleware_cfg[k]["ipaddress"] = self.middleware_server_list
        self.file_path = file_path
        self.db_backup_dir = path_join(file_path, proj, "backup")
        self.backup_result = []
        self.db_backup = False
        self.harbor_cfg = HarborConfigHandler().get_config_with_check_result()
        try:
            harbor_ip = self.harbor_cfg["harbor"]["ipaddress"][0]
        except IndexError:
            harbor_ip = check_result.servers.get_role_ip("harbor")[0]
        self.registry_hub = "{}:{}".format(harbor_ip, self.harbor_cfg["harbor"]["http_port"])

    
    def parse_docker_image_tag(self, image):
        return image.split(":")[-1]

    def check_version(self):
        cmd = "kubectl -n {} get deploy {} -o jsonpath={{..image}}".format(
            self.cfg.namespace, self.cfg.major_process
        )
        res = run_local_cmd(cmd)
        if res["code"] != 0:
            log.error("命令执行失败")
            log.error(res["stdout"])
            exit(2)
        else:
            return self.parse_docker_image_tag(res["stdout"])

    def check_install_identity(self):
        info = to_object({
            "name": "ids-server",
            "check_cmd": "docker ps --format \"{{ .Image }}\" --filter name=ids-server",
            "tag": "v1.1-pvt"
        })
        cmd_res = run_local_cmd(info.check_cmd)
        if cmd_res["code"] != 0:
            log.info("identity not found. deploy now")
        else:
            if cmd_res["stdout"] == info.tag:
                log.info("identity is newest version")
                return
            else:
                log.info("identity version: {}. upgrade now".format(
                    cmd_res["stdout"]
                ))
        identity_path = path_join(self.file_path, "middleware", "identity")
        identity_config = IdentityConfigHandler()
        s = IdentityController(check_result, identity_config, identity_path)
        s.deploy()

    def check_install_license(self):
        info = to_object({
            "name": "license-manager",
            "check_cmd": "kubectl -n mid get deploy license-manager -o jsonpath={..image}",
            "tag": "v2.0-pvt"
        })
        cmd_res = run_local_cmd(info.check_cmd)
        if cmd_res["code"] != 0:
            log.info("license not found. deploy now")
        else:
            if cmd_res["stdout"] == info.tag:
                log.info("license is newest version")
                return
            else:
                log.info("license version: {}. upgrade now".format(
                    cmd_res["stdout"]
                ))
        fp = ServicePackageHandler(self.file_path, "license")
        fp.unpack()
        s = LicenseController(check_result, fp.parse())
        s.deploy()


    def backup(self):
        db = SqlModule(host=self.middleware_cfg.mysql.ipaddress[0], port=int(self.middleware_cfg.mysql.port),
                        user=self.middleware_cfg.mysql.username, passwd=self.middleware_cfg.mysql.password)
        if not os.path.isdir(self.db_backup_dir):
            os.makedirs(self.db_backup_dir)
        for database in self.cfg["dbs"]:
            res = db.backup_db(database, self.db_backup_dir)
            r = {"db": database, "result": res}
            self.backup_result.append(r)
        self.db_backup = True

    def check_backup(self):
        if not self.db_backup:
            log.error("db not backup")
            exit(2)
        for i in self.backup_result:
            if i["result"]:
                lf = log.info
            else:
                lf = log.error
                lf("database {} backup failed".format(i["db"]))
            lf("db name: {}, backup status: {}".format(i["db"], i["result"]))

    def migration(self, p, force=False):
        pass

    def upgrade(self, p, service_path):
        pass
    
    def check(self):
        pass

    def run(self, p, service_path, force=False):
        self.check_install_license()
        self.check_install_identity()
        self.backup()
        self.check_backup()
        self.migration(p, force)
        self.upgrade(p, service_path)

class CommanderUpgrade(UpgradeInterface):
    def __init__(self, file_path):
        super().__init__("commander", file_path, commander_config)

    def parse_commander_tag(self, tag: str):
        # v5.5-pvt
        s = tag.split(".")
        return "{}.{}.0".format(s[0][-1], s[1].split("-")[0])

    def load_migration_image(self):
        img_path = path_join(self.file_path, self.proj, "upgrade", "commander-upgrade.tar")
        if os.path.isfile(img_path):
            cmd = "docker load < {}".format(img_path)
            run_local_cmd(cmd)
            log.info("导入数据迁移镜像成功")
        else:
            log.error("数据迁移镜像文件不存在")
            exit(3)

    def migration(self, p, force=False):
        if not force:
            if len(self.backup_result) > 0:
                for i in self.backup_result:
                    if not i["result"]:
                        log.error("database {} backup failed, cannot run migration".format(i["db"]))
                        exit(2)
        self.load_migration_image()
        if self.middleware_cfg["redis"]["is_deploy"]:
            CONFIG_SERVER = "\,".join(
                [
                    "{}:{}\,serviceName={}\,password={}\,allowAdmin=true".format(
                        server,
                        self.middleware_cfg["redis"]["port_sentinel"],
                        self.middleware_cfg["redis"]["master_name"],
                        self.middleware_cfg["redis"]["password"]
                    ) for server in check_result.servers.get_role_ip("master")
                ]
            )
        else:
            CONFIG_SERVER = "{}:{}\,password={}".format(
                self.middleware_cfg["redis"]["ipaddress"][0],
                self.middleware_cfg["redis"]["port"],
                self.middleware_cfg["redis"]["password"])
        MYSQL_ADDR = self.middleware_cfg.mysql.ipaddress[0]
        MYSQL_PORT = int(self.middleware_cfg.mysql.port)
        MYSQL_USER = self.middleware_cfg.mysql.username
        MYSQL_PASS = self.middleware_cfg.mysql.password
        db = SqlModule(host=self.middleware_cfg.mysql.ipaddress[0], port=int(self.middleware_cfg.mysql.port),
                        user=self.middleware_cfg.mysql.username, passwd=self.middleware_cfg.mysql.password)
        db.use_db("uibot_global")
        COMPANY_ID = db.select("SELECT id from tbl_company WHERE is_deleted = 0  ORDER BY id LIMIT 1")

        appsettings = COMMANDER_APPSETTINGS.format(
            CONFIG_SERVER=CONFIG_SERVER.replace('\\', ""),
            MYSQL_ADDR=MYSQL_ADDR,
            MYSQL_PORT=MYSQL_PORT,
            MYSQL_USER=MYSQL_USER,
            MYSQL_PASS=MYSQL_PASS
        )

        appsettings_config = COMMANDER_APPSETTINGS_CONFIG.format(
            CONFIG_SERVER=CONFIG_SERVER.replace('\\', ""),
            MYSQL_ADDR=MYSQL_ADDR,
            MYSQL_PORT=MYSQL_PORT,
            MYSQL_USER=MYSQL_USER,
            MYSQL_PASS=MYSQL_PASS,
            COMPANY_ID=COMPANY_ID[0]["id"]
        )
        write_to_file(path_join(self.file_path, self.proj, "upgrade", "appsettings.json"), appsettings)
        write_to_file(path_join(self.file_path, self.proj, "upgrade", "appsettings.json.config"), appsettings_config)
        old_tag = self.check_version()
        mysql_real_ip = run_local_cmd("kubectl get svc mysql -o jsonpath={..clusterIP}")["stdout"]
        cmd = self.cfg["migration"].format(
            MYSQL_REAL_IP=mysql_real_ip,
            PATH=path_join(self.file_path, self.proj, "upgrade"),
            OLD_TAG=self.parse_commander_tag(old_tag)
        )
        log.info("开始数据迁移，请勿中断操作")
        res = run_local_cmd(cmd)
        if res["code"] == 0:
            log.info("数据迁移成功")
        else:
            log.error("数据迁移失败")
            log.error(res["stdout"])
            exit(2)

    def upgrade(self, p, service_path):
        commander = CommanderController(check_result, service_path)
        commander.upgrade_service(p)
        commander.deploy_istio()

class MageUpgrade(UpgradeInterface):
    def __init__(self, file_path):
        super(MageUpgrade, self).__init__("mage", file_path, mage_config)

    def migration(self, p, force=False):
        if not force:
            if len(self.backup_result) > 0:
                for i in self.backup_result:
                    if not i["result"]:
                        log.error("database {} backup failed, cannot run migration".format(i["db"]))
                        exit(2)
        old_tag = self.check_version()
        cmd = self.cfg["migration"].format(
            REPO=path_join(self.registry_hub, p),
            NEW_TAG=self.cfg["new_version"],
            MYSQL_ADDR=self.middleware_cfg.mysql.ipaddress[0],
            MYSQL_PORT=int(self.middleware_cfg.mysql.port),
            MYSQL_USER=self.middleware_cfg.mysql.username,
            MYSQL_PASS=self.middleware_cfg.mysql.password,
            OLD_TAG=old_tag
        )
        run_local_cmd(cmd)

    def upgrade(self, p, service_path):
        mage = MageController(check_result, service_path)
        mage.deploy_configmap()
        mage.upgrade_service(p)

class OcrStandardUpgrade(UpgradeInterface):
    def __init__(self, file_path):
        super(OcrStandardUpgrade, self).__init__("ocr_standard", file_path, mage_config)

    def upgrade(self, p, service_path):
        o = OcrStandardController(check_result, service_path)
        o.upgrade_service(p)