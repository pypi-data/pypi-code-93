from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.sysutil.util import path_join, status_me


class SealController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(SealController, self).__init__(check_result, service_path)
        self.project = "mage"

        self.seal_model_src = path_join(self.data_dir, "ocr-seal-tf-serving/model")
        self.seal_model_remote = path_join(self.deploy_dir, "ocr-seal-tf-serving/model")

    @status_me("seal")
    def prepare_seal(self):
        self._send_file(src=self.seal_model_src, dest=self.seal_model_remote)

    @status_me("seal")
    def push_seal_images(self):
        self.push_images(self.project)

    @status_me("seal")
    def start_seal_service(self):
        self.start_service(project=self.project, version=self.private_deploy_version)

    def run(self):
        self.prepare_seal()
        self.push_seal_images()
        self.start_seal_service()
