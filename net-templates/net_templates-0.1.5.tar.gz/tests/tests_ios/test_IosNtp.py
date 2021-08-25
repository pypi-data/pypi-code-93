import unittest
from tests.tests_ios.BaseTemplateTestIos import BaseTemplateTestIos
from net_models.models.services.ServerModels import NtpKey, NtpServer, NtpConfig, NtpAccessGroups


class TestIosNtpAuthenticationKey(BaseTemplateTestIos):

    TEST_CLASS = NtpKey
    TEMPLATE_NAME = 'ios_ntp_authentication_key'

    def test_01(self):
        test_cases = [
            {
                "test_name": "Test-01",
                "data": {
                    "params": NtpKey(
                        key_id=1,
                        encryption_type=0,
                        method="md5",
                        value="SuperSecret",
                        trusted=True
                    )
                },
                "result": (
                    "ntp authentication-key 1 md5 SuperSecret 0\n"
                )
            }
        ]
        super().common_testbase(test_cases=test_cases)


class TestIosNtpTrustedKey(BaseTemplateTestIos):

    TEST_CLASS = NtpKey
    TEMPLATE_NAME = 'ios_ntp_trusted_key'

    def test_01(self):
        test_cases = [
            {
                "test_name": "Test-01",
                "data": {
                    "params": NtpKey(
                        key_id=1,
                        encryption_type=0,
                        method="md5",
                        value="SuperSecret",
                        trusted=True
                    )
                },
                "result": (
                    "ntp trusted-key 1\n"
                )
            }
        ]
        super().common_testbase(test_cases=test_cases)


class TestIosNtpKeys(BaseTemplateTestIos):

    TEST_CLASS = NtpKey
    TEMPLATE_NAME = 'ios_ntp_keys'

    def test_01(self):
        test_cases = [
            {
                "test_name": "Test-01",
                "data": {
                    "params": [
                        NtpKey(
                            key_id=1,
                            encryption_type=0,
                            method="md5",
                            value="SuperSecret",
                            trusted=True
                        ),
                        NtpKey(
                            key_id=2,
                            encryption_type=0,
                            method="md5",
                            value="SuperSecret2",
                            trusted=True
                        ),
                        NtpKey(
                            key_id=3,
                            encryption_type=0,
                            method="md5",
                            value="SuperSecret3",
                            trusted=False
                        )
                    ]
                },
                "result": (
                    "ntp authentication-key 1 md5 SuperSecret 0\n"
                    "ntp authentication-key 2 md5 SuperSecret2 0\n"
                    "ntp authentication-key 3 md5 SuperSecret3 0\n"
                    "ntp trusted-key 1\n"
                    "ntp trusted-key 2\n"
                )
            }
        ]
        super().common_testbase(test_cases=test_cases)


class TestNtpSession(BaseTemplateTestIos):

    TEST_CLASS = NtpServer
    TEMPLATE_NAME = 'ios_ntp_session'

    def test_01(self):
        test_cases = [
            {
                "test_name": "Test-Server-01",
                "data": {
                    "params": NtpServer(
                        server="192.0.2.1",
                        vrf="TEST-VRF",
                        prefer=True
                    ),
                    "session_type": "server"
                },
                "result": (
                    "ntp server vrf TEST-VRF 192.0.2.1 prefer\n"
                )
            }
        ]
        super().common_testbase(test_cases=test_cases)


class TestIosNtpConfig(BaseTemplateTestIos):

    TEST_CLASS = NtpConfig
    TEMPLATE_NAME = 'ios_ntp'

    def test_01(self):
        test_cases = [
            {
                "test_name": "Test-Model-01",
                "data": {
                    "params": NtpConfig(
                        authenticate=True,
                        servers=[
                            NtpServer(
                                server="192.0.2.1",
                                vrf="MGMT",
                                key_id=1,
                                prefer=True
                            ),
                            NtpServer(
                                server="192.0.2.2",
                                vrf="MGMT",
                                key_id=1
                            )
                        ],
                        ntp_keys=[
                            NtpKey(
                                value="SuperSecret",
                                encryption_type=0,
                                key_id=1,
                                method="md5",
                                trusted=True
                            )
                        ],
                        peers=[
                            NtpServer(
                                server="192.0.2.10",
                                vrf="MGMT",
                                key_id=1
                            )
                        ],
                        access_groups=NtpAccessGroups(
                            serve_only=1,
                            query_only=2,
                            serve=3,
                            peer=4
                        ),
                        src_interface="Loopback0"
                    )
                },
                "result": (
                    "ntp authenticate\n"
                    "ntp authentication-key 1 md5 SuperSecret 0\n"
                    "ntp trusted-key 1\n"
                    "ntp source Loopback0\n"
                    "ntp server vrf MGMT 192.0.2.1 key 1 prefer\n"
                    "ntp server vrf MGMT 192.0.2.2 key 1\n"
                    "ntp peer vrf MGMT 192.0.2.10 key 1\n"
                    "ntp access-group serve-only 1\n"
                    "ntp access-group query-only 2\n"
                    "ntp access-group serve 3\n"
                    "ntp access-group peer 4\n"
                )
            }
        ]
        super().common_testbase(test_cases=test_cases)

del BaseTemplateTestIos

if __name__ == '__main__':
    unittest.main()