import pytest
from django.conf import settings

from w.services.technical.models.yousign import YouSignRequest
from w.services.technical.yousign_service import YouSignService
from w.tests.helpers import request_test_helper
from w.tests.mixins.testcase_mixin import TestCaseMixin


class TestYouSignService(TestCaseMixin):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        data = {
            "procedure_name": "Test de création",
            "procedure_desc": "Un test pour valider le fonctionnement",
            "filename": cls.get_datasets_dir("pdf/exemple_pdf.pdf"),
            "member_firstname": "Jean",
            "member_lastname": "Bono",
            "member_email": "jb@gmail.fr",
            "member_phone": "+33612345678",
            "webhook_url": "url_de_webhook.fr/token/",
            "file_signature_position": "123,456,789,112",
        }
        cls.yousign_request = YouSignRequest(**data)
        cls.fake_file_id = "fake_file_id"

    @staticmethod
    def setup_method():
        # clear service on each test
        YouSignService.clear()
        YouSignService.init(settings.YOUSIGN_API_URL, settings.YOUSIGN_API_KEY)

    """
    create
    """

    def test_create_with_service_not_initialized_raise_runtime_error(self):
        """ Ensure method raise RuntimeError if service is not initialized """
        YouSignService.clear()
        match = "Service YouSignService must be initialized first"
        with pytest.raises(RuntimeError, match=match):
            YouSignService.create(self.yousign_request)

    def test_create_with_file_not_found_raise_runtime_error(self):
        """ Ensure method raise RuntimeError if file does not exists """
        # copy valid yousign request
        wrong_request = YouSignRequest(**self.yousign_request.to_dict())
        wrong_request.filename = "unknown.pdf"
        match = f"{wrong_request.filename} does not exists"
        with pytest.raises(RuntimeError, match=match):
            YouSignService.create(wrong_request)

    def test_create_with_failed_upload_raise_runtime_error(self):
        """ Ensure method raise """
        response = {
            "json_file": self.get_datasets_dir("yousign/files_bad_request.json"),
        }
        match = (
            "Failed to upload .*exemple_pdf.pdf.*\(400 - Bad Request\) "
            ': content: Format not allowed for this field. "application\/vnd.'
            'openxmlformats-officedocument.spreadsheetml.sheet" given.'
        )
        with request_test_helper.request_failure(response, method="post"):
            with pytest.raises(RuntimeError, match=match):
                YouSignService.create(self.yousign_request)

    def test_create_with_failed_create_procedure_raise_runtime_error(self):
        """ Ensure method raise RuntimeError """
        responses = request_test_helper.get_response(
            json_file=self.get_datasets_dir("yousign/files_success.json")
        ) + request_test_helper.get_400_response(
            json_file=self.get_datasets_dir("yousign/procedures_bad_request.json")
        )

        match = "Failed to create procedure .*"
        with request_test_helper.mock_request(responses, method="post"):
            with pytest.raises(RuntimeError, match=match):
                YouSignService.create(self.yousign_request)

    def test_create_with_success_return_dict(self):
        """ Ensure method succeed """
        response = {
            "json_file": [
                self.get_datasets_dir("yousign/files_success.json"),
                self.get_datasets_dir("yousign/procedures_success.json"),
            ]
        }
        with request_test_helper.request_success(response, method="post") as m:
            result = YouSignService.create(self.yousign_request)
        self.assert_equals_resultset(
            {"result": result, "mocks": self.get_mock_calls(m)}
        )

    """
    get_file
    """

    def test_get_file_with_service_not_initialized_raise_runtime_error(self):
        """ Ensure method raise RuntimeError if service is not initialized """
        YouSignService.clear()
        match = "Service YouSignService must be initialized first"
        with pytest.raises(RuntimeError, match=match):
            YouSignService.get_file(self.fake_file_id)

    def test_get_file_with_file_not_found_raise_runtime_error(self):
        """ Ensure method raise RuntimeError if file does not exists """
        # copy valid yousign request
        match = "Failed to get contract file"
        response = {
            "json_file": self.get_datasets_dir("yousign/files_bad_request.json"),
        }
        with request_test_helper.request_failure(response, method="get"):
            with pytest.raises(RuntimeError, match=match):
                YouSignService.get_file(self.fake_file_id)

    def test_get_file_with_success_return_base64(self):
        """ Ensure method succeed """
        response = {
            "json_file": [
                self.get_datasets_dir("yousign/files_base64_response"),
            ]
        }
        with request_test_helper.request_success(response, method="get") as m:
            result = YouSignService.get_file(self.fake_file_id)
        self.assert_equals_resultset(
            {"result": result, "mocks": self.get_mock_calls(m)}
        )
