from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.sysutil.util import path_join, status_me


class CaptchaController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(CaptchaController, self).__init__(check_result, service_path)
        self.project = "mage"

        self.captcha_model_src = path_join(self.data_dir, "verification-tf-serving/model")
        self.captcha_model_remote = path_join(self.deploy_dir, "verification-tf-serving/model")

    @status_me("captcha")
    def prepare_captcha(self):
        self._send_file(src=self.captcha_model_src, dest=self.captcha_model_remote)

    @status_me("captcha")
    def push_captcha_images(self):
        self.push_images(self.project)

    @status_me("captcha")
    def start_captcha_service(self):
        self.start_service(project=self.project, version=self.private_deploy_version)

    def run(self):
        self.prepare_captcha()
        self.push_captcha_images()
        self.start_captcha_service()
