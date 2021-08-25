#!/bin/env python
# -*- encoding: utf-8 -*-
import json
import os
from laipvt.sysutil.conf import status_file


dict_tmpl = {
    "basesystem": {
        "unpack": 0,
        "kubernetes_unpack": 0,
        "install_harbor": 0,
        "install_nginx": 0,
        "add_hosts": 0,
        "install_rpms": 0,
        "system_prepare": 0,
        "init_primary_master": 0,
        "kube_completion": 0,
        "install_network_plugin": 0,
        "join_master": 0,
        "join_node": 0,
        "install_helm": 0,
        "install_istio": 0
    },
    "middleware": {
        "deploy_etcd": 0,
        "deploy_license": 0,
        "deploy_minio": 0,
        "deploy_mysql": 0,
        "deploy_redis": 0,
        "deploy_es": 0,
        "deploy_rabbitmq": 0,
        "deploy_identity": 0,
        "deploy_commander_identity": 0,
        "deploy_monitor": 0,
        "deploy_keepalived": 0,
        "deploy_siber": 0
    },
    "mage": {
        "init_mage_mysql": 0,
        "init_identity_user": 0,
        "init_minio_data": 0,
        "push_mage_images": 0,
        "deploy_configmap": 0,
        "start_mage_service": 0,
        "mage_proxy_on_nginx": 0,
        "mage_transfer_data": 0
    },
    "nlp": {
        "prepare_nlp": 0,
        "push_nlp_images": 0,
        "start_nlp_service": 0
    },
    "ocr": {
        "gen_middleware_conf": 0,
        "prepare_ocr": 0,
        "install_ocr": 0
    },
    "captcha": {
        "prepare_captcha": 0,
        "push_captcha_images": 0,
        "start_captcha_service": 0
    },
    "seal": {
        "prepare_seal": 0,
        "push_seal_images": 0,
        "start_seal_service": 0
    },
    "commander": {
        "status": 0,
        "gen_commander_conf": 0,
        "install": 0,
        "install_harbor": 0,
        "install_nginx": 0,
        "init_rabbitmq": 0,
        "init_redis": 0,
        "init_mysql": 0,
        "init_minio": 0,
        "preparation": 0,
        "istio_proxy": 0,
        "proxy_nginx": 0,
        "init_tenant": 0,
        "apitest": 0
    }
}


class Status:
    def __init__(self):
        self.status_file = status_file
        self.STATUS_SUCCESS = 1
        self.STATUS_FAILED = 2
        self.STATUS_NOT_RUNNING = 0
        self.status_dicts = [self.STATUS_NOT_RUNNING, self.STATUS_SUCCESS, self.STATUS_FAILED]
        if os.path.exists(self.status_file):
            with open(self.status_file, 'r') as fp:
                self.status = json.load(fp)
        else:
            with open(self.status_file, 'a') as fp:
                fp.write(json.dumps(dict_tmpl, indent=4))
            self.status = dict_tmpl

    def reset_status(self):
        status = json.loads(json.dumps(dict_tmpl))
        with open(self.status_file, "w") as sf:
            json.dump(status, sf, indent=4)

    def _reload(self):
        with open(self.status_file) as sf:
            self.status = json.load(sf)

    def _update(self):
        with open(self.status_file, "w") as sf:
            json.dump(self.status, sf, indent=4)
        self._reload()

    def get_status_failed(self, project_name):
        step_list = []
        proj = self.status[project_name]
        for step in proj:
            if proj[step] == self.STATUS_FAILED:
                step_list.append(step)
        return step_list

    def get_status(self, project, step):
        try:
            self._reload()
            return self.status_dicts[self.status[project][step]]
        except KeyError:
            self.update_status(project, step, 0)
            self._reload()
            return self.status_dicts[self.status[project][step]]

    def update_status(self, project, step, value):
        try:
            self.status[project][step] = int(self.status_dicts[value])
            self._update()
            return True
        except IndexError:
            return False
