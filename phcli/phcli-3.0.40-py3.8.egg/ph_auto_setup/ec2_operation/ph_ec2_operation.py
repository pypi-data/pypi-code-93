import os
import json
from phcli.ph_auto_setup.ec2_operation.ph_jupyter_operation import PhJupyterOperation
from phcli.ph_auto_setup.ec2_operation.ph_c9_operation import Phc9Operation


class PhEc2Operation(object):
    def __init__(self, **kwargs):
        self.jupyter_name = kwargs.get('name', None)
        self.c9_name = kwargs.get('name', None)
        self.ec2_operation = kwargs.get('operation', None)
        self.ec2_ide = kwargs.get('ide', None)

    def choice_ide(self):
        if self.ec2_ide == "jupyter":
            PhJupyterOperation.choice_operation(self)
        if self.ec2_ide == "c9":
            Phc9Operation.choice_operation(self)

