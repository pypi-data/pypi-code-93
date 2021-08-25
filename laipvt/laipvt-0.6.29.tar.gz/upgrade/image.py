from laipvt.model.cmd import DockerImageModel
from laipvt.model.harbor import HarborModel
from laipvt.sysutil.util import path_join, log
import os

def ImportImage(project, path, user, passwd, addr):
    harbor = HarborModel(addr, user, passwd)
    if project not in harbor.list_project():
        harbor.create_project(project)
    image_path = path_join(path, "images")
    for image_name in os.listdir(image_path):
        img_p = path_join(image_path, image_name)
        log.info("将镜像push到私有仓库: {}".format(img_p))
        # print(image_path)
        docker = DockerImageModel(image=img_p, project=project, repo=addr)
        docker.run()