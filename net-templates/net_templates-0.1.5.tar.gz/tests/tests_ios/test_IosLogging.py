import unittest
from tests.tests_ios.BaseTemplateTestIos import BaseTemplateTestIos
from net_models.models.services.ServerModels import LoggingDiscriminatorAction, LoggingDiscriminator, LoggingServer, LoggingConfig


class TestIosLoggingDiscriminator(BaseTemplateTestIos):

    TEST_CLASS = LoggingDiscriminator
    TEMPLATE_NAME = 'ios_logging_discriminator'

    def test_01(self):
        test_cases = [
            {
                "test_name": "Test-01",
                "data": {
                    "params": LoggingDiscriminator(
                        name="DROP-IFD",
                        actions=[
                            LoggingDiscriminatorAction(
                                match="mnemonics",
                                value="IFDOWN",
                                action="drops"
                            )
                        ]
                    )
                },
                "result": (
                    "logging discriminator DROP-IFD mnemonics drops IFDOWN\n"
                )
            },
            {
                "test_name": "Test-02",
                "data": {
                    "params": LoggingDiscriminator(
                        name="DROP-IFD",
                        actions=[
                            LoggingDiscriminatorAction(
                                match="mnemonics",
                                value="IFDOWN",
                                action="drops"
                            ),
                            LoggingDiscriminatorAction(
                                match="msg-body",
                                value="Ethernet0/1",
                                action="drops"
                            )
                        ]
                    )
                },
                "result": (
                    "logging discriminator DROP-IFD mnemonics drops IFDOWN msg-body drops Ethernet0/1\n"
                )
            }
        ]
        super().common_testbase(test_cases=test_cases)



del BaseTemplateTestIos

if __name__ == '__main__':
    unittest.main()