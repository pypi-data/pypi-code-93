import argparse
import logging
import os
import re
from os import path
from .. import templates as tpls
from uuid import uuid1
logger = logging.getLogger("Boot Admin")
# TEMPLATES = path.realpath(
#     path.join(path.dirname(__file__), "../templates")   
# )

def create_files_from_tlp(dir_tpl, tpl, dir_target, target):
    with open(path.join(dir_tpl, tpl), "r") as f_tpl:
        tpl_body = f_tpl.read()
        os.makedirs(dir_target, exist_ok=1)
        with open(path.join(dir_target, target), "w+") as f:
            f.write(tpl_body)

def create_files(tpl_body, dir_target, target):
    os.makedirs(dir_target, exist_ok=1)
    if os.path.exists(path.join(dir_target, target)):
        return 
    with open(path.join(dir_target, target), "w+") as f:
        f.write(tpl_body)


def create_project(project=os.getcwd(), name="name"):

    # logger.info("%s" % args.name)
    if project == ".":
        target = os.getcwd()
    else:
        if not project.startswith("/"):
            target = path.join(os.getcwd(), project)
        target = project

    target_app = path.join(target, "app")
    target_app_main = path.join(target, f"app/{name}")
    logger.info("target : %s" % target)
    create_files(tpls.web, target, "web.py")
    create_files(tpls.cmd, target, "cmd.py")
    create_files(tpls.migrate, target, "migrate.py")
    create_files(tpls.pipfile, target, "Pipfile")
    create_files(tpls.readme, target, "README.md")
    create_files(tpls.setting, target_app, "__init__.py")
    create_files(tpls.config % dict(app=name), target_app, "config.py")
    create_files(tpls.env % dict(secret=uuid1()), target, ".env.example")
    create_files(tpls.app_config % dict(app=name), target_app_main, "config.py")
    create_files(tpls.app_api % dict(app=re.sub(r"[^\w]", "", name)), target_app_main, "api.py")
    create_files(tpls.app_cmd % dict(app=re.sub(r"[^\w]", "", name.lower())), target_app_main, "cmd.py")
    create_files(tpls.app_migrations % dict(app=re.sub(r"[^\w]", "", name.lower())), target_app_main, "migrations.py")
    create_files(tpls.app_view  % dict(app=name), target_app_main, "view.py")
    create_files(tpls.app_models % dict(app=name), target_app_main, "models.py")


def create_app(folder, name=None):
    

    logger.info("%s" % name)
    name_app = path.basename(name)
    target_app_main = path.join(folder, name)
    create_files(tpls.app_config % dict(app=name_app), target_app_main, "config.py")
    # create_files(tpls.app_api % dict(app=re.sub(r"[^\w]", "", name_app)), target_app_main, "api.py")
    create_files(tpls.app_view % dict(app=name_app), target_app_main, "view.py")
    create_files(tpls.app_models % dict(app=name_app), target_app_main, "models.py")
    create_files(tpls.app_cmd % dict(app=re.sub(r"[^\w]", "", name_app.lower())), target_app_main, "cmd.py")
    create_files(tpls.app_migrations % dict(app=re.sub(r"[^\w]", "", name_app.lower())), target_app_main, "migrations.py")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname).1s %(asctime).19s] %(message)s',
        datefmt='%y-%m-%d %H:%M:%S'
    )

    create_project()
