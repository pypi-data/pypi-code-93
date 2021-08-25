import unittest

from net_models.models import (
    ServiceInstance, InterfaceEncapsulation, Dot1QEncapsulation, ServiceInstanceL2Protocol,
    InterfaceServicePolicy, ServiceInstanceRewrite, RewriteOperation
)


from .BaseTemplateTestIos import BaseTemplateTestIos


class TestIosInterfaceIpv4(BaseTemplateTestIos):

    TEMPLATE_NAME = 'ios_interface_service_instance'
    TEST_CLASS = ServiceInstance

    def test_01(self):
        test_cases = [
            {
                "test_name": "Test-01",
                "data": {
                    "params": ServiceInstance(
                        si_id=1,
                        description="Test Service Instance",
                        encapsulation=InterfaceEncapsulation(
                            encapsulation_type='dot1q',
                            outer_tag=Dot1QEncapsulation(
                                vid_range=[5]
                            )
                        ),
                        bridge_domain=5,
                        l2_protocol=ServiceInstanceL2Protocol(
                            peer=['cdp']
                        ),
                        service_policy=InterfaceServicePolicy(
                            input="SP-IN",
                            output="SP-OUT"
                        ),
                        rewrite=ServiceInstanceRewrite(
                            ingress=RewriteOperation(
                                action='pop',
                                tag=1,
                                symetric=True
                            )
                        ),
                        enabled=False
                    )
                },
                "result": (
                    " service instance 1 ethernet\n"
                    "  description Test Service Instance\n"
                    "  encapsulation dot1q 5\n"
                    "  rewrite ingress tag pop 1 symetric\n"
                    "  l2protocol peer cdp\n"
                    "  bridge-domain 5\n"
                    "  service-policy input SP-IN\n"
                    "  service-policy output SP-OUT\n"
                    "  shutdown\n"
                )
            },
            {
                "test_name": "Test-02",
                "data": {
                    "params": ServiceInstance(
                        si_id=1,
                        encapsulation=InterfaceEncapsulation(encapsulation_type='untagged')
                    )
                },
                "result": (
                    " service instance 1 ethernet\n"
                    "  encapsulation untagged\n"
                )
            }
        ]
        self.maxDiff = None
        self.common_testbase(test_cases=test_cases)

if __name__ == '__main__':
    unittest.main()
