from laipvt.handler.middlewarehandler import HarborConfigHandler, MiddlewareConfigHandler
from laipvt.sysutil.gvalue import CHECK_FILE, LAIPVT_BASE_DIR
from laipvt.sysutil.util import path_join, to_object, find, write_to_file
from laipvt.sysutil.gvalue import UPGRADE_INFO_FILE
from laipvt.handler.packagehandler import DeployPackageHandler
from laipvt.handler.confighandler import CheckResultHandler
import json
import os

proj_permit = ("mage", "ocr_standard", "nlp", "commander")

check_result_file = CHECK_FILE
check_result = CheckResultHandler(check_result_file)

harbor_cfg = HarborConfigHandler().get_config_with_check_result()
middleware_cfg = to_object(MiddlewareConfigHandler("mysql").get_all_config_with_check_result())

try:
    harbor_ip = harbor_cfg["harbor"]["ipaddress"][0]
except IndexError:
    harbor_ip = check_result.servers.get_role_ip("harbor")[0]

registry_user = "admin"
registry_hub = "{}:{}".format(harbor_ip, harbor_cfg["harbor"]["http_port"])
registry_passwd = middleware_cfg["harbor"]["password"]

proj_repo_relation = {
    "mage": "mage",
    "commander": "rpa",
    "ocr_standard": "mage"
}

commander_config = {
    "new_version": "v5.5-pvt",
    "versions": ["5.0.0", "5.1.0", "5.2.0", "5.3.0"],
    "namespace": "rpa",
    "major_process": "webapi-global",
    "dbs": ["uibot_global", "uibot_rpa"],
    "migration": "docker run -ti --rm --add-host mysql.default.svc:{MYSQL_REAL_IP} -v {PATH}/appsettings.json:/app/appsettings.json -v {PATH}/appsettings.json.config:/app/Config/appsettings.json registry.cn-beijing.aliyuncs.com/laiye-rpa/commander-upgrade:v2.1 -v {OLD_TAG}"
}

mage_config = {
    "new_version": "v1.15-pvt",
    "versions": [],
    "namespace": "mage",
    "major_process": "document-mining-rpc",
    "dbs": ["im-saas-docuds"],
    "migration": "docker run --rm --entrypoint /home/works/program/mageTool {REPO}/document-mining-innerservice:{NEW_TAG} --operateMode dbupgrade --host {MYSQL_ADDR} --user {MYSQL_USER} --port {MYSQL_PORT} --password {MYSQL_PASS} --toVersion {NEW_TAG} --fromVersion {OLD_TAG} "
}

COMMANDER_APPSETTINGS = """
{{
  "Logging": {{
    "LogLevel": {{
      "Default": "Warning"
    }}
  }},
  "RedisConfig": "{CONFIG_SERVER}",
  "MySQLConfig": "server={MYSQL_ADDR};port={MYSQL_PORT};user id={MYSQL_USER};password={MYSQL_PASS};database=uibot_global;CharSet=utf8mb4;",
  "AllowedHosts": "*"
}}
"""

COMMANDER_APPSETTINGS_CONFIG = """
{{
  "FromDB": "server={MYSQL_ADDR};port={MYSQL_PORT};user id={MYSQL_USER};password={MYSQL_PASS};database=uibot_global;CharSet=utf8mb4;",
  "FromMongo": "mongodb://192.168.0.28:27017",
  "FromFileRoot": "E:\\temp2",
  "ToRedisConfig": "{CONFIG_SERVER}",
  "ToDB": "server={MYSQL_ADDR};port={MYSQL_PORT};user id={MYSQL_USER};password={MYSQL_PASS};database=uibot_global;CharSet=utf8mb4;",
  "RedisConfig": "{CONFIG_SERVER}",
  "CompanyId": {COMPANY_ID}
}}
"""


def check_env():
    if os.path.isfile(CHECK_FILE) and os.path.isdir(path_join(LAIPVT_BASE_DIR, "middleware")):
        return True
    return False

def prepare(tarfile):
    pkg_path = False
    if not os.path.exists(tarfile):
        cwd = [os.getcwd(), check_result.deploy_dir]
        for d in cwd:
            pkg_path = find(d, tarfile, file=True)
            if pkg_path:
                break
    else:
        pkg_path = os.path.join(os.getcwd(), tarfile)
    if not pkg_path:
        print("未找到文件")
        exit(2)
    PKG = os.path.dirname(pkg_path)
    ID = os.path.basename(pkg_path).split(".")[0]
    PKG_DIR = pkg_path.split(".")[0]
    deploy_package = DeployPackageHandler(PKG, ID)

    if not os.path.exists(PKG_DIR):
        # 将项目ID和path写入文件缓存
        project_dict = {"PKG": PKG, "ID": ID}
        write_to_file(UPGRADE_INFO_FILE, json.dumps(project_dict, indent=4))
        deploy_package.unpack()
    return deploy_package