from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.interface.kubeinterface import KubeInterface
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.handler.packagehandler import KubePackageHandler


class KubeController(KubeInterface):
    def __init__(self, result: CheckResultHandler, kube: KubePackageHandler.parse, *args, **kwargs):
        super(KubeController, self).__init__(result, kube, *args, **kwargs)
