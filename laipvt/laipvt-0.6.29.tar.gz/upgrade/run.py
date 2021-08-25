from base import check_env, registry_user, registry_hub, registry_passwd, proj_permit, check_result, prepare, proj_repo_relation
from image import ImportImage
from upgrade import CommanderUpgrade, MageUpgrade, OcrStandardUpgrade
from laipvt.sysutil.util import log, path_join
from laipvt.handler.packagehandler import ServicePackageHandler
import sys
import os

upgrade_proj = {
    "commander": CommanderUpgrade,
    "mage": MageUpgrade,
    "ocr_standard": OcrStandardUpgrade
}

def check():
    if check_env:
        log.info("环境检查通过，继续执行")
    else:
        log.error("未检测到环境信息！")
        exit(1)

def run(proj, file_path, force):
    fp = file_path.split(".")[0]
    deploy_package = prepare(file_path)
    check()
    proj_base_dir = path_join(deploy_package.root_dir, proj)
    svc_pkg = ServicePackageHandler(deploy_package.root_dir, proj)
    if not os.path.exists(proj_base_dir):
        svc_pkg.unpack()
    try:
        p = proj_repo_relation[proj]
    except:
        p = "mage"
    ImportImage(p, proj_base_dir, registry_user, registry_passwd, registry_hub)
    up = upgrade_proj[proj](fp)
    up.run(p, svc_pkg.parse(), force)

if __name__ == "__main__":
    try:
        proj = sys.argv[1]
        file_path = sys.argv[2]
        try:
            force = sys.argv[3]
            if force != True or force != False:
                exit(2)
        except IndexError:
            force = False

        if proj not in proj_permit:
            log.error("参数错误")
            exit(1)
        
        if not os.path.isfile(file_path):
            log.error("参数错误")
            exit(1)
        run(proj, file_path, force)
    except IndexError:
        log.error("参数长度错误")
        exit(1)
