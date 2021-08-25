from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.sysutil.util import path_join, status_me


class NlpController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(NlpController, self).__init__(check_result, service_path)
        self.project = "mage"

        self.info_engine_data_src = path_join(self.data_dir, "laiye-information-extract-engine")
        self.info_engine_data_remote = path_join(self.deploy_dir, "laiye-information-extract-engine")
        self.doc_classifer_data_src = path_join(self.data_dir, "laiye-doc-classifier")
        self.doc_classifer_data_remote = path_join(self.deploy_dir, "laiye-doc-classifier")
        self.bert_service_data_src = path_join(self.data_dir, "bert-service-tf")
        self.bert_service_data_remote = path_join(self.deploy_dir, "bert-service-tf")
        self.poi_search_engine_src = path_join(self.data_dir, "laiye-poi-search-engine")
        self.poi_search_engine_remote = path_join(self.deploy_dir, "data", "laiye-poi-search-engine")
        self.bert_service_pt_data_src = path_join(self.data_dir, "bert-service-pt")
        self.bert_service_pt_data_remote = path_join(self.deploy_dir, "bert-service-pt")

    @status_me("nlp")
    def prepare_nlp(self):
        self._send_file(src=self.info_engine_data_src, dest=self.info_engine_data_remote)
        self._send_file(src=self.doc_classifer_data_src, dest=self.doc_classifer_data_remote)
        self._send_file(src=self.bert_service_data_src, dest=self.bert_service_data_remote)
        self._send_file(src=self.bert_service_pt_data_src, dest=self.bert_service_pt_data_remote)
        self._send_file(src=self.poi_search_engine_src, dest=self.poi_search_engine_remote)

    @status_me("nlp")
    def push_nlp_images(self):
        self.push_images(self.project)

    @status_me("nlp")
    def start_nlp_service(self):
        self.start_service(project=self.project, version=self.private_deploy_version)

    def run(self):
        self.prepare_nlp()
        self.push_nlp_images()
        self.start_nlp_service()
