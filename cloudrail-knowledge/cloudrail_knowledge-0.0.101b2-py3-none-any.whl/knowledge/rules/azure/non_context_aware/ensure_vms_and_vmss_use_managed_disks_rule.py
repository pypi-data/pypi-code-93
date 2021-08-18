from typing import Dict, List, Union

from cloudrail.knowledge.context.azure.azure_environment_context import AzureEnvironmentContext
from cloudrail.knowledge.context.azure.vm.azure_virtual_machine import AzureVirtualMachine
from cloudrail.knowledge.context.azure.vmss.azure_virtual_machine_scale_set import AzureVirtualMachineScaleSet
from cloudrail.knowledge.rules.azure.azure_base_rule import AzureBaseRule
from cloudrail.knowledge.rules.base_rule import Issue
from cloudrail.knowledge.rules.rule_parameters.base_paramerter import ParameterType


class EnsureVmAndVmssUseManagedDisksRule(AzureBaseRule):

    def get_id(self) -> str:
        return 'non_car_virtual_machines_and_virtual_machine_scale_sets_only_use_managed_disks'

    def execute(self, env_context: AzureEnvironmentContext, parameters: Dict[ParameterType, any]) -> List[Issue]:
        issues: List[Issue] = []
        for virtual_machine in env_context.virtual_machines:
            if issues_found := self._get_unmanaged_disks_usage(virtual_machine):
                issues.extend(issues_found)
        for vmss in env_context.virtual_machines_scale_sets:
            if issues_found := self._get_unmanaged_disks_usage(vmss):
                issues.extend(issues_found)
        return issues

    def should_run_rule(self, environment_context: AzureEnvironmentContext) -> bool:
        return bool(environment_context.virtual_machines or environment_context.virtual_machines_scale_sets)

    @staticmethod
    def _get_unmanaged_disks_usage(vm_entity: Union[AzureVirtualMachine, AzureVirtualMachineScaleSet]) -> list:
        issues: List[Issue] = []
        disks_types_unmanaged = set()
        if not vm_entity.disk_settings.os_disk.is_managed_disk:
            disks_types_unmanaged.add('os_disk')
        elif (any(not disk.is_managed_disk for disk in vm_entity.disk_settings.data_disks)):
            disks_types_unmanaged.add('data_disk')
        if disks_types_unmanaged:
            if len(disks_types_unmanaged) > 1:
                issues.append(
                    Issue(
                        f"The {vm_entity.get_type()} `{vm_entity.get_friendly_name()}` is using an unmanaged disk for both it's os_disk and one of it's managed disks",
                        vm_entity, vm_entity))
            else:
                issues.append(
                    Issue(
                        f"The {vm_entity.get_type()} `{vm_entity.get_friendly_name()}` is using an unmanaged disk for disk type {next(iter(disks_types_unmanaged))}", vm_entity, vm_entity))
        return issues
