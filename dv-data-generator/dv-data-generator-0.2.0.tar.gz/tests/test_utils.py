import unittest

from .debug_dbm_service import DebugDbmService
from dv_data_generator.helper.dbm import get_report_url, try_run


class UtilsTests(unittest.TestCase):

    def test_get_report_url_success(self):
        gcs_path = "gcs://"
        service = DebugDbmService(
            response={
                "metadata": {
                    "googleCloudStoragePathForLatestReport": gcs_path,
                    "running": False,
                }
            }
        )
        report_url = get_report_url(service, gcs_path, sleep_limit=0)

        self.assertEqual(
            report_url,
            gcs_path,
            msg="The gcs path should be returned by the `get_report_url` method",
        )

    def test_get_report_url_failure(self):
        gcs_path = "gcs://"
        service = DebugDbmService(
            response={
                "metadata": {
                    "googleCloudStoragePathForLatestReport": gcs_path,
                    "running": True,
                }
            }
        )

        kwargs = {"service": service, "gcs_path": gcs_path, "sleep_limit": 0}

        self.assertRaises(
            Exception,
            get_report_url,
            kwargs=kwargs,
            msg="The method should fail because the report is running longer than the sleep period",
        )

        service = DebugDbmService(response={})

        kwargs = {"service": service, "gcs_path": gcs_path, "sleep_limit": 0}

        self.assertRaises(
            Exception,
            get_report_url,
            kwargs=kwargs,
            msg="The method should fail because the response is not correct",
        )

        service = DebugDbmService(response={}, exception=True)

        kwargs = {"service": service, "gcs_path": gcs_path, "sleep_limit": 0}

        self.assertRaises(
            Exception,
            get_report_url,
            kwargs=kwargs,
            msg="The method should fail because the service threw an exception",
        )

    def test_try_run(self):
        faillure_answer = "FAILLURE"
        input_value = True

        def testing_method(x=None):
            return x

        def faillure_method(x=None):
            return faillure_answer

        def exception_method(x=None):
            raise Exception("Exception method raised this")

        answer = try_run(testing_method, input_value,
                         faillure_method, sleep_limit=0)
        self.assertEqual(answer, input_value,
                         "The input value must be returned")

        answer = try_run(exception_method, input_value,
                         faillure_method, sleep_limit=0)
        self.assertEqual(answer, faillure_answer,
                         "The fallback answer must be returned")

        answer = try_run(exception_method, input_value,
                         faillure_method, sleep_limit=0)

        kwargs = {
            "method": exception_method,
            "value": input_value,
            "fail_method": exception_method,
            "sleep_limit": 0
        }

        self.assertRaises(Exception, try_run, kwargs=kwargs,
                          msg="When even the `fail_method` fails, the error must be raised")
